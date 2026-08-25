#!/usr/bin/env python3
"""Report progress against the predeclared retrospective-corpus study plan."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from gdi.corpus.metrics import CorpusCaseError, compute_metrics

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PLAN = ROOT / "corpus" / "study-plan.json"
DEFAULT_CASES_DIR = ROOT / "corpus" / "cases"


class StudyStatusError(Exception):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


def _load_json(path: Path, *, label: str, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StudyStatusError(f"cannot load {label} {path}: {exc}", code=code) from exc
    if not isinstance(value, dict):
        raise StudyStatusError(f"{label} must be a JSON object: {path}", code=code)
    return value


def _unique_strings(value: Any, *, label: str, code: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise StudyStatusError(f"{label} must be a list of non-empty strings", code=code)
    if len(value) != len(set(value)):
        raise StudyStatusError(f"{label} must not contain duplicates", code=code)
    return value


def _plan_parameters(plan: dict[str, Any]) -> tuple[int, int, list[str], list[str], float]:
    sampling = plan.get("sampling")
    annotation = plan.get("annotation")
    if not isinstance(sampling, dict) or not isinstance(annotation, dict):
        raise StudyStatusError("study plan must define sampling and annotation objects", code="STUDY001")

    minimum = sampling.get("targetMinimumCases")
    maximum = sampling.get("targetMaximumCases")
    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
        raise StudyStatusError("sampling.targetMinimumCases must be a positive integer", code="STUDY001")
    if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < minimum:
        raise StudyStatusError("sampling.targetMaximumCases must be >= targetMinimumCases", code="STUDY001")

    required = _unique_strings(
        sampling.get("requiredStrataWhereEvidenceExists"),
        label="sampling.requiredStrataWhereEvidenceExists",
        code="STUDY001",
    )
    conditional = _unique_strings(
        sampling.get("conditionalStrata"),
        label="sampling.conditionalStrata",
        code="STUDY001",
    )
    overlap = sorted(set(required) & set(conditional))
    if overlap:
        raise StudyStatusError(f"required and conditional strata must be disjoint: {overlap}", code="STUDY001")

    fraction = annotation.get("doubleAnnotationMinimumFraction")
    if not isinstance(fraction, (int, float)) or isinstance(fraction, bool) or not 0 <= fraction <= 1:
        raise StudyStatusError("annotation.doubleAnnotationMinimumFraction must be between 0 and 1", code="STUDY001")
    return minimum, maximum, required, conditional, float(fraction)


def _case_summary(case: dict[str, Any], *, source: str) -> dict[str, Any]:
    if case.get("template") is True:
        raise StudyStatusError(f"empirical case directory contains template=true case: {source}", code="STUDY004")
    case_id = case.get("caseId")
    selection = case.get("selection")
    review = case.get("review")
    if not isinstance(case_id, str) or not case_id:
        raise StudyStatusError(f"case has no non-empty caseId: {source}", code="STUDY003")
    if not isinstance(selection, dict) or not isinstance(review, dict):
        raise StudyStatusError(f"case lacks selection/review objects: {source}", code="STUDY003")
    strata = _unique_strings(selection.get("strata"), label=f"{case_id} selection.strata", code="STUDY003")
    double = review.get("doubleAnnotation")
    if not isinstance(double, bool):
        raise StudyStatusError(f"{case_id} review.doubleAnnotation must be boolean", code="STUDY003")
    return {"caseId": case_id, "source": source, "strata": strata, "doubleAnnotation": double}


def discover_cases(cases_dir: Path) -> list[dict[str, Any]]:
    if not cases_dir.is_dir():
        raise StudyStatusError(f"cases directory does not exist: {cases_dir}", code="STUDY002")
    cases: list[dict[str, Any]] = []
    for path in sorted(cases_dir.glob("*/case.json")):
        case = _load_json(path, label="corpus case", code="STUDY003")
        try:
            compute_metrics(case, base_dir=path.parent)
        except CorpusCaseError as exc:
            raise StudyStatusError(
                f"corpus case contract failed for {path} ({exc.code}): {exc}",
                code="STUDY003",
            ) from exc
        case["source"] = str(path.relative_to(ROOT))
        cases.append(case)
    return cases


def compute_study_status(plan: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
    minimum, maximum, required, conditional, minimum_double_fraction = _plan_parameters(plan)
    normalized = [_case_summary(case, source=case.get("source", "<memory>")) for case in cases]

    case_ids = [case["caseId"] for case in normalized]
    if len(case_ids) != len(set(case_ids)):
        duplicates = sorted({case_id for case_id in case_ids if case_ids.count(case_id) > 1})
        raise StudyStatusError(f"duplicate empirical caseId values: {duplicates}", code="STUDY005")

    coverage: dict[str, list[str]] = defaultdict(list)
    for case in normalized:
        for stratum in case["strata"]:
            coverage[stratum].append(case["caseId"])
    coverage = {stratum: sorted(ids) for stratum, ids in sorted(coverage.items())}

    count = len(normalized)
    double_count = sum(case["doubleAnnotation"] for case in normalized)
    observed_double_fraction = 0.0 if count == 0 else round(double_count / count, 6)
    required_unresolved = [stratum for stratum in required if stratum not in coverage]
    required_covered = [stratum for stratum in required if stratum in coverage]
    conditional_covered = [stratum for stratum in conditional if stratum in coverage]
    conditional_uncovered = [stratum for stratum in conditional if stratum not in coverage]
    additional = sorted(set(coverage) - set(required) - set(conditional))

    gates = {
        "minimumCaseCountMet": count >= minimum,
        "maximumCaseCountNotExceeded": count <= maximum,
        "requiredStrataDeclaredCoverageMet": not required_unresolved,
        "doubleAnnotationFractionMet": observed_double_fraction >= minimum_double_fraction,
    }
    ready = all(gates.values())
    status = "protocol-deviation" if count > maximum else "ready-for-final-review" if ready else "in-progress"

    blockers: list[str] = []
    if count < minimum:
        blockers.append(f"case-count: {count}/{minimum} minimum")
    if count > maximum:
        blockers.append(f"case-count: {count} exceeds predeclared maximum {maximum}")
    if required_unresolved:
        blockers.append(
            "required-strata-unresolved: "
            + ", ".join(required_unresolved)
            + " (coverage or evidence-availability disposition required)"
        )
    if observed_double_fraction < minimum_double_fraction:
        blockers.append(
            f"double-annotation: {double_count}/{count} cases ({observed_double_fraction:.6f}) "
            f"below minimum fraction {minimum_double_fraction:.6f}"
        )

    return {
        "ok": True,
        "studyPlanVersion": plan.get("studyPlanVersion"),
        "status": status,
        "readyForFinalReview": ready,
        "caseCount": {"observed": count, "targetMinimum": minimum, "targetMaximum": maximum},
        "cases": [
            {"caseId": case["caseId"], "strata": case["strata"], "doubleAnnotation": case["doubleAnnotation"]}
            for case in sorted(normalized, key=lambda item: item["caseId"])
        ],
        "strata": {
            "coverage": coverage,
            "requiredCovered": required_covered,
            "requiredUnresolved": required_unresolved,
            "conditionalCovered": conditional_covered,
            "conditionalUncovered": conditional_uncovered,
            "additionalObserved": additional,
        },
        "doubleAnnotation": {
            "caseCount": double_count,
            "observedFraction": observed_double_fraction,
            "minimumFraction": minimum_double_fraction,
            "minimumCasesNeededForCurrentCorpus": 0 if count == 0 else math.ceil(minimum_double_fraction * count),
            "minimumCasesNeededAtTargetMinimum": math.ceil(minimum_double_fraction * minimum),
        },
        "gates": gates,
        "blockers": blockers,
        "nonClaims": [
            "`ok=true` means the study-status computation and counted corpus cases satisfied their machine contracts; it does not mean the empirical study is complete.",
            "`readyForFinalReview=true` means only that the machine-checkable case-count, declared-stratum-coverage, and double-annotation gates are satisfied.",
            "The machine report cannot establish that evidence for an uncovered 'where evidence exists' stratum does not exist.",
            "Stratum coverage does not establish source truth, historical completeness, applicant merit, fairness, or institutional legitimacy.",
            "Conditional strata are reported but are not completion gates unless the predeclared study plan is changed explicitly.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--cases-dir", type=Path, default=DEFAULT_CASES_DIR)
    args = parser.parse_args()
    try:
        result = compute_study_status(
            _load_json(args.plan, label="study plan", code="STUDY001"),
            discover_cases(args.cases_dir),
        )
    except StudyStatusError as exc:
        print(json.dumps({"ok": False, "code": exc.code, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
