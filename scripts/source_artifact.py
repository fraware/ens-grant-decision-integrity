#!/usr/bin/env python3
"""Create and verify preserved source-artifact metadata.

This tool operates on bytes already captured by the operator. It intentionally
does not perform network retrieval: retrieval policy, authentication, redirects,
and archival custody are program-specific. The invariant here is narrower:
metadata must bind to the exact stored bytes through SHA-256 and byte length.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "source-artifact.schema.json"


def _sha256(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _validate(value: dict[str, Any]) -> None:
    import jsonschema

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        path = ".".join(str(part) for part in first.absolute_path) or "<root>"
        raise ValueError(f"source artifact schema failure at {path}: {first.message}")


def build_artifact(
    *,
    artifact_id: str,
    source_uri: str,
    file_path: Path,
    media_type: str,
    method: str,
    tool: str,
    tool_version: str,
    retrieved_at: str | None = None,
    resolved_uri: str | None = None,
    http_status: int | None = None,
    archive_uri: str | None = None,
    surfaces: list[str] | None = None,
) -> dict[str, Any]:
    digest, size = _sha256(file_path)
    value: dict[str, Any] = {
        "artifactVersion": "1",
        "artifactId": artifact_id,
        "sourceUri": source_uri,
        "resolvedUri": resolved_uri,
        "retrievedAt": retrieved_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "httpStatus": http_status,
        "mediaType": media_type,
        "byteLength": size,
        "sha256": digest,
        "storedPath": str(file_path),
        "archiveUri": archive_uri,
        "surfaces": surfaces or [],
        "capture": {
            "method": method,
            "tool": tool,
            "toolVersion": tool_version,
            "notes": None,
        },
        "contentEncoding": None,
        "observations": [],
    }
    _validate(value)
    return value


def verify_artifact(metadata: dict[str, Any], file_path: Path) -> dict[str, Any]:
    _validate(metadata)
    digest, size = _sha256(file_path)
    checks = {
        "sha256": digest == metadata["sha256"],
        "byteLength": size == metadata["byteLength"],
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "observedSha256": digest,
        "observedByteLength": size,
        "nonClaims": [
            "Content identity does not establish source truth.",
            "Content identity does not establish institutional adoption or authority.",
            "A captured artifact may be incomplete relative to a wider governing process.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify GDI source-artifact metadata")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--artifact-id", required=True)
    build.add_argument("--source-uri", required=True)
    build.add_argument("--file", required=True)
    build.add_argument("--media-type", required=True)
    build.add_argument("--method", required=True, choices=["http", "manual-export", "api", "repository", "onchain", "other"])
    build.add_argument("--tool", required=True)
    build.add_argument("--tool-version", required=True)
    build.add_argument("--retrieved-at")
    build.add_argument("--resolved-uri")
    build.add_argument("--http-status", type=int)
    build.add_argument("--archive-uri")
    build.add_argument("--surface", action="append", dest="surfaces")
    build.add_argument("--out", required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--metadata", required=True)
    verify.add_argument("--file", required=True)

    args = parser.parse_args()
    if args.command == "build":
        value = build_artifact(
            artifact_id=args.artifact_id,
            source_uri=args.source_uri,
            file_path=Path(args.file),
            media_type=args.media_type,
            method=args.method,
            tool=args.tool,
            tool_version=args.tool_version,
            retrieved_at=args.retrieved_at,
            resolved_uri=args.resolved_uri,
            http_status=args.http_status,
            archive_uri=args.archive_uri,
            surfaces=args.surfaces,
        )
        Path(args.out).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, "artifact": value}, indent=2))
        return 0

    metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    result = verify_artifact(metadata, Path(args.file))
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
