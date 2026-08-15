#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "grant-decision-record.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "spp3-marketplace-rfp.example.json"
PROVENANCE_PATH = ROOT / "provenance" / "simocracy-funding.json"

schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))

try:
    import jsonschema
except ImportError as exc:
    raise SystemExit("jsonschema is required: python -m pip install jsonschema") from exc

jsonschema.Draft202012Validator.check_schema(schema)
validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
errors = sorted(validator.iter_errors(example), key=lambda e: list(e.absolute_path))
if errors:
    for err in errors:
        loc = ".".join(str(p) for p in err.absolute_path) or "<root>"
        print(f"FAIL example {loc}: {err.message}")
    raise SystemExit(1)

weights = [c.get("weight") for c in example["evaluation"]["criteria"] if c.get("weight") is not None]
if abs(sum(weights) - 1.0) > 1e-9:
    raise SystemExit(f"FAIL criterion weights sum to {sum(weights)!r}, expected 1.0")

allocations = [d["allocationUsd"] for d in provenance["decisions"]]
recorded_total = provenance["confirmedCumulativeAllocationUsd"]
if sum(allocations) != recorded_total:
    raise SystemExit(f"FAIL allocations sum to {sum(allocations)}, recorded total is {recorded_total}")

if recorded_total != 219:
    raise SystemExit(f"FAIL expected v0.1 provenance total 219, got {recorded_total}")

print("PASS schema is valid Draft 2020-12")
print("PASS SPP3 example validates against schema")
print("PASS criterion weights sum to 1.0")
print(f"PASS Simocracy allocations reconcile to ${recorded_total}")
