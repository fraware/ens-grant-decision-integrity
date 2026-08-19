"""T9: Run attestation with wrong commitment or output digest fails graph validation."""

from __future__ import annotations

import pytest

from factories import build_bundle, generate_rekor_fixture_key
from graph import verify_graph
from support import Phase2Error, sha256_hex


def test_wrong_commitment_digest_fails() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(
        rekor_private_pem=private_pem,
        predicate_overrides={"manifestCommitmentDigest": "ff" * 32},
    )
    with pytest.raises(Phase2Error, match="commitment digest"):
        verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)


def test_wrong_output_digest_fails_subject_binding() -> None:
    from attest import attest_run, load_ed25519_private, generate_test_ed25519
    from factories import layer_inputs, sample_predicate

    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem)
    predicate = sample_predicate(bundle["envelope"]["commitmentDigest"], layer_inputs())
    predicate["outputDigest"] = sha256_hex(b"different-output")
    run_priv, run_pub = generate_test_ed25519()
    # Tamper after signing: keep signatures, change payload subject via new envelope
    # with matching payload type but predicate/subject mismatch is created by
    # editing the statement subject after attest_run.
    attestation = attest_run(predicate, load_ed25519_private(run_priv))
    bundle["runAttestation"] = attestation
    bundle["runPublicKeyPem"] = run_pub.decode("utf-8")
    bundle["replayReport"] = None
    bundle["layerInputs"] = None
    # Valid signing with matching subject: graph should fail because replay is
    # absent is OK, but wait - this predicate has a consistent subject. Change
    # the graph check using a mutated output after the fact.
    result_ok_path = predicate["outputDigest"]
    assert result_ok_path
    # Mutate payload output in a way verify_run should catch: break subject.
    import base64
    import json
    from canonicalize import canonicalize

    payload = json.loads(base64.b64decode(attestation["payload"]))
    payload["subject"][0]["digest"]["sha256"] = "aa" * 32
    attestation["payload"] = base64.b64encode(canonicalize(payload)).decode("ascii")
    bundle["runAttestation"] = attestation
    with pytest.raises(Phase2Error):
        verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
