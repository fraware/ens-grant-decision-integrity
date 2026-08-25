"""Projection v2 adversarial and property tests."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

from project import project_record as project_record_v1  # noqa: E402
from project_v2 import (  # noqa: E402
    ProjectionError,
    format_withheld_commitment,
    parse_json_pointer,
    project_record_v2,
    verify_projection_v2,
    verify_withheld_v2,
    withheld_digest_v2,
)

CONFIDENTIAL = json.loads((REPO / "examples" / "tier-a-simplified-grant.example.json").read_text(encoding="utf-8"))
SPEC_V1 = json.loads((ROOT / "examples" / "tier-a-projection-spec.json").read_text(encoding="utf-8"))
SPEC_V2 = json.loads((ROOT / "examples" / "tier-a-projection-spec-v2.json").read_text(encoding="utf-8"))
SPEC_SCHEMA = json.loads((ROOT / "schema" / "projection-spec-v2.schema.json").read_text(encoding="utf-8"))
PUBLIC_SCHEMA = json.loads((REPO / "schema" / "grant-decision-public-projection-v2.schema.json").read_text(encoding="utf-8"))


def test_v1_still_works() -> None:
    result = project_record_v1(CONFIDENTIAL, SPEC_V1)
    assert "application" not in result.public_record
    assert result.public_record["integrity"]["recordHashAlgorithm"] == "sha256-jcs-projection-v1"


def test_v2_deterministic_and_schema_valid() -> None:
    first = project_record_v2(CONFIDENTIAL, SPEC_V2)
    second = project_record_v2(CONFIDENTIAL, SPEC_V2)
    assert first.projection_digest == second.projection_digest
    assert first.public_record == second.public_record
    assert "application" not in first.public_record
    assert "notes" not in first.public_record
    assert "projectionIntegrity" in first.public_record
    assert "integrity" not in first.public_record or first.public_record.get("integrity") is None
    jsonschema.Draft202012Validator(SPEC_SCHEMA).validate(SPEC_V2)
    jsonschema.Draft202012Validator(PUBLIC_SCHEMA).validate(first.public_record)


def test_path_bound_commitment_differs_across_paths() -> None:
    subtree = {"flag": True}
    left = withheld_digest_v2(pointer="/a", subtree=subtree)
    right = withheld_digest_v2(pointer="/b", subtree=subtree)
    assert left != right


def test_key_reorder_same_digest() -> None:
    a = withheld_digest_v2(pointer="/x", subtree={"b": 1, "a": 2})
    b = withheld_digest_v2(pointer="/x", subtree={"a": 2, "b": 1})
    assert a == b


def test_nested_withhold_and_source_integrity_separation() -> None:
    record = copy.deepcopy(CONFIDENTIAL)
    record["integrity"] = {
        "recordHashAlgorithm": "sha256",
        "recordHash": "source-integrity-preserved",
    }
    spec = copy.deepcopy(SPEC_V2)
    # Replace whole-application withhold with descend + nested withhold.
    spec["rules"] = [rule for rule in spec["rules"] if rule["path"] != "/application"]
    spec["rules"].extend(
        [
            {"path": "/application", "action": "descend"},
            {"path": "/application/applicationId", "action": "publish-subtree"},
            {
                "path": "/application/applicantName",
                "action": "withhold-subtree",
                "category": "privacy",
                "explanation": "name withheld",
            },
            {"path": "/application/requestedAmount", "action": "publish-subtree"},
            {"path": "/application/currency", "action": "publish-subtree"},
            {"path": "/application/confidential", "action": "publish-subtree"},
            {
                "path": "/integrity",
                "action": "withhold-subtree",
                "category": "security",
                "explanation": "source integrity withheld",
            },
        ]
    )
    # Remove prior integrity publish rule.
    spec["rules"] = [rule for rule in spec["rules"] if not (rule["path"] == "/integrity" and rule["action"] == "publish-subtree")]
    result = project_record_v2(record, spec)
    assert result.public_record["application"]["applicationId"] == "tier-a-fictional-001"
    assert "applicantName" not in result.public_record["application"]
    assert "integrity" not in result.public_record or result.public_record.get("integrity") is None
    assert result.public_record["sourceIntegrityDisposition"]["action"] == "withheld-subtree"
    assert "projectionIntegrity" in result.public_record
    revealed = record["application"]["applicantName"]
    report = verify_withheld_v2(
        public=result.public_record,
        path="/application/applicantName",
        revealed_subtree=revealed,
    )
    assert report["ok"] is True


def test_omitted_child_under_descend_fails() -> None:
    spec = copy.deepcopy(SPEC_V2)
    spec["rules"] = [rule for rule in spec["rules"] if rule["path"] != "/challenge"]
    with pytest.raises(ProjectionError) as exc:
        project_record_v2(CONFIDENTIAL, spec)
    assert exc.value.code == "PROJ209"


def test_terminal_parent_plus_child_fails() -> None:
    spec = copy.deepcopy(SPEC_V2)
    spec["rules"].append({"path": "/program/name", "action": "publish-subtree"})
    with pytest.raises(ProjectionError) as exc:
        project_record_v2(CONFIDENTIAL, spec)
    assert exc.value.code == "PROJ210"


def test_duplicate_pointer_fails() -> None:
    spec = copy.deepcopy(SPEC_V2)
    spec["rules"].append({"path": "/recordId", "action": "publish-subtree"})
    with pytest.raises(ProjectionError) as exc:
        project_record_v2(CONFIDENTIAL, spec)
    assert exc.value.code == "PROJ208"


def test_malformed_pointer_fails() -> None:
    with pytest.raises(ProjectionError) as exc:
        parse_json_pointer("application/name")
    assert exc.value.code == "PROJ201"
    with pytest.raises(ProjectionError):
        parse_json_pointer("/bad/~2")


def test_pointer_escaping() -> None:
    assert parse_json_pointer("/a~1b/~0c") == ["a/b", "~c"]


def test_array_index_rejected() -> None:
    spec = copy.deepcopy(SPEC_V2)
    spec["rules"] = [rule for rule in spec["rules"] if rule["path"] != "/evidence"]
    spec["rules"].extend(
        [
            {"path": "/evidence", "action": "descend"},
            {"path": "/evidence/0", "action": "publish-subtree"},
        ]
    )
    with pytest.raises(ProjectionError) as exc:
        project_record_v2(CONFIDENTIAL, spec)
    assert exc.value.code == "PROJ214"


def test_atomic_array_withhold() -> None:
    spec = copy.deepcopy(SPEC_V2)
    for rule in spec["rules"]:
        if rule["path"] == "/evidence":
            rule["action"] = "withhold-subtree"
            rule["category"] = "privacy"
            rule["explanation"] = "evidence withheld"
    result = project_record_v2(CONFIDENTIAL, spec)
    assert "evidence" not in result.public_record
    assert "/evidence" in result.withheld_commitments


def test_absent_required_rule_target_fails() -> None:
    spec = copy.deepcopy(SPEC_V2)
    spec["rules"].append({"path": "/missingField", "action": "publish-subtree"})
    with pytest.raises(ProjectionError) as exc:
        project_record_v2(CONFIDENTIAL, spec)
    assert exc.value.code == "PROJ212"


def test_when_absent_ignore_succeeds() -> None:
    spec = copy.deepcopy(SPEC_V2)
    spec["rules"].append(
        {"path": "/optionalFuture", "action": "publish-subtree", "whenAbsent": "ignore"}
    )
    result = project_record_v2(CONFIDENTIAL, spec)
    assert "optionalFuture" not in result.public_record


def test_verify_projection_detects_tamper() -> None:
    result = project_record_v2(CONFIDENTIAL, SPEC_V2)
    public = copy.deepcopy(result.public_record)
    public["decision"] = copy.deepcopy(public["decision"])
    public["decision"]["awardedAmount"] = 1
    with pytest.raises(ProjectionError) as exc:
        verify_projection_v2(CONFIDENTIAL, SPEC_V2, public)
    assert exc.value.code in {"PROJ225", "PROJ228"}


def test_source_or_spec_mutation_invalidates() -> None:
    result = project_record_v2(CONFIDENTIAL, SPEC_V2)
    mutated_source = copy.deepcopy(CONFIDENTIAL)
    mutated_source["recordId"] = "tampered"
    with pytest.raises(ProjectionError):
        verify_projection_v2(mutated_source, SPEC_V2, result.public_record)
    mutated_spec = copy.deepcopy(SPEC_V2)
    mutated_spec["profileId"] = "other-profile"
    with pytest.raises(ProjectionError):
        verify_projection_v2(CONFIDENTIAL, mutated_spec, result.public_record)


def test_path_mutation_fails_reopen() -> None:
    result = project_record_v2(CONFIDENTIAL, SPEC_V2)
    with pytest.raises(ProjectionError) as exc:
        verify_withheld_v2(
            public=result.public_record,
            path="/application",
            revealed_subtree={"wrong": True},
        )
    assert exc.value.code == "PROJ230"


def test_algorithm_mismatch_fails() -> None:
    result = project_record_v2(CONFIDENTIAL, SPEC_V2)
    public = copy.deepcopy(result.public_record)
    public["withheldCommitments"]["/application"]["commitment"] = "sha256-jcs-v1:" + ("ab" * 32)
    with pytest.raises(ProjectionError) as exc:
        verify_withheld_v2(
            public=public,
            path="/application",
            revealed_subtree=CONFIDENTIAL["application"],
        )
    assert exc.value.code == "PROJ215"


def test_generated_fields_from_source_rejected() -> None:
    record = copy.deepcopy(CONFIDENTIAL)
    record["projectionIntegrity"] = {"algorithm": "evil"}
    with pytest.raises(ProjectionError) as exc:
        project_record_v2(record, SPEC_V2)
    assert exc.value.code == "PROJ216"


def test_commitment_format() -> None:
    digest = "a" * 64
    assert format_withheld_commitment(digest) == f"sha256-jcs-path-v2:{digest}"
