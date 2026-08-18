"""Evidence-bundle graph verifier and v0.1 linkage.

Never copies Phase II fields into decision.authorityKind.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from typing import Any

from anchors.base import select_adapter
from attest import load_ed25519_public, verify_run
from claims import (
    C1_ID,
    C2_ESTABLISHED,
    C2_ID,
    C3_ESTABLISHED,
    C3_ID,
    C4_ESTABLISHED,
    C4_ID,
    C5_ESTABLISHED,
    C5_ID,
    C6_ESTABLISHED,
    C6_ID,
    CLAIM_BY_ID,
    FORBIDDEN_AUTHORITY_KEYS,
    V01_COMMITMENT_ALGORITHM,
)
from envelope import envelope_bytes
from replay import verify_replay_report
from reveal import map_v01_reveal_status, verify_reveal
from support import PHASE2_ROOT, VECTOR_DIR, Phase2Error, VerificationResult, validate_schema

REPO_ROOT = PHASE2_ROOT.parent
V01_SCHEMA_PATH = REPO_ROOT / "schema" / "grant-decision-record.schema.json"


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _scan_forbidden(value: Any, *, path: str, hits: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}"
            if key in FORBIDDEN_AUTHORITY_KEYS:
                hits.append(child)
            _scan_forbidden(item, path=child, hits=hits)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_forbidden(item, path=f"{path}[{index}]", hits=hits)


def assert_phase2_has_no_authority_fields(bundle: dict[str, Any]) -> None:
    hits: list[str] = []
    for key, value in bundle.items():
        if key == "decisionRecord":
            continue
        _scan_forbidden(value, path=f"$.{key}", hits=hits)
    if hits:
        raise Phase2Error(
            "Phase II objects must not contain decision-authority fields: " + ", ".join(hits),
            code="AUTH-P2",
            claim="C6",
        )


def refuse_populate_authority_kind(_source: Any, decision_record: dict[str, Any]) -> None:
    """Explicit refusal: Phase II objects cannot populate v0.1 decision.authorityKind."""
    raise Phase2Error(
        "Phase II objects cannot populate decision.authorityKind; AI has no funding authority",
        code="AUTH-P2",
        claim="C6",
    )


def fill_v01_evaluator_manifest(
    record: dict[str, Any],
    *,
    digest: str,
    committed_at: str,
    reveal_status: str,
    models: list[dict[str, Any]],
    human_review_policy: str,
    reveal_uri: str | None = None,
    source_uri: str | None = None,
) -> dict[str, Any]:
    """Project Phase II outputs onto the existing v0.1 evaluatorManifest envelope.

    Does not read or write decision.authorityKind. Uses algorithm "other" because
    v0.1 has no salted-JCS identifier; "sha256" would describe a different function.
    """
    updated = copy.deepcopy(record)
    v01_status = map_v01_reveal_status(reveal_status)
    manifest = {
        "manifestVersion": "1",
        "commitment": {
            "algorithm": V01_COMMITMENT_ALGORITHM,
            "digest": digest,
            "committedAt": committed_at,
        },
        "revealStatus": v01_status,
        "revealUri": reveal_uri if v01_status == "revealed" else None,
        "models": [
            {
                "provider": model["provider"],
                "model": model["model"],
                "version": model.get("version"),
            }
            for model in models
        ],
        "humanReviewPolicy": human_review_policy,
    }
    if v01_status == "revealed" and not reveal_uri:
        raise Phase2Error("v0.1 revealed status requires revealUri", code="LNK001")
    updated["evaluatorManifest"] = manifest
    if source_uri:
        integrity = dict(updated.get("integrity") or {})
        integrity["sourceUri"] = source_uri
        updated["integrity"] = integrity
    return updated


def _validate_v01_record(record: dict[str, Any]) -> None:
    schema = json.loads(V01_SCHEMA_PATH.read_text(encoding="utf-8"))
    import jsonschema

    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        path = "/".join(str(p) for p in first.absolute_path) or "<root>"
        raise Phase2Error(f"v0.1 decision record failed schema at {path}: {first.message}", code="LNK002")


def _check_v01_linkage(
    record: dict[str, Any],
    *,
    digest: str,
    committed_at: str,
    reveal_status: str,
) -> None:
    _validate_v01_record(record)
    manifest = record.get("evaluatorManifest")
    if not manifest:
        raise Phase2Error("v0.1 record missing evaluatorManifest required for Phase II linkage", code="LNK003")
    algorithm = manifest.get("commitment", {}).get("algorithm")
    if algorithm == "sha256":
        raise Phase2Error(
            "v0.1 commitment.algorithm must not be sha256 for a salted JCS digest; use other",
            code="LNK004",
        )
    if algorithm != V01_COMMITMENT_ALGORITHM:
        raise Phase2Error("v0.1 commitment.algorithm must be other for Phase II linkage", code="LNK005")
    if manifest.get("commitment", {}).get("digest") != digest:
        raise Phase2Error("v0.1 commitment.digest does not match Phase II digest", code="LNK006")
    if manifest.get("commitment", {}).get("committedAt") != committed_at:
        raise Phase2Error("v0.1 committedAt is not the verified anchor time", code="LNK007")
    expected_status = map_v01_reveal_status(reveal_status)
    if manifest.get("revealStatus") != expected_status:
        raise Phase2Error("v0.1 revealStatus does not map from Phase II reveal state", code="LNK008")
    kind = record.get("decision", {}).get("authorityKind")
    if kind == "ai":
        raise Phase2Error("v0.1 decision.authorityKind must not be ai", code="LNK009", claim="C6")


def verify_graph(
    bundle: dict[str, Any],
    *,
    fixture_private_key_pem: str | bytes | None = None,
    trust_root_pem: str | None = None,
) -> VerificationResult:
    validate_schema(bundle, "evidence-bundle.schema.json")
    authority_before = copy.deepcopy(bundle.get("decisionRecord", {}).get("decision", {}).get("authorityKind"))
    assert_phase2_has_no_authority_fields(bundle)

    envelope = bundle["envelope"]
    receipt = bundle["receipt"]
    env_bytes = envelope_bytes(envelope)
    adapter_kwargs: dict[str, Any] = {}
    if receipt["profileId"] == "rekor-v1-recorded-fixture":
        default_root = VECTOR_DIR / "rekor-fixture-trust-root.pem"
        if fixture_private_key_pem:
            adapter_kwargs["fixture_private_key_pem"] = fixture_private_key_pem
        if trust_root_pem:
            adapter_kwargs["trust_root_pem"] = trust_root_pem
        elif default_root.is_file():
            adapter_kwargs["trust_root_pem"] = default_root.read_text(encoding="utf-8")
        elif "fixture_private_key_pem" not in adapter_kwargs:
            raise Phase2Error(
                "recorded-fixture graph verify requires the test-log public or private key",
                code="GRP001",
            )
    adapter = select_adapter(receipt["profileId"], **adapter_kwargs)
    claim = adapter.verify(env_bytes, receipt)
    deadline = _parse_dt(envelope["applicationDeadline"])
    established = [C2_ID, C3_ID]
    details: dict[str, Any] = {
        C2_ID: C2_ESTABLISHED,
        C3_ID: C3_ESTABLISHED,
        "trustBoundary": claim.trust_boundary,
        "anchoredAt": receipt["anchoredAt"],
        "profileId": receipt["profileId"],
    }
    if not claim.precedes(deadline):
        raise Phase2Error(
            "anchor time is not strictly before applicationDeadline",
            code="GRP002",
            claim="C2",
        )

    reveal_status = bundle["revealStatus"]
    salt = bytes.fromhex(bundle["saltHex"]) if bundle.get("saltHex") else None
    reveal_result = verify_reveal(
        envelope=envelope,
        reveal_status=reveal_status,
        manifest=bundle.get("manifest"),
        salt=salt,
    )
    established.extend(cid for cid in reveal_result.established if cid not in established)
    details.update(reveal_result.details)

    statement = None
    if bundle.get("runAttestation"):
        if not bundle.get("runPublicKeyPem"):
            raise Phase2Error("run attestation present without runPublicKeyPem", code="GRP003", claim="C4")
        public_key = load_ed25519_public(bundle["runPublicKeyPem"])
        statement = verify_run(bundle["runAttestation"], public_key)
        predicate = statement["predicate"]
        if predicate["manifestCommitmentDigest"] != envelope["commitmentDigest"]:
            raise Phase2Error("run predicate commitment digest does not match envelope", code="GRP004", claim="C4")
        if predicate["programId"] != envelope["programId"] or predicate["roundId"] != envelope["roundId"]:
            raise Phase2Error("run predicate round fields do not match envelope", code="GRP005", claim="C4")
        established.append(C4_ID)
        details[C4_ID] = C4_ESTABLISHED

    if bundle.get("replayReport"):
        if statement is None:
            raise Phase2Error("replay report requires a verified run attestation", code="GRP006", claim="C5")
        hosted_replayable = False
        if bundle.get("manifest"):
            hosted_replayable = any(model.get("replayable") for model in bundle["manifest"].get("models", []))
        verify_replay_report(
            bundle["replayReport"],
            attested_layer_digests=statement["predicate"]["layerDigests"],
            layer_inputs=bundle.get("layerInputs"),
            hosted_replayable=bool(hosted_replayable),
            manifest_commitment_digest=envelope["commitmentDigest"],
        )
        established.append(C5_ID)
        details[C5_ID] = C5_ESTABLISHED

    _check_v01_linkage(
        bundle["decisionRecord"],
        digest=envelope["commitmentDigest"],
        committed_at=receipt["anchoredAt"],
        reveal_status=reveal_status,
    )

    authority_after = bundle.get("decisionRecord", {}).get("decision", {}).get("authorityKind")
    if authority_after != authority_before:
        raise Phase2Error("graph verification mutated decision.authorityKind", code="GRP007", claim="C6")
    established.append(C6_ID)
    details[C6_ID] = C6_ESTABLISHED
    details["claims"] = {cid: CLAIM_BY_ID[cid] for cid in established}
    return VerificationResult(ok=True, established=established, details=details)
