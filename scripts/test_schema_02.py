"""Tests for schema 0.2 policy pinning and structured authority."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from conformance import check_schema_02_extensions, validate_record  # noqa: E402

EXAMPLE = json.loads((ROOT / "examples" / "tier-a-simplified-grant.example.json").read_text(encoding="utf-8"))


def codes(record: dict) -> set[str]:
    return {finding.code for finding in validate_record(record)}


def test_tier_a_example_passes() -> None:
    findings = validate_record(EXAMPLE)
    errors = [finding for finding in findings if finding.severity == "error"]
    assert not errors, [finding.render() for finding in errors]


def test_unpinned_uri_fails_pol007() -> None:
    record = copy.deepcopy(EXAMPLE)
    record["policyPinning"]["sources"].append(
        {
            "uri": "https://example.com/not-in-sources",
            "contentHash": "sha256:" + "ab" * 32,
            "surface": "other",
        }
    )
    assert "POL007" in codes(record)


def test_bad_content_hash_fails_pol008() -> None:
    record = copy.deepcopy(EXAMPLE)
    record["policyPinning"]["sources"][0]["contentHash"] = "sha256:" + "g" * 64
    findings = check_schema_02_extensions(record)
    assert any(finding.code == "POL008" for finding in findings)


def test_ai_in_authority_identity_fails_auth006() -> None:
    record = copy.deepcopy(EXAMPLE)
    record["evaluators"].append(
        {
            "evaluatorId": "ai-helper",
            "displayName": "Illustrative AI",
            "kind": "ai",
            "role": "advisory",
            "participated": True,
            "recused": False,
            "recusalReason": None,
            "materiallyInformedRecommendation": False,
        }
    )
    record["authorityIdentity"]["members"].append(
        {"memberId": "bad-ai", "evaluatorId": "ai-helper", "role": "member"}
    )
    assert "AUTH006" in codes(record)


def test_authority_kind_mismatch_fails_auth004() -> None:
    record = copy.deepcopy(EXAMPLE)
    record["authorityIdentity"]["authorityKind"] = "human"
    assert "AUTH004" in codes(record)
