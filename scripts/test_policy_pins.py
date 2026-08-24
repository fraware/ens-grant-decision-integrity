"""Tests for policy-pin linkage through metadata to preserved bytes."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from source_artifact import SourceArtifactError, build_artifact, verify_artifact  # noqa: E402
from verify_policy_pins import (  # noqa: E402
    ArtifactInput,
    PolicyPinError,
    load_verified_artifact,
    verify_policy_pins,
)


def _record(uri: str, content_hash: str, *, surface: str | None = "mandate") -> dict:
    pin = {"uri": uri, "contentHash": content_hash}
    if surface is not None:
        pin["surface"] = surface
    return {
        "policyPinning": {
            "algorithm": "sha256",
            "pinnedAt": "2026-08-24T12:00:00Z",
            "sources": [pin],
        }
    }


def _verified(
    tmp_path: Path,
    *,
    artifact_id: str = "artifact-1",
    source_uri: str = "https://example.org/policy",
    resolved_uri: str | None = None,
    content: bytes = b"policy bytes\n",
):
    path = tmp_path / f"{artifact_id}.bin"
    path.write_bytes(content)
    metadata = build_artifact(
        artifact_id=artifact_id,
        source_uri=source_uri,
        resolved_uri=resolved_uri,
        file_path=path,
        media_type="application/octet-stream",
        method="manual-export",
        tool="test-harness",
        tool_version="1",
        captured_at="2026-08-24T12:00:00Z",
    )
    return verify_artifact(metadata, path), path


def test_matching_policy_pin_requires_byte_verified_artifact(tmp_path: Path) -> None:
    verified, _ = _verified(tmp_path)
    result = verify_policy_pins(_record("https://example.org/policy", verified.observed_content_hash), [verified])
    assert result["ok"]
    assert result["checks"][0]["matchingArtifactIds"] == ["artifact-1"]


def test_policy_pin_hash_mismatch_fails(tmp_path: Path) -> None:
    verified, _ = _verified(tmp_path)
    record = _record("https://example.org/policy", "sha256:" + "ab" * 32)
    result = verify_policy_pins(record, [verified])
    assert not result["ok"]
    assert result["checks"][0]["matchingArtifactIds"] == []


def test_uri_mismatch_fails_even_for_identical_bytes(tmp_path: Path) -> None:
    verified, _ = _verified(tmp_path)
    record = _record("https://example.org/other-policy", verified.observed_content_hash)
    result = verify_policy_pins(record, [verified])
    assert not result["ok"]
    assert result["checks"][0]["candidateArtifactIds"] == []


def test_resolved_uri_can_match_pin_exactly(tmp_path: Path) -> None:
    resolved = "https://cdn.example.org/policy-v1"
    verified, _ = _verified(tmp_path, resolved_uri=resolved)
    result = verify_policy_pins(_record(resolved, verified.observed_content_hash), [verified])
    assert result["ok"]


def test_surface_is_record_context_not_source_artifact_trust(tmp_path: Path) -> None:
    verified, _ = _verified(tmp_path)
    result = verify_policy_pins(
        _record("https://example.org/policy", verified.observed_content_hash, surface="decisionProcedure"),
        [verified],
    )
    assert result["ok"]
    assert result["checks"][0]["surface"] == "decisionProcedure"


def test_duplicate_artifact_ids_fail_closed(tmp_path: Path) -> None:
    first, _ = _verified(tmp_path, artifact_id="duplicate", content=b"first\n")
    second_path = tmp_path / "second.bin"
    second_path.write_bytes(b"second\n")
    second_meta = build_artifact(
        artifact_id="duplicate",
        source_uri="https://example.org/policy-2",
        file_path=second_path,
        media_type="application/octet-stream",
        method="manual-export",
        tool="test-harness",
        tool_version="1",
        captured_at="2026-08-24T12:00:00Z",
    )
    second = verify_artifact(second_meta, second_path)
    with pytest.raises(PolicyPinError) as exc:
        verify_policy_pins(_record("https://example.org/policy", first.observed_content_hash), [first, second])
    assert exc.value.code == "PIN005"


def test_duplicate_policy_pin_uris_fail_closed(tmp_path: Path) -> None:
    verified, _ = _verified(tmp_path)
    record = _record("https://example.org/policy", verified.observed_content_hash)
    record["policyPinning"]["sources"].append(copy.deepcopy(record["policyPinning"]["sources"][0]))
    with pytest.raises(PolicyPinError) as exc:
        verify_policy_pins(record, [verified])
    assert exc.value.code == "PIN009"


def test_no_policy_pinning_is_explicitly_not_applicable() -> None:
    result = verify_policy_pins({}, [])
    assert result["ok"]
    assert result["applicable"] is False
    assert result["checks"] == []


def test_loader_rehashes_bytes_before_policy_matching(tmp_path: Path) -> None:
    verified, path = _verified(tmp_path)
    metadata_path = tmp_path / "artifact.json"
    metadata_path.write_text(json.dumps(verified.metadata), encoding="utf-8")
    path.write_bytes(b"tampered bytes\n")
    with pytest.raises(PolicyPinError) as exc:
        load_verified_artifact(ArtifactInput(metadata_path, path))
    assert exc.value.code == "PIN007"


def test_direct_artifact_verification_rejects_tampered_bytes(tmp_path: Path) -> None:
    verified, path = _verified(tmp_path)
    metadata = copy.deepcopy(verified.metadata)
    path.write_bytes(b"tampered bytes\n")
    with pytest.raises(SourceArtifactError):
        verify_artifact(metadata, path)
