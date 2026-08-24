"""Tests for preserved source-artifact byte binding."""

from __future__ import annotations

import tempfile
from pathlib import Path

from source_artifact import build_artifact, verify_artifact


def test_source_artifact_round_trip() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "policy.txt"
        path.write_bytes(b"fixed governing policy bytes\n")
        artifact = build_artifact(
            artifact_id="policy-1",
            source_uri="https://example.org/policy",
            file_path=path,
            media_type="text/plain",
            method="manual-export",
            tool="test-harness",
            tool_version="1",
            retrieved_at="2026-08-24T12:00:00Z",
            surfaces=["mandate", "eligibility"],
        )
        result = verify_artifact(artifact, path)
        assert result["ok"]


def test_source_artifact_tamper_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "policy.txt"
        path.write_bytes(b"original\n")
        artifact = build_artifact(
            artifact_id="policy-2",
            source_uri="https://example.org/policy",
            file_path=path,
            media_type="text/plain",
            method="manual-export",
            tool="test-harness",
            tool_version="1",
            retrieved_at="2026-08-24T12:00:00Z",
        )
        path.write_bytes(b"mutated\n")
        result = verify_artifact(artifact, path)
        assert not result["ok"]
        assert not result["checks"]["sha256"]
