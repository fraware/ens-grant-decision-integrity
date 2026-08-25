"""Rekor v2 offline verification and fail-closed adversarial tests."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from anchors.rekor_v2 import RekorV2Adapter, build_fixture_trust_policy, load_trust_policy
from envelope import envelope_bytes
from factories import generate_rekor_fixture_key
from support import Phase2Error

VECTORS = Path(__file__).resolve().parents[1] / "vectors" / "rekor-v2"


def _issue(private_pem: str, public_pem: str, *, when: datetime | None = None):
    policy = build_fixture_trust_policy(
        public_key_pem=public_pem,
        log_identity="ens-gdi-rekor-v2-fixture",
        shard="fixture",
    )
    adapter = RekorV2Adapter(
        profile_id="rekor-v2-recorded-fixture",
        trust_policy=policy,
        fixture_private_key_pem=private_pem,
    )
    envelope = {
        "envelopeType": "ens-gdi-evaluator-manifest-commitment",
        "programId": "demo",
        "roundId": "r1",
        "applicationDeadline": "2026-12-01T00:00:00Z",
        "commitmentAlgorithm": "sha256-salted-jcs-rfc8785-v1",
        "commitmentDigest": "ab" * 32,
    }
    # Minimal valid envelope for hashing via envelope_bytes requires full schema;
    # use factories when available. For unit tests, call adapter with raw bytes.
    raw = b'{"demo":true}'
    if when is None:
        receipt = adapter.anchor(raw)
    else:
        receipt = adapter.anchor_at(raw, integrated_time=when)
    return adapter, raw, receipt, policy


def test_fixture_receipt_verifies_offline() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    adapter, raw, receipt, _policy = _issue(private_pem, public_pem)
    claim = adapter.verify(raw, receipt)
    assert claim.profile_id == "rekor-v2-recorded-fixture"
    assert "production" not in claim.trust_boundary.lower() or "must not" in claim.trust_boundary.lower()
    assert receipt["verifierMaterial"]["logSubmissionSignature"]["role"] == "technical-log-submission-only"


def test_missing_trust_policy_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    _adapter, raw, receipt, _policy = _issue(private_pem, public_pem)
    bare = RekorV2Adapter(profile_id="rekor-v2-recorded-fixture", trust_policy=None)
    # Without fixture key or policy, verify must fail closed.
    with pytest.raises(Phase2Error) as exc:
        bare.verify(raw, receipt)
    assert exc.value.code == "RKR240"


def test_digest_substitution_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    adapter, raw, receipt, _ = _issue(private_pem, public_pem)
    with pytest.raises(Phase2Error) as exc:
        adapter.verify(b'{"tampered":true}', receipt)
    assert exc.value.code == "RKR255"


def test_wrong_log_identity_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    adapter, raw, receipt, policy = _issue(private_pem, public_pem)
    bad_policy = copy.deepcopy(policy)
    bad_policy["anchors"]["rekor-v2"]["logIdentity"] = "wrong-log"
    bad = RekorV2Adapter(
        profile_id="rekor-v2-recorded-fixture",
        trust_policy=bad_policy,
        fixture_private_key_pem=private_pem,
    )
    with pytest.raises(Phase2Error) as exc:
        bad.verify(raw, receipt)
    assert exc.value.code == "RKR257"


def test_wrong_shard_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    adapter, raw, receipt, policy = _issue(private_pem, public_pem)
    bad_policy = copy.deepcopy(policy)
    bad_policy["anchors"]["rekor-v2"]["shard"] = "other-shard"
    bad = RekorV2Adapter(
        profile_id="rekor-v2-recorded-fixture",
        trust_policy=bad_policy,
        fixture_private_key_pem=private_pem,
    )
    with pytest.raises(Phase2Error) as exc:
        bad.verify(raw, receipt)
    assert exc.value.code == "RKR258"


def test_untrusted_log_key_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    other_private, other_public = generate_rekor_fixture_key()
    adapter, raw, receipt, _ = _issue(private_pem, public_pem)
    bad_policy = build_fixture_trust_policy(
        public_key_pem=other_public,
        log_identity="ens-gdi-rekor-v2-fixture",
        shard="fixture",
    )
    bad = RekorV2Adapter(
        profile_id="rekor-v2-recorded-fixture",
        trust_policy=bad_policy,
        fixture_private_key_pem=other_private,
    )
    with pytest.raises(Phase2Error):
        bad.verify(raw, receipt)


def test_expired_trust_policy_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    adapter, raw, receipt, policy = _issue(
        private_pem,
        public_pem,
        when=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    bad_policy = copy.deepcopy(policy)
    bad_policy["anchors"]["rekor-v2"]["validUntil"] = "2020-01-01T00:00:00Z"
    bad = RekorV2Adapter(
        profile_id="rekor-v2-recorded-fixture",
        trust_policy=bad_policy,
        fixture_private_key_pem=private_pem,
    )
    with pytest.raises(Phase2Error) as exc:
        bad.verify(raw, receipt)
    assert exc.value.code == "RKR246"


def test_receipt_trust_substitution_rejected() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    adapter, raw, receipt, _ = _issue(private_pem, public_pem)
    mutated = copy.deepcopy(receipt)
    mutated["verifierMaterial"]["trustRootPem"] = public_pem
    with pytest.raises(Phase2Error) as exc:
        adapter.verify(raw, mutated)
    # Fail-closed either via schema additionalProperties or explicit RKR247.
    assert exc.value.code in {"RKR247", "SCHEMA002"}


def test_inclusion_root_mismatch_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    adapter, raw, receipt, _ = _issue(private_pem, public_pem)
    mutated = copy.deepcopy(receipt)
    mutated["verifierMaterial"]["inclusionProof"]["rootHash"] = "00" * 32
    with pytest.raises(Phase2Error):
        adapter.verify(raw, mutated)


def test_production_online_anchors_fail_closed() -> None:
    adapter = RekorV2Adapter(profile_id="rekor-v2", trust_policy=None)
    with pytest.raises(Phase2Error) as exc:
        adapter.anchor(b"{}")
    assert exc.value.code == "RKR250"


def test_production_rejects_fixture_receipt_profile_mismatch() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    _adapter, raw, receipt, policy = _issue(private_pem, public_pem)
    prod = RekorV2Adapter(profile_id="rekor-v2", trust_policy=policy)
    with pytest.raises(Phase2Error) as exc:
        prod.verify(raw, receipt)
    assert exc.value.code == "RKR252"


def test_load_trust_policy_requires_external_pin() -> None:
    with pytest.raises(Phase2Error) as exc:
        load_trust_policy(None)
    assert exc.value.code == "RKR240"


def test_vectors_dir_placeholder() -> None:
    VECTORS.mkdir(parents=True, exist_ok=True)
    readme = VECTORS / "README.md"
    if not readme.is_file():
        readme.write_text(
            "# Rekor v2 vectors\n\nNon-production fixtures only. Do not treat these as Sigstore production evidence.\n",
            encoding="utf-8",
        )
    assert readme.is_file()
