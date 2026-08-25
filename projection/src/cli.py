#!/usr/bin/env python3
"""Project and verify confidential records using projection v1 or v2 specs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from project import ProjectionError as ProjectionErrorV1  # noqa: E402
from project import load_json as load_json_v1  # noqa: E402
from project import project_record as project_record_v1  # noqa: E402
from project import verify_withheld_commitment as verify_withheld_v1  # noqa: E402
from project_v2 import ProjectionError as ProjectionErrorV2  # noqa: E402
from project_v2 import detect_spec_version  # noqa: E402
from project_v2 import load_json  # noqa: E402
from project_v2 import project_record_v2  # noqa: E402
from project_v2 import verify_projection_v2  # noqa: E402
from project_v2 import verify_withheld_v2  # noqa: E402

ProjectionError = (ProjectionErrorV1, ProjectionErrorV2)


def _write_out(path: Path, value: Any, *, force: bool, canonical: bool) -> None:
    if path.exists() and not force:
        raise ProjectionErrorV2(
            f"refusing to overwrite existing file without --force: {path}",
            code="PROJ232",
        )
    if canonical:
        from rfc8785 import dumps as jcs_dumps

        encoded = jcs_dumps(value)
        data = encoded if isinstance(encoded, bytes) else encoded.encode("utf-8")
        path.write_bytes(data)
    else:
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def cmd_project(args: argparse.Namespace) -> int:
    confidential = load_json(args.confidential)
    spec = load_json(args.spec)
    version = detect_spec_version(spec)
    if version == "1":
        result = project_record_v1(confidential, spec)
        public = result.public_record
        payload: dict[str, Any] = {"ok": True, **result.as_dict()}
    else:
        result_v2 = project_record_v2(confidential, spec)
        public = result_v2.public_record
        payload = {"ok": True, **result_v2.as_dict()}
    _write_out(Path(args.out), public, force=bool(args.force), canonical=bool(args.canonical))
    print(json.dumps(payload, indent=2))
    return 0


def cmd_verify_projection(args: argparse.Namespace) -> int:
    confidential = load_json(args.confidential)
    spec = load_json(args.spec)
    public = load_json(args.public)
    version = detect_spec_version(spec)
    if version == "1":
        expected = project_record_v1(confidential, spec)
        if expected.public_record != public:
            raise ProjectionErrorV1("public record does not match recomputed v1 projection", code="PROJ014")
        print(
            json.dumps(
                {"ok": True, "specVersion": "1", "projectionDigestSha256": expected.projection_digest},
                indent=2,
            )
        )
        return 0
    report = verify_projection_v2(confidential, spec, public)
    print(json.dumps(report, indent=2))
    return 0


def cmd_verify_withheld(args: argparse.Namespace) -> int:
    public = load_json(args.public)
    revealed = load_json(args.revealed_subtree)
    if isinstance(public.get("projectionIntegrity"), dict):
        report = verify_withheld_v2(public=public, path=args.path, revealed_subtree=revealed)
        print(json.dumps(report, indent=2))
        return 0
    if not args.confidential:
        print(
            json.dumps(
                {"ok": False, "error": "v1 verify-withheld requires --confidential", "code": "PROJ016"},
                indent=2,
            )
        )
        return 1
    commitments = public.get("withheldCommitments") or {}
    meta = commitments.get(args.path)
    if not isinstance(meta, dict):
        raise ProjectionErrorV1(f"no v1 withheld commitment for path {args.path}", code="PROJ015")
    confidential = load_json_v1(args.confidential)
    ok = verify_withheld_v1(confidential, args.path, meta["commitmentDigest"])
    print(json.dumps({"ok": ok, "specVersion": "1", "path": args.path}, indent=2))
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic confidential-to-public record projection (v1 + v2)."
    )
    sub = parser.add_subparsers(dest="command")

    project = sub.add_parser("project", help="project confidential record to public form")
    project.add_argument("--confidential", required=True)
    project.add_argument("--spec", required=True)
    project.add_argument("--out", required=True)
    project.add_argument("--force", action="store_true")
    project.add_argument("--canonical", action="store_true")
    project.set_defaults(func=cmd_project)

    verify_proj = sub.add_parser("verify-projection", help="recompute and verify a public projection")
    verify_proj.add_argument("--confidential", required=True)
    verify_proj.add_argument("--spec", required=True)
    verify_proj.add_argument("--public", required=True)
    verify_proj.set_defaults(func=cmd_verify_projection)

    verify_withheld = sub.add_parser("verify-withheld", help="reopen a withheld commitment")
    verify_withheld.add_argument("--public", required=True)
    verify_withheld.add_argument("--path", required=True)
    verify_withheld.add_argument("--revealed-subtree", required=True)
    verify_withheld.add_argument("--confidential")
    verify_withheld.set_defaults(func=cmd_verify_withheld)

    parser.add_argument("--confidential")
    parser.add_argument("--spec")
    parser.add_argument("--out")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if getattr(args, "command", None):
            return int(args.func(args))
        if args.confidential and args.spec and args.out:
            legacy = argparse.Namespace(
                confidential=args.confidential,
                spec=args.spec,
                out=args.out,
                force=True,
                canonical=False,
            )
            return cmd_project(legacy)
        parser.print_help()
        return 2
    except ProjectionError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "code": getattr(exc, "code", None)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
