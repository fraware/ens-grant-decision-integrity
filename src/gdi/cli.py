"""gdi command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from gdi import __version__
from gdi.bundle import BundleError, verify_bundle
from gdi.claims import ClaimRegistryError, lookup
from gdi.core.conformance import validate_record
from gdi.exit_codes import INTERNAL_ERROR, OK, USAGE_ERROR
from gdi.report import render_text
from gdi.source.artifact import SourceArtifactError, verify_artifact
from gdi.trust.policy import TrustPolicyError, load_trust_policy


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gdi", description="ENS Grant Decision Integrity verifier")
    parser.add_argument("--version", action="version", version=f"gdi {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    verify_record = sub.add_parser("verify-record", help="validate a decision record")
    verify_record.add_argument("record", type=Path)

    verify_source = sub.add_parser("verify-source", help="verify source artifact bytes")
    verify_source.add_argument("--metadata", type=Path, required=True)
    verify_source.add_argument("--file", type=Path, required=True)

    claims = sub.add_parser("claims", help="look up a claim registry entry")
    claims.add_argument("--id", required=True)

    trust = sub.add_parser("trust-policy", help="validate an external trust policy")
    trust.add_argument("policy", type=Path)

    bundle = sub.add_parser("verify-bundle", help="offline verification-bundle check")
    bundle.add_argument("bundle", type=Path)
    bundle.add_argument("--trust-policy", type=Path)
    bundle.add_argument("--online", action="store_true")
    bundle.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "verify-record":
            record = json.loads(args.record.read_text(encoding="utf-8"))
            findings = validate_record(record)
            for finding in findings:
                print(finding.render())
            return OK if not any(item.severity == "error" for item in findings) else 1

        if args.command == "verify-source":
            metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
            verified = verify_artifact(metadata, args.file)
            _print_json({"ok": True, "artifactId": verified.artifact_id})
            return OK

        if args.command == "claims":
            _print_json(lookup(args.id))
            return OK

        if args.command == "trust-policy":
            policy, digest = load_trust_policy(args.policy)
            _print_json({"ok": True, "policyId": policy["policyId"], "policyDigestSha256": digest})
            return OK

        if args.command == "verify-bundle":
            report, code = verify_bundle(
                args.bundle,
                trust_policy_path=args.trust_policy,
                online=bool(args.online),
            )
            if args.json:
                _print_json(report)
            else:
                sys.stdout.write(render_text(report))
            return code

        parser.error(f"unknown command {args.command}")
        return USAGE_ERROR
    except (BundleError, ClaimRegistryError, SourceArtifactError, TrustPolicyError) as exc:
        _print_json({"ok": False, "error": str(exc), "code": getattr(exc, "code", "ERROR")})
        return getattr(exc, "exit_code", 1)
    except Exception as exc:  # noqa: BLE001
        _print_json({"ok": False, "error": str(exc), "code": "INTERNAL"})
        return INTERNAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
