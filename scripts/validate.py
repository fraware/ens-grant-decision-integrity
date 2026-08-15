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
for finding in findings:
    print(finding.render())
errors = [finding for finding in findings if finding.severity == "error"]
warnings = {finding.code for finding in findings if finding.severity == "warning"}
if errors:
    raise SystemExit(1)
if warnings != {"CHAL003"}:
    raise SystemExit(f"FAIL unexpected worked-example warnings: {sorted(warnings)}")

charter = (ROOT / "CHARTER.md").read_text(encoding="utf-8")
authority_values = schema["properties"]["decision"]["properties"]["authorityKind"]["enum"]
decision_statuses = schema["properties"]["decision"]["properties"]["status"]["enum"]
if "ai" in authority_values:
    raise SystemExit("FAIL AI must not be a decision-authority type")
if "ineligible" not in decision_statuses:
    raise SystemExit("FAIL schema must distinguish hard-screen ineligibility from merit rejection")
if "An AI system MUST NOT exercise unilateral authority" not in charter:
    raise SystemExit("FAIL Charter no longer contains the AI unilateral-authority prohibition")
if "It does not establish that the evaluator used that manifest" not in charter:
    raise SystemExit("FAIL Charter commit–reveal limitation is missing")

allocations = [decision["allocationUsd"] for decision in provenance["decisions"]]
recorded_total = provenance["confirmedCumulativeAllocationUsd"]
if sum(allocations) != recorded_total:
    raise SystemExit(f"FAIL allocations sum to {sum(allocations)}, recorded total is {recorded_total}")
if recorded_total != 219:
    raise SystemExit(f"FAIL expected v0.1 provenance total 219, got {recorded_total}")

print("PASS schema is valid Draft 2020-12")
print("PASS SPP3 example has no conformance errors")
print("PASS SPP3 example exposes only expected warning CHAL003")
print("PASS AI is excluded from decision-authority types")
print("PASS hard-screen ineligibility is distinct from merit rejection")
print("PASS Charter preserves the AI unilateral-authority prohibition")
print("PASS Charter states the commit–reveal limitation explicitly")
print(f"PASS Simocracy allocations reconcile to ${recorded_total}")
