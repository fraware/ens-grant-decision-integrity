"""Tests for preserved source-artifact byte binding."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from source_artifact import SourceArtifactError, build_artifact, verify_artifact  # noqa: E402


def _build(path: Path) -> dict:
    return build_artifact(
        artifact_id="policy-1",
        source_uri="https://example.org/policy",
        resolved_uri="https://cdn.example.org/policy-v1",
        file_path=path,
        media_type="text/plain",
        method="manual-export",
        tool="test-harness",
        tool_version="1",
        captured_at="2026-08-24T12:00:00Z",
    )


def test_source_artifact_round_trip_binds_exact_bytes(tmp_path: Path) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(b"fixed governing policy bytes\n")
    artifact = _build(path)
    verified = verify_artifact(artifact, path)
    assert verified.observed_content_hash == artifact["contentHash"]
    assert verified.observed_byte_length == artifact["byteLength"]


def test_same_length_content_tamper_fails_hash(tmp_path: Path) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(b"original\n")
    artifact = _build(path)
    path.write_bytes(b"mutated!\n")
    assert len(b"original\n") == len(b"mutated!\n")
    with pytest.raises(SourceArtifactError) as exc:
        verify_artifact(artifact, path)
    assert exc.value.code == "SRC003"


def test_forged_metadata_hash_fails_against_real_bytes(tmp_path: Path) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(b"captured bytes\n")
    artifact = _build(path)
    forged = copy.deepcopy(artifact)
    forged["contentHash"] = "sha256:" + "00" * 32
    with pytest.raises(SourceArtifactError) as exc:
        verify_artifact(forged, path)
    assert exc.value.code == "SRC003"


def test_forged_byte_length_fails_even_when_hash_matches(tmp_path: Path) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(b"captured bytes\n")
    artifact = _build(path)
    forged = copy.deepcopy(artifact)
    forged["byteLength"] += 1
    with pytest.raises(SourceArtifactError) as exc:
        verify_artifact(forged, path)
    assert exc.value.code == "SRC004"


def test_build_does_not_expose_local_path_by_default(tmp_path: Path) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(b"captured bytes\n")
    artifact = _build(path)
    assert "storedPath" not in artifact


def test_invalid_hash_encoding_is_rejected_as_schema_error(tmp_path: Path) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(b"captured bytes\n")
    artifact = _build(path)
    artifact["contentHash"] = "not-a-hash"
    with pytest.raises(SourceArtifactError) as exc:
        verify_artifact(artifact, path)
    assert exc.value.code == "SRC002"


def test_invalid_capture_timestamp_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(b"captured bytes\n")
    with pytest.raises(SourceArtifactError) as exc:
        build_artifact(
            artifact_id="policy-1",
            source_uri="https://example.org/policy",
            file_path=path,
            media_type="text/plain",
            method="manual-export",
            tool="test-harness",
            tool_version="1",
            captured_at="not-a-time",
        )
    assert exc.value.code == "SRC002"


def test_capture_timestamp_requires_timezone(tmp_path: Path) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(b"captured bytes\n")
    with pytest.raises(SourceArtifactError) as exc:
        build_artifact(
            artifact_id="policy-1",
            source_uri="https://example.org/policy",
            file_path=path,
            media_type="text/plain",
            method="manual-export",
            tool="test-harness",
            tool_version="1",
            captured_at="2026-08-24T12:00:00",
        )
    assert exc.value.code == "SRC002"


def test_source_uri_requires_scheme(tmp_path: Path) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(b"captured bytes\n")
    with pytest.raises(SourceArtifactError) as exc:
        build_artifact(
            artifact_id="policy-1",
            source_uri="example.org/policy",
            file_path=path,
            media_type="text/plain",
            method="manual-export",
            tool="test-harness",
            tool_version="1",
            captured_at="2026-08-24T12:00:00Z",
        )
    assert exc.value.code == "SRC002"
