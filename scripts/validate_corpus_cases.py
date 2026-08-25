#!/usr/bin/env python3
"""Validate every checked-in empirical retrospective corpus case."""

from __future__ import annotations

import json
from pathlib import Path

from corpus_metrics import CorpusCaseError, compute_metrics

ROOT = Path(__file__).resolve().parents[1]
CASES_ROOT = ROOT / "corpus" / "cases"


def _load_case(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    case_paths = sorted(CASES_ROOT.glob("*/case.json"))
    if not case_paths:
        print("No empirical corpus cases found.")
        return 0

    failed = False
    for case_path in case_paths:
        try:
            result = compute_metrics(_load_case(case_path), base_dir=case_path.parent)
            print(json.dumps(result, indent=2, sort_keys=True))
        except (CorpusCaseError, OSError, json.JSONDecodeError, ValueError) as exc:
            failed = True
            code = exc.code if isinstance(exc, CorpusCaseError) else "CORP-CHECK"
            print(json.dumps({"ok": False, "case": str(case_path), "code": code, "error": str(exc)}, indent=2))

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
