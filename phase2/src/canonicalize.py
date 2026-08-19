"""RFC 8785 JCS adapter with I-JSON rejection.

Production canonicalization uses the pinned rfc8785 library. Tests compare
those bytes to an independent second implementation.
"""

from __future__ import annotations

import math
from typing import Any

import rfc8785

from support import Phase2Error

# RFC 7493 / ECMAScript MAX_SAFE_INTEGER
_MAX_SAFE_INTEGER = 9007199254740991


def _reject_i_json(value: Any, *, path: str) -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, str):
        if "\ud800" <= value <= "\udfff" or any("\ud800" <= ch <= "\udfff" for ch in value):
            raise Phase2Error(f"I-JSON rejected lone surrogate at {path}", code="JCS001")
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > _MAX_SAFE_INTEGER:
            raise Phase2Error(
                f"I-JSON rejected integer outside binary64 exact range at {path}; encode as string",
                code="JCS002",
            )
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise Phase2Error(f"I-JSON rejected non-finite number at {path}", code="JCS003")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _reject_i_json(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise Phase2Error(f"I-JSON rejected non-string key at {path}", code="JCS004")
            _reject_i_json(item, path=f"{path}.{key}")
        return
    raise Phase2Error(f"I-JSON rejected non-JSON type {type(value).__name__} at {path}", code="JCS005")


def canonicalize(value: Any) -> bytes:
    """Return RFC 8785 JCS bytes for an I-JSON value."""
    _reject_i_json(value, path="$")
    try:
        encoded = rfc8785.dumps(value)
    except Exception as exc:
        raise Phase2Error(f"RFC 8785 canonicalization failed: {exc}", code="JCS006") from exc
    if isinstance(encoded, str):
        return encoded.encode("utf-8")
    if not isinstance(encoded, (bytes, bytearray)):
        raise Phase2Error("RFC 8785 adapter returned a non-byte value", code="JCS007")
    return bytes(encoded)
