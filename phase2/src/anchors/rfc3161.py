"""RFC 3161 timestamp authority adapter.

Profiles:
- ``rfc3161``: reserved production profile. Live issuance/verification currently
  fails closed until a standards-conformant CMS/RFC 3161 verifier with independent
  trust-anchor validation is integrated.
- ``rfc3161-recorded-fixture``: offline fixture tokens signed by a test TSA key.

A certificate copied inside a receipt is verifier material, never an independent
trust root. Production C2 claims MUST NOT be established by this module until the
full CMS signer, signed-attributes, TSA certificate, EKU/policy, and chain checks
are implemented against a verifier-pinned trust policy.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
from datetime import datetime, timezone
from typing import Any

from asn1crypto import algos, core, tsp
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

from anchors.base import AnchorAdapter, TemporalClaim
from support import Phase2Error, sha256_hex, validate_schema

DEFAULT_TSA_URL = "http://timestamp.digicert.com"
RFC3161_TRUST_BOUNDARY = (
    "Production RFC 3161 verification is disabled in this implementation. A future "
    "profile must validate CMS/RFC 3161 semantics and a TSA chain against an "
    "independently pinned verifier trust policy before establishing C2."
)
RFC3161_FIXTURE_TRUST_BOUNDARY = (
    "rfc3161-recorded-fixture tokens are verified under an independently supplied "
    "test TSA trust root. They do not establish a third-party TSA attestation."
)

OID_SHA256 = "2.16.840.1.101.3.4.2.1"


def _load_private_key(pem: str | bytes) -> PrivateKeyTypes:
    try:
        return serialization.load_pem_private_key(
            pem.encode("utf-8") if isinstance(pem, str) else pem,
            password=None,
        )
    except (TypeError, ValueError) as exc:
        raise Phase2Error("invalid RFC 3161 fixture private key PEM", code="TS3183") from exc


def _load_public_key(pem: str | bytes) -> PublicKeyTypes:
    try:
        return serialization.load_pem_public_key(
            pem.encode("utf-8") if isinstance(pem, str) else pem,
        )
    except (TypeError, ValueError) as exc:
        raise Phase2Error("invalid RFC 3161 trust public key PEM", code="TS3182", claim="C2") from exc


def _sign_digest(private_key: PrivateKeyTypes, digest: bytes) -> bytes:
    if isinstance(private_key, ec.EllipticCurvePrivateKey):
        from cryptography.hazmat.primitives.asymmetric import utils

        return private_key.sign(digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
    if isinstance(private_key, rsa.RSAPrivateKey):
        return private_key.sign(digest, padding.PKCS1v15(), hashes.SHA256())
    raise Phase2Error("unsupported TSA private key type", code="TS3161")


def _verify_digest(public_key: PublicKeyTypes, digest: bytes, signature: bytes) -> None:
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        from cryptography.hazmat.primitives.asymmetric import utils

        public_key.verify(signature, digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        return
    if isinstance(public_key, rsa.RSAPublicKey):
        public_key.verify(signature, digest, padding.PKCS1v15(), hashes.SHA256())
        return
    raise Phase2Error("unsupported TSA public key type", code="TS3162")


def _build_ts_req(envelope_digest_hex: str) -> bytes:
    message_imprint = tsp.MessageImprint(
        {
            "hash_algorithm": algos.DigestAlgorithm({"algorithm": OID_SHA256}),
            "hashed_message": bytes.fromhex(envelope_digest_hex),
        }
    )
    return tsp.TimeStampReq(
        {
            "version": 1,
            "message_imprint": message_imprint,
            "cert_req": True,
            "nonce": core.Integer(1),
        }
    ).dump()


def _build_tst_info(envelope_digest_hex: str, integrated_time: datetime) -> bytes:
    if integrated_time.tzinfo is None:
        integrated_time = integrated_time.replace(tzinfo=timezone.utc)
    else:
        integrated_time = integrated_time.astimezone(timezone.utc)
    tst_info = tsp.TSTInfo(
        {
            "version": 1,
            "policy": core.ObjectIdentifier("1.2.3.4.5.6"),
            "message_imprint": tsp.MessageImprint(
                {
                    "hash_algorithm": algos.DigestAlgorithm({"algorithm": OID_SHA256}),
                    "hashed_message": bytes.fromhex(envelope_digest_hex),
                }
            ),
            "serial_number": 1,
            "gen_time": core.GeneralizedTime(integrated_time.strftime("%Y%m%d%H%M%S") + "Z"),
            "nonce": core.Integer(1),
        }
    )
    return tst_info.dump()


def _parse_tst_info(tst_info_der: bytes) -> tuple[bytes, int]:
    tst_info = tsp.TSTInfo.load(tst_info_der)
    imprint = tst_info["message_imprint"]["hashed_message"].native
    gen_time = tst_info["gen_time"].native
    if gen_time.tzinfo is None:
        gen_time = gen_time.replace(tzinfo=timezone.utc)
    else:
        gen_time = gen_time.astimezone(timezone.utc)
    return imprint, int(gen_time.timestamp())


def _trust_public_key(trust_pem: str | bytes) -> PublicKeyTypes:
    raw = trust_pem.encode("utf-8") if isinstance(trust_pem, str) else trust_pem
    if b"BEGIN CERTIFICATE" in raw:
        from cryptography import x509 as cx509

        try:
            return cx509.load_pem_x509_certificate(raw).public_key()
        except ValueError as exc:
            raise Phase2Error("invalid RFC 3161 trust certificate PEM", code="TS3182", claim="C2") from exc
    return _load_public_key(raw)


def _strict_b64(value: str, *, field: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise Phase2Error(f"invalid base64 in RFC 3161 fixture field {field}", code="TS3180", claim="C2") from exc


def _verify_fixture_token(
    *,
    tst_info_der: bytes,
    signature: bytes,
    envelope_digest_hex: str,
    trust_pem: str | bytes,
) -> datetime:
    try:
        imprint, unix_time = _parse_tst_info(tst_info_der)
    except (ValueError, TypeError, KeyError) as exc:
        raise Phase2Error("malformed RFC 3161 fixture TSTInfo", code="TS3181", claim="C2") from exc
    if imprint.hex() != envelope_digest_hex.lower():
        raise Phase2Error("timestamp token imprint does not match envelope digest", code="TS3165", claim="C2")
    tst_digest = hashlib.sha256(tst_info_der).digest()
    try:
        _verify_digest(_trust_public_key(trust_pem), tst_digest, signature)
    except InvalidSignature as exc:
        raise Phase2Error("RFC 3161 fixture signature does not verify under the configured trust root", code="TS3179", claim="C2") from exc
    return datetime.fromtimestamp(unix_time, tz=timezone.utc)


def generate_fixture_tsa_key() -> tuple[str, str, bytes, str]:
    """Return (private_pem, public_pem, certificate_der, certificate_pem)."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    public_pem = private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    from cryptography import x509 as cx509
    from cryptography.x509.oid import NameOID

    subject = issuer = cx509.Name(
        [
            cx509.NameAttribute(NameOID.COMMON_NAME, "ENS GDI RFC3161 Test TSA"),
            cx509.NameAttribute(NameOID.ORGANIZATION_NAME, "ens-gdi-fixture"),
        ]
    )
    cert = (
        cx509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(1)
        .not_valid_before(datetime(2020, 1, 1, tzinfo=timezone.utc))
        .not_valid_after(datetime(2040, 1, 1, tzinfo=timezone.utc))
        .sign(private_key, hashes.SHA256())
    )
    cert_der = cert.public_bytes(Encoding.DER)
    cert_pem = cert.public_bytes(Encoding.PEM).decode("utf-8")
    return private_pem.decode("utf-8"), public_pem.decode("utf-8"), cert_der, cert_pem


class Rfc3161Adapter(AnchorAdapter):
    def __init__(
        self,
        *,
        profile_id: str = "rfc3161",
        tsa_url: str = DEFAULT_TSA_URL,
        trust_root_pem: str | bytes | None = None,
        fixture_private_key_pem: str | bytes | None = None,
        fixture_certificate_pem: str | bytes | None = None,
    ) -> None:
        if profile_id not in {"rfc3161", "rfc3161-recorded-fixture"}:
            raise Phase2Error(f"unsupported RFC 3161 profile {profile_id}", code="TS3167")
        self.profile_id = profile_id
        self.tsa_url = tsa_url.rstrip("/")
        self._fixture_key = _load_private_key(fixture_private_key_pem) if fixture_private_key_pem else None
        self._fixture_cert_pem = fixture_certificate_pem
        if not trust_root_pem:
            raise Phase2Error(
                f"{profile_id} requires an independently supplied pinned TSA trust root PEM",
                code="TS3168" if profile_id == "rfc3161" else "TS3169",
            )
        self._trust_pem = trust_root_pem

    def _trust_boundary(self) -> str:
        return RFC3161_FIXTURE_TRUST_BOUNDARY if self.profile_id == "rfc3161-recorded-fixture" else RFC3161_TRUST_BOUNDARY

    def anchor(self, envelope_bytes: bytes) -> dict[str, Any]:
        digest = sha256_hex(envelope_bytes)
        if self.profile_id == "rfc3161-recorded-fixture":
            return self._anchor_fixture(envelope_bytes, digest, integrated_time=None)
        raise Phase2Error(
            "production RFC 3161 issuance is disabled until standards-conformant CMS verification is integrated",
            code="TS3178",
            claim="C2",
        )

    def anchor_at(self, envelope_bytes: bytes, *, integrated_time: datetime) -> dict[str, Any]:
        if self.profile_id != "rfc3161-recorded-fixture":
            raise Phase2Error("anchor_at is only defined for rfc3161-recorded-fixture", code="TS3170")
        return self._anchor_fixture(envelope_bytes, sha256_hex(envelope_bytes), integrated_time=integrated_time)

    def _anchor_fixture(
        self,
        envelope_bytes: bytes,
        digest: str,
        *,
        integrated_time: datetime | None,
    ) -> dict[str, Any]:
        if self._fixture_key is None or self._fixture_cert_pem is None:
            raise Phase2Error("fixture issuance requires TSA private key and certificate PEM", code="TS3171")
        if integrated_time is None:
            integrated_time = datetime.now(timezone.utc)
        tst_info_der = _build_tst_info(digest, integrated_time)
        signature = _sign_digest(self._fixture_key, hashlib.sha256(tst_info_der).digest())
        anchored_at = integrated_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        receipt = {
            "profileId": self.profile_id,
            "envelopeDigestSha256": digest,
            "anchorId": f"tsa-fixture:{digest[:16]}",
            "anchoredAt": anchored_at,
            "logIndex": None,
            "verifierMaterial": {
                "kind": "rfc3161-fixture-v1",
                "tstInfoDerB64": base64.b64encode(tst_info_der).decode("ascii"),
                "signatureB64": base64.b64encode(signature).decode("ascii"),
                "tsaCertificatePem": (
                    self._fixture_cert_pem.decode("utf-8")
                    if isinstance(self._fixture_cert_pem, bytes)
                    else str(self._fixture_cert_pem)
                ),
            },
        }
        validate_schema(receipt, "anchor-receipt.schema.json")
        self.verify(envelope_bytes, receipt)
        return receipt

    def verify(self, envelope_bytes: bytes, receipt: dict[str, Any]) -> TemporalClaim:
        validate_schema(receipt, "anchor-receipt.schema.json")
        if receipt["profileId"] != self.profile_id:
            raise Phase2Error(
                f"receipt profile {receipt['profileId']} does not match adapter {self.profile_id}",
                code="TS3173",
                claim="C2",
            )
        digest = sha256_hex(envelope_bytes)
        if receipt["envelopeDigestSha256"] != digest:
            raise Phase2Error("receipt envelope digest does not match envelope bytes", code="TS3174", claim="C2")
        material = receipt["verifierMaterial"]
        kind = material.get("kind")
        if self.profile_id == "rfc3161":
            raise Phase2Error(
                "production RFC 3161 verification is disabled until complete CMS/RFC 3161 trust validation is integrated",
                code="TS3178",
                claim="C2",
            )
        if kind != "rfc3161-fixture-v1":
            raise Phase2Error(f"unsupported RFC 3161 fixture material kind {kind!r}", code="TS3177", claim="C2")
        anchored_at = _verify_fixture_token(
            tst_info_der=_strict_b64(material["tstInfoDerB64"], field="tstInfoDerB64"),
            signature=_strict_b64(material["signatureB64"], field="signatureB64"),
            envelope_digest_hex=digest,
            trust_pem=self._trust_pem,
        )
        claimed = datetime.fromisoformat(receipt["anchoredAt"].replace("Z", "+00:00"))
        if int(claimed.timestamp()) != int(anchored_at.timestamp()):
            raise Phase2Error("receipt anchoredAt does not match token genTime", code="TS3175", claim="C2")
        return TemporalClaim(
            profile_id=self.profile_id,
            anchored_at=anchored_at,
            envelope_digest_hex=digest,
            trust_boundary=self._trust_boundary(),
        )
