"""Shared schema loading, I-JSON helpers, and verifier result objects."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from claims import NON_CLAIMS

SRC_DIR = Path(__file__).resolve().parent
PHASE2_ROOT = SRC_DIR.parent
SCHEMA_DIR = PHASE2_ROOT / "schema"
VECTOR_DIR = PHASE2_ROOT / "vectors"
EXAMPLE_DIR = PHASE2_ROOT / "examples"

_REGISTRY: Registry | None = None
_SCHEMAS: dict[str, dict[str, Any]] | None = None


class Phase2Error(Exception):
    def __init__(self, message: str, *, code: str | None = None, claim: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.claim = claim


@dataclass
class VerificationResult:
    ok: bool
    established: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    non_claims: tuple[str, ...] = NON_CLAIMS

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "established": list(self.established),
            "failed": list(self.failed),
            "details": self.details,
            "nonClaims": list(self.non_claims),
        }


def load_schemas() -> dict[str, dict[str, Any]]:
    global _SCHEMAS
    if _SCHEMAS is None:
        _SCHEMAS = {}
        for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
            _SCHEMAS[path.name] = json.loads(path.read_text(encoding="utf-8"))
    return _SCHEMAS


def registry() -> Registry:
    global _REGISTRY
    if _REGISTRY is None:
        resources = []
        for name, schema in load_schemas().items():
            resources.append((name, Resource.from_contents(schema, default_specification=DRAFT202012)))
        _REGISTRY = Registry().with_resources(resources)
    return _REGISTRY


def validate_schema(instance: Any, schema_name: str) -> None:
    schemas = load_schemas()
    if schema_name not in schemas:
        raise Phase2Error(f"unknown schema {schema_name}", code="SCHEMA001")
    validator = jsonschema.Draft202012Validator(
        schemas[schema_name],
        registry=registry(),
        format_checker=jsonschema.FormatChecker(),
    )
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        path = "/".join(str(p) for p in first.absolute_path) or "<root>"
        raise Phase2Error(
            f"{schema_name} failed at {path}: {first.message}",
            code="SCHEMA002",
        )


def sha256_hex(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()
