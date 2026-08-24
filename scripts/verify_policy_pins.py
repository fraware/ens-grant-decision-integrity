#!/usr/bin/env python3
"""Verify schema 0.2 policy pins against byte-verified source artifacts.

A successful check closes a narrow local chain from a policy pin's exact URI and
content hash to source-artifact metadata and then to exact preserved bytes. It
does not establish policy adoption, source truth/completeness, source ownership,
or independent existence at ``pinnedAt``. Decision-surface semantics remain the
responsibility of record schema/conformance validation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from source_artifact import SourceArtifactError, VerifiedSourceArtifact, verify_artifact  # noqa: E402

HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SURFACES = frozenset({
    "mandate",
    "eligibility",
    "evaluationCriteria",
    "conflictRules",
    "decisionProcedure",
    "challengeProcedure",
    "delivery",
    "evidence",
    "other",
})


class PolicyPinError(Exception):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ArtifactInput:
    metadata_path: Path
    bytes_path: Path


def _policy_sources(record: dict[str, Any]) -> list[dict[str, Any]] | None:
    pinning = record.get("policyPinning")
    if pinning is None:
        return None
    if not isinstance(pinning, dict):
        raise PolicyPinError("policyPinning must be an object", code="PIN001")
    if pinning.get("algorithm") != "sha256":
        raise PolicyPinError("policyPinning.algorithm must be sha256", code="PIN002")
    sources = pinning.get("sources")
    if not isinstance(sources, list) or not sources:
        raise PolicyPinError("policyPinning.sources must be a non-empty array", code="PIN003")

    seen_uris: set[str] = set()
    for index, pin in enumerate(sources):
        if not isinstance(pin, dict):
            raise PolicyPinError(f"policyPinning.sources[{index}] must be an object", code="PIN004")
        uri = pin.get("uri")
        content_hash = pin.get("contentHash")
        surface = pin.get("surface")
        if not isinstance(uri, str) or not uri:
            raise PolicyPinError(f"policy pin {index} has invalid uri", code="PIN004")
        if uri in seen_uris:
            raise PolicyPinError(f"policyPinning.sources contains duplicate uri {uri!r}", code="PIN009")
        seen_uris.add(uri)
        if not isinstance(content_hash, str) or not HASH_RE.fullmatch(content_hash):
            raise PolicyPinError(f"policy pin {index} has invalid contentHash", code="PIN004")
        if surface is not None and surface not in SURFACES:
            raise PolicyPinError(f"policy pin {index} has invalid surface", code="PIN004")
    return sources


def verify_policy_pins(
    record: dict[str, Any],
    artifacts: list[VerifiedSourceArtifact],
) -> dict[str, Any]:
    sources = _policy_sources(record)
    if sources is None:
        return {
            "ok": True,
            "applicable": False,
            "checks": [],
            "nonClaims": ["No policyPinning object is present; no source-content identity claim was checked."],
        }

    artifact_ids = [artifact.artifact_id for artifact in artifacts]
    if len(set(artifact_ids)) != len(artifact_ids):
        raise PolicyPinError("verified source-artifact ids must be unique", code="PIN005")

    indexed: dict[str, list[VerifiedSourceArtifact]] = {}
    for artifact in artifacts:
        metadata = artifact.metadata
        for uri in (metadata.get("sourceUri"), metadata.get("resolvedUri")):
            if isinstance(uri, str):
                indexed.setdefault(uri, []).append(artifact)

    checks: list[dict[str, Any]] = []
    overall_ok = True
    for pin in sources:
        uri = pin["uri"]
        candidates = indexed.get(uri, [])
        matches = [artifact for artifact in candidates if artifact.observed_content_hash == pin["contentHash"]]
        check = {
            "uri": uri,
            "surface": pin.get("surface"),
            "expectedContentHash": pin["contentHash"],
            "candidateArtifactIds": [artifact.artifact_id for artifact in candidates],
            "matchingArtifactIds": [artifact.artifact_id for artifact in matches],
            "ok": bool(matches),
        }
        checks.append(check)
        overall_ok = overall_ok and check["ok"]

    return {
        "ok": overall_ok,
        "applicable": True,
        "checks": checks,
        "nonClaims": [
            "A matching byte hash establishes content identity for preserved bytes, not institutional adoption.",
            "A matching byte hash does not establish source truth, completeness, or ownership.",
            "URI matching is exact against sourceUri or resolvedUri; it is not semantic URL equivalence.",
            "The policy pin's decision-surface classification is checked by record conformance, not inferred from source bytes.",
            "This check does not independently prove that the bytes existed at policyPinning.pinnedAt.",
        ],
    }


def load_verified_artifact(item: ArtifactInput) -> VerifiedSourceArtifact:
    try:
        metadata = json.loads(item.metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyPinError(f"cannot load source-artifact metadata: {exc}", code="PIN006") from exc
    if not isinstance(metadata, dict):
        raise PolicyPinError("source-artifact metadata must be a JSON object", code="PIN006")
    try:
        return verify_artifact(metadata, item.bytes_path)
    except SourceArtifactError as exc:
        raise PolicyPinError(
            f"source-artifact byte verification failed ({exc.code}): {exc}",
            code="PIN007",
        ) from exc


def _failure(exc: PolicyPinError) -> dict[str, Any]:
    return {
        "ok": False,
        "applicable": True,
        "code": exc.code,
        "error": str(exc),
        "checks": [],
        "nonClaims": ["A failed policy-pin verification establishes no source-content identity claim."],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify policyPinning against exact preserved source bytes")
    parser.add_argument("--record", required=True)
    parser.add_argument(
        "--artifact",
        action="append",
        nargs=2,
        metavar=("METADATA_JSON", "CAPTURED_BYTES"),
        default=[],
        dest="artifacts",
    )
    args = parser.parse_args(argv)
    try:
        raw_record = json.loads(Path(args.record).read_text(encoding="utf-8"))
        if not isinstance(raw_record, dict):
            raise PolicyPinError("policy-pin record must be a JSON object", code="PIN008")
        verified = [
            load_verified_artifact(ArtifactInput(Path(metadata), Path(raw_bytes)))
            for metadata, raw_bytes in args.artifacts
        ]
        result = verify_policy_pins(raw_record, verified)
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    except (OSError, json.JSONDecodeError) as exc:
        wrapped = PolicyPinError(f"cannot load policy-pin record: {exc}", code="PIN008")
        print(json.dumps(_failure(wrapped), indent=2))
        return 1
    except PolicyPinError as exc:
        print(json.dumps(_failure(exc), indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
