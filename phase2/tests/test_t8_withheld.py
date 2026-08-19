"""T8: Withheld disclosure reports only anchor-supported claims; no C1."""

from __future__ import annotations

from factories import build_bundle, generate_rekor_fixture_key
from graph import verify_graph
from reveal import verify_reveal


def test_withheld_does_not_establish_c1() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(
        rekor_private_pem=private_pem,
        reveal_status="withheld",
        include_run=False,
        include_replay=False,
    )
    result = verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
    assert result.ok
    assert "C1" not in result.established
    assert "C2" in result.established
    assert "C3" in result.established
    assert "C6" in result.established
    local = verify_reveal(envelope=bundle["envelope"], reveal_status="withheld")
    assert "C1" not in local.established
    assert "Manifest contents were not checked." in local.details["establishedNote"]


def test_selective_audit_establishes_c1_when_manifest_supplied() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(
        rekor_private_pem=private_pem,
        reveal_status="selective-audit",
        include_run=False,
        include_replay=False,
    )
    result = verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
    assert result.ok
    assert "C1" in result.established
    assert "C2" in result.established
    assert bundle["decisionRecord"]["evaluatorManifest"]["revealStatus"] == "partially-revealed"
