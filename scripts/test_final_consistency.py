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


def finalize_human(record, include_committee_evaluator=False):
    record["eligibility"]["status"] = "eligible"
    for rule in record["eligibility"]["rules"]:
        rule["result"] = "pass"
    record["evaluators"] = [{
        "evaluatorId": "human-final",
        "displayName": "Illustrative decision-maker",
        "kind": "human",
        "role": "decision authority",
        "participated": True,
        "recused": False,
        "recusalReason": None,
    }]
    if include_committee_evaluator:
        record["evaluators"].append({
            "evaluatorId": "committee-review",
            "displayName": "Illustrative review committee",
            "kind": "committee",
            "role": "advisory evaluation",
            "participated": True,
            "recused": False,
            "recusalReason": None,
        })
    record["evaluation"]["materialFindings"] = [{
        "findingId": "F1",
        "statement": "Illustrative final finding.",
        "classification": "judgment",
        "evidenceIds": [],
        "evaluatorIds": ["human-final"],
        "materiality": "high",
    }]
    record["decision"].update({
        "status": "approved",
        "authority": "Illustrative decision-maker",
        "authorityKind": "human",
        "decidedAt": "2026-08-16T13:00:00Z",
        "awardedAmount": 100000,
        "currency": "USD",
        "rationale": "Illustrative decision rationale.",
        "aiRecommendationOverridden": False,
        "aiOverrideRationale": None,
        "quorum": None,
        "decisionRule": None,
    })
    record["challenge"].update({
        "status": "not-open",
        "scope": "Factual and procedural correction only.",
        "processDefined": True,
        "resolution": None,
    })
    record["timestamps"]["updatedAt"] = "2026-08-16T13:00:00Z"


def disagreement_from_nonparticipant(record):
    record["evaluation"]["disagreements"] = [{
        "disagreementId": "D1",
        "issue": "Illustrative disagreement.",
        "evaluatorIds": ["committee"],
        "status": "open",
        "resolution": None,
    }]


def disagreement_without_attribution(record):
    record["evaluation"]["disagreements"] = [{
        "disagreementId": "D1",
        "issue": "Illustrative unattributed disagreement.",
        "evaluatorIds": [],
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


def failed_eligibility_without_evidence(record):
    record["eligibility"]["rules"][0]["result"] = "fail"
    record["eligibility"]["rules"][0]["evidenceIds"] = []


def conflict_claims_recusal_without_evaluator_recusal(record):
    record["evaluators"].append({
        "evaluatorId": "human-reviewer",
        "displayName": "Illustrative reviewer",
        "kind": "human",
        "role": "reviewer",
        "participated": True,
        "recused": False,
        "recusalReason": None,
    })
    record["conflicts"] = [{
        "conflictId": "C1",
        "subjectId": "human-reviewer",
        "description": "Illustrative conflict.",
        "status": "recused",
        "resolution": "Illustrative recusal record.",
        "affectedDecisionSurfaces": ["application scoring"],
        "substitutionUsed": False,
        "substituteEvaluatorId": None,
    }]


def human_authority_with_committee_evaluator(record):
    finalize_human(record, include_committee_evaluator=True)


def active_challenge_without_process(record):
    record["challenge"].update({"status": "open", "processDefined": False})


def pending_with_submitted_challenge(record):
    record["challenge"].update({"status": "submitted", "processDefined": True})


def resolved_challenge_without_resolution(record):
    finalize_human(record)
    record["challenge"].update({"status": "resolved", "processDefined": True, "resolution": None})


def eligibility_check_after_adjudication(record):
    finalize_human(record)
    record["eligibility"]["checkedAt"] = "2026-08-17T13:00:00Z"


def decision_after_last_update(record):
    finalize_human(record)
    record["timestamps"]["updatedAt"] = "2026-08-15T13:00:00Z"


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
expect("recorded disagreement requires attribution", "EVAL005", disagreement_without_attribution)
expect_no_errors("valid disagreement attribution", valid_disagreement)
expect("failed eligibility gate requires evidence", "EVID004", failed_eligibility_without_evidence)
expect("conflict recusal must agree with evaluator state", "COI009", conflict_claims_recusal_without_evaluator_recusal)
expect_no_errors("committee evaluator does not convert human authority into committee authority", human_authority_with_committee_evaluator)
expect("active challenge requires a defined process", "CHAL004", active_challenge_without_process)
expect("pending decision cannot claim submitted challenge", "CHAL005", pending_with_submitted_challenge)
expect("resolved challenge requires resolution", "CHAL006", resolved_challenge_without_resolution)
expect("eligibility check cannot postdate adjudication", "TIME004", eligibility_check_after_adjudication)
expect("decision cannot postdate record update", "TIME005", decision_after_last_update)
expect("AI rationale requires a recorded departure", "AI009", stale_ai_departure_rationale)
expect("no-change policy record rejects stale change metadata", "POL006", stale_policy_change_metadata)
expect_no_errors("canonical no-change policy metadata", canonical_no_change)

print("PASS final cross-field consistency suite")
