#!/usr/bin/env python3
"""Validate a retrospective corpus case and compute descriptive assurance metrics."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "corpus" / "schema" / "case.schema.json"
REQUIRED_NONCLAIMS = {
    "This corpus case does not reassess applicant merit.",
    "Missing public evidence does not prove a private or internal procedure did not exist.",
    "Validator success does not establish substantive correctness, fairness, or institutional legitimacy.",
}
CATEGORIES = ("direct-source", "derived", "interpretive", "unknown", "not-applicable")


class CorpusCaseError(Exception):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


def _schema_validate(case: dict[str, Any]) -> None:
    import jsonschema

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusCaseError(f"cannot load corpus case schema: {exc}", code="CORP001") from exc
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        raise CorpusCaseError(f"corpus case schema is invalid: {exc.message}", code="CORP001") from exc
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(case), key=lambda error: list(error.absolute_path))
    if errors:
        first = errors[0]
        path = "/".join(str(part) for part in first.absolute_path) or "<root>"
        raise CorpusCaseError(f"schema failure at {path}: {first.message}", code="CORP002")


def _unique(values: list[str], *, label: str, code: str) -> None:
    if len(values) != len(set(values)):
        raise CorpusCaseError(f"{label} must be unique", code=code)


def validate_case(case: dict[str, Any]) -> None:
    _schema_validate(case)

    source_ids = [item["artifactId"] for item in case["sourceArtifacts"]]
    _unique(source_ids, label="source artifact ids", code="CORP003")
    known_sources = set(source_ids)

    annotations = case["annotations"]
    _unique([item["annotationId"] for item in annotations], label="annotation ids", code="CORP004")
    _unique([item["annotatorId"] for item in annotations], label="annotator ids", code="CORP005")

    for annotation in annotations:
        paths = [field["path"] for field in annotation["fields"]]
        _unique(paths, label=f"field paths in {annotation['annotationId']}", code="CORP006")
        for field in annotation["fields"]:
            unknown_refs = sorted(set(field["sourceArtifactIds"]) - known_sources)
            if unknown_refs:
                raise CorpusCaseError(
                    f"{annotation['annotationId']} {field['path']} references unknown source artifacts: {unknown_refs}",
                    code="CORP007",
                )

    finding_ids = [item["findingId"] for item in case["verification"]["initialFindings"]]
    _unique(finding_ids, label="finding ids", code="CORP008")
    for finding in case["verification"]["initialFindings"]:
        unknown_refs = sorted(set(finding.get("sourceArtifactIds", [])) - known_sources)
        if unknown_refs:
            raise CorpusCaseError(
                f"finding {finding['findingId']} references unknown source artifacts: {unknown_refs}",
                code="CORP007",
            )

    double = case["review"]["doubleAnnotation"]
    if double:
        if len(annotations) != 2 or not all(item["independent"] for item in annotations):
            raise CorpusCaseError(
                "doubleAnnotation requires exactly two independently produced annotation sets",
                code="CORP009",
            )
        left = {field["path"] for field in annotations[0]["fields"]}
        right = {field["path"] for field in annotations[1]["fields"]}
        if left != right:
            raise CorpusCaseError(
                "double annotations must cover the same material field paths before reconciliation",
                code="CORP010",
            )
    elif len(annotations) != 1:
        raise CorpusCaseError(
            "case v1 permits one annotation, or exactly two when doubleAnnotation is true",
            code="CORP009",
        )

    if case["verification"]["recordChangedAfterReview"]:
        initial_hash = case["recordSnapshots"]["initial"]["recordHash"]
        reconciled_hash = case["recordSnapshots"]["reconciled"]["recordHash"]
        if initial_hash == reconciled_hash:
            raise CorpusCaseError(
                "recordChangedAfterReview is true but initial and reconciled record hashes are identical",
                code="CORP011",
            )

    if not REQUIRED_NONCLAIMS.issubset(set(case["nonClaims"])):
        missing = sorted(REQUIRED_NONCLAIMS - set(case["nonClaims"]))
        raise CorpusCaseError(f"required corpus non-claims are missing: {missing}", code="CORP012")


def _safe_rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else round(numerator / denominator, 6)


def _annotation_metrics(annotation: dict[str, Any]) -> dict[str, Any]:
    required = [field for field in annotation["fields"] if field["requiredForProfile"]]
    applicable = [field for field in required if field["classification"] != "not-applicable"]
    counts = Counter(field["classification"] for field in applicable)
    reconstructable = counts["direct-source"] + counts["derived"] + counts["interpretive"]
    return {
        "annotationId": annotation["annotationId"],
        "annotatorId": annotation["annotatorId"],
        "elapsedMinutes": annotation["elapsedMinutes"],
        "requiredFieldCount": len(required),
        "applicableRequiredFieldCount": len(applicable),
        "classificationCounts": {category: counts.get(category, 0) for category in CATEGORIES if category != "not-applicable"},
        "reconstructabilityRate": _safe_rate(reconstructable, len(applicable)),
        "directSourceRate": _safe_rate(counts["direct-source"], len(applicable)),
        "unknownRate": _safe_rate(counts["unknown"], len(applicable)),
        "interpretiveShareOfReconstructable": _safe_rate(counts["interpretive"], reconstructable),
    }


def _agreement(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_by_path = {field["path"]: field["classification"] for field in left["fields"]}
    right_by_path = {field["path"]: field["classification"] for field in right["fields"]}
    paths = sorted(left_by_path)
    n = len(paths)
    observed_matches = sum(left_by_path[path] == right_by_path[path] for path in paths)
    observed = observed_matches / n if n else 0.0

    left_counts = Counter(left_by_path[path] for path in paths)
    right_counts = Counter(right_by_path[path] for path in paths)
    expected = sum((left_counts[category] / n) * (right_counts[category] / n) for category in CATEGORIES) if n else 0.0
    if n == 0 or expected == 1.0:
        kappa = None
    else:
        kappa = round((observed - expected) / (1.0 - expected), 6)
    return {
        "comparedFieldCount": n,
        "rawClassificationAgreement": round(observed, 6) if n else None,
        "cohenKappa": kappa,
        "note": "Agreement metrics describe annotation consistency; they do not establish annotation correctness.",
    }


def compute_metrics(case: dict[str, Any]) -> dict[str, Any]:
    validate_case(case)
    finding_counts = Counter(item["disposition"] for item in case["verification"]["initialFindings"])
    result: dict[str, Any] = {
        "ok": True,
        "caseId": case["caseId"],
        "template": case["template"],
        "sourceArtifactCount": len(case["sourceArtifacts"]),
        "annotations": [_annotation_metrics(annotation) for annotation in case["annotations"]],
        "findingDispositionCounts": dict(sorted(finding_counts.items())),
        "initialFindingCount": len(case["verification"]["initialFindings"]),
        "recordChangedAfterReview": case["verification"]["recordChangedAfterReview"],
        "nonClaims": [
            "These are descriptive reconstructability and agreement metrics, not merit or fairness scores.",
            "A low unknown rate does not establish that source evidence is true or complete.",
            "Agreement between annotators does not establish that either annotation is correct."
        ],
    }
    if case["review"]["doubleAnnotation"]:
        result["agreement"] = _agreement(case["annotations"][0], case["annotations"][1])
    else:
        result["agreement"] = None
    return result


def _load_case(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusCaseError(f"cannot load corpus case: {exc}", code="CORP013") from exc
    if not isinstance(value, dict):
        raise CorpusCaseError("corpus case must be a JSON object", code="CORP013")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a retrospective corpus case and compute metrics")
    parser.add_argument("case")
    args = parser.parse_args(argv)
    try:
        result = compute_metrics(_load_case(Path(args.case)))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except CorpusCaseError as exc:
        print(json.dumps({"ok": False, "code": exc.code, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
