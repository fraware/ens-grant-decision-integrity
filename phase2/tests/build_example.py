"""Write the public retrospective example and fixture keys. Test keys only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from attest import generate_test_ed25519, load_ed25519_private, attest_run  # noqa: E402
from canonicalize import canonicalize  # noqa: E402
from factories import (  # noqa: E402
    ANCHOR_TIME,
    generate_rekor_fixture_key,
    issue_fixture_receipt,
    layer_inputs,
    sample_manifest,
    sample_predicate,
    v01_record,
)
from envelope import build_envelope  # noqa: E402
from commitment import generate_salt  # noqa: E402
from graph import verify_graph  # noqa: E402
from replay import replay  # noqa: E402

PHASE2 = Path(__file__).resolve().parents[1]
VECTORS = PHASE2 / "vectors"
EXAMPLES = PHASE2 / "examples"
SOURCE_URI = (
    "https://github.com/fraware/ens-grant-decision-integrity/blob/"
    "main/phase2/examples/retrospective-public.bundle.json"
)


def main() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    VECTORS.mkdir(parents=True, exist_ok=True)
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    (VECTORS / "rekor-fixture-private.pem").write_text(private_pem, encoding="utf-8")
    (VECTORS / "rekor-fixture-trust-root.pem").write_text(public_pem, encoding="utf-8")

    manifest = sample_manifest()
    salt = generate_salt()
    envelope = build_envelope(manifest, salt)
    receipt = issue_fixture_receipt(envelope, private_pem=private_pem, integrated_time=ANCHOR_TIME)
    run_priv, run_pub = generate_test_ed25519()
    (VECTORS / "run-attestation-ed25519-private.pem").write_text(run_priv.decode("utf-8"), encoding="utf-8")
    (VECTORS / "run-attestation-ed25519-public.pem").write_text(run_pub.decode("utf-8"), encoding="utf-8")
    inputs = layer_inputs()
    predicate = sample_predicate(envelope["commitmentDigest"], inputs)
    attestation = attest_run(predicate, load_ed25519_private(run_priv))
    report = replay(
        attested_layer_digests=predicate["layerDigests"],
        layer_inputs=inputs,
        hosted_replayable=False,
        manifest_commitment_digest=envelope["commitmentDigest"],
    )
    record = v01_record(
        digest=envelope["commitmentDigest"],
        committed_at=receipt["anchoredAt"],
        reveal_status="revealed",
        manifest=manifest,
        source_uri=SOURCE_URI,
    )
    bundle = {
        "bundleVersion": "1",
        "envelope": envelope,
        "receipt": receipt,
        "revealStatus": "revealed",
        "manifest": manifest,
        "saltHex": salt.hex(),
        "selectiveAuditResult": None,
        "runAttestation": attestation,
        "runPublicKeyPem": run_pub.decode("utf-8"),
        "replayReport": report,
        "layerInputs": inputs,
        "decisionRecord": record,
        "notes": [
            "Fictional, non-evaluative retrospective example.",
            "Uses only public ENS forum URIs. No real applicant is identified or scored.",
            "Anchor is rekor-v1-recorded-fixture with a test-log key; not production Rekor inclusion.",
            "Hosted generation is not-replayable. Deterministic layers are exact-match.",
            "Test keys only. A real program must supply its own signing identity.",
            "AI output is advisory and cannot populate decision.authorityKind.",
        ],
    }
    out = EXAMPLES / "retrospective-public.bundle.json"
    out.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    result = verify_graph(bundle, trust_root_pem=public_pem)
    if not result.ok:
        raise SystemExit("example failed graph verification")
    rfc_sample = json.loads(
        '{"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27],'
        '"string":"\\u20ac$\\u000f\\nA\'B\\"\\\\\\\\\\"/",'
        '"literals":[null,true,false]}'
    )
    (VECTORS / "t1_rfc8785_section_322.jcs.txt").write_bytes(canonicalize(rfc_sample) + b"\n")
    print("wrote", out)
    print("established", result.established)


if __name__ == "__main__":
    main()
