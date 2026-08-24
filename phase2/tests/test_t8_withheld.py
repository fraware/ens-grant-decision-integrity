"""T8: unopened disclosure states report only anchor-supported claims; no C1."""

from __future__ import annotations

import copy

import pytest

from factories import build_bundle, generate_rekor_fixture_key
from graph import verify_graph
from reveal import verify_reveal
from support import Phase2Error, validate_schema


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


def test_committed_state_is_unopened_and_does_not_establish_c1() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(
        rekor_private_pem=private_pem,
        reveal_status="revealed",
        include_run=False,
        include_replay=False,
    )
    bundle["revealStatus"] = "committed"
    bundle["manifest"] = None
    bundle["saltHex"] = None
    bundle["decisionRecord"]["evaluatorManifest"]["revealStatus"] = "committed"
    bundle["decisionRecord"]["evaluatorManifest"]["revealUri"] = None

    result = verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
    assert result.ok
    assert "C1" not in result.established
    assert "C2" in result.established
    assert "C3" in result.established
    assert "C6" in result.established
    local = verify_reveal(envelope=bundle["envelope"], reveal_status="committed")
    assert local.established == []
    assert "Commitment remains unopened." in local.details["establishedNote"]


def test_committed_state_rejects_disclosed_manifest_material() -> None:
    private_pem, _ = generate_rekor_fixture_key()
    bundle = build_bundle(
        rekor_private_pem=private_pem,
        reveal_status="revealed",
        include_run=False,
        include_replay=False,
    )
    with pytest.raises(Phase2Error) as exc:
        verify_reveal(
            envelope=bundle["envelope"],
            reveal_status="committed",
            manifest=bundle["manifest"],
            salt=bytes.fromhex(bundle["saltHex"]),
        )
    assert exc.value.code == "REV002"


def test_bundle_v2_requires_private_material_for_selective_audit() -> None:
    private_pem, _ = generate_rekor_fixture_key()
    bundle = build_bundle(
        rekor_private_pem=private_pem,
        reveal_status="selective-audit",
        include_run=False,
        include_replay=False,
    )
    bundle["bundleVersion"] = "2"
    bundle["replayReport"] = None
    validate_schema(bundle, "evidence-bundle-v2.schema.json")

    missing = copy.deepcopy(bundle)
    missing["manifest"] = None
    missing["saltHex"] = None
    with pytest.raises(Phase2Error) as exc:
        validate_schema(missing, "evidence-bundle-v2.schema.json")
    assert exc.value.code == "SCHEMA002"


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
    assert "C3" in result.established
    assert bundle["decisionRecord"]["evaluatorManifest"]["revealStatus"] == "partially-revealed"
