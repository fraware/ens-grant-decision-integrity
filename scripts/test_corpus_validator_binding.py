"""Adversarial tests binding corpus findings to exact decision-record validator output."""

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

from corpus_metrics import CorpusCaseError, compute_metrics  # noqa: E402

ROOT = SCRIPT_DIR.parent
TEMPLATE = json.loads((ROOT / "corpus" / "case-template.json").read_text(encoding="utf-8"))
EXAMPLE = ROOT / "examples" / "spp3-marketplace-rfp.example.json"
CHAL003_MESSAGE = (
    "no factual or procedural correction process is recorded; "
    "the reviewed public governing artifacts do not identify one"
)
CHAL003_RENDERED = f"WARNING CHAL003 challenge.processDefined: {CHAL003_MESSAGE}"


def _sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _recorded_finding(
    *,
    finding_id: str,
    severity: str,
    code: str,
    path: str,
    message: str,
    disposition: str = "unresolved",
) -> dict:
    return {
        "findingId": finding_id,
        "code": code,
        "severity": severity,
        "path": path,
        "message": message,
        "disposition": disposition,
        "rationale": "Synthetic fixture records the observed validator output without treating it as a merits judgment.",
    }


def _case_for_bytes(
    tmp_path: Path,
    record_bytes: bytes,
    *,
    initial_findings: list[dict],
    final_errors: list[str],
    final_warnings: list[str],
) -> dict:
    case = copy.deepcopy(TEMPLATE)
    case["caseId"] = "validator-binding-fixture"
    case["title"] = "Validator binding synthetic fixture"
    case["template"] = False
    case["selection"]["inclusionRationale"] = "Synthetic protocol test; not an empirical corpus case."
    case["sourceArtifacts"] = [
        {
            "artifactId": "source-1",
            "sourceUri": "https://example.org/process",
            "role": "governing-policy",
            "availability": "reference-only",
            "notes": "Synthetic source reference used only to satisfy the empirical-case protocol shape.",
        }
    ]
    path = tmp_path / "record-initial.json"
    path.write_bytes(record_bytes)
    case["recordSnapshots"]["initial"] = {
        "recordHash": _sha256(record_bytes),
        "path": path.name,
        "notes": "Exact bytes used by the validator-binding test.",
    }
    case["verification"]["initialFindings"] = initial_findings
    case["verification"]["finalErrors"] = final_errors
    case["verification"]["finalWarnings"] = final_warnings
    return case


def _marketplace_case(tmp_path: Path) -> dict:
    finding = _recorded_finding(
        finding_id="initial-chal003",
        severity="warning",
        code="CHAL003",
        path="challenge.processDefined",
        message=CHAL003_MESSAGE,
        disposition="expected-warning",
    )
    return _case_for_bytes(
        tmp_path,
        EXAMPLE.read_bytes(),
        initial_findings=[finding],
        final_errors=[],
        final_warnings=[CHAL003_RENDERED],
    )


def test_exact_initial_and_final_validator_findings_are_machine_bound(tmp_path: Path) -> None:
    case = _marketplace_case(tmp_path)
    result = compute_metrics(case, base_dir=tmp_path)
    assert result["initialValidatorFindingsVerified"] is True
    assert result["finalValidatorFindingsVerified"] is True
    assert result["initialFindingCount"] == 1


def test_omitted_initial_validator_finding_fails_closed(tmp_path: Path) -> None:
    case = _marketplace_case(tmp_path)
    case["verification"]["initialFindings"] = []
    with pytest.raises(CorpusCaseError) as exc:
        compute_metrics(case, base_dir=tmp_path)
    assert exc.value.code == "CORP026"
    assert "omitted from case" in str(exc.value)


def test_invented_initial_validator_finding_fails_closed(tmp_path: Path) -> None:
    case = _marketplace_case(tmp_path)
    case["verification"]["initialFindings"].append(
        _recorded_finding(
            finding_id="invented",
            severity="error",
            code="DEC999",
            path="decision.status",
            message="invented finding",
        )
    )
    with pytest.raises(CorpusCaseError) as exc:
        compute_metrics(case, base_dir=tmp_path)
    assert exc.value.code == "CORP026"
    assert "not produced by validator" in str(exc.value)


def test_initial_validator_message_mismatch_fails_closed(tmp_path: Path) -> None:
    case = _marketplace_case(tmp_path)
    case["verification"]["initialFindings"][0]["message"] = "nearby but non-identical message"
    with pytest.raises(CorpusCaseError) as exc:
        compute_metrics(case, base_dir=tmp_path)
    assert exc.value.code == "CORP026"


def test_final_validator_output_mismatch_fails_closed(tmp_path: Path) -> None:
    case = _marketplace_case(tmp_path)
    case["verification"]["finalWarnings"] = []
    with pytest.raises(CorpusCaseError) as exc:
        compute_metrics(case, base_dir=tmp_path)
    assert exc.value.code == "CORP027"


def test_schema_invalid_record_can_be_preserved_when_finding_is_exact(tmp_path: Path) -> None:
    record = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    del record["decision"]["authorityKind"]
    record_bytes = (json.dumps(record, separators=(",", ":")) + "\n").encode("utf-8")
    message = "'authorityKind' is a required property"
    rendered = f"ERROR SCHEMA decision: {message}"
    case = _case_for_bytes(
        tmp_path,
        record_bytes,
        initial_findings=[
            _recorded_finding(
                finding_id="initial-schema-authority",
                severity="error",
                code="SCHEMA",
                path="decision",
                message=message,
                disposition="unresolved",
            )
        ],
        final_errors=[rendered],
        final_warnings=[],
    )
    result = compute_metrics(case, base_dir=tmp_path)
    assert result["ok"] is True
    assert result["initialValidatorFindingsVerified"] is True
    assert result["findingDispositionCounts"] == {"unresolved": 1}


def test_invalid_decision_record_json_fails_before_findings_can_be_claimed(tmp_path: Path) -> None:
    case = _case_for_bytes(
        tmp_path,
        b"{not valid json\n",
        initial_findings=[],
        final_errors=[],
        final_warnings=[],
    )
    with pytest.raises(CorpusCaseError) as exc:
        compute_metrics(case, base_dir=tmp_path)
    assert exc.value.code == "CORP025"


def test_without_case_directory_context_validator_binding_is_not_claimed(tmp_path: Path) -> None:
    case = _marketplace_case(tmp_path)
    result = compute_metrics(case)
    assert result["recordSnapshotBytesVerified"] is False
    assert result["initialValidatorFindingsVerified"] is False
    assert result["finalValidatorFindingsVerified"] is False
