"""T12: No Phase II object can populate or imply v0.1 decision.authorityKind."""

from __future__ import annotations

import copy

import pytest

from factories import build_bundle, generate_rekor_fixture_key
from graph import refuse_populate_authority_kind, verify_graph
from support import Phase2Error


def test_refuse_helper_never_writes_authority_kind() -> None:
    private_pem, _public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    with pytest.raises(Phase2Error, match="cannot populate decision.authorityKind"):
        refuse_populate_authority_kind(bundle["runAttestation"], bundle["decisionRecord"])
    assert bundle["decisionRecord"]["decision"]["authorityKind"] == "committee"


def test_phase2_object_with_authority_kind_fails_graph() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    poisoned = copy.deepcopy(bundle)
    poisoned["selectiveAuditResult"] = {"authorityKind": "ai", "note": "must not be accepted"}
    with pytest.raises(Phase2Error, match="decision-authority fields") as exc:
        verify_graph(poisoned, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
    assert exc.value.claim == "C6"


def test_run_predicate_authority_kind_fails_graph() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    poisoned = copy.deepcopy(bundle)
    poisoned["runAttestation"]["authorityKind"] = "committee"
    with pytest.raises(Phase2Error, match="decision-authority fields"):
        verify_graph(poisoned, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)


def test_sha256_algorithm_rejected_for_salted_digest() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    bundle["decisionRecord"]["evaluatorManifest"]["commitment"]["algorithm"] = "sha256"
    with pytest.raises(Phase2Error, match="must not be sha256"):
        verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)


def test_valid_bundle_establishes_c6_without_touching_authority() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    before = bundle["decisionRecord"]["decision"]["authorityKind"]
    result = verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
    assert result.ok
    assert "C6" in result.established
    assert bundle["decisionRecord"]["decision"]["authorityKind"] == before == "committee"
    assert "ai" not in (
        bundle["decisionRecord"]["decision"]["authorityKind"],
        bundle["envelope"],
    )


def test_v01_ai_authority_kind_rejected_by_graph() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    bundle["decisionRecord"]["decision"]["authorityKind"] = "ai"
    with pytest.raises(Phase2Error, match="authorityKind"):
        verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)


def test_envelope_forbidden_authority_field_fails_graph() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    bundle["envelope"]["fundingAuthority"] = "must-not-appear"
    with pytest.raises(Phase2Error, match="(decision-authority fields|Additional properties)"):
        verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)


def test_manifest_nested_forbidden_authority_field_fails_graph() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    bundle["manifest"]["instructions"]["decisionAuthority"] = "must-not-appear"
    with pytest.raises(Phase2Error, match="decision-authority fields"):
        verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
