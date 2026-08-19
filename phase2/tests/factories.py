"""Shared builders for Phase II tests. Test keys only."""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from anchors.rekor import RekorAdapter
from attest import attest_run, generate_test_ed25519, load_ed25519_private
from commitment import generate_salt
from envelope import build_envelope
from graph import fill_v01_evaluator_manifest
from replay import layer_digest, replay
from support import PHASE2_ROOT, sha256_hex

REPO_ROOT = PHASE2_ROOT.parent
MARKETPLACE = json.loads(
    (REPO_ROOT / "examples" / "spp3-marketplace-rfp.example.json").read_text(encoding="utf-8")
)

PUBLIC_FORUM = {
    "rfp": "https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263",
    "timeline": "https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309",
    "committee": "https://discuss.ens.domains/t/social-spp3-program-authorization-and-committee-model/22086",
    "ai_experiment": "https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939",
}

DEADLINE = "2026-08-05T23:59:00Z"
ANCHOR_TIME = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)


def sample_manifest(**overrides: Any) -> dict[str, Any]:
    manifest = {
        "manifestVersion": "1",
        "programId": "ens-gdi-phase2-retrospective-public",
        "roundId": "marketplace-like-illustrative-2026",
        "applicationDeadline": DEADLINE,
        "createdAt": "2026-07-15T00:00:00Z",
        "models": [
            {
                "provider": "hosted-generative-api",
                "model": "frontier-class-hosted",
                "version": "unspecified-hosted",
                "replayable": False,
            }
        ],
        "instructions": {
            "text": (
                "Illustrative screening instructions. Apply the published public rubric "
                "surfaces only. Do not invent applicant facts. Do not issue a funding decision."
            )
        },
        "retrieval": {
            "mode": "public-forum-uris-only",
            "sources": [
                PUBLIC_FORUM["rfp"],
                PUBLIC_FORUM["timeline"],
                PUBLIC_FORUM["committee"],
                PUBLIC_FORUM["ai_experiment"],
            ],
        },
        "tools": {"allowed": ["retrieve-public-uri"]},
        "parameters": {"temperature": "0", "maxTokens": "1024"},
        "aggregation": {"method": "single-hosted-draft-then-human-review"},
        "humanReviewPolicy": (
            "A human decision authority must review any AI draft. AI output is advisory "
            "and cannot approve, reject, suspend, or release funding."
        ),
        "canonicalization": "RFC8785",
    }
    manifest.update(overrides)
    return manifest


def issue_fixture_receipt(
    envelope: dict[str, Any],
    *,
    private_pem: str,
    integrated_time: datetime = ANCHOR_TIME,
) -> dict[str, Any]:
    from envelope import envelope_bytes

    adapter = RekorAdapter(
        profile_id="rekor-v1-recorded-fixture",
        fixture_private_key_pem=private_pem,
    )
    return adapter.anchor_at(envelope_bytes(envelope), integrated_time=integrated_time)


def generate_rekor_fixture_key() -> tuple[str, str]:
    key = ec.generate_private_key(ec.SECP256R1())
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


def layer_inputs() -> dict[str, Any]:
    return {
        "preprocessing": {"normalizedApplication": "illustrative-applicant", "policyUris": [PUBLIC_FORUM["timeline"]]},
        "retrieval-snapshot": {"uris": [PUBLIC_FORUM["rfp"], PUBLIC_FORUM["timeline"], PUBLIC_FORUM["committee"]]},
        "scoring": {"rubric": ["M1", "M2", "M3", "M4", "M5"], "scores": None, "note": "no real applicant scored"},
        "aggregation": {"method": "single-hosted-draft-then-human-review", "aggregate": None},
        "hosted-generation": {"draft": "not-replayable-hosted-output"},
    }


def attested_digests(inputs: dict[str, Any]) -> dict[str, str]:
    return {layer_id: layer_digest(value) for layer_id, value in inputs.items()}


def sample_predicate(digest: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    inputs = inputs or layer_inputs()
    digests = attested_digests(inputs)
    return {
        "manifestCommitmentDigest": digest,
        "programId": "ens-gdi-phase2-retrospective-public",
        "roundId": "marketplace-like-illustrative-2026",
        "operator": "illustrative-operator-test-key",
        "implementation": {
            "name": "ens-gdi-phase2-reference-replay",
            "digestSha256": sha256_hex(b"ens-gdi-phase2-reference-replay-v1"),
        },
        "inputSnapshots": {
            "applicationSha256": sha256_hex(b"illustrative-applicant"),
            "evidenceSha256": sha256_hex(PUBLIC_FORUM["rfp"].encode("utf-8")),
            "retrievalSha256": digests["retrieval-snapshot"],
        },
        "environment": {"note": "test harness; not a production evaluator host"},
        "outputDigest": sha256_hex(b"illustrative-advisory-draft-not-a-decision"),
        "humanReviewState": "pending-human-review",
        "layerDigests": digests,
    }


def v01_record(*, digest: str, committed_at: str, reveal_status: str, manifest: dict[str, Any], source_uri: str) -> dict[str, Any]:
    record = copy.deepcopy(MARKETPLACE)
    record["recordId"] = "illustrative-phase2-retrospective-public"
    record["evaluators"] = [
        {
            "evaluatorId": "committee",
            "displayName": "SPP3 Committee",
            "kind": "committee",
            "role": "evaluation and award recommendation",
            "participated": False,
            "recused": False,
            "recusalReason": None,
        },
        {
            "evaluatorId": "hosted-screener",
            "displayName": "Illustrative hosted screening model",
            "kind": "ai",
            "role": "advisory screen",
            "participated": True,
            "recused": False,
            "recusalReason": None,
            "materiallyInformedRecommendation": True,
        },
    ]
    record["notes"] = [
        "Fictional Phase II retrospective example. Not an evaluation of any real applicant.",
        "Anchor is a rekor-v1-recorded-fixture receipt, not production Rekor inclusion.",
        "Hosted generation is not-replayable. Deterministic layers are exact-match.",
        "AI output is advisory. Decision authority remains human-governed and pending.",
    ]
    reveal_uri = source_uri if reveal_status == "revealed" else None
    return fill_v01_evaluator_manifest(
        record,
        digest=digest,
        committed_at=committed_at,
        reveal_status=reveal_status,
        models=manifest["models"],
        human_review_policy=manifest["humanReviewPolicy"],
        reveal_uri=reveal_uri,
        source_uri=source_uri,
    )


def build_bundle(
    *,
    rekor_private_pem: str,
    reveal_status: str = "revealed",
    integrated_time: datetime = ANCHOR_TIME,
    mutate_manifest: dict[str, Any] | None = None,
    salt: bytes | None = None,
    include_run: bool = True,
    include_replay: bool = True,
    predicate_overrides: dict[str, Any] | None = None,
    corrupt_receipt: Any | None = None,
) -> dict[str, Any]:
    manifest = sample_manifest(**(mutate_manifest or {}))
    salt = salt or generate_salt()
    envelope = build_envelope(manifest, salt)
    receipt = issue_fixture_receipt(envelope, private_pem=rekor_private_pem, integrated_time=integrated_time)
    if callable(corrupt_receipt):
        receipt = corrupt_receipt(receipt)
    private_pem, public_pem = generate_test_ed25519()
    inputs = layer_inputs()
    predicate = sample_predicate(envelope["commitmentDigest"], inputs)
    if predicate_overrides:
        predicate.update(predicate_overrides)
        if "layerDigests" not in predicate_overrides:
            pass
    attestation = None
    replay_report = None
    if include_run:
        attestation = attest_run(predicate, load_ed25519_private(private_pem))
        if include_replay:
            replay_report = replay(
                attested_layer_digests=predicate["layerDigests"],
                layer_inputs=inputs,
                hosted_replayable=False,
                manifest_commitment_digest=envelope["commitmentDigest"],
            )
    source_uri = (
        "https://github.com/fraware/ens-grant-decision-integrity/blob/"
        "phase-ii-evaluator-provenance/phase2/examples/retrospective-public.bundle.json"
    )
    record = v01_record(
        digest=envelope["commitmentDigest"],
        committed_at=receipt["anchoredAt"],
        reveal_status=reveal_status,
        manifest=manifest,
        source_uri=source_uri,
    )
    bundle = {
        "bundleVersion": "1",
        "envelope": envelope,
        "receipt": receipt,
        "revealStatus": reveal_status,
        "manifest": manifest if reveal_status != "withheld" else None,
        "saltHex": salt.hex() if reveal_status != "withheld" else None,
        "selectiveAuditResult": None,
        "runAttestation": attestation,
        "runPublicKeyPem": public_pem.decode("utf-8") if include_run else None,
        "replayReport": replay_report,
        "layerInputs": inputs if include_replay else None,
        "decisionRecord": record,
        "notes": [
            "Test or example bundle. Test keys only.",
            "Does not evaluate a real applicant.",
        ],
    }
    return bundle
