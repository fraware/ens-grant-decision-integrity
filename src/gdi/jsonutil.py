"""Strict JSON decoding helpers for evidence-bearing inputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StrictJSONError(ValueError):
    """Raised when input uses syntax/values that are unsafe for evidence JSON."""


def _reject_constant(value: str) -> None:
    raise StrictJSONError(f"non-standard JSON numeric constant is not allowed: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJSONError(f"duplicate JSON object key is not allowed: {key!r}")
        result[key] = value
    return result


def loads_strict(text: str) -> Any:
    """Decode standards-conforming JSON while rejecting ambiguous extensions."""
    try:
        return json.loads(
            text,
            parse_constant=_reject_constant,
            object_pairs_hook=_unique_object,
        )
    except json.JSONDecodeError as exc:
        raise StrictJSONError(str(exc)) from exc


def load_path_strict(path: str | Path) -> Any:
    """Read one UTF-8 JSON file and apply strict evidence decoding rules."""
    candidate = Path(path)
    try:
        text = candidate.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise StrictJSONError(f"cannot read UTF-8 JSON from {candidate}: {exc}") from exc
    return loads_strict(text)


__all__ = ["StrictJSONError", "load_path_strict", "loads_strict"]
