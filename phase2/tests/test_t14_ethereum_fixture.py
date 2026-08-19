"""Tests for Ethereum calldata fixture profile."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from anchors.ethereum import EthereumAdapter
from envelope import commit_manifest, envelope_bytes
from factories import sample_manifest
from support import Phase2Error


def test_ethereum_fixture_anchor_and_verify() -> None:
    manifest = sample_manifest(programId="ethereum-fixture-test")
    envelope, _salt = commit_manifest(manifest)
    env_bytes = envelope_bytes(envelope)
    adapter = EthereumAdapter(profile_id="ethereum-calldata-fixture")
    when = datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
    receipt = adapter.anchor_fixture(
        env_bytes,
        tx_hash="0xillustrative0000000000000000000000000000000000000000000000000001",
        block_timestamp=when,
    )
    claim = adapter.verify(env_bytes, receipt)
    assert claim.profile_id == "ethereum-calldata-fixture"
    assert claim.precedes(datetime.fromisoformat(manifest["applicationDeadline"].replace("Z", "+00:00")))


def test_ethereum_live_not_implemented() -> None:
    adapter = EthereumAdapter(profile_id="ethereum")
    with pytest.raises(NotImplementedError):
        adapter.anchor(b"{}")
