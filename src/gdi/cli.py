"""gdi command-line interface."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from gdi import __version__
from gdi.bundle import BundleError, verify_bundle
from gdi.claims import ClaimRegistryError, lookup
from gdi.core.runtime import validate_record
from gdi.exit_codes import (
    EVIDENCE_FAILURE,
    INTERNAL_ERROR,
    OK,
    UNSUPPORTED,
    USAGE_ERROR,
)
from gdi.phase2 import phase2_error_type, verify_graph_bundle
from gdi.report import render_text
from gdi.resources import ResourceError, resource_path
from gdi.source import artifact as source_artifact
from gdi.trust.policy import TrustPolicyError, load_trust_policy


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _profiles_dir() -> Path:
    """Resolve versioned operational profiles from explicit or packaged data."""
    env = os.environ.get("GDI_PROFILES_DIR")
    if env:
        return Path(env)
    return resource_path("profiles")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gdi",
        description="ENS Grant Decision Integrity verifier",
    )
    parser.add_argument("--version", action="version", version=f"gdi {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    verify_record = sub.add_parser("verify-record", help="validate a decision record")
    verify_record.add_argument("record", type=Path)

    verify_source = sub.add_parser("verify-source", help="verify source artifact bytes offline")
    verify_source.add_argument("--metadata", type=Path, required=True)
    verify_source.add_argument("--file", type=Path, required=True)

    source_cmd = sub.add_parser("source", help="source-artifact build/capture/verify")
    source_cmd.add_argument("source_args", nargs=argparse.REMAINDER)

    project = sub.add_parser("project", help="project confidential record to public form")
    project.add_argument("--confidential", type=Path, required=True)
    project.add_argument("--spec", type=Path, required=True)
    project.add_argument("--out", type=Path, required=True)
    project.add_argument("--force", action="store_true")
    project.add_argument("--canonical", action="store_true")

    verify_projection = sub.add_parser(
        "verify-projection",
        help="verify a public projection offline",
    )
    verify_projection.add_argument("--confidential", type=Path, required=True)
    verify_projection.add_argument("--spec", type=Path, required=True)
    verify_projection.add_argument("--public", type=Path, required=True)

    verify_withheld = sub.add_parser("verify-withheld", help="reopen a withheld commitment")
    verify_withheld.add_argument("--public", type=Path, required=True)
    verify_withheld.add_argument("--path", required=True)
    verify_withheld.add_argument("--revealed-subtree", type=Path, required=True)
    verify_withheld.add_argument("--confidential", type=Path)

    claims = sub.add_parser("claims", help="look up a claim registry entry")
    claims.add_argument("--id", required=True)

    trust = sub.add_parser("trust-policy", help="validate an external trust policy")
    trust.add_argument("policy", type=Path)

    phase2 = sub.add_parser("verify-phase2", help="verify a Phase II evidence graph offline")
    phase2.add_argument("bundle", type=Path)
    phase2.add_argument("--trust-policy", type=Path)
    phase2.add_argument("--trust-root", type=Path)
    phase2.add_argument("--json", action="store_true")

    bundle = sub.add_parser("verify-bundle", help="offline verification-bundle check")
    bundle.add_argument("bundle", type=Path)
    bundle.add_argument("--trust-policy", type=Path)
    bundle.add_argument("--trust-root", type=Path)
    bundle.add_argument("--online", action="store_true")
    bundle.add_argument("--json", action="store_true")

    profiles = sub.add_parser("profiles", help="list or show operational adoption profiles")
    profiles.add_argument("profile_id", nargs="?", help="optional profile ID to print")
    profiles.add_argument("--format", choices=("text", "json"), default="text")

    return parser


def _run_projection_cli(argv: list[str]) -> int:
    projection_src = resource_path("projection", "src")
    if str(projection_src) not in sys.path:
        sys.path.insert(0, str(projection_src))
    from cli import main as projection_main  # type: ignore[import-not-found]

    return int(projection_main(argv))


def _load_phase2_inputs(
    bundle_path: Path,
    trust_policy_path: Path | None,
    trust_root_path: Path | None,
) -> tuple[dict[str, Any], dict[str, Any] | None, str | None]:
    raw = json.loads(bundle_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Phase II evidence bundle must be a JSON object")
    policy = None
    if trust_policy_path is not None:
        policy, _digest = load_trust_policy(trust_policy_path)
    trust_root = None
    if trust_root_path is not None:
        trust_root = trust_root_path.read_text(encoding="utf-8")
    return raw, policy, trust_root


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "verify-record":
            record = json.loads(args.record.read_text(encoding="utf-8"))
            findings = validate_record(record)
            for finding in findings:
                print(finding.render())
            has_errors = any(item.severity == "error" for item in findings)
            return EVIDENCE_FAILURE if has_errors else OK

        if args.command == "verify-source":
            metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
            verified = source_artifact.verify_artifact(metadata, args.file)
            _print_json({"ok": True, "artifactId": verified.artifact_id})
            return OK

        if args.command == "source":
            source_argv = list(args.source_args)
            if source_argv and source_argv[0] == "--":
                source_argv = source_argv[1:]
            return int(source_artifact.main(source_argv))

        if args.command == "project":
            cli_argv = [
                "project",
                "--confidential",
                str(args.confidential),
                "--spec",
                str(args.spec),
                "--out",
                str(args.out),
            ]
            if args.force:
                cli_argv.append("--force")
            if args.canonical:
                cli_argv.append("--canonical")
            return _run_projection_cli(cli_argv)

        if args.command == "verify-projection":
            return _run_projection_cli(
                [
                    "verify-projection",
                    "--confidential",
                    str(args.confidential),
                    "--spec",
                    str(args.spec),
                    "--public",
                    str(args.public),
                ]
            )

        if args.command == "verify-withheld":
            cli_argv = [
                "verify-withheld",
                "--public",
                str(args.public),
                "--path",
                args.path,
                "--revealed-subtree",
                str(args.revealed_subtree),
            ]
            if args.confidential:
                cli_argv.extend(["--confidential", str(args.confidential)])
            return _run_projection_cli(cli_argv)

        if args.command == "claims":
            _print_json(lookup(args.id))
            return OK

        if args.command == "trust-policy":
            policy, digest = load_trust_policy(args.policy)
            _print_json(
                {
                    "ok": True,
                    "policyId": policy["policyId"],
                    "policyDigestSha256": digest,
                }
            )
            return OK

        if args.command == "verify-phase2":
            raw, policy, trust_root = _load_phase2_inputs(
                args.bundle,
                args.trust_policy,
                args.trust_root,
            )
            try:
                result = verify_graph_bundle(
                    raw,
                    trust_root_pem=trust_root,
                    trust_policy=policy,
                )
            except phase2_error_type() as exc:
                payload = {
                    "ok": False,
                    "error": str(exc),
                    "code": getattr(exc, "code", "PHASE2"),
                    "claim": getattr(exc, "claim", None),
                }
                _print_json(payload)
                if getattr(exc, "code", None) in {"RKR263", "TS3178"}:
                    return UNSUPPORTED
                return EVIDENCE_FAILURE
            payload = result.as_dict()
            _print_json(payload)
            return OK if result.ok else EVIDENCE_FAILURE

        if args.command == "verify-bundle":
            report, code = verify_bundle(
                args.bundle,
                trust_policy_path=args.trust_policy,
                trust_root_path=args.trust_root,
                online=bool(args.online),
            )
            if args.json:
                _print_json(report)
            else:
                sys.stdout.write(render_text(report))
            return code

        if args.command == "profiles":
            root = _profiles_dir()
            if not root.is_dir():
                raise FileNotFoundError(
                    "profiles directory not found; set GDI_PROFILES_DIR or reinstall package"
                )
            if args.profile_id:
                path = root / f"{args.profile_id}.json"
                if not path.is_file():
                    raise FileNotFoundError(f"unknown profile: {args.profile_id}")
                text = path.read_text(encoding="utf-8")
                sys.stdout.write(text if text.endswith("\n") else text + "\n")
                return OK
            ids = sorted(
                path.stem
                for path in root.glob("*.json")
                if path.name != "profile.schema.json"
            )
            if args.format == "json":
                _print_json({"profiles": ids})
            else:
                for profile_id in ids:
                    print(profile_id)
            return OK

        parser.error(f"unknown command {args.command}")
        return USAGE_ERROR
    except (
        BundleError,
        ClaimRegistryError,
        source_artifact.SourceArtifactError,
        TrustPolicyError,
    ) as exc:
        _print_json({"ok": False, "error": str(exc), "code": getattr(exc, "code", "ERROR")})
        return getattr(exc, "exit_code", EVIDENCE_FAILURE)
    except (FileNotFoundError, ResourceError) as exc:
        _print_json({"ok": False, "error": str(exc), "code": "USAGE"})
        return USAGE_ERROR
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        _print_json({"ok": False, "error": str(exc), "code": "USAGE"})
        return USAGE_ERROR
    except Exception as exc:  # noqa: BLE001
        _print_json({"ok": False, "error": str(exc), "code": "INTERNAL"})
        return INTERNAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
