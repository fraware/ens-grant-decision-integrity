"""Sigstore Rekor v1 profile and recorded-fixture profile (historical compatibility).

Rekor v1 is a maintenance-line compatibility target. Prefer ``rekor-v2`` for new
production anchoring. Verification uses a client-pinned trust root. A PEM copied
into a receipt is not an independent root. Production profile `rekor-v1` pins the
Sigstore Rekor v1 public key retrieved from the public instance and stored here so a
network substitution of /api/v1/log/publicKey cannot change the root.

`rekor-v1-recorded-fixture` uses a test-log key supplied to the adapter. It
does not establish inclusion in the public Rekor log.
"""

from __future__ import annotations

import base64
import hashlib
import json
import struct
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey

from anchors.base import AnchorAdapter, TemporalClaim
from canonicalize import canonicalize
from claims import FIXTURE_TRUST_BOUNDARY, REKOR_TRUST_BOUNDARY
from support import Phase2Error, sha256_hex, validate_schema

DEFAULT_REKOR_URL = "https://rekor.sigstore.dev"

# Pinned Rekor v1 production public key (ECDSA P-256). Fetched from
# https://rekor.sigstore.dev/api/v1/log/publicKey with Accept: application/x-pem-file
# on 2026-08-18 and stored so verification does not trust a live key endpoint.
REKOR_V1_PRODUCTION_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE2G2Y+2tabdTV5BcGiBIx0a9fAFwr
kBbmLSGtks4L3qX6yYY0zufBnhC8Ur/iy55GhWP/9A/bY2LhC30M9+RYtw==
-----END PUBLIC KEY-----
"""

_LEAF_PREFIX = 0
_NODE_PREFIX = 1


def load_public_key_pem(pem: str | bytes) -> EllipticCurvePublicKey:
    key = serialization.load_pem_public_key(pem.encode("utf-8") if isinstance(pem, str) else pem)
    if not isinstance(key, EllipticCurvePublicKey):
        raise Phase2Error("Rekor trust root must be an ECDSA public key", code="RKR001")
    return key


def load_private_key_pem(pem: str | bytes, password: bytes | None = None) -> EllipticCurvePrivateKey:
    key = serialization.load_pem_private_key(
        pem.encode("utf-8") if isinstance(pem, str) else pem,
        password=password,
    )
    if not isinstance(key, EllipticCurvePrivateKey):
        raise Phase2Error("Rekor fixture key must be ECDSA", code="RKR002")
    return key


def key_id_bytes(public_key: EllipticCurvePublicKey) -> bytes:
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).digest()


def _hash_leaf(leaf: bytes) -> bytes:
    return hashlib.sha256(struct.pack(f"B{len(leaf)}s", _LEAF_PREFIX, leaf)).digest()


def _hash_children(lhs: bytes, rhs: bytes) -> bytes:
    return hashlib.sha256(
        struct.pack(f"B{len(lhs)}s{len(rhs)}s", _NODE_PREFIX, lhs, rhs)
    ).digest()


def _decomp_inclusion_proof(index: int, size: int) -> tuple[int, int]:
    inner = (index ^ (size - 1)).bit_length()
    border = bin(index >> inner).count("1")
    return inner, border


def _chain_inner(seed: bytes, hashes: list[bytes], log_index: int) -> bytes:
    for i, sibling in enumerate(hashes):
        if (log_index >> i) & 1 == 0:
            seed = _hash_children(seed, sibling)
        else:
            seed = _hash_children(sibling, seed)
    return seed


def _chain_border_right(seed: bytes, hashes: list[bytes]) -> bytes:
    for sibling in hashes:
        seed = _hash_children(sibling, seed)
    return seed


def verify_merkle_inclusion(*, body: bytes, log_index: int, tree_size: int, hashes_hex: list[str], root_hex: str) -> None:
    inner, border = _decomp_inclusion_proof(log_index, tree_size)
    if len(hashes_hex) != inner + border:
        raise Phase2Error(
            f"inclusion proof has wrong size: expected {inner + border}, got {len(hashes_hex)}",
            code="RKR003",
            claim="C2",
        )
    siblings = [bytes.fromhex(item) for item in hashes_hex]
    leaf_hash = _hash_leaf(body)
    intermediate = _chain_inner(leaf_hash, siblings[:inner], log_index)
    calc = _chain_border_right(intermediate, siblings[inner:])
    if calc.hex() != root_hex.lower():
        raise Phase2Error("inclusion proof does not reconstruct the claimed root", code="RKR004", claim="C2")


def _set_payload(*, body: bytes, integrated_time: int, log_id_hex: str, log_index: int) -> bytes:
    payload = {
        "body": base64.b64encode(body).decode("ascii"),
        "integratedTime": integrated_time,
        "logID": log_id_hex.lower(),
        "logIndex": log_index,
    }
    return canonicalize(payload)


def verify_set(
    *,
    body: bytes,
    integrated_time: int,
    log_id_hex: str,
    log_index: int,
    signature_b64: str,
    public_key: EllipticCurvePublicKey,
) -> None:
    expected_log_id = key_id_bytes(public_key).hex()
    if log_id_hex.lower() != expected_log_id:
        raise Phase2Error("receipt logID does not match the pinned trust root", code="RKR005", claim="C2")
    payload = _set_payload(
        body=body,
        integrated_time=integrated_time,
        log_id_hex=log_id_hex,
        log_index=log_index,
    )
    try:
        public_key.verify(
            base64.b64decode(signature_b64),
            payload,
            ec.ECDSA(hashes.SHA256()),
        )
    except InvalidSignature as exc:
        raise Phase2Error("signed entry timestamp is invalid under the pinned trust root", code="RKR006", claim="C2") from exc


def _sign_checkpoint(
    *,
    origin: str,
    tree_size: int,
    root_hash: bytes,
    private_key: EllipticCurvePrivateKey,
    key_id: bytes,
) -> str:
    root_b64 = base64.b64encode(root_hash).decode("ascii")
    body = f"{origin}\n{tree_size}\n{root_b64}\n"
    signature = private_key.sign(body.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
    packed = key_id[:4] + signature
    name = origin.split()[0]
    return body + "\n— " + name + " " + base64.b64encode(packed).decode("ascii") + "\n"


def verify_checkpoint(
    *,
    checkpoint: str,
    public_key: EllipticCurvePublicKey,
    key_id: bytes,
    root_hex: str,
    tree_size: int,
) -> None:
    separator = "\n\n"
    if checkpoint.count(separator) != 1:
        raise Phase2Error("malformed checkpoint: expected one blank line", code="RKR007", claim="C2")
    split = checkpoint.index(separator)
    note = checkpoint[: split + 1]
    sig_block = checkpoint[split + len(separator) :]
    if not sig_block.endswith("\n"):
        raise Phase2Error("malformed checkpoint signature block", code="RKR008", claim="C2")
    lines = [line for line in sig_block.split("\n") if line]
    if not lines:
        raise Phase2Error("malformed checkpoint: no signatures", code="RKR009", claim="C2")
    verified = False
    for line in lines:
        if not line.startswith("— "):
            raise Phase2Error("malformed checkpoint signature line", code="RKR010", claim="C2")
        parts = line.split()
        if len(parts) < 3:
            raise Phase2Error("malformed checkpoint signature line", code="RKR010", claim="C2")
        packed = base64.b64decode(parts[-1])
        if len(packed) < 5:
            raise Phase2Error("malformed checkpoint signature bytes", code="RKR011", claim="C2")
        if packed[:4] != key_id[:4]:
            continue
        try:
            public_key.verify(packed[4:], note.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
            verified = True
            break
        except InvalidSignature:
            raise Phase2Error("checkpoint signature is invalid under the pinned trust root", code="RKR012", claim="C2")
    if not verified:
        raise Phase2Error("checkpoint has no signature for the pinned log key", code="RKR013", claim="C2")
    header_lines = note.strip().split("\n")
    if len(header_lines) < 3:
        raise Phase2Error("malformed checkpoint header", code="RKR014", claim="C2")
    try:
        checkpoint_size = int(header_lines[1])
        checkpoint_root = base64.b64decode(header_lines[2]).hex()
    except (ValueError, Exception) as exc:
        raise Phase2Error("malformed checkpoint size or root", code="RKR015", claim="C2") from exc
    if checkpoint_size != tree_size or checkpoint_root != root_hex.lower():
        raise Phase2Error("checkpoint root or tree size does not match the inclusion proof", code="RKR016", claim="C2")


def _hashedrekord_body(envelope_digest_hex: str, signature: bytes, public_pem: bytes) -> bytes:
    record = {
        "apiVersion": "0.0.1",
        "kind": "hashedrekord",
        "spec": {
            "data": {"hash": {"algorithm": "sha256", "value": envelope_digest_hex}},
            "signature": {
                "content": base64.b64encode(signature).decode("ascii"),
                "publicKey": {"content": base64.b64encode(public_pem).decode("ascii")},
            },
        },
    }
    return canonicalize(record)


def _sign_prehashed(private_key: EllipticCurvePrivateKey, digest: bytes) -> bytes:
    return private_key.sign(digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))


def _parse_hashedrekord_hash(body: bytes) -> str:
    record = json.loads(body.decode("utf-8"))
    try:
        return str(record["spec"]["data"]["hash"]["value"]).lower()
    except (KeyError, TypeError) as exc:
        raise Phase2Error("hashedrekord body missing spec.data.hash.value", code="RKR017", claim="C2") from exc


def _http_json(url: str, *, data: bytes | None = None, timeout: int = 30) -> Any:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    request = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise Phase2Error(f"Rekor HTTP {exc.code}: {detail}", code="RKR018") from exc
    except urllib.error.URLError as exc:
        raise Phase2Error(f"Rekor network error: {exc}", code="RKR019") from exc


class RekorAdapter(AnchorAdapter):
    def __init__(
        self,
        *,
        profile_id: str = "rekor-v1",
        trust_root_pem: str | None = None,
        fixture_private_key_pem: str | bytes | None = None,
        artifact_private_key_pem: str | bytes | None = None,
        rekor_url: str = DEFAULT_REKOR_URL,
        fixture_origin: str = "ens-gdi-rekor-fixture",
    ) -> None:
        if profile_id not in {"rekor-v1", "rekor-v1-recorded-fixture"}:
            raise Phase2Error(f"unsupported Rekor profile {profile_id}", code="RKR020")
        self.profile_id = profile_id
        self.rekor_url = rekor_url.rstrip("/")
        self.fixture_origin = fixture_origin
        if profile_id == "rekor-v1":
            self._trust_pem = trust_root_pem or REKOR_V1_PRODUCTION_PUBLIC_KEY_PEM
            self._fixture_key = None
        else:
            self._fixture_key = load_private_key_pem(fixture_private_key_pem) if fixture_private_key_pem else None
            if self._fixture_key is not None:
                derived = self._fixture_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                ).decode("utf-8")
                self._trust_pem = trust_root_pem or derived
            elif trust_root_pem:
                self._trust_pem = trust_root_pem
            else:
                raise Phase2Error(
                    "recorded fixture profile requires a test-log private key to issue receipts "
                    "or a pinned test-log public key to verify them",
                    code="RKR021",
                )
        self._trust_key = load_public_key_pem(self._trust_pem)
        self._artifact_key = load_private_key_pem(artifact_private_key_pem) if artifact_private_key_pem else None

    def _trust_boundary(self) -> str:
        return REKOR_TRUST_BOUNDARY if self.profile_id == "rekor-v1" else FIXTURE_TRUST_BOUNDARY

    def anchor(self, envelope_bytes: bytes) -> dict[str, Any]:
        digest = sha256_hex(envelope_bytes)
        if self.profile_id == "rekor-v1-recorded-fixture":
            return self._anchor_fixture(envelope_bytes, digest, integrated_time=None)
        return self._anchor_live(envelope_bytes, digest)

    def anchor_at(self, envelope_bytes: bytes, *, integrated_time: datetime) -> dict[str, Any]:
        """Issue a recorded-fixture receipt at a specified UTC time. Test/example only."""
        if self.profile_id != "rekor-v1-recorded-fixture":
            raise Phase2Error("anchor_at is only defined for rekor-v1-recorded-fixture", code="RKR022")
        return self._anchor_fixture(envelope_bytes, sha256_hex(envelope_bytes), integrated_time=integrated_time)

    def _anchor_fixture(
        self,
        envelope_bytes: bytes,
        digest: str,
        *,
        integrated_time: datetime | None,
    ) -> dict[str, Any]:
        if self._fixture_key is None:
            raise Phase2Error("recorded fixture issuance requires a test-log private key", code="RKR021")
        artifact_key = self._artifact_key or self._fixture_key
        artifact_pub_pem = artifact_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        signature = _sign_prehashed(artifact_key, bytes.fromhex(digest))
        body = _hashedrekord_body(digest, signature, artifact_pub_pem)
        kid = key_id_bytes(self._trust_key)
        log_index = 0
        tree_size = 1
        leaf = _hash_leaf(body)
        root_hex = leaf.hex()
        if integrated_time is None:
            integrated_time = datetime.now(timezone.utc)
        if integrated_time.tzinfo is None:
            integrated_time = integrated_time.replace(tzinfo=timezone.utc)
        unix_time = int(integrated_time.timestamp())
        set_payload = _set_payload(body=body, integrated_time=unix_time, log_id_hex=kid.hex(), log_index=log_index)
        set_sig = self._fixture_key.sign(set_payload, ec.ECDSA(hashes.SHA256()))
        checkpoint = _sign_checkpoint(
            origin=f"{self.fixture_origin} - {int.from_bytes(kid[:8], 'big')}",
            tree_size=tree_size,
            root_hash=leaf,
            private_key=self._fixture_key,
            key_id=kid,
        )
        receipt = {
            "profileId": self.profile_id,
            "envelopeDigestSha256": digest,
            "anchorId": f"fixture:{kid.hex()}:{log_index}",
            "anchoredAt": datetime.fromtimestamp(unix_time, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "logIndex": log_index,
            "verifierMaterial": {
                "kind": "rekor-v1-offline",
                "bodyB64": base64.b64encode(body).decode("ascii"),
                "integratedTime": unix_time,
                "logIdHex": kid.hex(),
                "signedEntryTimestampB64": base64.b64encode(set_sig).decode("ascii"),
                "inclusionProof": {
                    "logIndex": log_index,
                    "treeSize": tree_size,
                    "rootHash": root_hex,
                    "hashes": [],
                },
                "checkpoint": checkpoint,
                "uuid": f"fixture-{digest[:16]}",
            },
        }
        validate_schema(receipt, "anchor-receipt.schema.json")
        return receipt

    def _anchor_live(self, envelope_bytes: bytes, digest: str) -> dict[str, Any]:
        artifact_key = self._artifact_key
        if artifact_key is None:
            artifact_key = ec.generate_private_key(ec.SECP256R1())
        artifact_pub_pem = artifact_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        signature = _sign_prehashed(artifact_key, bytes.fromhex(digest))
        proposed = {
            "apiVersion": "0.0.1",
            "kind": "hashedrekord",
            "spec": {
                "data": {"hash": {"algorithm": "sha256", "value": digest}},
                "signature": {
                    "content": base64.b64encode(signature).decode("ascii"),
                    "publicKey": {"content": base64.b64encode(artifact_pub_pem).decode("ascii")},
                },
            },
        }
        response = _http_json(f"{self.rekor_url}/api/v1/log/entries", data=json.dumps(proposed).encode("utf-8"))
        if not isinstance(response, dict) or len(response) != 1:
            raise Phase2Error("unexpected Rekor POST response shape", code="RKR023")
        uuid, entry = next(iter(response.items()))
        verification = entry.get("verification") or {}
        proof = verification.get("inclusionProof") or {}
        body_b64 = entry["body"]
        if isinstance(body_b64, dict):
            raise Phase2Error("Rekor body was not base64 text", code="RKR024")
        receipt = {
            "profileId": "rekor-v1",
            "envelopeDigestSha256": digest,
            "anchorId": str(uuid),
            "anchoredAt": datetime.fromtimestamp(int(entry["integratedTime"]), tz=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "logIndex": int(entry["logIndex"]),
            "verifierMaterial": {
                "kind": "rekor-v1-offline",
                "bodyB64": body_b64 if isinstance(body_b64, str) else base64.b64encode(canonicalize(body_b64)).decode("ascii"),
                "integratedTime": int(entry["integratedTime"]),
                "logIdHex": str(entry["logID"]).lower(),
                "signedEntryTimestampB64": verification["signedEntryTimestamp"],
                "inclusionProof": {
                    "logIndex": int(proof["logIndex"]),
                    "treeSize": int(proof["treeSize"]),
                    "rootHash": str(proof["rootHash"]).lower(),
                    "hashes": [str(item).lower() for item in proof.get("hashes") or []],
                },
                "checkpoint": proof["checkpoint"],
                "uuid": str(uuid),
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
                code="RKR025",
                claim="C2",
            )
        digest = sha256_hex(envelope_bytes)
        if receipt["envelopeDigestSha256"] != digest:
            raise Phase2Error("receipt envelope digest does not match envelope bytes", code="RKR026", claim="C2")
        material = receipt["verifierMaterial"]
        body = base64.b64decode(material["bodyB64"])
        rekord_hash = _parse_hashedrekord_hash(body)
        if rekord_hash != digest:
            raise Phase2Error("hashedrekord hash does not match envelope digest", code="RKR027", claim="C2")
        proof = material["inclusionProof"]
        log_index = int(material.get("logIndex", proof["logIndex"]))
        verify_set(
            body=body,
            integrated_time=int(material["integratedTime"]),
            log_id_hex=str(material["logIdHex"]),
            log_index=int(receipt["logIndex"]),
            signature_b64=str(material["signedEntryTimestampB64"]),
            public_key=self._trust_key,
        )
        verify_merkle_inclusion(
            body=body,
            log_index=int(proof["logIndex"]),
            tree_size=int(proof["treeSize"]),
            hashes_hex=list(proof.get("hashes") or []),
            root_hex=str(proof["rootHash"]),
        )
        verify_checkpoint(
            checkpoint=str(material["checkpoint"]),
            public_key=self._trust_key,
            key_id=key_id_bytes(self._trust_key),
            root_hex=str(proof["rootHash"]),
            tree_size=int(proof["treeSize"]),
        )
        anchored_at = datetime.fromtimestamp(int(material["integratedTime"]), tz=timezone.utc)
        claimed = datetime.fromisoformat(receipt["anchoredAt"].replace("Z", "+00:00"))
        if int(claimed.timestamp()) != int(anchored_at.timestamp()):
            raise Phase2Error("receipt anchoredAt does not match signed integratedTime", code="RKR028", claim="C2")
        return TemporalClaim(
            profile_id=self.profile_id,
            anchored_at=anchored_at,
            envelope_digest_hex=digest,
            trust_boundary=self._trust_boundary(),
        )
