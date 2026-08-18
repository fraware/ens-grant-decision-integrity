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

authority_values = schema["properties"]["decision"]["properties"]["authorityKind"]["enum"]
decision_statuses = schema["properties"]["decision"]["properties"]["status"]["enum"]
evaluator_properties = schema["properties"]["evaluators"]["items"]["properties"]
manifest_schema = schema["properties"]["evaluatorManifest"]
decision_properties = schema["properties"]["decision"]["properties"]
governing_policy_schema = schema["properties"]["governingPolicy"]
governing_policy_properties = governing_policy_schema["properties"]
policy_surface_schema = governing_policy_properties["surfaceSources"]
conflict_properties = schema["properties"]["conflicts"]["items"]["properties"]
finding_classifications = schema["properties"]["evaluation"]["properties"]["materialFindings"]["items"]["properties"]["classification"]["enum"]

if "ai" in authority_values:
    raise SystemExit("FAIL AI must not be a decision-authority type")
if "ineligible" not in decision_statuses:
    raise SystemExit("FAIL schema must distinguish hard-screen ineligibility from merit rejection")
if "materiallyInformedRecommendation" not in evaluator_properties:
    raise SystemExit("FAIL AI evaluator materiality must be expressed against the recommendation")
if "materiallyInformedDecision" in evaluator_properties:
    raise SystemExit("FAIL stale materiallyInformedDecision field remains in the schema")
if set(manifest_schema.get("required", [])) != {"manifestVersion", "commitment", "revealStatus", "models", "humanReviewPolicy"}:
    raise SystemExit("FAIL evaluator manifest minimum provenance envelope changed")
if "aiRecommendationOverridden" not in decision_properties or "humanOverride" in decision_properties:
    raise SystemExit("FAIL AI departure field is missing or stale generic override field remains")
for required_policy_field in {"publicRulesUri", "surfaceSources", "previousVersion", "changeNoticeUri", "priorEvaluationsRerun"}:
    if required_policy_field not in governing_policy_properties:
        raise SystemExit(f"FAIL governing-policy traceability field missing: {required_policy_field}")
expected_policy_surfaces = {"mandate", "eligibility", "evaluationCriteria", "conflictRules", "decisionProcedure"}
if set(policy_surface_schema.get("required", [])) != expected_policy_surfaces:
    raise SystemExit("FAIL governing-policy decision-surface map changed")
if set(finding_classifications) != {"supported-fact", "judgment", "uncertainty", "unverified-claim"}:
    raise SystemExit("FAIL material-finding classification must remain epistemic")
for required_conflict_field in {"affectedDecisionSurfaces", "substitutionUsed", "substituteEvaluatorId"}:
    if required_conflict_field not in conflict_properties:
        raise SystemExit(f"FAIL recusal provenance field missing: {required_conflict_field}")
if example["program"].get("submissionDeadline") != "2026-08-05T23:59:00Z":
    raise SystemExit("FAIL Marketplace example submission deadline changed from the published process")
if example["governingPolicy"].get("publicRulesUri") not in example["governingPolicy"].get("sources", []):
    raise SystemExit("FAIL Marketplace publicRulesUri is not declared as a governing source")
if set(example["governingPolicy"].get("surfaceSources", {})) != expected_policy_surfaces:
    raise SystemExit("FAIL Marketplace example does not map every governing decision surface")

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
print("PASS AI materiality is defined against the recommendation")
print("PASS evaluator manifest has the minimum provenance envelope")
print("PASS AI recommendation departure field is explicit")
print("PASS governing policy exposes public rules and all five decision surfaces")
print("PASS in-round policy changes can identify prior version, disclosure, and rerun status")
print("PASS material-finding classification remains epistemic")
print("PASS recusal decision-surface and substitution provenance are representable")
print("PASS Marketplace submission deadline matches the published process")
print("PASS Marketplace governing-policy surface mapping is complete")
print(f"PASS Simocracy allocations reconcile to ${recorded_total}")
