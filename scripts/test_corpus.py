"""Adversarial tests for retrospective corpus case integrity and metrics."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from corpus_metrics import CorpusCaseError, compute_metrics, validate_case  # noqa: E402

ROOT = SCRIPT_DIR.parent
TEMPLATE = json.loads((ROOT / "corpus" / "case-template.json").read_text(encoding="utf-8"))


def _source(artifact_id: str = "src-1") -> dict:
    return {"artifactId": artifact_id, "role": "governing-policy", "availability": "redistributable"}


def _field(path: str, classification: str, *, source_ids: list[str] | None = None, required: bool = True) -> dict:
    value = {
        "path": path,
        "requiredForProfile": required,
        "classification": classification,
        "sourceArtifactIds": source_ids or [],
    }
    if classification in {"derived", "interpretive", "not-applicable"}:
        value["rationale"] = "documented mapping rationale"
    return value


def _case() -> dict:
    case = copy.deepcopy(TEMPLATE)
    case["caseId"] = "case-1"
    case["title"] = "Historical test case"
    case["template"] = False
    case["sourceArtifacts"] = [_source()]
    case["annotations"][0]["annotationId"] = "ann-1"
    case["annotations"][0]["annotatorId"] = "reviewer-a"
    case["annotations"][0]["elapsedMinutes"] = 30
    case["annotations"][0]["fields"] = [
        _field("/program/roundId", "direct-source", source_ids=["src-1"]),
        _field("/decision/status", "derived", source_ids=["src-1"]),
        _field("/challenge/processDefined", "unknown"),
        _field("/deliveryConditions", "not-applicable"),
    ]
    return case


def test_template_is_schema_and_protocol_valid_but_flagged_template() -> None:
    result = compute_metrics(copy.deepcopy(TEMPLATE))
    assert result["ok"]
    assert result["template"] is True
    assert result["annotations"][0]["unknownRate"] == 1.0


def test_required_field_metrics_do_not_treat_unknown_as_success() -> None:
    result = compute_metrics(_case())
    metrics = result["annotations"][0]
    assert metrics["requiredFieldCount"] == 4
    assert metrics["applicableRequiredFieldCount"] == 3
    assert metrics["reconstructabilityRate"] == pytest.approx(2 / 3, abs=1e-6)
    assert metrics["directSourceRate"] == pytest.approx(1 / 3, abs=1e-6)
    assert metrics["unknownRate"] == pytest.approx(1 / 3, abs=1e-6)


def test_duplicate_source_artifact_ids_fail_closed() -> None:
    case = _case()
    case["sourceArtifacts"].append(_source())
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP003"


def test_unknown_source_reference_fails_closed() -> None:
    case = _case()
    case["annotations"][0]["fields"][0]["sourceArtifactIds"] = ["missing"]
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP007"


def test_direct_source_without_source_reference_is_schema_failure() -> None:
    case = _case()
    case["annotations"][0]["fields"][0]["sourceArtifactIds"] = []
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP002"


def test_duplicate_annotation_field_paths_fail_closed() -> None:
    case = _case()
    case["annotations"][0]["fields"].append(copy.deepcopy(case["annotations"][0]["fields"][0]))
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP006"


def test_changed_record_requires_distinct_reconciled_hash() -> None:
    case = _case()
    case["verification"]["recordChangedAfterReview"] = True
    case["verification"]["changeRationale"] = "Review corrected an annotation defect."
    case["recordSnapshots"]["reconciled"] = copy.deepcopy(case["recordSnapshots"]["initial"])
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP011"


def test_changed_record_requires_reconciled_snapshot_at_schema_level() -> None:
    case = _case()
    case["verification"]["recordChangedAfterReview"] = True
    case["verification"]["changeRationale"] = "Review corrected an annotation defect."
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP002"


def test_double_annotation_requires_same_field_set() -> None:
    case = _case()
    second = copy.deepcopy(case["annotations"][0])
    second["annotationId"] = "ann-2"
    second["annotatorId"] = "reviewer-b"
    second["fields"] = second["fields"][:-1]
    case["annotations"].append(second)
    case["review"]["doubleAnnotation"] = True
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP010"


def test_double_annotation_exact_agreement_reports_one() -> None:
    case = _case()
    second = copy.deepcopy(case["annotations"][0])
    second["annotationId"] = "ann-2"
    second["annotatorId"] = "reviewer-b"
    case["annotations"].append(second)
    case["review"]["doubleAnnotation"] = True
    result = compute_metrics(case)
    assert result["agreement"]["rawClassificationAgreement"] == 1.0
    assert result["agreement"]["cohenKappa"] == 1.0


def test_double_annotation_disagreement_changes_agreement_metrics() -> None:
    case = _case()
    second = copy.deepcopy(case["annotations"][0])
    second["annotationId"] = "ann-2"
    second["annotatorId"] = "reviewer-b"
    second["fields"][2]["classification"] = "interpretive"
    second["fields"][2]["rationale"] = "Reviewer mapped an ambiguous public statement."
    case["annotations"].append(second)
    case["review"]["doubleAnnotation"] = True
    result = compute_metrics(case)
    assert result["agreement"]["rawClassificationAgreement"] == 0.75
    assert result["agreement"]["cohenKappa"] < 1.0


def test_required_nonclaims_cannot_be_silently_removed() -> None:
    case = _case()
    case["nonClaims"] = case["nonClaims"][:-1] + ["different caveat"]
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP012"
