#!/usr/bin/env python3
"""Validate a retrospective corpus case and compute descriptive assurance metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from gdi.core.conformance import Finding as RecordFinding
from gdi.core.conformance import validate_record
from gdi.source.artifact import SourceArtifactError, verify_artifact

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "corpus" / "schema" / "case.schema.json"
REQUIRED_NONCLAIMS = {
    "This corpus case does not reassess applicant merit.",
    "Missing public evidence does not prove a private or internal procedure did not exist.",
    "Validator success does not establish substantive correctness, fairness, or institutional legitimacy.",
}
CATEGORIES = ("direct-source", "derived", "interpretive", "unknown", "not-applicable")
ZERO_HASH = "sha256:" + "0" * 64


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


def _resolve_case_path(base_dir: Path, raw_path: str, *, label: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        raise CorpusCaseError(f"{label} path must be relative to the case directory: {raw_path}", code="CORP019")
    base = base_dir.resolve()
    candidate = (base / path).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise CorpusCaseError(
            f"{label} path escapes the case directory: {raw_path}",
            code="CORP019",
        ) from exc
    return candidate


def _hash_file(path: Path) -> str:
    try:
        handle = path.open("rb")
    except OSError as exc:
        raise CorpusCaseError(f"cannot open corpus record snapshot {path}: {exc}", code="CORP018") from exc
    digest = hashlib.sha256()
    with handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _verify_snapshot(snapshot: dict[str, Any], *, base_dir: Path, label: str) -> Path:
    raw_path = snapshot.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise CorpusCaseError(f"empirical {label} snapshot must declare a path", code="CORP018")
    candidate = _resolve_case_path(base_dir, raw_path, label=f"{label} snapshot")
    observed = _hash_file(candidate)
    if observed != snapshot["recordHash"]:
        raise CorpusCaseError(
            f"empirical {label} snapshot hash mismatch: declared {snapshot['recordHash']}, observed {observed}",
            code="CORP020",
        )
    return candidate


def _load_decision_record(path: Path, *, label: str) -> dict[str, Any]:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CorpusCaseError(f"cannot load empirical {label} decision record: {exc}", code="CORP025") from exc
    if not isinstance(record, dict):
        raise CorpusCaseError(f"empirical {label} decision record must be a JSON object", code="CORP025")
    return record


def _run_record_validator(path: Path, *, label: str) -> list[RecordFinding]:
    record = _load_decision_record(path, label=label)
    try:
        return validate_record(record)
    except ValueError as exc:
        raise CorpusCaseError(f"cannot validate empirical {label} decision record: {exc}", code="CORP025") from exc


def _finding_key_from_observed(finding: RecordFinding) -> tuple[str, str, str, str]:
    return (finding.severity, finding.code, finding.path, finding.message)


def _finding_key_from_recorded(finding: dict[str, Any]) -> tuple[str, str, str, str]:
    path = finding.get("path")
    if not isinstance(path, str) or not path:
        raise CorpusCaseError(
            f"recorded initial finding {finding.get('findingId')!r} must include the validator path",
            code="CORP026",
        )
    return (finding["severity"], finding["code"], path, finding["message"])


def _format_finding_key(key: tuple[str, str, str, str]) -> str:
    severity, code, path, message = key
    return f"{severity.upper()} {code} {path}: {message}"


def _verify_initial_findings(case: dict[str, Any], observed: list[RecordFinding]) -> None:
    recorded = Counter(_finding_key_from_recorded(item) for item in case["verification"]["initialFindings"])
    actual = Counter(_finding_key_from_observed(item) for item in observed)
    if recorded == actual:
        return

    omitted = sorted(_format_finding_key(item) for item in (actual - recorded).elements())
    unsupported = sorted(_format_finding_key(item) for item in (recorded - actual).elements())
    details: list[str] = []
    if omitted:
        details.append(f"validator findings omitted from case: {omitted}")
    if unsupported:
        details.append(f"case findings not produced by validator: {unsupported}")
    raise CorpusCaseError(
        "verification.initialFindings does not match the exact initial decision-record validator output; " + "; ".join(details),
        code="CORP026",
    )


def _verify_final_findings(case: dict[str, Any], observed: list[RecordFinding]) -> None:
    expected_errors = [item.render() for item in observed if item.severity == "error"]
    expected_warnings = [item.render() for item in observed if item.severity == "warning"]
    recorded_errors = case["verification"].get("finalErrors")
    recorded_warnings = case["verification"].get("finalWarnings")
    if not isinstance(recorded_errors, list) or not isinstance(recorded_warnings, list):
        raise CorpusCaseError(
            "empirical corpus cases must record finalErrors and finalWarnings from the final decision-record validator run",
            code="CORP027",
        )
    if recorded_errors != expected_errors or recorded_warnings != expected_warnings:
        raise CorpusCaseError(
            "verification.finalErrors/finalWarnings do not match the exact final decision-record validator output; "
            f"expected errors={expected_errors}, warnings={expected_warnings}; "
            f"recorded errors={recorded_errors}, warnings={recorded_warnings}",
            code="CORP027",
        )


def _verify_redistributable_sources(case: dict[str, Any], *, base_dir: Path) -> int:
    verified_count = 0
    for source in case["sourceArtifacts"]:
        if source["availability"] != "redistributable":
            continue
        metadata_path = _resolve_case_path(base_dir, source["metadataPath"], label=f"source {source['artifactId']} metadata")
        bytes_path = _resolve_case_path(base_dir, source["bytesPath"], label=f"source {source['artifactId']} bytes")
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CorpusCaseError(
                f"cannot load source-artifact metadata for {source['artifactId']}: {exc}",
                code="CORP021",
            ) from exc
        if not isinstance(metadata, dict):
            raise CorpusCaseError(
                f"source-artifact metadata for {source['artifactId']} must be a JSON object",
                code="CORP021",
            )
        try:
            verified = verify_artifact(metadata, bytes_path)
        except SourceArtifactError as exc:
            raise CorpusCaseError(
                f"source-artifact verification failed for {source['artifactId']} ({exc.code}): {exc}",
                code="CORP021",
            ) from exc
        if verified.artifact_id != source["artifactId"]:
            raise CorpusCaseError(
                f"case source id {source['artifactId']} does not match source-artifact metadata id {verified.artifact_id}",
                code="CORP022",
            )
        if verified.metadata["sourceUri"] != source["sourceUri"]:
            raise CorpusCaseError(
                f"case source URI for {source['artifactId']} does not match source-artifact metadata sourceUri",
                code="CORP023",
            )
        verified_count += 1
    return verified_count


def validate_case(case: dict[str, Any], *, base_dir: Path | None = None) -> int:
    _schema_validate(case)

    source_ids = [item["artifactId"] for item in case["sourceArtifacts"]]
    _unique(source_ids, label="source artifact ids", code="CORP003")
    known_sources = set(source_ids)

    if case["sourceAccess"] == "public-only" and any(
        item["availability"] == "authorized-audit-only" for item in case["sourceArtifacts"]
    ):
        raise CorpusCaseError(
            "public-only corpus cases cannot declare authorized-audit-only source artifacts",
            code="CORP024",
        )

    for source in case["sourceArtifacts"]:
        if source["availability"] in {"reference-only", "authorized-audit-only"} and (
            "metadataPath" in source or "bytesPath" in source
        ):
            raise CorpusCaseError(
                f"source {source['artifactId']} with availability={source['availability']!r} "
                "cannot claim byte-verified metadataPath/bytesPath; only redistributable sources are byte-verified",
                code="CORP028",
            )

    verified_redistributable = 0
    initial_record_path: Path | None = None
    final_record_path: Path | None = None
    if not case["template"]:
        if not source_ids:
            raise CorpusCaseError(
                "an empirical corpus case must declare at least one source artifact or reference-only source record",
                code="CORP014",
            )
        if case["recordSnapshots"]["initial"]["recordHash"] == ZERO_HASH:
            raise CorpusCaseError(
                "an empirical corpus case cannot use the template zero hash for its initial record",
                code="CORP015",
            )
        if base_dir is not None:
            initial_record_path = _verify_snapshot(case["recordSnapshots"]["initial"], base_dir=base_dir, label="initial")
            final_record_path = initial_record_path
            verified_redistributable = _verify_redistributable_sources(case, base_dir=base_dir)

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

    changed = case["verification"]["recordChangedAfterReview"]
    if changed:
        initial_hash = case["recordSnapshots"]["initial"]["recordHash"]
        reconciled = case["recordSnapshots"]["reconciled"]
        reconciled_hash = reconciled["recordHash"]
        if initial_hash == reconciled_hash:
            raise CorpusCaseError(
                "recordChangedAfterReview is true but initial and reconciled record hashes are identical",
                code="CORP011",
            )
        if not case["review"]["reconciled"]:
            raise CorpusCaseError(
                "recordChangedAfterReview requires review.reconciled=true",
                code="CORP016",
            )
        if not case["template"] and reconciled_hash == ZERO_HASH:
            raise CorpusCaseError(
                "an empirical reconciled record cannot use the template zero hash",
                code="CORP015",
            )
        if not case["template"] and base_dir is not None:
            if "path" not in reconciled:
                raise CorpusCaseError("empirical reconciled snapshot must declare a path", code="CORP018")
            final_record_path = _verify_snapshot(reconciled, base_dir=base_dir, label="reconciled")

    if case["review"]["reconciled"] and not case["review"]["reconciliationNotes"]:
        raise CorpusCaseError(
            "a reconciled review must retain at least one reconciliation note",
            code="CORP017",
        )

    if not REQUIRED_NONCLAIMS.issubset(set(case["nonClaims"])):
        missing = sorted(REQUIRED_NONCLAIMS - set(case["nonClaims"]))
        raise CorpusCaseError(f"required corpus non-claims are missing: {missing}", code="CORP012")

    if not case["template"] and base_dir is not None:
        if initial_record_path is None or final_record_path is None:
            raise CorpusCaseError("empirical decision-record paths were not resolved", code="CORP018")
        initial_findings = _run_record_validator(initial_record_path, label="initial")
        _verify_initial_findings(case, initial_findings)
        final_findings = initial_findings if final_record_path == initial_record_path else _run_record_validator(final_record_path, label="final")
        _verify_final_findings(case, final_findings)

    return verified_redistributable


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
        "note": "Agreement metrics describe annotation consistency; they do not establish annotation correctness. Cohen's kappa is undefined when expected agreement is 1."
    }


def compute_metrics(case: dict[str, Any], *, base_dir: Path | None = None) -> dict[str, Any]:
    verified_redistributable = validate_case(case, base_dir=base_dir)
    finding_counts = Counter(item["disposition"] for item in case["verification"]["initialFindings"])
    validator_bound = bool(base_dir is not None and not case["template"])
    result: dict[str, Any] = {
        "ok": True,
        "caseId": case["caseId"],
        "template": case["template"],
        "sourceArtifactCount": len(case["sourceArtifacts"]),
        "redistributableSourceArtifactsVerified": verified_redistributable if base_dir is not None else None,
        "recordSnapshotBytesVerified": validator_bound,
        "initialValidatorFindingsVerified": validator_bound,
        "finalValidatorFindingsVerified": validator_bound,
        "annotations": [_annotation_metrics(annotation) for annotation in case["annotations"]],
        "findingDispositionCounts": dict(sorted(finding_counts.items())),
        "initialFindingCount": len(case["verification"]["initialFindings"]),
        "recordChangedAfterReview": case["verification"]["recordChangedAfterReview"],
        "nonClaims": [
            "These are descriptive reconstructability and agreement metrics, not merit or fairness scores.",
            "A low unknown rate does not establish that source evidence is true or complete.",
            "Agreement between annotators does not establish that either annotation is correct.",
            "Reference-only and authorized-audit-only sources are not represented as byte-verified by this public case verifier."
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
    case_path = Path(args.case)
    try:
        result = compute_metrics(_load_case(case_path), base_dir=case_path.parent)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except CorpusCaseError as exc:
        print(json.dumps({"ok": False, "code": exc.code, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
