#!/usr/bin/env python3
"""Prepare and verify source-only handoffs for independent second annotation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from corpus_metrics import CATEGORIES, CorpusCaseError, validate_case

INDEPENDENCE_ATTESTATION = (
    "I produced this annotation without consulting the withheld primary reconstruction "
    "materials before submission."
)


class SecondAnnotationError(Exception):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


def _load_json(path: Path, *, label: str, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SecondAnnotationError(f"cannot load {label} {path}: {exc}", code=code) from exc
    if not isinstance(value, dict):
        raise SecondAnnotationError(f"{label} must be a JSON object: {path}", code=code)
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exact LF UTF-8 bytes so handoff hashes are stable under Windows text-mode newline translation.
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _validated_single_annotation_case(case: dict[str, Any], *, base_dir: Path) -> dict[str, Any]:
    try:
        validate_case(case, base_dir=base_dir)
    except CorpusCaseError as exc:
        raise SecondAnnotationError(
            f"corpus case contract failed ({exc.code}): {exc}",
            code="ANN001",
        ) from exc

    if case.get("template") is True:
        raise SecondAnnotationError("template cases cannot be prepared for empirical second annotation", code="ANN002")
    annotations = case.get("annotations")
    review = case.get("review")
    if not isinstance(annotations, list) or len(annotations) != 1:
        raise SecondAnnotationError(
            "handoff preparation requires exactly one existing primary annotation",
            code="ANN003",
        )
    if not isinstance(review, dict) or review.get("doubleAnnotation") is not False:
        raise SecondAnnotationError(
            "handoff preparation requires review.doubleAnnotation=false before the second annotation is integrated",
            code="ANN003",
        )
    return annotations[0]


def _source_inventory(case: dict[str, Any]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for source in case["sourceArtifacts"]:
        item = {
            "artifactId": source["artifactId"],
            "sourceUri": source["sourceUri"],
            "role": source["role"],
            "availability": source["availability"],
        }
        if source["availability"] == "redistributable":
            item["metadataPath"] = source["metadataPath"]
            item["bytesPath"] = source["bytesPath"]
        inventory.append(item)
    return inventory


def _material_fields(primary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "path": field["path"],
            "requiredForProfile": field["requiredForProfile"],
        }
        for field in primary["fields"]
    ]


def build_handoff(case: dict[str, Any], *, base_dir: Path) -> dict[str, Any]:
    primary = _validated_single_annotation_case(case, base_dir=base_dir)
    fields = _material_fields(primary)
    return {
        "handoffVersion": "1",
        "caseId": case["caseId"],
        "sourceAccess": case["sourceAccess"],
        "initialRecordHash": case["recordSnapshots"]["initial"]["recordHash"],
        "sourceArtifacts": _source_inventory(case),
        "materialFields": fields,
        "classificationDefinitions": {
            "direct-source": "The field is directly represented by cited source evidence.",
            "derived": "The field is mechanically derived from cited source evidence; record the derivation in rationale.",
            "interpretive": "The field requires a documented mapping judgment over cited source evidence.",
            "unknown": "The supplied source set is insufficient to reconstruct the field.",
            "not-applicable": "The field is outside the represented process/profile; explain why in rationale.",
        },
        "independenceInstructions": [
            "Work from the supplied source inventory and material field list without consulting the primary annotation, reconstructed decision record, validator findings, reconciliation notes, or previously computed corpus metrics.",
            "Use unknown when the supplied evidence is insufficient. Do not infer private or undocumented facts to complete the record.",
            "Do not reassess applicant merit or substitute a preferred substantive funding judgment.",
            "Record elapsed annotation time and use source artifact IDs exactly as supplied.",
            "Set independent=true only if the annotation was produced without access to the withheld primary reconstruction materials before submission.",
        ],
        "annotationSubmission": {
            "annotationId": None,
            "annotatorId": None,
            "independent": True,
            "elapsedMinutes": None,
            "fields": [
                {
                    "path": field["path"],
                    "requiredForProfile": field["requiredForProfile"],
                    "classification": None,
                    "sourceArtifactIds": [],
                    "rationale": None,
                }
                for field in fields
            ],
        },
        "withheldFromHandoff": [
            "primary annotation classifications and rationales",
            "primary reconstructed decision-record values",
            "validator findings and finding dispositions",
            "case selection rationale and strata labels",
            "case review and reconciliation notes",
            "computed corpus metrics and agreement results",
        ],
        "nonClaims": [
            "This handoff reduces direct exposure to the primary reconstruction; it does not prove that a human annotator remained independent.",
            "Public sources may reveal the historical outcome. Independence here means independent encoding from the supplied sources, not blindness to source facts.",
            "Agreement between annotations does not establish source truth, substantive correctness, fairness, merit, or institutional legitimacy.",
        ],
    }


def _require_nonempty_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SecondAnnotationError(f"{label} must be a non-empty string", code="ANN005")
    return value


def _validate_static_handoff(handoff: dict[str, Any], expected: dict[str, Any]) -> None:
    for key, expected_value in expected.items():
        if key == "annotationSubmission":
            continue
        if handoff.get(key) != expected_value:
            raise SecondAnnotationError(
                f"handoff field {key!r} does not match the handoff generated from the current case",
                code="ANN004",
            )


def verify_submission(
    case: dict[str, Any],
    handoff: dict[str, Any],
    *,
    base_dir: Path,
) -> dict[str, Any]:
    primary = _validated_single_annotation_case(case, base_dir=base_dir)
    expected = build_handoff(case, base_dir=base_dir)
    _validate_static_handoff(handoff, expected)

    submission = handoff.get("annotationSubmission")
    if not isinstance(submission, dict):
        raise SecondAnnotationError("annotationSubmission must be a JSON object", code="ANN005")
    allowed_submission_keys = {
        "annotationId",
        "annotatorId",
        "independent",
        "independenceAttestation",
        "elapsedMinutes",
        "fields",
    }
    if set(submission) != allowed_submission_keys:
        raise SecondAnnotationError(
            "annotationSubmission must contain exactly annotationId, annotatorId, independent, "
            "independenceAttestation, elapsedMinutes, and fields",
            code="ANN005",
        )

    annotation_id = _require_nonempty_string(
        submission.get("annotationId"), label="annotationSubmission.annotationId"
    )
    annotator_id = _require_nonempty_string(
        submission.get("annotatorId"), label="annotationSubmission.annotatorId"
    )
    if annotator_id == primary["annotatorId"]:
        raise SecondAnnotationError(
            "second annotation must use an annotatorId distinct from the primary annotation",
            code="ANN006",
        )
    if submission.get("independent") is not True:
        raise SecondAnnotationError(
            "second annotator must explicitly attest independent=true",
            code="ANN006",
        )
    attestation = _require_nonempty_string(
        submission.get("independenceAttestation"),
        label="annotationSubmission.independenceAttestation",
    )
    if attestation != INDEPENDENCE_ATTESTATION:
        raise SecondAnnotationError(
            "independenceAttestation must exactly match the required human attestation text",
            code="ANN006",
        )

    elapsed = submission.get("elapsedMinutes")
    if not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool) or elapsed < 0:
        raise SecondAnnotationError("annotationSubmission.elapsedMinutes must be a non-negative number", code="ANN005")

    submitted_fields = submission.get("fields")
    if not isinstance(submitted_fields, list):
        raise SecondAnnotationError("annotationSubmission.fields must be a list", code="ANN005")

    expected_fields = {item["path"]: item["requiredForProfile"] for item in expected["materialFields"]}
    seen_paths: set[str] = set()
    known_sources = {source["artifactId"] for source in expected["sourceArtifacts"]}
    normalized_fields: list[dict[str, Any]] = []

    for index, field in enumerate(submitted_fields):
        if not isinstance(field, dict):
            raise SecondAnnotationError(f"annotation field {index} must be a JSON object", code="ANN005")
        allowed_field_keys = {"path", "requiredForProfile", "classification", "sourceArtifactIds", "rationale"}
        if set(field) != allowed_field_keys:
            raise SecondAnnotationError(
                f"annotation field {index} must contain exactly path, requiredForProfile, classification, sourceArtifactIds, and rationale",
                code="ANN005",
            )
        path = _require_nonempty_string(field.get("path"), label=f"annotation field {index}.path")
        if path in seen_paths:
            raise SecondAnnotationError(f"annotation field path is duplicated: {path}", code="ANN007")
        seen_paths.add(path)
        if path not in expected_fields:
            raise SecondAnnotationError(f"annotation field path is outside the fixed material field set: {path}", code="ANN007")
        if field.get("requiredForProfile") is not expected_fields[path]:
            raise SecondAnnotationError(
                f"requiredForProfile changed for fixed material field {path}",
                code="ANN007",
            )

        classification = field.get("classification")
        if classification not in CATEGORIES:
            raise SecondAnnotationError(
                f"invalid classification for {path}: {classification!r}",
                code="ANN005",
            )
        source_ids = field.get("sourceArtifactIds")
        if not isinstance(source_ids, list) or any(not isinstance(item, str) or not item for item in source_ids):
            raise SecondAnnotationError(f"sourceArtifactIds for {path} must be a list of non-empty strings", code="ANN005")
        if len(source_ids) != len(set(source_ids)):
            raise SecondAnnotationError(f"sourceArtifactIds for {path} must be unique", code="ANN005")
        unknown_sources = sorted(set(source_ids) - known_sources)
        if unknown_sources:
            raise SecondAnnotationError(
                f"{path} references source artifact IDs outside the handoff: {unknown_sources}",
                code="ANN008",
            )
        if classification in {"direct-source", "derived", "interpretive"} and not source_ids:
            raise SecondAnnotationError(
                f"{classification} field {path} requires at least one source artifact ID",
                code="ANN008",
            )

        rationale = field.get("rationale")
        if classification in {"derived", "interpretive", "not-applicable"}:
            _require_nonempty_string(rationale, label=f"rationale for {classification} field {path}")
        elif rationale is not None and (not isinstance(rationale, str) or not rationale.strip()):
            raise SecondAnnotationError(
                f"optional rationale for {path} must be null or a non-empty string",
                code="ANN005",
            )

        normalized = {
            "path": path,
            "requiredForProfile": expected_fields[path],
            "classification": classification,
            "sourceArtifactIds": source_ids,
        }
        if isinstance(rationale, str) and rationale.strip():
            normalized["rationale"] = rationale
        normalized_fields.append(normalized)

    if seen_paths != set(expected_fields):
        missing = sorted(set(expected_fields) - seen_paths)
        raise SecondAnnotationError(
            f"second annotation does not cover the complete fixed material field set; missing={missing}",
            code="ANN007",
        )

    normalized_by_path = {field["path"]: field for field in normalized_fields}
    ordered_fields = [normalized_by_path[field["path"]] for field in expected["materialFields"]]
    return {
        "annotationId": annotation_id,
        "annotatorId": annotator_id,
        "independent": True,
        "elapsedMinutes": elapsed,
        "fields": ordered_fields,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="prepare a source-only second-annotation handoff")
    prepare.add_argument("case", type=Path)
    prepare.add_argument("--out", type=Path, required=True)

    verify = subparsers.add_parser("verify", help="verify a completed second-annotation handoff")
    verify.add_argument("case", type=Path)
    verify.add_argument("handoff", type=Path)
    verify.add_argument("--out", type=Path)

    args = parser.parse_args()
    try:
        case = _load_json(args.case, label="corpus case", code="ANN001")
        base_dir = args.case.parent
        if args.command == "prepare":
            handoff = build_handoff(case, base_dir=base_dir)
            _write_json(args.out, handoff)
            print(
                json.dumps(
                    {
                        "ok": True,
                        "caseId": handoff["caseId"],
                        "materialFieldCount": len(handoff["materialFields"]),
                        "sourceArtifactCount": len(handoff["sourceArtifacts"]),
                        "out": str(args.out),
                        "nonClaim": "Preparation strips primary classifications, reconstructed record values, validator findings, review notes, and computed metrics from the handoff; it does not prove human independence.",
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        handoff = _load_json(args.handoff, label="annotation handoff", code="ANN004")
        annotation = verify_submission(case, handoff, base_dir=base_dir)
        result = {
            "ok": True,
            "caseId": case["caseId"],
            "annotation": annotation,
            "independenceAttestation": handoff["annotationSubmission"]["independenceAttestation"],
            "nextStep": "Freeze the verified annotation before exposing the second annotator to the primary reconstruction; then integrate both annotations and begin reconciliation.",
            "nonClaims": [
                "Tool verification establishes handoff consistency and an explicit human attestation value, not that the human process was independent.",
                "A verified second annotation is not a substantive correctness, fairness, merit, or legitimacy judgment.",
            ],
        }
        if args.out is not None:
            _write_json(args.out, result)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except SecondAnnotationError as exc:
        print(json.dumps({"ok": False, "code": exc.code, "error": str(exc)}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
