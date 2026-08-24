"""Layer-specific replay artifact verification.

Exact digest equality establishes object identity under the declared JCS
serialization. Agreement is not correctness, fairness, or proof that a recorded
implementation was re-executed.

Replay report v1 is retained as a historical wire format. Its ``bounded-match``
mechanism is not accepted by the verifier because cryptographic digest distance
has no semantic relationship to distance between underlying computations.
Replay report v2 removes that mechanism. Both accepted versions require their
reported evidence fields to agree with verifier recomputation, using each
version's defined reason text. Approximate reproducibility, if added, requires a
separately versioned layer-specific comparator over typed outputs.
"""

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
OUTCOMES = ("exact-match", "diverged", "not-replayable")
CURRENT_REPORT_VERSION = "2"
REPORT_SCHEMAS = {
    "1": "replay-report.schema.json",
    "2": "replay-report-v2.schema.json",
}
V1_DIVERGENCE_REASON = "recomputed digest does not match attested digest"
V2_DIVERGENCE_REASON = "recomputed canonical digest does not match attested digest"
HOSTED_NOT_REPLAYABLE_REASON = (
    "Hosted generation is not replayable: model identity and decoding "
    "behavior are not under this protocol's control."
)


def layer_digest(layer_input: Any) -> str:
    return sha256_hex(canonicalize(layer_input))


def _require_attested_layers(attested_layer_digests: dict[str, str]) -> None:
    missing = sorted(set(ALL_LAYERS) - set(attested_layer_digests))
    extra = sorted(set(attested_layer_digests) - set(ALL_LAYERS))
    if missing or extra:
        parts: list[str] = []
        if missing:
            parts.append("missing: " + ", ".join(missing))
        if extra:
            parts.append("unexpected: " + ", ".join(extra))
        raise Phase2Error(
            "attested replay layer set does not match the defined layers (" + "; ".join(parts) + ")",
            code="RPL010",
            claim="C5",
        )


def replay(
    *,
    attested_layer_digests: dict[str, str],
    layer_inputs: dict[str, Any],
    hosted_replayable: bool = False,
    bounds: dict[str, str] | None = None,
    manifest_commitment_digest: str,
) -> dict[str, Any]:
    """Recompute canonical layer digests and emit replay report v2."""
    if bounds:
        raise Phase2Error(
            "bounded replay over cryptographic digest distance is unsupported; use a versioned typed comparator over underlying outputs",
            code="RPL008",
            claim="C5",
        )
    _require_attested_layers(attested_layer_digests)

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
                    "reason": HOSTED_NOT_REPLAYABLE_REASON,
                }
            )
            continue
        if layer_id not in layer_inputs:
            raise Phase2Error(f"missing layer input for {layer_id}", code="RPL001", claim="C5")
        recomputed = layer_digest(layer_inputs[layer_id])
        if recomputed == attested:
            outcome = "exact-match"
            reason = None
        else:
            outcome = "diverged"
            reason = V2_DIVERGENCE_REASON
        layers.append(
            {
                "layerId": layer_id,
                "outcome": outcome,
                "attestedDigest": attested,
                "recomputedDigest": recomputed,
                "bound": None,
                "reason": reason,
            }
        )
    report = {
        "reportVersion": CURRENT_REPORT_VERSION,
        "manifestCommitmentDigest": manifest_commitment_digest,
        "layers": layers,
    }
    validate_schema(report, REPORT_SCHEMAS[CURRENT_REPORT_VERSION])
    return report


def _expected_reason(report_version: str, expected_item: dict[str, Any]) -> str | None:
    if expected_item["outcome"] != "diverged":
        return expected_item.get("reason")
    if report_version == "1":
        return V1_DIVERGENCE_REASON
    return V2_DIVERGENCE_REASON


def verify_replay_report(
    report: dict[str, Any],
    *,
    attested_layer_digests: dict[str, str],
    layer_inputs: dict[str, Any] | None,
    hosted_replayable: bool,
    manifest_commitment_digest: str,
) -> None:
    report_version = report.get("reportVersion")
    schema_name = REPORT_SCHEMAS.get(report_version)
    if schema_name is None:
        raise Phase2Error(
            f"unsupported replay report version {report_version!r}",
            code="RPL009",
            claim="C5",
        )
    validate_schema(report, schema_name)
    _require_attested_layers(attested_layer_digests)

    if report["manifestCommitmentDigest"] != manifest_commitment_digest:
        raise Phase2Error("replay report commitment digest does not match envelope", code="RPL003", claim="C5")

    layer_ids = [item["layerId"] for item in report["layers"]]
    by_id = {item["layerId"]: item for item in report["layers"]}
    if len(by_id) != len(layer_ids):
        raise Phase2Error("replay report contains duplicate layer ids", code="RPL004", claim="C5")
    if set(by_id) != set(ALL_LAYERS):
        raise Phase2Error("replay report must include every defined layer exactly once", code="RPL004", claim="C5")

    # v1 remains parseable for historical compatibility, but its approximate
    # hash-distance mechanism is not evidence this verifier is willing to accept.
    if any(item.get("outcome") == "bounded-match" or item.get("bound") not in {None, ""} for item in report["layers"]):
        raise Phase2Error(
            "bounded replay over cryptographic digest distance is not accepted",
            code="RPL008",
            claim="C5",
        )

    expected = replay(
        attested_layer_digests=attested_layer_digests,
        layer_inputs=layer_inputs or {},
        hosted_replayable=hosted_replayable,
        manifest_commitment_digest=manifest_commitment_digest,
    )
    expected_by_id = {item["layerId"]: item for item in expected["layers"]}
    for layer_id, item in by_id.items():
        expected_item = expected_by_id[layer_id]
        if item["outcome"] not in OUTCOMES:
            raise Phase2Error(f"invalid outcome for {layer_id}", code="RPL005", claim="C5")
        if item["outcome"] != expected_item["outcome"]:
            raise Phase2Error(
                f"replay outcome for {layer_id} is inconsistent with recomputation",
                code="RPL006",
                claim="C5",
            )
        if item.get("attestedDigest") != attested_layer_digests[layer_id]:
            raise Phase2Error(f"replay attested digest for {layer_id} does not match run predicate", code="RPL007", claim="C5")
        if item.get("recomputedDigest") != expected_item.get("recomputedDigest"):
            raise Phase2Error(
                f"replay recomputed digest for {layer_id} is inconsistent with supplied artifact material",
                code="RPL011",
                claim="C5",
            )
        if item.get("reason") != _expected_reason(str(report_version), expected_item):
            raise Phase2Error(
                f"replay reason for {layer_id} is inconsistent with the verified outcome",
                code="RPL012",
                claim="C5",
            )
