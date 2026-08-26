"""Tests for machine-readable retrospective-corpus study progress reporting."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from study_status import StudyStatusError, _load_json, compute_study_status  # noqa: E402

ROOT = SCRIPT_DIR.parent
PLAN = json.loads((ROOT / "corpus" / "study-plan.json").read_text(encoding="utf-8"))


def _case(case_id: str, strata: list[str], *, double: bool = False) -> dict:
    return {
        "caseId": case_id,
        "template": False,
        "selection": {"strata": strata},
        "review": {"doubleAnnotation": double},
        "source": f"synthetic/{case_id}/case.json",
    }


def test_study_plan_loader_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    path = tmp_path / "study-plan.json"
    path.write_text('{"studyPlanVersion":"1","studyPlanVersion":"2"}\n', encoding="utf-8")

    with pytest.raises(StudyStatusError) as exc:
        _load_json(path, label="study plan", code="STUDY001")
    assert exc.value.code == "STUDY001"
    assert "duplicate JSON object key" in str(exc.value)


def test_in_progress_report_does_not_treat_incomplete_study_as_machine_failure() -> None:
    cases = [
        _case("a", ["approved-award", "merit-decision", "committee-quorum", "recusal-or-conflict"]),
        _case("b", ["policy-change-or-ambiguity", "delivery-or-milestone", "incomplete-public-record"]),
        _case("c", ["public-private-separation"]),
    ]
    result = compute_study_status(copy.deepcopy(PLAN), cases)
    assert result["ok"] is True
    assert result["status"] == "in-progress"
    assert result["readyForFinalReview"] is False
    assert result["caseCount"]["observed"] == 3
    assert result["strata"]["requiredUnresolved"] == ["hard-eligibility"]
    assert result["doubleAnnotation"]["observedFraction"] == 0.0
    assert result["doubleAnnotation"]["minimumCasesNeededForCurrentCorpus"] == 1
    assert "public-private-separation" in result["strata"]["conditionalCovered"]


def test_ready_for_final_review_requires_all_machine_checkable_gates() -> None:
    required = PLAN["sampling"]["requiredStrataWhereEvidenceExists"]
    cases = [
        _case("case-1", required[:4], double=True),
        _case("case-2", required[4:], double=True),
    ]
    for index in range(3, 9):
        cases.append(_case(f"case-{index}", ["merit-decision"]))
    result = compute_study_status(copy.deepcopy(PLAN), cases)
    assert result["caseCount"]["observed"] == 8
    assert result["doubleAnnotation"]["observedFraction"] == 0.25
    assert result["strata"]["requiredUnresolved"] == []
    assert result["readyForFinalReview"] is True
    assert result["status"] == "ready-for-final-review"
    assert all(result["gates"].values())


def test_exceeding_predeclared_maximum_is_reported_as_protocol_deviation() -> None:
    required = PLAN["sampling"]["requiredStrataWhereEvidenceExists"]
    cases = [_case("covered", required, double=True)]
    for index in range(2, 14):
        cases.append(_case(f"case-{index}", ["merit-decision"], double=index <= 4))
    result = compute_study_status(copy.deepcopy(PLAN), cases)
    assert result["caseCount"]["observed"] == 13
    assert result["status"] == "protocol-deviation"
    assert result["readyForFinalReview"] is False
    assert result["gates"]["maximumCaseCountNotExceeded"] is False


def test_duplicate_case_ids_fail_closed() -> None:
    cases = [_case("duplicate", ["merit-decision"]), _case("duplicate", ["approved-award"])]
    with pytest.raises(StudyStatusError) as exc:
        compute_study_status(copy.deepcopy(PLAN), cases)
    assert exc.value.code == "STUDY005"


def test_template_case_in_empirical_set_fails_closed() -> None:
    case = _case("template", ["merit-decision"])
    case["template"] = True
    with pytest.raises(StudyStatusError) as exc:
        compute_study_status(copy.deepcopy(PLAN), [case])
    assert exc.value.code == "STUDY004"


def test_required_and_conditional_strata_must_be_disjoint() -> None:
    plan = copy.deepcopy(PLAN)
    plan["sampling"]["conditionalStrata"].append(plan["sampling"]["requiredStrataWhereEvidenceExists"][0])
    with pytest.raises(StudyStatusError) as exc:
        compute_study_status(plan, [])
    assert exc.value.code == "STUDY001"


def test_additional_observed_strata_are_reported_without_becoming_completion_gates() -> None:
    result = compute_study_status(copy.deepcopy(PLAN), [_case("a", ["other"])])
    assert result["strata"]["additionalObserved"] == ["other"]
    assert "other" not in result["strata"]["requiredUnresolved"]
