"""T7: Corrupted inclusion proof or mismatched digest fails.

Uses rekor-v1-recorded-fixture receipts so the suite does not depend on live
Sigstore availability. A recorded-from-live hashedrekord, when present, is
checked separately against the pinned production key.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from anchors.ethereum import EthereumAdapter
from anchors.rekor import RekorAdapter
from envelope import envelope_bytes
from factories import build_bundle, generate_rekor_fixture_key
from graph import verify_graph
from support import Phase2Error

VECTORS = Path(__file__).resolve().parents[1] / "vectors"


def test_corrupted_inclusion_root_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()

    def corrupt(receipt: dict) -> dict:
        mutated = copy.deepcopy(receipt)
        mutated["verifierMaterial"]["inclusionProof"]["rootHash"] = "00" * 32
        return mutated

    bundle = build_bundle(rekor_private_pem=private_pem, corrupt_receipt=corrupt)
    with pytest.raises(Phase2Error):
        verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)


def test_mismatched_envelope_digest_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    bundle["receipt"]["envelopeDigestSha256"] = "ab" * 32
    with pytest.raises(Phase2Error, match="digest"):
        verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)


def test_valid_fixture_receipt_verifies() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    adapter = RekorAdapter(
        profile_id="rekor-v1-recorded-fixture",
        fixture_private_key_pem=private_pem,
        trust_root_pem=public_pem,
    )
    adapter.verify(envelope_bytes(bundle["envelope"]), bundle["receipt"])


def test_ethereum_live_is_unimplemented() -> None:
    with pytest.raises(NotImplementedError, match="Ethereum"):
        EthereumAdapter(profile_id="ethereum").anchor(b"{}")


def test_recorded_from_live_rekor_if_present() -> None:
    path = VECTORS / "rekor-live-hashedrekord.json"
    if not path.is_file():
        pytest.skip("no recorded-from-live Rekor fixture; T7 uses recorded-fixture receipts")
    recorded = json.loads(path.read_text(encoding="utf-8"))
    adapter = RekorAdapter(profile_id="rekor-v1")
    envelope = recorded["envelopeBytesUtf8"].encode("utf-8")
    adapter.verify(envelope, recorded["receipt"])
