"""Runtime binding for the historical core conformance implementation.

The conformance module preserves its source-tree layout for compatibility. This
wrapper rebinds its schema root to immutable packaged data before exposing the
public validation functions and rejects non-finite numeric values before schema
or semantic comparisons can observe them.
"""

from __future__ import annotations

import math
from typing import Any

from gdi.core import conformance as _impl
from gdi.resources import data_root, resource_path

_impl.ROOT = data_root()
_impl.SCHEMA_PATH = resource_path("schema", "grant-decision-record.schema.json")
_impl.SCHEMA_02_PATH = resource_path("schema", "grant-decision-record-0.2.schema.json")

Finding = _impl.Finding
check_semantics = _impl.check_semantics
check_schema_02_extensions = _impl.check_schema_02_extensions
load_schema_for_record = _impl.load_schema_for_record
validate_schema = _impl.validate_schema


def _nonfinite_findings(value: Any, *, path: str = "<root>") -> list[Finding]:
    findings: list[Finding] = []
    if isinstance(value, float) and not math.isfinite(value):
        findings.append(
            Finding(
                "error",
                "SCHEMA",
                path,
                "numeric values must be finite JSON numbers",
            )
        )
        return findings
    if isinstance(value, dict):
        for key, item in value.items():
            child = str(key) if path == "<root>" else f"{path}.{key}"
            findings.extend(_nonfinite_findings(item, path=child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"[{index}]" if path == "<root>" else f"{path}[{index}]"
            findings.extend(_nonfinite_findings(item, path=child))
    return findings


def validate_record(record: dict, schema: dict | None = None) -> list[Finding]:
    """Validate one record and fail structurally on NaN or infinity anywhere."""
    numeric = _nonfinite_findings(record)
    if numeric:
        return numeric
    return _impl.validate_record(record, schema)


__all__ = [
    "Finding",
    "check_semantics",
    "check_schema_02_extensions",
    "load_schema_for_record",
    "validate_record",
    "validate_schema",
]
