"""Layer-specific replay. Agreement is not correctness or fairness."""

from __future__ import annotations

from typing import Any

from canonicalize import canonicalize
from support import Phase2Error, sha256_hex, validate_schema

DETERMINISTIC_LAYERS = (
    "preprocessing",
    "retrieval-snapshot",
    "scoring",
    "aggregation",
)
HOSTED_LAYER = "hosted-generation"
ALL_LAYERS = DETERMINISTIC_LAYERS + (HOSTED_LAYER,)
OUTCOMES = ("exact-match", "bounded-match", "diverged", "not-replayable")


def layer_digest(layer_input: Any) -> str:
    return sha256_hex(canonicalize(layer_input))


def replay(
    *,
    attested_layer_digests: dict[str, str],
    layer_inputs: dict[str, Any],
    hosted_replayable: bool = False,
    bounds: dict[str, str] | None = None,
    manifest_commitment_digest: str,
) -> dict[str, Any]:
    bounds = bounds or {}
    layers: list[dict[str, Any]] = []
    for layer_id in ALL_LAYERS:
        attested = attested_layer_digests[layer_id]
        if layer_id == HOSTED_LAYER and not hosted_replayable:
            layers.append(
                {
                    "layerId": layer_id,
                    "outcome": "not-replayable",
                    "attestedDigest": attested,
                    "recomputedDigest": None,
                    "bound": None,
                    "reason": (
                        "Hosted generation is not replayable: model identity and decoding "
                        "behavior are not under this protocol's control."
                    ),
                }
            )
            continue
        if layer_id not in layer_inputs:
            raise Phase2Error(f"missing layer input for {layer_id}", code="RPL001")
        recomputed = layer_digest(layer_inputs[layer_id])
        if recomputed == attested:
            outcome = "exact-match"
            reason = None
        elif layer_id in bounds:
            outcome = "bounded-match" if _within_bound(attested, recomputed, bounds[layer_id]) else "diverged"
            reason = None if outcome == "bounded-match" else "recomputed digest outside declared bound"
        else:
            outcome = "diverged"
            reason = "recomputed digest does not match attested digest"
        layers.append(
            {
                "layerId": layer_id,
                "outcome": outcome,
                "attestedDigest": attested,
                "recomputedDigest": recomputed,
                "bound": bounds.get(layer_id),
                "reason": reason,
            }
        )
    report = {
        "reportVersion": "1",
        "manifestCommitmentDigest": manifest_commitment_digest,
        "layers": layers,
    }
    validate_schema(report, "replay-report.schema.json")
    return report


def _within_bound(attested: str, recomputed: str, bound: str) -> bool:
    """Hamming distance over hex encoded digests compared to an integer bound string."""
    if len(attested) != len(recomputed):
        return False
    distance = sum(a != b for a, b in zip(attested, recomputed))
    try:
        limit = int(bound)
    except ValueError as exc:
        raise Phase2Error(f"invalid replay bound {bound}", code="RPL002") from exc
    return distance <= limit


def verify_replay_report(
    report: dict[str, Any],
    *,
    attested_layer_digests: dict[str, str],
    layer_inputs: dict[str, Any] | None,
    hosted_replayable: bool,
    manifest_commitment_digest: str,
) -> None:
    validate_schema(report, "replay-report.schema.json")
    if report["manifestCommitmentDigest"] != manifest_commitment_digest:
        raise Phase2Error("replay report commitment digest does not match envelope", code="RPL003", claim="C5")
    by_id = {item["layerId"]: item for item in report["layers"]}
    if set(by_id) != set(ALL_LAYERS):
        raise Phase2Error("replay report must include every defined layer", code="RPL004", claim="C5")
    expected = replay(
        attested_layer_digests=attested_layer_digests,
        layer_inputs=layer_inputs or {},
        hosted_replayable=hosted_replayable,
        bounds={
            item["layerId"]: item["bound"]
            for item in report["layers"]
            if item.get("outcome") == "bounded-match" and item.get("bound")
        },
        manifest_commitment_digest=manifest_commitment_digest,
    )
    expected_by_id = {item["layerId"]: item for item in expected["layers"]}
    for layer_id, item in by_id.items():
        if item["outcome"] not in OUTCOMES:
            raise Phase2Error(f"invalid outcome for {layer_id}", code="RPL005", claim="C5")
        if item["outcome"] != expected_by_id[layer_id]["outcome"]:
            raise Phase2Error(
                f"replay outcome for {layer_id} is inconsistent with recomputation",
                code="RPL006",
                claim="C5",
            )
        if item["attestedDigest"] != attested_layer_digests[layer_id]:
            raise Phase2Error(f"replay attested digest for {layer_id} does not match run predicate", code="RPL007", claim="C5")
