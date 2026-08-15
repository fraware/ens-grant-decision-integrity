#!/usr/bin/env python3
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from conformance import validate_record  # noqa: E402

SCHEMA = json.loads((ROOT / "schema" / "grant-decision-record.schema.json").read_text(encoding="utf-8"))
BASE = json.loads((ROOT / "examples" / "spp3-marketplace-rfp.example.json").read_text(encoding="utf-8"))


def codes(record):
    return {finding.code for finding in validate_record(record, SCHEMA)}


def expect(label, code, mutate):
    record = copy.deepcopy(BASE)
    mutate(record)
    got = codes(record)
    if code not in got:
        raise AssertionError(f"{label}: expected {code}, got {sorted(got)}")
    print(f"PASS {label}: {code}")


def expect_no_errors(label, mutate):
    record = copy.deepcopy(BASE)
    mutate(record)
    errors = [finding.render() for finding in validate_record(record, SCHEMA) if finding.severity == "error"]
    if errors:
        raise AssertionError(f"{label}: {errors}")
    print(f"PASS {label}")


def disagreement_from_nonparticipant(record):
    record["evaluation"]["disagreements"] = [{
        "disagreementId": "D1",
        "issue": "Illustrative disagreement.",
        "evaluatorIds": ["committee"],
        "status": "open",
        "resolution": None,
    }]


def valid_disagreement(record):
    record["evaluators"].append({
        "evaluatorId": "human-reviewer",
        "displayName": "Illustrative reviewer",
        "kind": "human",
        "role": "reviewer",
        "participated": True,
        "recused": False,
        "recusalReason": None,
    })
    record["evaluation"]["disagreements"] = [{
        "disagreementId": "D1",
        "issue": "Illustrative disagreement.",
        "evaluatorIds": ["human-reviewer"],
        "status": "open",
        "resolution": None,
    }]


def stale_ai_departure_rationale(record):
    record["decision"]["aiRecommendationOverridden"] = False
    record["decision"]["aiOverrideRationale"] = "Stale departure rationale."


def stale_policy_change_metadata(record):
    record["governingPolicy"]["changeDuringReview"] = False
    record["governingPolicy"]["changeSummary"] = "Stale change metadata."


def canonical_no_change(record):
    # The canonical example is the positive control for a no-change policy record.
    pass


expected_eligibility_rule_ids = ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]
actual_eligibility_rule_ids = [rule["ruleId"] for rule in BASE["eligibility"]["rules"]]
if actual_eligibility_rule_ids != expected_eligibility_rule_ids:
    raise AssertionError(
        f"Marketplace eligibility mapping drifted: expected {expected_eligibility_rule_ids}, got {actual_eligibility_rule_ids}"
    )
if BASE["eligibility"]["rules"][-1]["description"] != "Application acknowledges the SPP3 Program Terms and Award Notice":
    raise AssertionError("Marketplace eligibility mapping is missing the Program Terms/Award Notice acknowledgment gate")
print("PASS Marketplace eligibility mapping preserves all seven published gates")

expected_rubric_weights = {"M1": 0.25, "M2": 0.20, "M3": 0.35, "M4": 0.10, "M5": 0.10}
actual_rubric_weights = {criterion["criterionId"]: criterion.get("weight") for criterion in BASE["evaluation"]["criteria"]}
if actual_rubric_weights != expected_rubric_weights:
    raise AssertionError(
        f"Marketplace rubric mapping drifted: expected {expected_rubric_weights}, got {actual_rubric_weights}"
    )
print("PASS Marketplace rubric mapping preserves published M1–M5 weights")

expect("disagreement requires participating, non-recused attribution", "EVAL004", disagreement_from_nonparticipant)
expect_no_errors("valid disagreement attribution", valid_disagreement)
expect("AI rationale requires a recorded departure", "AI009", stale_ai_departure_rationale)
expect("no-change policy record rejects stale change metadata", "POL006", stale_policy_change_metadata)
expect_no_errors("canonical no-change policy metadata", canonical_no_change)

print("PASS final cross-field consistency suite")
