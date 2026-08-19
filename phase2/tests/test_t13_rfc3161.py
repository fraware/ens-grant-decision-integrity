"""Tests for RFC 3161 anchor profile."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from anchors.rfc3161 import Rfc3161Adapter, generate_fixture_tsa_key
from envelope import commit_manifest, envelope_bytes
from factories import sample_manifest
from support import Phase2Error


@pytest.fixture(scope="module")
def tsa_material() -> tuple[str, str, str]:
    private_pem, public_pem, _cert_der, cert_pem = generate_fixture_tsa_key()
    return private_pem, public_pem, cert_pem


def test_rfc3161_fixture_anchor_and_verify(tsa_material: tuple[str, str, str]) -> None:
    private_pem, public_pem, cert_pem = tsa_material
    manifest = sample_manifest(programId="rfc3161-fixture-test")
    envelope, _salt = commit_manifest(manifest)
    env_bytes = envelope_bytes(envelope)
    adapter = Rfc3161Adapter(
        profile_id="rfc3161-recorded-fixture",
        fixture_private_key_pem=private_pem,
        fixture_certificate_pem=cert_pem,
        trust_root_pem=cert_pem,
    )
    when = datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
    receipt = adapter.anchor_at(env_bytes, integrated_time=when)
    claim = adapter.verify(env_bytes, receipt)
    assert claim.profile_id == "rfc3161-recorded-fixture"
    assert claim.precedes(datetime.fromisoformat(manifest["applicationDeadline"].replace("Z", "+00:00")))


def test_rfc3161_wrong_digest_fails(tsa_material: tuple[str, str, str]) -> None:
    private_pem, _, cert_pem = tsa_material
    manifest = sample_manifest(programId="rfc3161-negative")
    envelope, _salt = commit_manifest(manifest)
    env_bytes = envelope_bytes(envelope)
    adapter = Rfc3161Adapter(
        profile_id="rfc3161-recorded-fixture",
        fixture_private_key_pem=private_pem,
        fixture_certificate_pem=cert_pem,
        trust_root_pem=cert_pem,
    )
    receipt = adapter.anchor(env_bytes)
    receipt["envelopeDigestSha256"] = "00" * 32
    with pytest.raises(Phase2Error):
        adapter.verify(env_bytes, receipt)


def test_rfc3161_deadline_after_anchor_fails(tsa_material: tuple[str, str, str]) -> None:
    private_pem, _, cert_pem = tsa_material
    manifest = sample_manifest(
        programId="rfc3161-deadline",
        applicationDeadline="2026-01-01T00:00:00Z",
    )
    envelope, _salt = commit_manifest(manifest)
    env_bytes = envelope_bytes(envelope)
    adapter = Rfc3161Adapter(
        profile_id="rfc3161-recorded-fixture",
        fixture_private_key_pem=private_pem,
        fixture_certificate_pem=cert_pem,
        trust_root_pem=cert_pem,
    )
    when = datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
    receipt = adapter.anchor_at(env_bytes, integrated_time=when)
    claim = adapter.verify(env_bytes, receipt)
    deadline = datetime.fromisoformat("2026-01-01T00:00:00Z")
    assert not claim.precedes(deadline)
