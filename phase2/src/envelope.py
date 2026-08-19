"""Public commitment envelope. Must not contain salt or hidden contents."""

from __future__ import annotations

from typing import Any

from canonicalize import canonicalize
from claims import COMMITMENT_ALGORITHM_ID, ENVELOPE_TYPE
from commitment import commitment_digest, generate_salt
from support import Phase2Error, sha256_hex, validate_schema


def build_envelope(manifest: dict[str, Any], salt: bytes) -> dict[str, Any]:
    for field in ("programId", "roundId", "applicationDeadline"):
        if field not in manifest:
            raise Phase2Error(f"manifest missing {field}", code="ENV001")
    envelope = {
        "type": ENVELOPE_TYPE,
        "version": "1",
        "programId": manifest["programId"],
        "roundId": manifest["roundId"],
        "applicationDeadline": manifest["applicationDeadline"],
        "commitmentAlgorithm": COMMITMENT_ALGORITHM_ID,
        "commitmentDigest": commitment_digest(manifest, salt),
        "manifestSchemaVersion": str(manifest["manifestVersion"]),
    }
    validate_schema(envelope, "commitment-envelope.schema.json")
    if "salt" in envelope or "saltHex" in envelope or "manifest" in envelope:
        raise Phase2Error("envelope leaked hidden material", code="ENV002")
    return envelope


def commit_manifest(manifest: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
    validate_schema(manifest, "evaluator-manifest.schema.json")
    salt = generate_salt()
    envelope = build_envelope(manifest, salt)
    return envelope, salt


def envelope_bytes(envelope: dict[str, Any]) -> bytes:
    validate_schema(envelope, "commitment-envelope.schema.json")
    return canonicalize(envelope)


def envelope_digest(envelope: dict[str, Any]) -> str:
    return sha256_hex(envelope_bytes(envelope))


def assert_round_binding(envelope: dict[str, Any], manifest: dict[str, Any]) -> None:
    for field in ("programId", "roundId", "applicationDeadline"):
        if envelope.get(field) != manifest.get(field):
            raise Phase2Error(
                f"envelope {field} does not match manifest",
                code="ENV003",
                claim="C3",
            )
