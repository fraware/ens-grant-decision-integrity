"""Rekor v2 production profile and recorded-fixture profile.

Design
------
- ``rekor-v2``: production transparency profile. Offline verification requires an
  externally supplied trust policy (TrustedRoot-shaped log key + validity window).
  Online issuance prefers Sigstore SigningConfig / TrustedRoot discovery; when that
  stack is unavailable this adapter fails closed with a structured availability
  error rather than inventing a hard-coded production endpoint as authority.
- ``rekor-v2-recorded-fixture``: non-production offline fixture for CI. Fixture
  evidence MUST NOT establish production-profile C2.

Submission signatures
---------------------
Any ECDSA signature over the envelope digest that appears in a hashedrekord-style
body is a **technical log-submission signature** (``logSubmissionSignature``).
It never grants grant authority, decision authority, reviewer approval, or
operator honesty.

Trust roots
-----------
Receipt-carried PEMs are verifier material only. The verifier-pinned trust policy
appoints the log key. Receipt-supplied trust substitution is rejected.
"""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

from anchors.base import AnchorAdapter, TemporalClaim
from anchors import rekor as rekor_v1
from canonicalize import canonicalize
from claims import REKOR_V2_TRUST_BOUNDARY
from support import Phase2Error, sha256_hex, validate_schema

REKOR_V2_PROFILES = frozenset({"rekor-v2", "rekor-v2-recorded-fixture"})
VERIFIER_KIND = "rekor-v2-offline"


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_trust_policy(policy: dict[str, Any] | None) -> dict[str, Any]:
    """Validate and extract the rekor-v2 anchor pin from an external trust policy."""
    if not isinstance(policy, dict):
        raise Phase2Error(
            "rekor-v2 verification requires an externally supplied trust policy",
            code="RKR240",
            claim="C2",
        )
    if str(policy.get("trustPolicyVersion")) != "1":
        raise Phase2Error("unsupported trustPolicyVersion", code="RKR241", claim="C2")
    policy_id = policy.get("policyId")
    if not isinstance(policy_id, str) or not policy_id:
        raise Phase2Error("trust policy missing policyId", code="RKR241", claim="C2")
    anchors = policy.get("anchors")
    if not isinstance(anchors, dict) or "rekor-v2" not in anchors:
        raise Phase2Error("trust policy missing anchors.rekor-v2", code="RKR242", claim="C2")
    pin = anchors["rekor-v2"]
    if not isinstance(pin, dict):
        raise Phase2Error("anchors.rekor-v2 must be an object", code="RKR242", claim="C2")
    pem = pin.get("publicKeyPem")
    if not isinstance(pem, str) or "BEGIN PUBLIC KEY" not in pem:
        raise Phase2Error("anchors.rekor-v2.publicKeyPem is required", code="RKR243", claim="C2")
    log_identity = pin.get("logIdentity")
    if not isinstance(log_identity, str) or not log_identity:
        raise Phase2Error("anchors.rekor-v2.logIdentity is required", code="RKR244", claim="C2")
    shard = pin.get("shard") or "default"
    if not isinstance(shard, str) or not shard:
        raise Phase2Error("anchors.rekor-v2.shard must be a non-empty string", code="RKR244", claim="C2")
    return {
        "policyId": policy_id,
        "policy": policy,
        "pin": pin,
        "publicKeyPem": pem,
        "logIdentity": log_identity,
        "shard": shard,
        "validFrom": pin.get("validFrom") or policy.get("validFrom"),
        "validUntil": pin.get("validUntil") or policy.get("validUntil"),
        "keyIdHex": pin.get("keyIdHex"),
    }


def policy_digest_sha256(policy: dict[str, Any]) -> str:
    return sha256_hex(canonicalize(policy))


def _assert_validity_window(*, when: datetime, valid_from: str | None, valid_until: str | None) -> None:
    if valid_from:
        start = _parse_dt(valid_from)
        if when < start:
            raise Phase2Error("anchor time precedes trust-policy validFrom", code="RKR245", claim="C2")
    if valid_until:
        end = _parse_dt(valid_until)
        if when > end:
            raise Phase2Error("anchor time is after trust-policy validUntil", code="RKR246", claim="C2")


def _reject_receipt_trust_substitution(material: dict[str, Any]) -> None:
    forbidden = ("trustRootPem", "trustedRoot", "signingConfig", "tufRoot", "policyPublicKeyPem")
    for key in forbidden:
        if key in material:
            raise Phase2Error(
                f"receipt must not supply trust authority field {key!r}",
                code="RKR247",
                claim="C2",
            )


class RekorV2Adapter(AnchorAdapter):
    def __init__(
        self,
        *,
        profile_id: str = "rekor-v2",
        trust_policy: dict[str, Any] | None = None,
        fixture_private_key_pem: str | bytes | None = None,
        artifact_private_key_pem: str | bytes | None = None,
        fixture_origin: str = "ens-gdi-rekor-v2-fixture",
        allow_online: bool = False,
    ) -> None:
        if profile_id not in REKOR_V2_PROFILES:
            raise Phase2Error(f"unsupported Rekor v2 profile {profile_id}", code="RKR248")
        self.profile_id = profile_id
        self.fixture_origin = fixture_origin
        self.allow_online = allow_online
        self._trust_policy = trust_policy
        self._fixture_key: EllipticCurvePrivateKey | None = None
        self._artifact_key = (
            rekor_v1.load_private_key_pem(artifact_private_key_pem) if artifact_private_key_pem else None
        )
        if profile_id == "rekor-v2-recorded-fixture":
            if fixture_private_key_pem:
                self._fixture_key = rekor_v1.load_private_key_pem(fixture_private_key_pem)
            # Trust policy may be supplied at verify time; for issuance derive from fixture key.
            if trust_policy is None and self._fixture_key is not None:
                pub_pem = (
                    self._fixture_key.public_key()
                    .public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo,
                    )
                    .decode("utf-8")
                )
                kid = rekor_v1.key_id_bytes(self._fixture_key.public_key()).hex()
                self._trust_policy = {
                    "trustPolicyVersion": "1",
                    "policyId": "rekor-v2-recorded-fixture-auto",
                    "validFrom": "2020-01-01T00:00:00Z",
                    "validUntil": "2099-01-01T00:00:00Z",
                    "anchors": {
                        "rekor-v2": {
                            "logIdentity": fixture_origin,
                            "shard": "fixture",
                            "publicKeyPem": pub_pem,
                            "keyIdHex": kid,
                            "validFrom": "2020-01-01T00:00:00Z",
                            "validUntil": "2099-01-01T00:00:00Z",
                        }
                    },
                }

    def _trust_boundary(self) -> str:
        if self.profile_id == "rekor-v2":
            return REKOR_V2_TRUST_BOUNDARY
        return (
            "rekor-v2-recorded-fixture receipts are verified under a test-log key and "
            "external fixture trust policy. They do not establish inclusion in a production "
            "Sigstore Rekor v2 log and must not establish production-profile C2."
        )

    def anchor(self, envelope_bytes: bytes) -> dict[str, Any]:
        digest = sha256_hex(envelope_bytes)
        if self.profile_id == "rekor-v2-recorded-fixture":
            return self._anchor_fixture(envelope_bytes, digest, integrated_time=None)
        return self._anchor_live_fail_closed(digest)

    def anchor_at(self, envelope_bytes: bytes, *, integrated_time: datetime) -> dict[str, Any]:
        if self.profile_id != "rekor-v2-recorded-fixture":
            raise Phase2Error("anchor_at is only defined for rekor-v2-recorded-fixture", code="RKR249")
        return self._anchor_fixture(envelope_bytes, sha256_hex(envelope_bytes), integrated_time=integrated_time)

    def _anchor_live_fail_closed(self, digest: str) -> dict[str, Any]:
        # Prefer Sigstore SigningConfig / TrustedRoot when integrated. Until then, do not
        # hard-code a production URL as an authority source.
        raise Phase2Error(
            "rekor-v2 online anchoring requires Sigstore SigningConfig/TrustedRoot integration; "
            "unavailable in this build (structured availability error, not a verification failure)",
            code="RKR250",
        )

    def _anchor_fixture(
        self,
        envelope_bytes: bytes,
        digest: str,
        *,
        integrated_time: datetime | None,
    ) -> dict[str, Any]:
        if self._fixture_key is None:
            raise Phase2Error("recorded fixture issuance requires a test-log private key", code="RKR251")
        artifact_key = self._artifact_key or self._fixture_key
        artifact_pub_pem = artifact_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        signature = rekor_v1._sign_prehashed(artifact_key, bytes.fromhex(digest))
        body = rekor_v1._hashedrekord_body(digest, signature, artifact_pub_pem)
        trust_key = rekor_v1.load_public_key_pem(
            load_trust_policy(self._trust_policy)["publicKeyPem"]
        )
        kid = rekor_v1.key_id_bytes(trust_key)
        log_index = 0
        tree_size = 1
        leaf = rekor_v1._hash_leaf(body)
        root_hex = leaf.hex()
        if integrated_time is None:
            integrated_time = datetime.now(timezone.utc)
        if integrated_time.tzinfo is None:
            integrated_time = integrated_time.replace(tzinfo=timezone.utc)
        unix_time = int(integrated_time.timestamp())
        set_payload = rekor_v1._set_payload(
            body=body, integrated_time=unix_time, log_id_hex=kid.hex(), log_index=log_index
        )
        set_sig = self._fixture_key.sign(set_payload, ec.ECDSA(hashes.SHA256()))
        checkpoint = rekor_v1._sign_checkpoint(
            origin=f"{self.fixture_origin} - {int.from_bytes(kid[:8], 'big')}",
            tree_size=tree_size,
            root_hash=leaf,
            private_key=self._fixture_key,
            key_id=kid,
        )
        pin = load_trust_policy(self._trust_policy)
        receipt = {
            "profileId": self.profile_id,
            "envelopeDigestSha256": digest,
            "anchorId": f"fixture-v2:{kid.hex()}:{log_index}",
            "anchoredAt": datetime.fromtimestamp(unix_time, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "logIndex": log_index,
            "verifierMaterial": {
                "kind": VERIFIER_KIND,
                "bodyB64": base64.b64encode(body).decode("ascii"),
                "integratedTime": unix_time,
                "logIdHex": kid.hex(),
                "logIdentity": pin["logIdentity"],
                "shard": pin["shard"],
                "signedEntryTimestampB64": base64.b64encode(set_sig).decode("ascii"),
                "inclusionProof": {
                    "logIndex": log_index,
                    "treeSize": tree_size,
                    "rootHash": root_hex,
                    "hashes": [],
                },
                "checkpoint": checkpoint,
                "uuid": f"fixture-v2-{digest[:16]}",
                "logSubmissionSignature": {
                    "role": "technical-log-submission-only",
                    "algorithm": "ecdsa-sha256-prehash",
                    "signatureB64": base64.b64encode(signature).decode("ascii"),
                    "verifierPublicKeyPemB64": base64.b64encode(artifact_pub_pem).decode("ascii"),
                    "nonClaim": (
                        "logSubmissionSignature is a technical Rekor submission artifact; "
                        "it does not grant grant authority, decision authority, or operator honesty."
                    ),
                },
            },
        }
        validate_schema(receipt, "anchor-receipt.schema.json")
        return receipt

    def verify(self, envelope_bytes: bytes, receipt: dict[str, Any]) -> TemporalClaim:
        if not isinstance(receipt, dict):
            raise Phase2Error("receipt must be an object", code="RKR256", claim="C2")
        material_early = receipt.get("verifierMaterial")
        if isinstance(material_early, dict):
            _reject_receipt_trust_substitution(material_early)
        validate_schema(receipt, "anchor-receipt.schema.json")
        if receipt["profileId"] != self.profile_id:
            raise Phase2Error(
                f"receipt profile {receipt['profileId']} does not match adapter {self.profile_id}",
                code="RKR252",
                claim="C2",
            )
        if self.profile_id == "rekor-v2" and receipt.get("profileId") == "rekor-v2-recorded-fixture":
            raise Phase2Error("fixture evidence cannot establish production rekor-v2 C2", code="RKR253", claim="C2")

        pin = load_trust_policy(self._trust_policy)
        trust_key = rekor_v1.load_public_key_pem(pin["publicKeyPem"])
        expected_kid = rekor_v1.key_id_bytes(trust_key).hex()
        if pin.get("keyIdHex") and str(pin["keyIdHex"]).lower() != expected_kid:
            raise Phase2Error("trust policy keyIdHex does not match publicKeyPem", code="RKR254", claim="C2")

        digest = sha256_hex(envelope_bytes)
        if receipt["envelopeDigestSha256"] != digest:
            raise Phase2Error("receipt envelope digest does not match envelope bytes", code="RKR255", claim="C2")

        material = receipt["verifierMaterial"]
        if material.get("kind") != VERIFIER_KIND:
            raise Phase2Error("unexpected rekor-v2 verifierMaterial.kind", code="RKR256", claim="C2")
        _reject_receipt_trust_substitution(material)

        if str(material.get("logIdentity")) != pin["logIdentity"]:
            raise Phase2Error("receipt logIdentity does not match trust policy", code="RKR257", claim="C2")
        if str(material.get("shard") or "default") != pin["shard"]:
            raise Phase2Error("receipt shard does not match trust policy", code="RKR258", claim="C2")
        if str(material["logIdHex"]).lower() != expected_kid:
            raise Phase2Error("receipt logIdHex does not match trust-policy log key", code="RKR259", claim="C2")

        body = base64.b64decode(material["bodyB64"])
        rekord_hash = rekor_v1._parse_hashedrekord_hash(body)
        if rekord_hash != digest:
            raise Phase2Error("hashedrekord hash does not match envelope digest", code="RKR260", claim="C2")

        # Technical submission signature must bind the same digest; never treat as authority.
        submission = material.get("logSubmissionSignature")
        if isinstance(submission, dict):
            if submission.get("role") not in {None, "technical-log-submission-only"}:
                raise Phase2Error(
                    "logSubmissionSignature role must be technical-log-submission-only",
                    code="RKR261",
                    claim="C2",
                )

        proof = material["inclusionProof"]
        rekor_v1.verify_set(
            body=body,
            integrated_time=int(material["integratedTime"]),
            log_id_hex=str(material["logIdHex"]),
            log_index=int(receipt["logIndex"]),
            signature_b64=str(material["signedEntryTimestampB64"]),
            public_key=trust_key,
        )
        rekor_v1.verify_merkle_inclusion(
            body=body,
            log_index=int(proof["logIndex"]),
            tree_size=int(proof["treeSize"]),
            hashes_hex=list(proof.get("hashes") or []),
            root_hex=str(proof["rootHash"]),
        )
        rekor_v1.verify_checkpoint(
            checkpoint=str(material["checkpoint"]),
            public_key=trust_key,
            key_id=rekor_v1.key_id_bytes(trust_key),
            root_hex=str(proof["rootHash"]),
            tree_size=int(proof["treeSize"]),
        )

        anchored_at = datetime.fromtimestamp(int(material["integratedTime"]), tz=timezone.utc)
        claimed = datetime.fromisoformat(receipt["anchoredAt"].replace("Z", "+00:00"))
        if int(claimed.timestamp()) != int(anchored_at.timestamp()):
            raise Phase2Error("receipt anchoredAt does not match signed integratedTime", code="RKR262", claim="C2")
        _assert_validity_window(
            when=anchored_at,
            valid_from=pin.get("validFrom"),
            valid_until=pin.get("validUntil"),
        )

        # Fixture profile is labeled in trust boundary; production profile rejects fixture receipts above.
        return TemporalClaim(
            profile_id=self.profile_id,
            anchored_at=anchored_at,
            envelope_digest_hex=digest,
            trust_boundary=self._trust_boundary(),
        )


def build_fixture_trust_policy(*, public_key_pem: str, log_identity: str, shard: str = "fixture") -> dict[str, Any]:
    key = rekor_v1.load_public_key_pem(public_key_pem)
    return {
        "trustPolicyVersion": "1",
        "policyId": "ens-gdi-rekor-v2-fixture-policy",
        "validFrom": "2020-01-01T00:00:00Z",
        "validUntil": "2099-01-01T00:00:00Z",
        "anchors": {
            "rekor-v2": {
                "logIdentity": log_identity,
                "shard": shard,
                "publicKeyPem": public_key_pem,
                "keyIdHex": rekor_v1.key_id_bytes(key).hex(),
                "validFrom": "2020-01-01T00:00:00Z",
                "validUntil": "2099-01-01T00:00:00Z",
            }
        },
    }
