#!/usr/bin/env python3
"""Compatibility shim — implementation lives in gdi.core.conformance."""

from __future__ import annotations

from gdi.core.conformance import Finding, check_schema_02_extensions, check_semantics, load_schema_for_record, main, validate_record, validate_schema

__all__ = [
    "Finding",
    "check_schema_02_extensions",
    "check_semantics",
    "load_schema_for_record",
    "main",
    "validate_record",
    "validate_schema",
]

if __name__ == "__main__":
    raise SystemExit(main())
