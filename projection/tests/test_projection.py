"""Projection module tests."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(REPO / "scripts"))

from conformance import validate_record  # noqa: E402
from project import ProjectionError, project_record, verify_withheld_commitment  # noqa: E402

CONFIDENTIAL = json.loads((REPO / "examples" / "tier-a-simplified-grant.example.json").read_text(encoding="utf-8"))
SPEC = json.loads((ROOT / "examples" / "tier-a-projection-spec.json").read_text(encoding="utf-8"))


def test_projection_is_deterministic() -> None:
    first = project_record(CONFIDENTIAL, SPEC)
    second = project_record(CONFIDENTIAL, SPEC)
    assert first.projection_digest == second.projection_digest
    assert first.public_record == second.public_record


def test_withheld_application_commitment() -> None:
    result = project_record(CONFIDENTIAL, SPEC)
    assert "application" not in result.public_record
    commitment = result.public_record["withheldCommitments"]["application"]
    assert commitment["category"] == "privacy"
    assert verify_withheld_commitment(CONFIDENTIAL, "application", commitment["commitmentDigest"])


def test_tampered_withheld_commitment_detected() -> None:
    result = project_record(CONFIDENTIAL, SPEC)
    assert not verify_withheld_commitment(CONFIDENTIAL, "application", "00" * 64)


def test_public_projection_validates_as_schema_02() -> None:
    result = project_record(CONFIDENTIAL, SPEC)
    findings = validate_record(result.public_record)
    errors = [finding for finding in findings if finding.severity == "error"]
    assert not errors, [finding.render() for finding in errors]


def test_missing_allowlist_field_fails() -> None:
    bad_spec = copy.deepcopy(SPEC)
    bad_spec["fieldAllowlist"] = ["recordId", "nonexistentField"]
    with pytest.raises(ProjectionError):
        project_record(CONFIDENTIAL, bad_spec)


def test_silent_top_level_omission_fails() -> None:
    bad_spec = copy.deepcopy(SPEC)
    bad_spec["fieldAllowlist"].remove("challenge")
    with pytest.raises(ProjectionError) as exc:
        project_record(CONFIDENTIAL, bad_spec)
    assert exc.value.code == "PROJ011"


def test_publish_and_withhold_same_field_fails() -> None:
    bad_spec = copy.deepcopy(SPEC)
    bad_spec["fieldAllowlist"].append("application")
    with pytest.raises(ProjectionError) as exc:
        project_record(CONFIDENTIAL, bad_spec)
    assert exc.value.code == "PROJ012"
