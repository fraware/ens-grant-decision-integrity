"""T10: Perturbing deterministic preprocessing, scoring, or aggregation is detected as diverged."""

from __future__ import annotations

import copy

import pytest

from factories import attested_digests, layer_inputs, sample_predicate
from replay import replay


@pytest.mark.parametrize("layer_id", ["preprocessing", "scoring", "aggregation"])
def test_deterministic_perturbation_is_diverged(layer_id: str) -> None:
    inputs = layer_inputs()
    attested = attested_digests(inputs)
    predicate = sample_predicate("ab" * 32, inputs)
    perturbed = copy.deepcopy(inputs)
    perturbed[layer_id] = copy.deepcopy(perturbed[layer_id])
    perturbed[layer_id]["perturbation"] = "material-change"
    report = replay(
        attested_layer_digests=attested,
        layer_inputs=perturbed,
        hosted_replayable=False,
        manifest_commitment_digest=predicate["manifestCommitmentDigest"],
    )
    by_id = {item["layerId"]: item for item in report["layers"]}
    assert by_id[layer_id]["outcome"] == "diverged"
    assert by_id["hosted-generation"]["outcome"] == "not-replayable"
