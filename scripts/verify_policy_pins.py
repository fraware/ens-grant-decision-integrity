#!/usr/bin/env python3
"""Verify schema 0.2 policy pins against preserved source-artifact metadata.

This establishes content-identity linkage between a record's policy pin and a
captured artifact. It does not establish that the captured artifact was validly
adopted policy or that the source was complete.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from source_artifact import _validate as validate_source_artifact


def verify_policy_pins(record: dict[str, Any], artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    pinning = record.get("policyPinning")
    if not isinstance(pinning, dict):
        return {
            "ok": True,
            "applicable": False,
            "checks": [],
            "nonClaims": ["No policyPinning object is present; no source-content identity claim was checked."],
        }

    indexed: dict[str, list[dict[str, Any]]] = {}
    for artifact in artifacts:
        validate_source_artifact(artifact)
        for uri in {artifact.get("sourceUri"), artifact.get("resolvedUri")}:
            if isinstance(uri, str):
                indexed.setdefault(uri, []).append(artifact)

    checks: list[dict[str, Any]] = []
    ok = True
    for pin in pinning.get("sources", []):
        uri = pin["uri"]
        expected = pin["contentHash"].removeprefix("sha256:")
        candidates = indexed.get(uri, [])
        matches = [artifact for artifact in candidates if artifact["sha256"] == expected]
        check = {
            "uri": uri,
            "surface": pin.get("surface"),
            "expectedSha256": expected,
            "candidateArtifactIds": [artifact["artifactId"] for artifact in candidates],
            "matchingArtifactIds": [artifact["artifactId"] for artifact in matches],
            "ok": bool(matches),
        }
        checks.append(check)
        ok = ok and check["ok"]

    return {
        "ok": ok,
        "applicable": True,
        "checks": checks,
        "nonClaims": [
            "A matching hash establishes content identity for the preserved bytes, not institutional adoption.",
            "A matching hash does not establish that the source artifact is complete or substantively correct.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify policyPinning against source-artifact metadata")
    parser.add_argument("--record", required=True)
    parser.add_argument("--artifact", action="append", required=True, dest="artifacts")
    args = parser.parse_args()
    record = json.loads(Path(args.record).read_text(encoding="utf-8"))
    artifacts = [json.loads(Path(path).read_text(encoding="utf-8")) for path in args.artifacts]
    result = verify_policy_pins(record, artifacts)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
