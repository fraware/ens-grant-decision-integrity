"""T11: Hosted-model not-replayable does not void deterministic-layer claims."""

from __future__ import annotations

from pathlib import Path

from factories import build_bundle, generate_rekor_fixture_key
from graph import verify_graph


def test_hosted_not_replayable_keeps_deterministic_exact_match() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    result = verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
    assert result.ok
    assert "C5" in result.established
    by_id = {item["layerId"]: item for item in bundle["replayReport"]["layers"]}
    assert by_id["hosted-generation"]["outcome"] == "not-replayable"
    for layer_id in ("preprocessing", "retrieval-snapshot", "scoring", "aggregation"):
        assert by_id[layer_id]["outcome"] == "exact-match"


def test_public_example_preserves_hosted_and_chal003() -> None:
    import json
    import sys

    example = Path(__file__).resolve().parents[1] / "examples" / "retrospective-public.bundle.json"
    bundle = json.loads(example.read_text(encoding="utf-8"))
    result = verify_graph(bundle)
    assert result.ok
    by_id = {item["layerId"]: item for item in bundle["replayReport"]["layers"]}
    assert by_id["hosted-generation"]["outcome"] == "not-replayable"
    for layer_id in ("preprocessing", "retrieval-snapshot", "scoring", "aggregation"):
        assert by_id[layer_id]["outcome"] == "exact-match"
    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo / "scripts"))
    from conformance import validate_record

    schema = json.loads((repo / "schema" / "grant-decision-record.schema.json").read_text(encoding="utf-8"))
    findings = validate_record(bundle["decisionRecord"], schema)
    errors = [item for item in findings if item.severity == "error"]
    warnings = {item.code for item in findings if item.severity == "warning"}
    assert errors == []
    assert warnings == {"CHAL003"}
    assert bundle["decisionRecord"]["decision"]["authorityKind"] == "committee"
    assert bundle["decisionRecord"]["evaluatorManifest"]["commitment"]["algorithm"] == "other"

