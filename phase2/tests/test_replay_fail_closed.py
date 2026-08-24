"""Regression tests for replay claim boundaries and protocol versioning."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from factories import attested_digests, layer_inputs, sample_predicate
from graph import verify_graph
from replay import replay, verify_replay_report
from support import Phase2Error, validate_schema

PHASE2_ROOT = Path(__file__).resolve().parents[1]


def _report_fixture() -> tuple[dict, dict, dict]:
    inputs = layer_inputs()
    attested = attested_digests(inputs)
    predicate = sample_predicate("ab" * 32, inputs)
    report = replay(
        attested_layer_digests=attested,
        layer_inputs=inputs,
        hosted_replayable=False,
        manifest_commitment_digest=predicate["manifestCommitmentDigest"],
    )
    return inputs, attested, report


def test_replay_emits_version_2_without_repurposing_v1() -> None:
    _, _, report = _report_fixture()
    assert report["reportVersion"] == "2"
    validate_schema(report, "replay-report-v2.schema.json")


def test_bounds_are_rejected_instead_of_comparing_hash_distance() -> None:
    inputs = layer_inputs()
    attested = attested_digests(inputs)
    predicate = sample_predicate("ab" * 32, inputs)
    with pytest.raises(Phase2Error) as exc:
        replay(
            attested_layer_digests=attested,
            layer_inputs=inputs,
            bounds={"scoring": "2"},
            hosted_replayable=False,
            manifest_commitment_digest=predicate["manifestCommitmentDigest"],
        )
    assert exc.value.code == "RPL008"


def test_legacy_v1_bounded_report_remains_schema_valid_but_verifier_rejects_it() -> None:
    inputs, attested, report = _report_fixture()
    legacy = copy.deepcopy(report)
    legacy["reportVersion"] = "1"
    scoring = next(item for item in legacy["layers"] if item["layerId"] == "scoring")
    scoring["outcome"] = "bounded-match"
    scoring["bound"] = "2"

    # Historical v1 wire semantics remain frozen and parseable.
    validate_schema(legacy, "replay-report.schema.json")

    with pytest.raises(Phase2Error) as exc:
        verify_replay_report(
            legacy,
            attested_layer_digests=attested,
            layer_inputs=inputs,
            hosted_replayable=False,
            manifest_commitment_digest=legacy["manifestCommitmentDigest"],
        )
    assert exc.value.code == "RPL008"


def test_safe_legacy_v1_exact_report_can_still_be_verified() -> None:
    inputs, attested, report = _report_fixture()
    legacy = copy.deepcopy(report)
    legacy["reportVersion"] = "1"
    validate_schema(legacy, "replay-report.schema.json")
    verify_replay_report(
        legacy,
        attested_layer_digests=attested,
        layer_inputs=inputs,
        hosted_replayable=False,
        manifest_commitment_digest=legacy["manifestCommitmentDigest"],
    )


def test_bundle_v2_carries_replay_v2_without_rewriting_bundle_v1() -> None:
    bundle = json.loads(
        (PHASE2_ROOT / "examples" / "retrospective-public.bundle.json").read_text(encoding="utf-8")
    )
    bundle["bundleVersion"] = "2"
    bundle["replayReport"]["reportVersion"] = "2"
    validate_schema(bundle, "evidence-bundle-v2.schema.json")
    result = verify_graph(bundle)
    assert result.ok
    assert "C5" in result.established
    assert result.details["bundleVersion"] == "2"


def test_duplicate_layer_ids_fail_closed() -> None:
    inputs, attested, report = _report_fixture()
    duplicate = copy.deepcopy(report)
    duplicate["layers"].append(copy.deepcopy(duplicate["layers"][0]))
    with pytest.raises(Phase2Error) as exc:
        verify_replay_report(
            duplicate,
            attested_layer_digests=attested,
            layer_inputs=inputs,
            hosted_replayable=False,
            manifest_commitment_digest=duplicate["manifestCommitmentDigest"],
        )
    assert exc.value.code == "SCHEMA002"


def test_missing_attested_layer_fails_as_protocol_error() -> None:
    inputs = layer_inputs()
    attested = attested_digests(inputs)
    attested.pop("aggregation")
    predicate = sample_predicate("ab" * 32, inputs)
    with pytest.raises(Phase2Error) as exc:
        replay(
            attested_layer_digests=attested,
            layer_inputs=inputs,
            hosted_replayable=False,
            manifest_commitment_digest=predicate["manifestCommitmentDigest"],
        )
    assert exc.value.code == "RPL010"
    assert exc.value.claim == "C5"


def test_unexpected_attested_layer_fails_as_protocol_error() -> None:
    inputs = layer_inputs()
    attested = attested_digests(inputs)
    attested["unexpected-layer"] = "00" * 32
    predicate = sample_predicate("ab" * 32, inputs)
    with pytest.raises(Phase2Error) as exc:
        replay(
            attested_layer_digests=attested,
            layer_inputs=inputs,
            hosted_replayable=False,
            manifest_commitment_digest=predicate["manifestCommitmentDigest"],
        )
    assert exc.value.code == "RPL010"


def test_tampered_recomputed_digest_fails_even_when_outcome_is_unchanged() -> None:
    inputs, attested, report = _report_fixture()
    tampered = copy.deepcopy(report)
    scoring = next(item for item in tampered["layers"] if item["layerId"] == "scoring")
    scoring["recomputedDigest"] = "00" * 32
    with pytest.raises(Phase2Error) as exc:
        verify_replay_report(
            tampered,
            attested_layer_digests=attested,
            layer_inputs=inputs,
            hosted_replayable=False,
            manifest_commitment_digest=tampered["manifestCommitmentDigest"],
        )
    assert exc.value.code == "RPL011"
    assert exc.value.claim == "C5"


def test_not_replayable_layer_cannot_claim_a_recomputed_digest() -> None:
    inputs, attested, report = _report_fixture()
    tampered = copy.deepcopy(report)
    hosted = next(item for item in tampered["layers"] if item["layerId"] == "hosted-generation")
    hosted["recomputedDigest"] = "00" * 32
    with pytest.raises(Phase2Error) as exc:
        verify_replay_report(
            tampered,
            attested_layer_digests=attested,
            layer_inputs=inputs,
            hosted_replayable=False,
            manifest_commitment_digest=tampered["manifestCommitmentDigest"],
        )
    assert exc.value.code == "SCHEMA002"


def test_tampered_reason_fails_even_when_verified_outcome_is_unchanged() -> None:
    inputs = layer_inputs()
    attested = attested_digests(inputs)
    predicate = sample_predicate("ab" * 32, inputs)
    perturbed = copy.deepcopy(inputs)
    perturbed["scoring"]["materialChange"] = True
    report = replay(
        attested_layer_digests=attested,
        layer_inputs=perturbed,
        hosted_replayable=False,
        manifest_commitment_digest=predicate["manifestCommitmentDigest"],
    )
    tampered = copy.deepcopy(report)
    scoring = next(item for item in tampered["layers"] if item["layerId"] == "scoring")
    assert scoring["outcome"] == "diverged"
    scoring["reason"] = "different schema-valid explanation"
    with pytest.raises(Phase2Error) as exc:
        verify_replay_report(
            tampered,
            attested_layer_digests=attested,
            layer_inputs=perturbed,
            hosted_replayable=False,
            manifest_commitment_digest=tampered["manifestCommitmentDigest"],
        )
    assert exc.value.code == "RPL012"
    assert exc.value.claim == "C5"


def test_material_change_remains_diverged_without_approximate_hash_semantics() -> None:
    inputs = layer_inputs()
    attested = attested_digests(inputs)
    predicate = sample_predicate("ab" * 32, inputs)
    perturbed = copy.deepcopy(inputs)
    perturbed["scoring"]["materialChange"] = True
    report = replay(
        attested_layer_digests=attested,
        layer_inputs=perturbed,
        hosted_replayable=False,
        manifest_commitment_digest=predicate["manifestCommitmentDigest"],
    )
    by_id = {item["layerId"]: item for item in report["layers"]}
    assert by_id["scoring"]["outcome"] == "diverged"
    assert by_id["scoring"]["bound"] is None
