"""Reveal, committed, withheld, and selective-audit verification."""

from __future__ import annotations

from typing import Any

from claims import C1_ESTABLISHED, C1_ID, COMMITMENT_DOMAIN
from commitment import open_commitment
from envelope import assert_round_binding
from support import Phase2Error, VerificationResult, validate_schema

V01_REVEAL_MAP = {
    "committed": "committed",
    "revealed": "revealed",
    "selective-audit": "partially-revealed",
    "withheld": "withheld",
}


def map_v01_reveal_status(phase2_status: str) -> str:
    try:
        return V01_REVEAL_MAP[phase2_status]
    except KeyError as exc:
        raise Phase2Error(f"unknown reveal status {phase2_status}", code="REV001") from exc


def verify_reveal(
    *,
    envelope: dict[str, Any],
    reveal_status: str,
    manifest: dict[str, Any] | None = None,
    salt: bytes | None = None,
    domain: str = COMMITMENT_DOMAIN,
) -> VerificationResult:
    established: list[str] = []
    details: dict[str, Any] = {"revealStatus": reveal_status}

    if reveal_status in {"committed", "withheld"}:
        if manifest is not None or salt is not None:
            raise Phase2Error(
                f"{reveal_status} disclosure state must not carry manifest or salt",
                code="REV002",
            )
        if reveal_status == "committed":
            details["establishedNote"] = (
                "Commitment remains unopened. Manifest contents were not checked."
            )
        else:
            details["establishedNote"] = (
                "Withheld disclosure leaves the commitment unopened. Manifest contents were not checked."
            )
        return VerificationResult(ok=True, established=established, details=details)

    if reveal_status == "selective-audit":
        details["establishedNote"] = (
            "Selective-audit is a private full disclosure to an authorized auditor plus a signed "
            "result. This check confirms opening only when manifest and salt are supplied to the verifier."
        )

    if manifest is None or salt is None:
        raise Phase2Error("reveal requires manifest and salt", code="REV003", claim="C1")

    validate_schema(manifest, "evaluator-manifest.schema.json")
    validate_schema(envelope, "commitment-envelope.schema.json")
    open_commitment(digest_hex=envelope["commitmentDigest"], manifest=manifest, salt=salt, domain=domain)
    assert_round_binding(envelope, manifest)
    established.append(C1_ID)
    details[C1_ID] = C1_ESTABLISHED
    return VerificationResult(ok=True, established=established, details=details)
