"""Profile schema and ENS adoption profile tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    Draft202012Validator = None

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "profiles"
SCHEMA_PATH = PROFILES / "profile.schema.json"

EXPECTED_PROFILES = {
    "ens-foundation-tier-a-v1",
    "ens-foundation-tier-b-v1",
    "ens-foundation-tier-c-v1",
    "legacy-spp-mapping-v1",
}


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


@pytest.mark.skipif(Draft202012Validator is None, reason="jsonschema not installed")
def test_profile_schema_is_draft_2020_12() -> None:
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)


@pytest.mark.skipif(Draft202012Validator is None, reason="jsonschema not installed")
def test_all_profiles_validate_and_list_claims() -> None:
    schema = _load(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    found = set()
    for path in sorted(PROFILES.glob("*.json")):
        if path.name == "profile.schema.json":
            continue
        data = _load(path)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        assert not errors, f"{path.name}: {errors[0].message}"
        assert "requiredClaims" in data
        assert "optionalClaims" in data
        assert data["profileId"] == path.stem
        # Profiles state evidence requirements, not merit criteria.
        blob = json.dumps(data).lower()
        assert "merit score" not in blob
        assert "approve/reject recommendation engine" in blob or "no merit" in blob
        found.add(data["profileId"])
    assert found == EXPECTED_PROFILES


def test_legacy_profile_is_historical_only() -> None:
    data = _load(PROFILES / "legacy-spp-mapping-v1.json")
    assert data["legacyMapping"]["historicalOnly"] is True
    assert "contemporaneously" in data["legacyMapping"]["disclaimer"]


def test_each_profile_states_policy_source_capture() -> None:
    for profile_id in EXPECTED_PROFILES:
        data = _load(PROFILES / f"{profile_id}.json")
        assert "policySourceCapture" in data
        assert isinstance(data["policySourceCapture"]["required"], bool)


def test_templates_cover_required_worksheets() -> None:
    templates = ROOT / "templates"
    required = {
        "round-setup.md",
        "roster-conflicts.md",
        "decision-memo.md",
        "delivery-milestone.md",
        "challenge-correction.md",
        "evaluator-manifest.md",
        "projection-redaction.md",
        "source-capture.md",
    }
    present = {p.name for p in templates.glob("*.md")}
    assert required <= present
