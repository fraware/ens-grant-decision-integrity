"""CLI regressions for ambiguous or profile-incompatible inputs."""

from __future__ import annotations

import argparse

import pytest

from cli import cmd_anchor, cmd_verify_commitment
from support import Phase2Error


def test_verify_commitment_rejects_manifest_without_salt_before_io() -> None:
    args = argparse.Namespace(
        envelope="unused-envelope.json",
        receipt="unused-receipt.json",
        manifest="manifest.json",
        salt=None,
        fixture_key=None,
        trust_root=None,
    )
    with pytest.raises(Phase2Error) as exc:
        cmd_verify_commitment(args)
    assert exc.value.code == "CLI007"
    assert exc.value.claim == "C1"


def test_verify_commitment_rejects_salt_without_manifest_before_io() -> None:
    args = argparse.Namespace(
        envelope="unused-envelope.json",
        receipt="unused-receipt.json",
        manifest=None,
        salt="salt.json",
        fixture_key=None,
        trust_root=None,
    )
    with pytest.raises(Phase2Error) as exc:
        cmd_verify_commitment(args)
    assert exc.value.code == "CLI007"


def _anchor_args(**overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "envelope": "unused-envelope.json",
        "profile": "rekor-v1",
        "fixture_key": None,
        "artifact_key": None,
        "trust_root": None,
        "tsa_cert": None,
        "tx_hash": None,
        "at": None,
        "out": "unused-receipt.json",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_live_profile_rejects_caller_selected_fixture_time_before_io() -> None:
    with pytest.raises(Phase2Error) as exc:
        cmd_anchor(_anchor_args(at="2026-08-24T12:00:00Z"))
    assert exc.value.code == "CLI008"


def test_non_ethereum_profile_rejects_transaction_hash_before_io() -> None:
    with pytest.raises(Phase2Error) as exc:
        cmd_anchor(_anchor_args(tx_hash="0x1234"))
    assert exc.value.code == "CLI009"


def test_non_rfc_fixture_profile_rejects_tsa_certificate_before_io() -> None:
    with pytest.raises(Phase2Error) as exc:
        cmd_anchor(_anchor_args(tsa_cert="tsa.pem"))
    assert exc.value.code == "CLI010"
