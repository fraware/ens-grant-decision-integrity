#!/usr/bin/env python3
"""Phase II CLI. Mechanism-first names. Prints claim ceilings, not aspirations."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from anchors.base import select_adapter  # noqa: E402
from attest import attest_run, load_ed25519_private, load_ed25519_public, verify_run  # noqa: E402
from claims import CLAIM_BY_ID, NON_CLAIMS  # noqa: E402
from envelope import commit_manifest, envelope_bytes  # noqa: E402
from graph import verify_graph  # noqa: E402
from replay import replay  # noqa: E402
from reveal import verify_reveal  # noqa: E402
from support import Phase2Error, VerificationResult  # noqa: E402


def _load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str, value: Any) -> None:
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _print_result(result: VerificationResult | dict[str, Any]) -> None:
    payload = result.as_dict() if isinstance(result, VerificationResult) else result
    print(json.dumps(payload, indent=2))
    print("---")
    print("Non-claims:")
    for line in NON_CLAIMS:
        print(f"- {line}")


def _fail(exc: Phase2Error) -> int:
    payload = {
        "ok": False,
        "error": str(exc),
        "code": exc.code,
        "claim": exc.claim,
        "nonClaims": list(NON_CLAIMS),
    }
    print(json.dumps(payload, indent=2))
    print("---")
    print("Non-claims:")
    for line in NON_CLAIMS:
        print(f"- {line}")
    return 1


def cmd_commit(args: argparse.Namespace) -> int:
    manifest = _load_json(args.manifest)
    envelope, salt = commit_manifest(manifest)
    _write_json(args.out_envelope, envelope)
    _write_json(args.out_salt, {"saltHex": salt.hex(), "domain": "ens-gdi/evaluator-manifest/v1"})
    _print_result(
        {
            "ok": True,
            "established": [],
            "failed": [],
            "details": {
                "note": "Local digest construction only. No C1-C6 until later checks succeed.",
                "commitmentDigest": envelope["commitmentDigest"],
            },
            "nonClaims": list(NON_CLAIMS),
        }
    )
    return 0


def cmd_anchor(args: argparse.Namespace) -> int:
    fixture_time_profiles = {
        "rekor-v1-recorded-fixture",
        "rfc3161-recorded-fixture",
        "ethereum-calldata-fixture",
    }
    if args.at and args.profile not in fixture_time_profiles:
        raise Phase2Error("--at is only valid for recorded fixture profiles", code="CLI008")
    if args.tx_hash and args.profile != "ethereum-calldata-fixture":
        raise Phase2Error("--tx-hash is only valid for ethereum-calldata-fixture", code="CLI009")
    if args.tsa_cert and args.profile != "rfc3161-recorded-fixture":
        raise Phase2Error("--tsa-cert is only valid for rfc3161-recorded-fixture", code="CLI010")
    if args.artifact_key and args.profile not in {"rekor-v1", "rekor-v1-recorded-fixture"}:
        raise Phase2Error("--artifact-key is only valid for Rekor profiles", code="CLI011")

    envelope = _load_json(args.envelope)
    env_bytes = envelope_bytes(envelope)
    kwargs: dict[str, Any] = {}
    if args.profile == "rekor-v1-recorded-fixture":
        if not args.fixture_key:
            raise Phase2Error("rekor-v1-recorded-fixture requires --fixture-key", code="CLI001")
        kwargs["fixture_private_key_pem"] = Path(args.fixture_key).read_text(encoding="utf-8")
        if args.artifact_key:
            kwargs["artifact_private_key_pem"] = Path(args.artifact_key).read_text(encoding="utf-8")
        adapter = select_adapter(args.profile, **kwargs)
        if args.at:
            when = datetime.fromisoformat(args.at.replace("Z", "+00:00")).astimezone(timezone.utc)
            receipt = adapter.anchor_at(env_bytes, integrated_time=when)  # type: ignore[attr-defined]
        else:
            receipt = adapter.anchor(env_bytes)
    elif args.profile in {"rfc3161", "rfc3161-recorded-fixture"}:
        if not args.trust_root:
            raise Phase2Error(f"{args.profile} requires --trust-root", code="CLI005")
        kwargs["trust_root_pem"] = Path(args.trust_root).read_text(encoding="utf-8")
        if args.profile == "rfc3161-recorded-fixture":
            if not args.fixture_key:
                raise Phase2Error("rfc3161-recorded-fixture requires --fixture-key", code="CLI004")
            if not args.tsa_cert:
                raise Phase2Error("rfc3161-recorded-fixture issuance requires --tsa-cert", code="CLI006")
            kwargs["fixture_private_key_pem"] = Path(args.fixture_key).read_text(encoding="utf-8")
            kwargs["fixture_certificate_pem"] = Path(args.tsa_cert).read_text(encoding="utf-8")
        adapter = select_adapter(args.profile, **kwargs)
        if args.profile == "rfc3161-recorded-fixture" and args.at:
            when = datetime.fromisoformat(args.at.replace("Z", "+00:00")).astimezone(timezone.utc)
            receipt = adapter.anchor_at(env_bytes, integrated_time=when)  # type: ignore[attr-defined]
        else:
            receipt = adapter.anchor(env_bytes)
    elif args.profile == "ethereum-calldata-fixture":
        adapter = select_adapter(args.profile, **kwargs)
        when = (
            datetime.fromisoformat(args.at.replace("Z", "+00:00")).astimezone(timezone.utc)
            if args.at
            else datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        receipt = adapter.anchor_fixture(  # type: ignore[attr-defined]
            env_bytes,
            tx_hash=args.tx_hash or "0xillustrative0000000000000000000000000000000000000000000000000001",
            block_timestamp=when,
        )
    elif args.profile == "ethereum":
        adapter = select_adapter(args.profile, **kwargs)
        receipt = adapter.anchor(env_bytes)
    else:
        if args.artifact_key:
            kwargs["artifact_private_key_pem"] = Path(args.artifact_key).read_text(encoding="utf-8")
        adapter = select_adapter(args.profile, **kwargs)
        receipt = adapter.anchor(env_bytes)
    _write_json(args.out, receipt)
    _print_result(
        {
            "ok": True,
            "established": [],
            "failed": [],
            "details": {
                "note": "Submission recorded. C2 is not established until verify-commitment succeeds.",
                "profileId": receipt["profileId"],
                "anchoredAt": receipt["anchoredAt"],
                "anchorId": receipt["anchorId"],
            },
            "nonClaims": list(NON_CLAIMS),
        }
    )
    return 0


def cmd_verify_commitment(args: argparse.Namespace) -> int:
    if bool(args.manifest) != bool(args.salt):
        raise Phase2Error("--manifest and --salt must be supplied together", code="CLI007", claim="C1")

    envelope = _load_json(args.envelope)
    receipt = _load_json(args.receipt)
    kwargs: dict[str, Any] = {}
    if args.fixture_key:
        kwargs["fixture_private_key_pem"] = Path(args.fixture_key).read_text(encoding="utf-8")
    if args.trust_root:
        kwargs["trust_root_pem"] = Path(args.trust_root).read_text(encoding="utf-8")
    adapter = select_adapter(receipt["profileId"], **kwargs)
    claim = adapter.verify(envelope_bytes(envelope), receipt)
    deadline = datetime.fromisoformat(envelope["applicationDeadline"].replace("Z", "+00:00"))
    if not claim.precedes(deadline):
        raise Phase2Error("anchor time is not strictly before applicationDeadline", code="CLI002", claim="C2")
    established = ["C2", "C3"]
    details = {
        "C2": CLAIM_BY_ID["C2"],
        "C3": CLAIM_BY_ID["C3"],
        "trustBoundary": claim.trust_boundary,
    }
    if args.manifest and args.salt:
        salt_obj = _load_json(args.salt)
        reveal = verify_reveal(
            envelope=envelope,
            reveal_status="revealed",
            manifest=_load_json(args.manifest),
            salt=bytes.fromhex(salt_obj["saltHex"]),
        )
        established = reveal.established + [cid for cid in established if cid not in reveal.established]
        details.update(reveal.details)
    _print_result(VerificationResult(ok=True, established=established, details=details))
    return 0


def cmd_reveal(args: argparse.Namespace) -> int:
    envelope = _load_json(args.envelope)
    salt_obj = _load_json(args.salt)
    result = verify_reveal(
        envelope=envelope,
        reveal_status="revealed",
        manifest=_load_json(args.manifest),
        salt=bytes.fromhex(salt_obj["saltHex"]),
    )
    _print_result(result)
    return 0


def cmd_attest_run(args: argparse.Namespace) -> int:
    predicate = _load_json(args.predicate)
    key = load_ed25519_private(Path(args.key).read_text(encoding="utf-8"))
    envelope = attest_run(predicate, key)
    _write_json(args.out, envelope)
    _print_result(
        {
            "ok": True,
            "established": [],
            "failed": [],
            "details": {
                "note": "Local DSSE wrapping of an assertion. C4 is not established until verify-run succeeds."
            },
            "nonClaims": list(NON_CLAIMS),
        }
    )
    return 0


def cmd_verify_run(args: argparse.Namespace) -> int:
    statement = verify_run(
        _load_json(args.attestation),
        load_ed25519_public(Path(args.public_key).read_text(encoding="utf-8")),
    )
    _print_result(
        VerificationResult(
            ok=True,
            established=["C4"],
            details={"C4": CLAIM_BY_ID["C4"], "predicateType": statement["predicateType"]},
        )
    )
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    attestation = _load_json(args.attestation)
    public_key = load_ed25519_public(Path(args.public_key).read_text(encoding="utf-8"))
    statement = verify_run(attestation, public_key)
    layer_inputs = _load_json(args.layer_inputs)
    report = replay(
        attested_layer_digests=statement["predicate"]["layerDigests"],
        layer_inputs=layer_inputs,
        hosted_replayable=args.hosted_replayable,
        manifest_commitment_digest=statement["predicate"]["manifestCommitmentDigest"],
    )
    _write_json(args.out, report)
    _print_result(
        {
            "ok": True,
            "established": [],
            "failed": [],
            "details": {
                "note": "Local canonical artifact-recomputation outcomes. C5 is not established until verify-graph accepts the report.",
                "reportVersion": report["reportVersion"],
                "outcomes": {item["layerId"]: item["outcome"] for item in report["layers"]},
            },
            "nonClaims": list(NON_CLAIMS),
        }
    )
    return 0


def cmd_verify_graph(args: argparse.Namespace) -> int:
    kwargs: dict[str, Any] = {}
    if args.fixture_key:
        kwargs["fixture_private_key_pem"] = Path(args.fixture_key).read_text(encoding="utf-8")
    if args.trust_root:
        kwargs["trust_root_pem"] = Path(args.trust_root).read_text(encoding="utf-8")
    result = verify_graph(_load_json(args.bundle), **kwargs)
    _print_result(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase II evaluator-manifest commitment, anchor, attest, and replay-evidence tools."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    commit = sub.add_parser("commit", help="Construct envelope and salt (local only).")
    commit.add_argument("--manifest", required=True)
    commit.add_argument("--out-envelope", required=True)
    commit.add_argument("--out-salt", required=True)
    commit.set_defaults(func=cmd_commit)

    anchor = sub.add_parser("anchor", help="Submit envelope to an anchor profile.")
    anchor.add_argument("--envelope", required=True)
    anchor.add_argument(
        "--profile",
        required=True,
        choices=[
            "rekor-v1",
            "rekor-v1-recorded-fixture",
            "rfc3161",
            "rfc3161-recorded-fixture",
            "ethereum",
            "ethereum-calldata-fixture",
        ],
    )
    anchor.add_argument("--fixture-key")
    anchor.add_argument("--artifact-key")
    anchor.add_argument("--trust-root")
    anchor.add_argument("--tsa-cert", help="TSA certificate PEM for rfc3161-recorded-fixture issuance.")
    anchor.add_argument("--tx-hash", help="Transaction hash for ethereum-calldata-fixture.")
    anchor.add_argument("--at", help="RFC 3339 time for recorded-fixture receipts only.")
    anchor.add_argument("--out", required=True)
    anchor.set_defaults(func=cmd_anchor)

    verify_c = sub.add_parser("verify-commitment", help="Verify envelope against a receipt.")
    verify_c.add_argument("--envelope", required=True)
    verify_c.add_argument("--receipt", required=True)
    verify_c.add_argument("--manifest")
    verify_c.add_argument("--salt")
    verify_c.add_argument("--fixture-key")
    verify_c.add_argument("--trust-root")
    verify_c.set_defaults(func=cmd_verify_commitment)

    reveal = sub.add_parser("reveal", help="Open a commitment with manifest and salt.")
    reveal.add_argument("--envelope", required=True)
    reveal.add_argument("--manifest", required=True)
    reveal.add_argument("--salt", required=True)
    reveal.set_defaults(func=cmd_reveal)

    attest = sub.add_parser("attest-run", help="Wrap a run predicate in DSSE.")
    attest.add_argument("--predicate", required=True)
    attest.add_argument("--key", required=True)
    attest.add_argument("--out", required=True)
    attest.set_defaults(func=cmd_attest_run)

    verify_r = sub.add_parser("verify-run", help="Verify a DSSE run attestation.")
    verify_r.add_argument("--attestation", required=True)
    verify_r.add_argument("--public-key", required=True)
    verify_r.set_defaults(func=cmd_verify_run)

    replay_cmd = sub.add_parser("replay", help="Recompute canonical layer-artifact outcomes.")
    replay_cmd.add_argument("--attestation", required=True)
    replay_cmd.add_argument("--public-key", required=True)
    replay_cmd.add_argument("--layer-inputs", required=True)
    replay_cmd.add_argument("--hosted-replayable", action="store_true")
    replay_cmd.add_argument("--out", required=True)
    replay_cmd.set_defaults(func=cmd_replay)

    graph = sub.add_parser("verify-graph", help="Verify a Phase II evidence bundle.")
    graph.add_argument("--bundle", required=True)
    graph.add_argument("--fixture-key")
    graph.add_argument("--trust-root")
    graph.set_defaults(func=cmd_verify_graph)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Phase2Error as exc:
        return _fail(exc)
    except NotImplementedError as exc:
        return _fail(Phase2Error(str(exc), code="CLI003"))


if __name__ == "__main__":
    raise SystemExit(main())
