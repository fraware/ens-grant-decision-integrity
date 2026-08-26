#!/usr/bin/env python3
"""Compatibility shim — implementation lives in packaged GDI runtime modules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gdi.core.runtime import (
    Finding,
    check_schema_02_extensions,
    check_semantics,
    load_schema_for_record,
    validate_record,
    validate_schema,
)

__all__ = [
    "Finding",
    "check_schema_02_extensions",
    "check_semantics",
    "load_schema_for_record",
    "main",
    "validate_record",
    "validate_schema",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ENS Grant Decision Integrity records.")
    parser.add_argument("records", nargs="+", help="JSON decision record(s) to validate")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    failed = False
    for raw in args.records:
        path = Path(raw)
        record = json.loads(path.read_text(encoding="utf-8"))
        record_findings = validate_record(record)
        print(f"{path}:")
        if not record_findings:
            print("  PASS")
            continue
        for item in record_findings:
            print(f"  {item.render()}")
        if any(item.severity == "error" for item in record_findings):
            failed = True
        if args.strict and record_findings:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
