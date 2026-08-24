"""Regression tests for replay claim boundaries."""

from __future__ import annotations

import copy

import pytest

from factories import attested_digests, layer_inputs, sample_predicate
from replay import replay
from support import Phase2Error


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
