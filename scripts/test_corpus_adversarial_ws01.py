"""Adversarial corpus tests from Workstream 01 §7 beyond the existing suites."""

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
from second_annotation import (  # noqa: E402
    INDEPENDENCE_ATTESTATION,
    SecondAnnotationError,
    build_handoff,
    verify_submission,
)
from study_status import compute_study_status  # noqa: E402
from test_corpus import (  # noqa: E402
    EXAMPLE,
    _case,
    _mark_reconciled,
    _set_marketplace_validator_output,
    _sha256,
    _write_initial_record,
)
from test_corpus_validator_binding import _marketplace_case, _recorded_finding  # noqa: E402

ROOT = SCRIPT_DIR.parent
PLAN = json.loads((ROOT / "corpus" / "study-plan.json").read_text(encoding="utf-8"))
NAMESPACE_CASE = ROOT / "corpus" / "cases" / "spp3-namespace-2026" / "case.json"


def test_final_findings_rewritten_message_fails_closed(tmp_path: Path) -> None:
    case = _marketplace_case(tmp_path)
    case["verification"]["finalWarnings"] = [
        "WARNING CHAL003 challenge.processDefined: rewritten non-identical message"
    ]
    with pytest.raises(CorpusCaseError) as exc:
        compute_metrics(case, base_dir=tmp_path)
    assert exc.value.code == "CORP027"


def test_final_findings_reordered_errors_fail_closed(tmp_path: Path) -> None:
    record = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    del record["application"]["applicantName"]
    del record["decision"]["authorityKind"]
    record_bytes = (json.dumps(record, separators=(",", ":")) + "\n").encode("utf-8")
    path = tmp_path / "record-initial.json"
    path.write_bytes(record_bytes)
    msg_name = "'applicantName' is a required property"
    msg_auth = "'authorityKind' is a required property"
    # Validator emits application then decision; reverse the recorded finalErrors.
    case = _case()
    case["recordSnapshots"]["initial"]["recordHash"] = _sha256(record_bytes)
    case["recordSnapshots"]["initial"]["path"] = path.name
    case["verification"]["initialFindings"] = [
        _recorded_finding(
            finding_id="init-applicant",
            severity="error",
            code="SCHEMA",
            path="application",
            message=msg_name,
        ),
        _recorded_finding(
            finding_id="init-authority",
            severity="error",
            code="SCHEMA",
            path="decision",
            message=msg_auth,
        ),
    ]
    case["verification"]["finalErrors"] = [
        f"ERROR SCHEMA decision: {msg_auth}",
        f"ERROR SCHEMA application: {msg_name}",
    ]
    case["verification"]["finalWarnings"] = []
    with pytest.raises(CorpusCaseError) as exc:
        compute_metrics(case, base_dir=tmp_path)
    assert exc.value.code == "CORP027"


def test_reference_only_source_cannot_claim_byte_paths() -> None:
    case = _case()
    case["sourceArtifacts"][0]["metadataPath"] = "source.artifact.json"
    case["sourceArtifacts"][0]["bytesPath"] = "source.bin"
    case["sourceArtifacts"][0]["notes"] = "Incorrectly claims byte verification while remaining reference-only."
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP028"


def test_double_annotation_rejects_independent_false() -> None:
    case = _case()
    second = copy.deepcopy(case["annotations"][0])
    second["annotationId"] = "ann-2"
    second["annotatorId"] = "reviewer-b"
    second["independent"] = False
    case["annotations"].append(second)
    case["review"]["doubleAnnotation"] = True
    with pytest.raises(CorpusCaseError) as exc:
        validate_case(case)
    assert exc.value.code == "CORP009"


def test_second_annotation_rejects_required_for_profile_change() -> None:
    case = json.loads(NAMESPACE_CASE.read_text(encoding="utf-8"))
    handoff = build_handoff(case, base_dir=NAMESPACE_CASE.parent)
    submission = handoff["annotationSubmission"]
    submission["annotationId"] = "namespace-independent-second-v1"
    submission["annotatorId"] = "independent-reviewer-b"
    submission["independent"] = True
    submission["independenceAttestation"] = INDEPENDENCE_ATTESTATION
    submission["elapsedMinutes"] = 10
    for field in submission["fields"]:
        field["classification"] = "unknown"
        field["sourceArtifactIds"] = []
        field["rationale"] = None
    submission["fields"][0]["requiredForProfile"] = not submission["fields"][0]["requiredForProfile"]
    with pytest.raises(SecondAnnotationError) as exc:
        verify_submission(case, handoff, base_dir=NAMESPACE_CASE.parent)
    assert exc.value.code == "ANN007"


def test_reconciled_case_preserves_original_annotation_set(tmp_path: Path) -> None:
    """Reconciliation may change the record, but must not silently rewrite the frozen annotation."""
    case = _case()
    initial = EXAMPLE.read_bytes()
    reconciled = initial + b"\n"
    (tmp_path / "record-initial.json").write_bytes(initial)
    (tmp_path / "record-reconciled.json").write_bytes(reconciled)
    case["recordSnapshots"]["initial"]["recordHash"] = _sha256(initial)
    _set_marketplace_validator_output(case)
    _mark_reconciled(case, record_hash=_sha256(reconciled))
    frozen = copy.deepcopy(case["annotations"][0])
    validate_case(case, base_dir=tmp_path)
    assert case["annotations"][0] == frozen


def test_uncovered_stratum_is_unresolved_not_absence_claim() -> None:
    plan = copy.deepcopy(PLAN)
    cases = [
        {
            "caseId": "only-merit",
            "template": False,
            "selection": {"strata": ["merit-decision"]},
            "review": {"doubleAnnotation": False},
            "source": "synthetic/only-merit/case.json",
        }
    ]
    result = compute_study_status(plan, cases)
    assert "hard-eligibility" in result["strata"]["requiredUnresolved"]
    absence_claim = "no such evidence exists"
    encoded = json.dumps(result)
    assert absence_claim not in encoded.lower()
    assert any("cannot establish that evidence" in note for note in result["nonClaims"])


def test_study_count_above_twelve_is_protocol_deviation_not_ready() -> None:
    required = PLAN["sampling"]["requiredStrataWhereEvidenceExists"]
    cases = [
        {
            "caseId": f"case-{index}",
            "template": False,
            "selection": {"strata": required if index == 1 else ["merit-decision"]},
            "review": {"doubleAnnotation": index <= 4},
            "source": f"synthetic/case-{index}/case.json",
        }
        for index in range(1, 14)
    ]
    result = compute_study_status(copy.deepcopy(PLAN), cases)
    assert result["caseCount"]["observed"] == 13
    assert result["status"] == "protocol-deviation"
    assert result["readyForFinalReview"] is False
    assert result["gates"]["maximumCaseCountNotExceeded"] is False
