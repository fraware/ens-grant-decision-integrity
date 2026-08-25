"""External trust-policy loading. Bundles cannot self-appoint trust."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "schema" / "trust-policy.schema.json"


class TrustPolicyError(Exception):
    def __init__(self, message: str, *, code: str = "TRUST001") -> None:
        super().__init__(message)
        self.code = code


def _parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def load_trust_policy(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise TrustPolicyError(f"cannot read trust policy: {exc}", code="TRUST002") from exc
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    try:
        policy = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TrustPolicyError(f"trust policy is not valid JSON: {exc}", code="TRUST003") from exc
    try:
        import jsonschema

        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(policy)
    except Exception as exc:  # noqa: BLE001
        raise TrustPolicyError(f"trust policy failed schema validation: {exc}", code="TRUST004") from exc
    return policy, digest


def signer_authorized(
    policy: dict[str, Any],
    *,
    key_id: str,
    role: str,
    at: datetime | None = None,
) -> bool:
    when = at or datetime.now(timezone.utc)
    for signer in policy.get("runSigners", []):
        if signer.get("keyId") != key_id:
            continue
        if role not in signer.get("roles", []):
            continue
        start = _parse_time(signer["validFor"]["start"])
        end = _parse_time(signer["validFor"].get("end"))
        if start is not None and when < start:
            continue
        if end is not None and when >= end:
            continue
        return True
    return False
