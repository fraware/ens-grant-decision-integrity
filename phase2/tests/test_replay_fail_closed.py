"""Regression tests for replay claim boundaries and protocol versioning."""

from __future__ import annotations

import copy

import pytest

from factories import attested_digests, layer_inputs, sample_predicate
from replay import replay, verify_replay_report
from support import Phase2Error, validate_schema


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


def test_duplicate_layer_ids_fail_closed() -> None:
    inputs, attested, report = _report_fixture()
    duplicate = copy.deepcopy(report)
    duplicate["layers"].append(copy.deepcopy(duplicate["layers"][0]))
    validate_schema(duplicate, "replay-report-v2.schema.json")
    with pytest.raises(Phase2Error) as exc:
        verify_replay_report(
            duplicate,
            attested_layer_digests=attested,
            layer_inputs=inputs,
            hosted_replayable=False,
            manifest_commitment_digest=duplicate["manifestCommitmentDigest"],
        )
    assert exc.value.code == "RPL004"


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
