#!/usr/bin/env python3
"""Project a confidential record to a public record using a projection spec."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from project import ProjectionError, load_json, project_record  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic confidential-to-public record projection.")
    parser.add_argument("--confidential", required=True, help="Confidential canonical record JSON")
    parser.add_argument("--spec", required=True, help="Projection spec JSON")
    parser.add_argument("--out", required=True, help="Output public record JSON")
    args = parser.parse_args()
    try:
        result = project_record(load_json(args.confidential), load_json(args.spec))
    except ProjectionError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "code": exc.code}, indent=2))
        return 1
    payload = result.as_dict()
    Path(args.out).write_text(json.dumps(result.public_record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, **payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
