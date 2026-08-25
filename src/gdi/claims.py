"""Claim registry loading and lookup."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "claims" / "claim-registry.v1.json"
SCHEMA_PATH = ROOT / "claims" / "claim-registry.schema.json"


class ClaimRegistryError(Exception):
    def __init__(self, message: str, *, code: str = "CLAIM001") -> None:
        super().__init__(message)
        self.code = code


@lru_cache(maxsize=1)
def load_registry() -> dict[str, Any]:
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ClaimRegistryError(f"cannot load claim registry: {exc}") from exc
    try:
        import jsonschema

        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(registry)
    except Exception as exc:  # noqa: BLE001 - surface as registry error
        raise ClaimRegistryError(f"claim registry failed schema validation: {exc}") from exc
    return registry


def claims_by_id() -> dict[str, dict[str, Any]]:
    registry = load_registry()
    by_id: dict[str, dict[str, Any]] = {}
    for claim in registry["claims"]:
        by_id[claim["claimId"]] = claim
        for alias in claim.get("aliases", []):
            by_id[alias] = claim
    return by_id


def require_known_claim_ids(claim_ids: list[str]) -> None:
    known = claims_by_id()
    unknown = sorted({item for item in claim_ids if item not in known})
    if unknown:
        raise ClaimRegistryError(f"unknown claim IDs: {unknown}", code="CLAIM002")


def lookup(claim_id: str) -> dict[str, Any]:
    claim = claims_by_id().get(claim_id)
    if claim is None:
        raise ClaimRegistryError(f"unknown claim ID: {claim_id}", code="CLAIM002")
    return claim


def active_claim_ids() -> list[str]:
    return sorted(
        claim["claimId"]
        for claim in load_registry()["claims"]
        if claim["status"] == "active"
    )
