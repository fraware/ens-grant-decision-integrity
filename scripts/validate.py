#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from conformance import validate_record  # noqa: E402

SCHEMA_PATH = ROOT / "schema" / "grant-decision-record.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "spp3-marketplace-rfp.example.json"
PROVENANCE_PATH = ROOT / "provenance" / "simocracy-funding.json"

schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))

findings = validate_record(example, schema)
if findings:
    for finding in findings:
        print(finding.render())
    raise SystemExit(1)

allocations = [d["allocationUsd"] for d in provenance["decisions"]]
recorded_total = provenance["confirmedCumulativeAllocationUsd"]
if sum(allocations) != recorded_total:
    raise SystemExit(f"FAIL allocations sum to {sum(allocations)}, recorded total is {recorded_total}")
if recorded_total != 219:
    raise SystemExit(f"FAIL expected v0.1 provenance total 219, got {recorded_total}")

print("PASS schema is valid Draft 2020-12")
print("PASS SPP3 example is structurally and semantically conformant")
print(f"PASS Simocracy allocations reconcile to ${recorded_total}")
