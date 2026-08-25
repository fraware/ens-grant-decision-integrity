"""Adversarial tests for retrospective corpus case integrity and metrics."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from corpus_metrics import CorpusCaseError, compute_metrics, validate_case  # noqa: E402
from source_artifact import build_artifact  # noqa: E402

ROOT = SCRIPT_DIR.parent
TEMPLATE = json.loads((ROOT / "corpus" / "case-template.json").read_text(encoding="utf-8"))
EXAMPLE = ROOT / "examples" / "spp3-marketplace-rfp.example.json"
CHAL003_MESSAGE = (
    "no factual or procedural correction process is recorded; "
    "the reviewed public governing artifacts do not identify one"
)
CHAL003_RENDERED = f"WARNING CHAL003 challenge.processDefined: {CHAL003_MESSAGE}"


def _source(artifact_id: str = "src-1") -> dict:
    return {
        "artifactId": artifact_id,
        "sourceUri": f"https://example.org/{artifact_id}",
        "role": "governing-policy",
        "availability": "reference-only",
        "notes": "Reference-only synthetic source for protocol tests.",
    }


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
    case["recordSnapshots"]["initial"]["recordHash"] = "sha256:" + "11" * 32
    case["recordSnapshots"]["initial"]["path"] = "record-initial.json"
    case["recordSnapshots"]["initial"]["notes"] = "Synthetic non-template hash for test fixture."
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


def _sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _set_marketplace_validator_output(case: dict) -> None:
    case["verification"]["initialFindings"] = [
        {
            "findingId": "fixture-chal003",
            "code": "CHAL003",
            "severity": "warning",
            "path": "challenge.processDefined",
            "message": CHAL003_MESSAGE,
            "disposition": "expected-warning",
            "rationale": "Synthetic fixture preserves the canonical example's expected warning.",
        }
    ]
    case["verification"]["finalErrors"] = []
    case["verification"]["finalWarnings"] = [CHAL003_RENDERED]


def _write_initial_record(case: dict, tmp_path: Path, content: bytes | None = None) -> None:
    if content is None:
        content = EXAMPLE.read_bytes()
        _set_marketplace_validator_output(case)
    (tmp_path / "record-initial.json").write_bytes(content)
    case["recordSnapshots"]["initial"]["recordHash"] = _sha256(content)


def _set_redistributable_source(
    case: dict,
    tmp_path: Path,
    *,
    artifact_id: str = "src-1",
    source_uri: str | None = None,
) -> tuple[Path, Path]:
    source_uri = source_uri or f"https://example.org/{artifact_id}"
    bytes_path = tmp_path / "source.bin"
    metadata_path = tmp_path / "source.artifact.json"
    bytes_path.write_bytes(b"preserved source bytes\n")
    metadata = build_artifact(
        artifact_id=artifact_id,
        source_uri=source_uri,
        file_path=bytes_path,
        media_type="application/octet-stream",
        method="manual-export",
        tool="test-harness",
        tool_version="1",
        captured_at="2026-08-24T12:00:00Z",
    )
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    case["sourceArtifacts"] = [{
        "artifactId": artifact_id,
        "sourceUri": source_uri,
        "role": "governing-policy",
        "availability": "redistributable",
        "metadataPath": metadata_path.name,
        "bytesPath": bytes_path.name,
    }]
    return metadata_path, bytes_path


def _mark_reconciled(case: dict, *, record_hash: str, path: str = "record-reconciled.json") -> None:
    case["verification"]["recordChangedAfterReview"] = True
    case["verification"]["changeRationale"] = "Review corrected an annotation defect."
    case["recordSnapshots"]["reconciled"] = {"recordHash": record_hash, "path": path}
    case["review"]["reconciled"] = True
    case["review"]["reconciliationNotes"] = ["Reconciled after reviewing the initial evidence mapping."]


def test_template_is_schema_and_protocol_valid_but_flagged_template() -> None:
    result = compute_metrics(copy.deepcopy(TEMPLATE))
    assert result["ok"]
    assert result["template"] is True
    assert result["annotations"][0]["unknownRate"] == 1.0


def test_empirical_case_requires_source_artifact_reference() -> None:
    case = _case()
    case["sourceArtifacts"] = []
    case["annotations"][0]["fields"] = [_field("/challenge/processDefined", "unknown")]
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP002"


def test_empirical_case_rejects_template_zero_hash() -> None:
    case = _case()
    case["recordSnapshots"]["initial"]["recordHash"] = "sha256:" + "0" * 64
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP015"


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


def test_derived_without_source_reference_is_schema_failure() -> None:
    case = _case()
    case["annotations"][0]["fields"][1]["sourceArtifactIds"] = []
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP002"


def test_interpretive_without_source_reference_is_schema_failure() -> None:
    case = _case()
    field = _field("/evaluation/materialFindings/0", "interpretive")
    case["annotations"][0]["fields"].append(field)
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
    _mark_reconciled(case, record_hash=case["recordSnapshots"]["initial"]["recordHash"])
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


def test_changed_record_requires_reconciled_review_state() -> None:
    case = _case()
    case["verification"]["recordChangedAfterReview"] = True
    case["verification"]["changeRationale"] = "Review corrected an annotation defect."
    case["recordSnapshots"]["reconciled"] = {
        "recordHash": "sha256:" + "22" * 32,
        "path": "record-reconciled.json",
    }
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP016"


def test_reconciled_review_requires_note() -> None:
    case = _case()
    case["review"]["reconciled"] = True
    case["review"]["reconciliationNotes"] = []
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP017"


def test_empirical_reconciled_record_rejects_template_zero_hash() -> None:
    case = _case()
    _mark_reconciled(case, record_hash="sha256:" + "0" * 64)
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP015"


def test_cli_context_verifies_initial_snapshot_exact_bytes(tmp_path: Path) -> None:
    case = _case()
    _write_initial_record(case, tmp_path)
    validate_case(case, base_dir=tmp_path)


def test_snapshot_byte_tamper_fails_closed(tmp_path: Path) -> None:
    case = _case()
    original = b'{"record":"initial"}\n'
    path = tmp_path / "record-initial.json"
    path.write_bytes(original)
    case["recordSnapshots"]["initial"]["recordHash"] = _sha256(original)
    path.write_bytes(b'{"record":"tampered"}\n')
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case, base_dir=tmp_path)
    assert exc.value.code == "CORP020"


def test_snapshot_path_cannot_escape_case_directory(tmp_path: Path) -> None:
    case = _case()
    case["recordSnapshots"]["initial"]["path"] = "../outside.json"
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case, base_dir=tmp_path)
    assert exc.value.code == "CORP019"


def test_snapshot_path_must_be_relative(tmp_path: Path) -> None:
    case = _case()
    case["recordSnapshots"]["initial"]["path"] = str((tmp_path / "record-initial.json").resolve())
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case, base_dir=tmp_path)
    assert exc.value.code == "CORP019"


def test_reconciled_snapshot_bytes_are_verified(tmp_path: Path) -> None:
    case = _case()
    initial = EXAMPLE.read_bytes()
    reconciled = initial + b"\n"
    (tmp_path / "record-initial.json").write_bytes(initial)
    (tmp_path / "record-reconciled.json").write_bytes(reconciled)
    case["recordSnapshots"]["initial"]["recordHash"] = _sha256(initial)
    _set_marketplace_validator_output(case)
    _mark_reconciled(case, record_hash=_sha256(reconciled))
    validate_case(case, base_dir=tmp_path)


def test_redistributable_source_is_byte_verified(tmp_path: Path) -> None:
    case = _case()
    _write_initial_record(case, tmp_path)
    _set_redistributable_source(case, tmp_path)
    result = compute_metrics(case, base_dir=tmp_path)
    assert result["redistributableSourceArtifactsVerified"] == 1
    assert result["recordSnapshotBytesVerified"] is True


def test_redistributable_source_byte_tamper_fails_closed(tmp_path: Path) -> None:
    case = _case()
    _write_initial_record(case, tmp_path)
    _, bytes_path = _set_redistributable_source(case, tmp_path)
    bytes_path.write_bytes(b"tampered source bytes\n")
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case, base_dir=tmp_path)
    assert exc.value.code == "CORP021"


def test_case_source_id_must_match_source_artifact_metadata(tmp_path: Path) -> None:
    case = _case()
    _write_initial_record(case, tmp_path)
    metadata_path, _ = _set_redistributable_source(case, tmp_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["artifactId"] = "different-id"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case, base_dir=tmp_path)
    assert exc.value.code == "CORP022"


def test_case_source_uri_must_match_source_artifact_metadata(tmp_path: Path) -> None:
    case = _case()
    _write_initial_record(case, tmp_path)
    metadata_path, _ = _set_redistributable_source(case, tmp_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["sourceUri"] = "https://example.org/other"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case, base_dir=tmp_path)
    assert exc.value.code == "CORP023"


def test_public_only_case_rejects_authorized_audit_only_source() -> None:
    case = _case()
    case["sourceArtifacts"][0]["availability"] = "authorized-audit-only"
    case["sourceArtifacts"][0]["notes"] = "Protected audit source."
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP024"


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
    second["fields"][2]["sourceArtifactIds"] = ["src-1"]
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
