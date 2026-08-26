"""External trust-policy loading. Bundles cannot self-appoint trust."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gdi.jsonutil import StrictJSONError, loads_strict
from gdi.resources import resource_path


class TrustPolicyError(Exception):
    def __init__(self, message: str, *, code: str = "TRUST001") -> None:
        super().__init__(message)
        self.code = code


def _parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise TrustPolicyError(
            f"trust-policy time is not a valid offset date-time: {value!r}",
            code="TRUST007",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TrustPolicyError(
            f"trust-policy time must include a UTC designator or numeric offset: {value!r}",
            code="TRUST007",
        )
    return parsed


def _validate_window(window: dict[str, Any], *, label: str) -> None:
    start = _parse_time(window["start"])
    end = _parse_time(window.get("end"))
    if start is None:
        raise TrustPolicyError(f"{label} validity window is missing start", code="TRUST007")
    if end is not None and end <= start:
        raise TrustPolicyError(
            f"{label} validity end must be later than start",
            code="TRUST008",
        )


def _within_window(window: dict[str, Any], when: datetime) -> bool:
    start = _parse_time(window["start"])
    end = _parse_time(window.get("end"))
    if start is not None and when < start:
        return False
    if end is not None and when >= end:
        return False
    return True


def load_trust_policy(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise TrustPolicyError(f"cannot read trust policy: {exc}", code="TRUST002") from exc
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    try:
        policy = loads_strict(raw.decode("utf-8"))
    except (UnicodeDecodeError, StrictJSONError) as exc:
        raise TrustPolicyError(f"trust policy is not valid strict JSON: {exc}", code="TRUST003") from exc
    if not isinstance(policy, dict):
        raise TrustPolicyError("trust policy must be a JSON object", code="TRUST003")
    try:
        import jsonschema

        schema_path = resource_path("schema", "trust-policy.schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(
            schema,
            format_checker=jsonschema.FormatChecker(),
        )
        validator.validate(policy)
    except Exception as exc:  # noqa: BLE001
        raise TrustPolicyError(
            f"trust policy failed schema validation: {exc}",
            code="TRUST004",
        ) from exc

    _validate_window(policy["validFor"], label="trust policy")
    for index, signer in enumerate(policy.get("runSigners", [])):
        _validate_window(signer["validFor"], label=f"runSigners[{index}]")
    return policy, digest


def signer_authorized(
    policy: dict[str, Any],
    *,
    key_id: str,
    role: str,
    at: datetime | None = None,
) -> bool:
    when = at or datetime.now(UTC)
    if when.tzinfo is None or when.utcoffset() is None:
        raise TrustPolicyError("authorization time must be timezone-aware", code="TRUST009")
    if not _within_window(policy["validFor"], when):
        return False
    for signer in policy.get("runSigners", []):
        if signer.get("keyId") != key_id:
            continue
        if role not in signer.get("roles", []):
            continue
        if not _within_window(signer["validFor"], when):
            continue
        return True
    return False
