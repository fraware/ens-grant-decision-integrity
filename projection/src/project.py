"""Deterministic confidential-to-public record projection.

Given a canonical confidential record and a versioned projection spec, produce a
public decision record with field allowlists, redaction categories, and SHA-256
commitments for withheld subtrees. Output bytes are RFC 8785 JCS canonical.

Projection v1 is intentionally conservative: every top-level source field must
be either published by the allowlist or explicitly withheld by a redaction rule.
Silently dropping source fields is rejected because omission without disposition
would defeat reconstructable disclosure accounting.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rfc8785 import dumps as jcs_dumps

PROJECTION_DOMAIN = "ens-gdi/public-projection/v1"
REDACTION_CATEGORIES = frozenset({"privacy", "security", "commercial", "legal", "contractual", "other"})


class ProjectionError(Exception):
    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ProjectionResult:
    public_record: dict[str, Any]
    projection_digest: str
    withheld_commitments: dict[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "publicRecord": self.public_record,
            "projectionDigestSha256": self.projection_digest,
            "withheldCommitments": self.withheld_commitments,
        }


def _canonical_bytes(value: Any) -> bytes:
    encoded = jcs_dumps(value)
    if isinstance(encoded, bytes):
        return encoded
    return encoded.encode("utf-8")


def _path_get(record: dict[str, Any], path: str) -> Any:
    current: Any = record
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ProjectionError(f"path not found: {path}", code="PROJ001")
        current = current[part]
    return current


def project_record(confidential: dict[str, Any], spec: dict[str, Any]) -> ProjectionResult:
    """Apply a projection spec deterministically to a confidential canonical record."""
    if spec.get("specVersion") != "1":
        raise ProjectionError("unsupported projection specVersion", code="PROJ004")
    if spec.get("domain") != PROJECTION_DOMAIN:
        raise ProjectionError("projection domain mismatch", code="PROJ005")

    allowlist = list(spec.get("fieldAllowlist") or [])
    if not allowlist:
        raise ProjectionError("fieldAllowlist must be non-empty", code="PROJ006")
    if len(set(allowlist)) != len(allowlist):
        raise ProjectionError("fieldAllowlist contains duplicate fields", code="PROJ009")

    redactions = sorted(spec.get("redactions") or [], key=lambda item: item["path"])
    source = copy.deepcopy(confidential)
    withheld_meta: dict[str, dict[str, Any]] = {}
    redacted_top_level: set[str] = set()

    for rule in redactions:
        path = rule["path"]
        category = rule["category"]
        if category not in REDACTION_CATEGORIES:
            raise ProjectionError(f"unknown redaction category {category!r}", code="PROJ003")
        subtree = _path_get(confidential, path)
        digest = hashlib.sha256(_canonical_bytes(subtree)).hexdigest()
        if "." not in path:
            if path in redacted_top_level:
                raise ProjectionError(f"duplicate redaction path: {path}", code="PROJ010")
            redacted_top_level.add(path)
            withheld_meta[path] = {
                "category": category,
                "commitmentAlgorithm": "sha256-jcs-v1",
                "commitmentDigest": digest,
            }
            if rule.get("explanation"):
                withheld_meta[path]["explanation"] = rule["explanation"]
        else:
            raise ProjectionError(
                f"nested redaction path not supported in v1 reference: {path}",
                code="PROJ008",
            )

    output_fields = {"withheldCommitments"}
    allowlisted_source = {field for field in allowlist if field not in output_fields}
    undisposed = sorted(set(source) - allowlisted_source - redacted_top_level)
    if undisposed:
        raise ProjectionError(
            "projection spec silently omits top-level source fields: " + ", ".join(undisposed),
            code="PROJ011",
        )

    overlap = sorted(allowlisted_source & redacted_top_level)
    if overlap:
        raise ProjectionError(
            "projection fields cannot be both published and withheld: " + ", ".join(overlap),
            code="PROJ012",
        )

    projected: dict[str, Any] = {}
    for field in sorted(allowlist):
        if field in redacted_top_level or field in output_fields:
            continue
        if field not in source:
            raise ProjectionError(f"allowlisted field missing from record: {field}", code="PROJ007")
        projected[field] = source[field]

    if withheld_meta:
        projected["withheldCommitments"] = {key: withheld_meta[key] for key in sorted(withheld_meta)}

    envelope = {
        "domain": PROJECTION_DOMAIN,
        "specVersion": spec["specVersion"],
        "recordId": confidential.get("recordId"),
        "publicRecord": projected,
        "withheldCommitments": {
            key: withheld_meta[key]["commitmentDigest"] for key in sorted(withheld_meta)
        },
    }
    projection_digest = hashlib.sha256(_canonical_bytes(envelope)).hexdigest()
    projected["integrity"] = {
        "recordHashAlgorithm": "sha256-jcs-projection-v1",
        "recordHash": projection_digest,
        "sourceUri": spec.get("sourceUri"),
    }
    return ProjectionResult(
        public_record=projected,
        projection_digest=projection_digest,
        withheld_commitments={key: withheld_meta[key]["commitmentDigest"] for key in sorted(withheld_meta)},
    )


def verify_withheld_commitment(confidential: dict[str, Any], path: str, expected_digest: str) -> bool:
    subtree = _path_get(confidential, path)
    actual = hashlib.sha256(_canonical_bytes(subtree)).hexdigest()
    return actual == expected_digest.lower()


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
