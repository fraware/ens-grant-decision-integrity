"""Tests for policy-pin linkage to preserved source artifacts."""

from __future__ import annotations

from verify_policy_pins import verify_policy_pins


def _artifact(uri: str, digest: str) -> dict:
    return {
        "artifactVersion": "1",
        "artifactId": "artifact-1",
        "sourceUri": uri,
        "resolvedUri": None,
        "retrievedAt": "2026-08-24T12:00:00Z",
        "httpStatus": 200,
        "mediaType": "text/html",
        "byteLength": 10,
        "sha256": digest,
        "storedPath": None,
        "archiveUri": None,
        "surfaces": ["mandate"],
        "capture": {
            "method": "http",
            "tool": "test-harness",
            "toolVersion": "1",
            "notes": None
        },
        "contentEncoding": None,
        "observations": []
    }


def test_matching_policy_pin_passes() -> None:
    digest = "ab" * 32
    uri = "https://example.org/policy"
    record = {
        "policyPinning": {
            "algorithm": "sha256",
            "pinnedAt": "2026-08-24T12:00:00Z",
            "sources": [{"uri": uri, "contentHash": f"sha256:{digest}", "surface": "mandate"}]
        }
    }
    result = verify_policy_pins(record, [_artifact(uri, digest)])
    assert result["ok"]
    assert result["checks"][0]["matchingArtifactIds"] == ["artifact-1"]


def test_mismatching_policy_pin_fails() -> None:
    uri = "https://example.org/policy"
    record = {
        "policyPinning": {
            "algorithm": "sha256",
            "pinnedAt": "2026-08-24T12:00:00Z",
            "sources": [{"uri": uri, "contentHash": f"sha256:{'ab' * 32}", "surface": "mandate"}]
        }
    }
    result = verify_policy_pins(record, [_artifact(uri, "cd" * 32)])
    assert not result["ok"]
