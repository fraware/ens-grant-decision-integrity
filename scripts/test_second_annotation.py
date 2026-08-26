from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from second_annotation import (
    INDEPENDENCE_ATTESTATION,
    SecondAnnotationError,
    build_handoff,
    verify_submission,
)

ROOT = Path(__file__).resolve().parents[1]
CASE_PATH = ROOT / "corpus" / "cases" / "spp3-namespace-2026" / "case.json"
HANDOFF_PATH = (
    ROOT
    / "corpus"
    / "second-annotation-handoffs"
    / "spp3-namespace-2026.handoff.json"
)
FROZEN_HANDOFF_SHA256 = "48047269447cf331ed76403773d8431bcb44fe39dd3ee3853fff5e555a4d4674"


def _case() -> dict:
    return json.loads(CASE_PATH.read_text(encoding="utf-8"))


def _complete_submission(handoff: dict) -> None:
    submission = handoff["annotationSubmission"]
    submission["annotationId"] = "namespace-independent-second-v1"
    submission["annotatorId"] = "independent-reviewer-b"
    submission["independent"] = True
    submission["independenceAttestation"] = INDEPENDENCE_ATTESTATION
    submission["elapsedMinutes"] = 12.5
    for field in submission["fields"]:
        field["classification"] = "unknown"
        field["sourceArtifactIds"] = []
        field["rationale"] = None


def _completed_unknown_handoff() -> tuple[dict, dict]:
    case = _case()
    handoff = build_handoff(case, base_dir=CASE_PATH.parent)
    _complete_submission(handoff)
    return case, handoff


def test_prepare_strips_primary_reconstruction_material() -> None:
    case = _case()
    primary = case["annotations"][0]
    handoff = build_handoff(case, base_dir=CASE_PATH.parent)
    encoded = json.dumps(handoff, sort_keys=True)

    assert primary["annotationId"] not in encoded
    assert primary["annotatorId"] not in encoded
    assert "selection" not in handoff
    assert "verification" not in handoff
    assert "review" not in handoff
    assert "annotations" not in handoff
    assert "decision" not in handoff
    assert all(set(field) == {"path", "requiredForProfile"} for field in handoff["materialFields"])


def test_handoff_exposes_full_classification_vocabulary() -> None:
    handoff = build_handoff(_case(), base_dir=CASE_PATH.parent)

    assert set(handoff["classificationDefinitions"]) == {
        "direct-source",
        "derived",
        "interpretive",
        "unknown",
        "not-applicable",
    }


def test_frozen_handoff_digest_and_current_verifier_compatibility() -> None:
    frozen_bytes = HANDOFF_PATH.read_bytes()
    assert hashlib.sha256(frozen_bytes).hexdigest() == FROZEN_HANDOFF_SHA256

    case = _case()
    handoff = json.loads(frozen_bytes.decode("utf-8"))
    _complete_submission(handoff)
    annotation = verify_submission(case, handoff, base_dir=CASE_PATH.parent)

    assert annotation["annotatorId"] == "independent-reviewer-b"
    assert annotation["independent"] is True
    assert {field["classification"] for field in annotation["fields"]} == {"unknown"}


def test_verify_accepts_complete_independent_unknown_annotation() -> None:
    case, handoff = _completed_unknown_handoff()
    annotation = verify_submission(case, handoff, base_dir=CASE_PATH.parent)

    assert annotation["annotatorId"] == "independent-reviewer-b"
    assert annotation["independent"] is True
    assert len(annotation["fields"]) == len(case["annotations"][0]["fields"])
    assert {field["classification"] for field in annotation["fields"]} == {"unknown"}


def test_verify_accepts_not_applicable_with_rationale() -> None:
    case, handoff = _completed_unknown_handoff()
    field = next(
        item
        for item in handoff["annotationSubmission"]["fields"]
        if item["path"] == "/timestamps/createdAt"
    )
    field["classification"] = "not-applicable"
    field["rationale"] = "Reconstruction metadata is outside the historical process being reconstructed."

    annotation = verify_submission(case, handoff, base_dir=CASE_PATH.parent)
    verified = next(item for item in annotation["fields"] if item["path"] == "/timestamps/createdAt")
    assert verified["classification"] == "not-applicable"
    assert verified["rationale"]


def test_verify_rejects_primary_annotation_id_reuse() -> None:
    case, handoff = _completed_unknown_handoff()
    handoff["annotationSubmission"]["annotationId"] = case["annotations"][0]["annotationId"]

    with pytest.raises(SecondAnnotationError, match="annotationId distinct") as exc:
        verify_submission(case, handoff, base_dir=CASE_PATH.parent)
    assert exc.value.code == "ANN006"


def test_verify_rejects_primary_annotator_reuse() -> None:
    case, handoff = _completed_unknown_handoff()
    handoff["annotationSubmission"]["annotatorId"] = case["annotations"][0]["annotatorId"]

    with pytest.raises(SecondAnnotationError, match="distinct") as exc:
        verify_submission(case, handoff, base_dir=CASE_PATH.parent)
    assert exc.value.code == "ANN006"


def test_verify_rejects_independence_not_attested() -> None:
    case, handoff = _completed_unknown_handoff()
    handoff["annotationSubmission"]["independent"] = False

    with pytest.raises(SecondAnnotationError, match="independent=true") as exc:
        verify_submission(case, handoff, base_dir=CASE_PATH.parent)
    assert exc.value.code == "ANN006"


def test_verify_rejects_missing_independence_attestation() -> None:
    case, handoff = _completed_unknown_handoff()
    handoff["annotationSubmission"].pop("independenceAttestation")

    with pytest.raises(SecondAnnotationError, match="independenceAttestation") as exc:
        verify_submission(case, handoff, base_dir=CASE_PATH.parent)
    assert exc.value.code == "ANN005"


def test_verify_rejects_wrong_independence_attestation() -> None:
    case, handoff = _completed_unknown_handoff()
    handoff["annotationSubmission"]["independenceAttestation"] = "I agree."

    with pytest.raises(SecondAnnotationError, match="attestation text") as exc:
        verify_submission(case, handoff, base_dir=CASE_PATH.parent)
    assert exc.value.code == "ANN006"


def test_verify_rejects_nonfinite_elapsed_minutes() -> None:
    case, handoff = _completed_unknown_handoff()
    handoff["annotationSubmission"]["elapsedMinutes"] = float("nan")

    with pytest.raises(SecondAnnotationError, match="finite non-negative") as exc:
        verify_submission(case, handoff, base_dir=CASE_PATH.parent)
    assert exc.value.code == "ANN005"


def test_verify_rejects_missing_material_field() -> None:
    case, handoff = _completed_unknown_handoff()
    handoff["annotationSubmission"]["fields"].pop()

    with pytest.raises(SecondAnnotationError, match="complete fixed material field set") as exc:
        verify_submission(case, handoff, base_dir=CASE_PATH.parent)
    assert exc.value.code == "ANN007"


def test_verify_rejects_unknown_source_reference() -> None:
    case, handoff = _completed_unknown_handoff()
    field = handoff["annotationSubmission"]["fields"][0]
    field["classification"] = "direct-source"
    field["sourceArtifactIds"] = ["NOT-IN-HANDOFF"]

    with pytest.raises(SecondAnnotationError, match="outside the handoff") as exc:
        verify_submission(case, handoff, base_dir=CASE_PATH.parent)
    assert exc.value.code == "ANN008"


def test_verify_rejects_static_handoff_tampering() -> None:
    case, handoff = _completed_unknown_handoff()
    tampered = copy.deepcopy(handoff)
    tampered["initialRecordHash"] = "sha256:" + "0" * 64

    with pytest.raises(SecondAnnotationError, match="initialRecordHash") as exc:
        verify_submission(case, tampered, base_dir=CASE_PATH.parent)
    assert exc.value.code == "ANN004"
