#!/usr/bin/env python3
"""Build and verify metadata for exact preserved source bytes.

This module hashes bytes exactly as supplied. It does not retrieve network
resources, normalize content, authenticate source ownership, establish source
truth, or provide independent evidence of capture time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "source-artifact.schema.json"
HASH_PREFIX = "sha256:"
URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*$")


class SourceArtifactError(Exception):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class VerifiedSourceArtifact:
    metadata: dict[str, Any]
    observed_content_hash: str
    observed_byte_length: int

    @property
    def artifact_id(self) -> str:
        return str(self.metadata["artifactId"])


def _hash_file(path: Path) -> tuple[str, int]:
    try:
        handle = path.open("rb")
    except OSError as exc:
        raise SourceArtifactError(f"cannot open captured source bytes: {exc}", code="SRC001") from exc
    digest = hashlib.sha256()
    size = 0
    with handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return HASH_PREFIX + digest.hexdigest(), size


def _validate_offset_datetime(value: Any, field: str) -> None:
    if not isinstance(value, str):
        raise SourceArtifactError(f"{field} must be a date-time string", code="SRC002")
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise SourceArtifactError(f"{field} must be a valid RFC 3339-style date-time", code="SRC002") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SourceArtifactError(f"{field} must include a UTC designator or numeric offset", code="SRC002")


def _validate_uri(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value or any(character.isspace() for character in value):
        raise SourceArtifactError(f"{field} must be a non-empty URI without whitespace", code="SRC002")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise SourceArtifactError(f"{field} must be a valid URI", code="SRC002") from exc
    if not parsed.scheme or not URI_SCHEME_RE.fullmatch(parsed.scheme):
        raise SourceArtifactError(f"{field} must include a valid URI scheme", code="SRC002")


def validate_source_artifact(value: dict[str, Any]) -> None:
    import jsonschema

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceArtifactError(f"cannot load source-artifact schema: {exc}", code="SRC006") from exc
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        raise SourceArtifactError(f"source-artifact schema is invalid: {exc.message}", code="SRC006") from exc
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        path = "/".join(str(part) for part in first.absolute_path) or "<root>"
        raise SourceArtifactError(
            f"source-artifact schema failure at {path}: {first.message}",
            code="SRC002",
        )

    # Do not rely on optional jsonschema format-checking dependencies for critical
    # provenance fields. Enforce the minimum URI/date-time contract explicitly.
    _validate_offset_datetime(value.get("capturedAt"), "capturedAt")
    _validate_uri(value.get("sourceUri"), "sourceUri")
    for field in ("resolvedUri", "archiveUri"):
        if field in value:
            _validate_uri(value[field], field)


def build_artifact(
    *,
    artifact_id: str,
    source_uri: str,
    file_path: Path,
    media_type: str,
    method: str,
    tool: str,
    tool_version: str,
    captured_at: str | None = None,
    resolved_uri: str | None = None,
    http_status: int | None = None,
    archive_uri: str | None = None,
    stored_path: str | None = None,
    content_encoding: str | None = None,
    capture_notes: str | None = None,
    observations: list[str] | None = None,
) -> dict[str, Any]:
    content_hash, size = _hash_file(file_path)
    value: dict[str, Any] = {
        "artifactVersion": "1",
        "artifactId": artifact_id,
        "sourceUri": source_uri,
        "capturedAt": captured_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mediaType": media_type,
        "byteLength": size,
        "contentHash": content_hash,
        "capture": {
            "method": method,
            "tool": tool,
            "toolVersion": tool_version,
        },
    }
    if resolved_uri is not None:
        value["resolvedUri"] = resolved_uri
    if http_status is not None:
        value["httpStatus"] = http_status
    if archive_uri is not None:
        value["archiveUri"] = archive_uri
    if stored_path is not None:
        value["storedPath"] = stored_path
    if content_encoding is not None:
        value["contentEncoding"] = content_encoding
    if capture_notes is not None:
        value["capture"]["notes"] = capture_notes
    if observations:
        value["observations"] = observations
    validate_source_artifact(value)
    return value


def verify_artifact(metadata: dict[str, Any], file_path: Path) -> VerifiedSourceArtifact:
    validate_source_artifact(metadata)
    observed_hash, observed_size = _hash_file(file_path)
    if observed_hash != metadata["contentHash"]:
        raise SourceArtifactError(
            "captured source bytes do not match source-artifact contentHash",
            code="SRC003",
        )
    if observed_size != metadata["byteLength"]:
        raise SourceArtifactError(
            "captured source byte length does not match source-artifact metadata",
            code="SRC004",
        )
    return VerifiedSourceArtifact(
        metadata=metadata,
        observed_content_hash=observed_hash,
        observed_byte_length=observed_size,
    )


def verification_result(verified: VerifiedSourceArtifact) -> dict[str, Any]:
    return {
        "ok": True,
        "artifactId": verified.artifact_id,
        "observedContentHash": verified.observed_content_hash,
        "observedByteLength": verified.observed_byte_length,
        "nonClaims": [
            "Byte identity does not establish source truth or completeness.",
            "Byte identity does not establish institutional adoption or authority.",
            "capturedAt is capture metadata, not an independently verified timestamp.",
            "sourceUri and resolvedUri are declared provenance fields; this verifier does not authenticate source ownership.",
        ],
    }


def _failure(exc: SourceArtifactError) -> dict[str, Any]:
    return {
        "ok": False,
        "code": exc.code,
        "error": str(exc),
        "nonClaims": ["A failed byte-binding check establishes no source-content identity claim."],
    }


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceArtifactError(f"source-artifact input error: {exc}", code="SRC005") from exc
    if not isinstance(value, dict):
        raise SourceArtifactError("source-artifact metadata must be a JSON object", code="SRC005")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    try:
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise SourceArtifactError(f"cannot write source-artifact output: {exc}", code="SRC007") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or verify preserved source-artifact metadata")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--artifact-id", required=True)
    build.add_argument("--source-uri", required=True)
    build.add_argument("--file", required=True)
    build.add_argument("--media-type", required=True)
    build.add_argument("--method", required=True, choices=["http", "manual-export", "api", "repository", "onchain", "other"])
    build.add_argument("--tool", required=True)
    build.add_argument("--tool-version", required=True)
    build.add_argument("--captured-at")
    build.add_argument("--resolved-uri")
    build.add_argument("--http-status", type=int)
    build.add_argument("--archive-uri")
    build.add_argument("--stored-path")
    build.add_argument("--content-encoding")
    build.add_argument("--capture-notes")
    build.add_argument("--observation", action="append", dest="observations")
    build.add_argument("--out", required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--metadata", required=True)
    verify.add_argument("--file", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            value = build_artifact(
                artifact_id=args.artifact_id,
                source_uri=args.source_uri,
                file_path=Path(args.file),
                media_type=args.media_type,
                method=args.method,
                tool=args.tool,
                tool_version=args.tool_version,
                captured_at=args.captured_at,
                resolved_uri=args.resolved_uri,
                http_status=args.http_status,
                archive_uri=args.archive_uri,
                stored_path=args.stored_path,
                content_encoding=args.content_encoding,
                capture_notes=args.capture_notes,
                observations=args.observations,
            )
            _write_json(Path(args.out), value)
            print(json.dumps({"ok": True, "artifact": value}, indent=2))
            return 0

        metadata = _load_json(Path(args.metadata))
        verified = verify_artifact(metadata, Path(args.file))
        print(json.dumps(verification_result(verified), indent=2))
        return 0
    except SourceArtifactError as exc:
        print(json.dumps(_failure(exc), indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
