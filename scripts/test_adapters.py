"""Adapter invariant tests: evidence marshaling only."""

from __future__ import annotations

import pytest

from adapters import (
    AdapterError,
    FieldProvenance,
    OperatorConfirmation,
    build_draft,
    explain,
    import_normalized_event,
    map_field,
    refuse_forbidden_operation,
)


def test_refuses_merit_and_authority_operations() -> None:
    for op in (
        "merit_score",
        "recommend_approval",
        "infer_eligibility",
        "assign_authority",
        "ai_as_authority",
        "unknown_to_pass",
    ):
        with pytest.raises(AdapterError):
            refuse_forbidden_operation(op)


def test_material_interpretive_requires_confirmation() -> None:
    conf = [
        OperatorConfirmation(
            confirmation_id="confirm-eligibility-vs-merit",
            confirmed=True,
            operator="op-1",
        )
    ]
    with pytest.raises(AdapterError):
        map_field(
            path="eligibility.disposition",
            value="eligible",
            provenance=FieldProvenance(
                kind="interpretive",
                mapping_rule_id="elig-1",
                confirmation_id="confirm-eligibility-vs-merit",
                operator_confirmed=False,
            ),
            material=True,
            confirmations=conf,
        )

    mapped = map_field(
        path="eligibility.disposition",
        value="eligible",
        provenance=FieldProvenance(
            kind="interpretive",
            mapping_rule_id="elig-1",
            confirmation_id="confirm-eligibility-vs-merit",
            operator_confirmed=True,
        ),
        material=True,
        confirmations=conf,
    )
    assert mapped.provenance.kind == "interpretive"


def test_unknown_cannot_become_pass() -> None:
    with pytest.raises(AdapterError):
        map_field(
            path="eligibility.disposition",
            value="pass",
            provenance=FieldProvenance(
                kind="unknown",
                confirmation_id="confirm-eligibility-vs-merit",
                operator_confirmed=True,
            ),
            material=True,
            confirmations=[
                OperatorConfirmation(
                    confirmation_id="confirm-eligibility-vs-merit",
                    confirmed=True,
                )
            ],
        )


def test_cannot_assign_ai_authority() -> None:
    with pytest.raises(AdapterError):
        build_draft(
            profile_id="ens-foundation-tier-a-v1",
            mapping_version="1",
            fields=[
                map_field(
                    path="decision.authorityKind",
                    value="ai",
                    provenance=FieldProvenance(
                        kind="direct",
                        source_path="memo.md",
                    ),
                    material=True,
                    confirmations=[],
                )
            ],
            confirmations=[],
        )


def test_participant_requires_source_or_confirmation() -> None:
    with pytest.raises(AdapterError):
        build_draft(
            profile_id="ens-foundation-tier-b-v1",
            mapping_version="1",
            fields=[
                map_field(
                    path="evaluators[0].participant",
                    value=True,
                    provenance=FieldProvenance(kind="unknown"),
                    material=False,
                    confirmations=[],
                )
            ],
            confirmations=[],
        )


def test_explain_lists_provenance() -> None:
    conf = [
        OperatorConfirmation(
            confirmation_id="confirm-decision-authority",
            confirmed=True,
            operator="op-1",
        )
    ]
    field = map_field(
        path="decision.authorityKind",
        value="committee",
        provenance=FieldProvenance(
            kind="interpretive",
            mapping_rule_id="auth-1",
            confirmation_id="confirm-decision-authority",
            operator_confirmed=True,
            source_path="decision-memo.md",
        ),
        material=True,
        confirmations=conf,
    )
    draft = build_draft(
        profile_id="ens-foundation-tier-a-v1",
        mapping_version="1",
        fields=[field],
        confirmations=conf,
    )
    rows = explain(draft)
    assert rows[0]["path"] == "decision.authorityKind"
    assert rows[0]["provenanceKind"] == "interpretive"
    assert rows[0]["operatorConfirmed"] is True
    assert draft.warnings  # other material confirmations still missing


def test_import_normalized_event_requires_type() -> None:
    with pytest.raises(AdapterError):
        import_normalized_event({})
    event = import_normalized_event(
        {"eventType": "decision-memo", "sourceId": "memo-1", "payload": {"x": 1}}
    )
    assert event["eventType"] == "decision-memo"
