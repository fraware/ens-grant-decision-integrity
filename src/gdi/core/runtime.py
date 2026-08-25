"""Runtime binding for the historical core conformance implementation.

The conformance module preserves its source-tree layout for compatibility. This
wrapper rebinds its schema root to immutable packaged data before exposing the
public validation functions.
"""

from __future__ import annotations

from gdi.core import conformance as _impl
from gdi.resources import data_root, resource_path

_impl.ROOT = data_root()
_impl.SCHEMA_PATH = resource_path("schema", "grant-decision-record.schema.json")
_impl.SCHEMA_02_PATH = resource_path("schema", "grant-decision-record-0.2.schema.json")

Finding = _impl.Finding
check_semantics = _impl.check_semantics
check_schema_02_extensions = _impl.check_schema_02_extensions
load_schema_for_record = _impl.load_schema_for_record
validate_record = _impl.validate_record
validate_schema = _impl.validate_schema

__all__ = [
    "Finding",
    "check_semantics",
    "check_schema_02_extensions",
    "load_schema_for_record",
    "validate_record",
    "validate_schema",
]
