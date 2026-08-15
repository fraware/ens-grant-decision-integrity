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


def findings(record):
    return validate_record(record, SCHEMA)


def codes(record):
    return {finding.code for finding in findings(record)}


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
    got = findings(record)
    errors = [finding.render() for finding in got if finding.severity == "error"]
    if errors:
        raise AssertionError(f"{label} has errors: {errors}")
    print(f"PASS {label}")


base_findings = findings(BASE)
if any(item.severity == "error" for item in base_findings):
    raise AssertionError(f"canonical example has errors: {[x.render() for x in base_findings]}")
if "CHAL003" not in {item.code for item in base_findings}:
    raise AssertionError("canonical pending example should expose the undocumented correction path")
print("PASS canonical example: no errors; expected CHAL003 warning exposed")

expect("pending record cannot claim a decision timestamp", "SCHEMA", lambda record: record["decision"].update({"decidedAt": "2026-08-15T13:00:00Z"}))


def make_approved(record):
    record["eligibility"]["status"] = "eligible"
    for rule in record["eligibility"]["rules"]:
        rule["result"] = "pass"
    record["evaluators"] = [{"evaluatorId":"human-final","displayName":"Illustrative decision-maker","kind":"human","role":"decision authority","participated":True,"recused":False,"recusalReason":None}]
    record["evaluation"]["materialFindings"] = [{"findingId":"F1","statement":"Illustrative final finding.","classification":"judgment","evidenceIds":[],"evaluatorIds":["human-final"],"materiality":"high"}]
    record["decision"].update({"status":"approved","authority":"Illustrative decision-maker","authorityKind":"human","decidedAt":"2026-08-16T13:00:00Z","awardedAmount":100000,"currency":"USD","rationale":"Illustrative decision rationale.","quorum":None,"decisionRule":None})
    record["challenge"].update({"status":"not-open","scope":"Factual and procedural correction only.","processDefined":True})


def approved_without_delivery(record):
    make_approved(record)
    record["deliveryConditions"] = []


def supported_fact_without_evidence(record):
    record["evaluation"]["materialFindings"] = [{"findingId":"F1","statement":"Claim presented as fact.","classification":"supported-fact","evidenceIds":[],"evaluatorIds":["committee"],"materiality":"high"}]


def broken_reference(record):
    record["eligibility"]["rules"][0]["evidenceIds"] = ["DOES-NOT-EXIST"]


def eligible_with_failed_rule(record):
    record["eligibility"]["status"] = "eligible"
    record["eligibility"]["rules"][0]["result"] = "fail"


def recused_but_participating(record):
    record["evaluators"].append({"evaluatorId":"human-1","displayName":"Illustrative reviewer","kind":"human","role":"reviewer","participated":True,"recused":True,"recusalReason":"Illustrative conflict."})


def unresolved_conflict(record):
    make_approved(record)
    record["conflicts"] = [{"conflictId":"C1","subjectId":"human-final","description":"Material relationship with applicant.","status":"unresolved","resolution":None}]


def committee_without_members(record):
    make_approved(record)
    record["evaluators"] = [{"evaluatorId":"committee","displayName":"Illustrative committee","kind":"committee","role":"decision authority","participated":True,"recused":False,"recusalReason":None}]
    record["evaluation"]["materialFindings"][0]["evaluatorIds"] = ["committee"]
    record["decision"].update({"authority":"Illustrative committee","authorityKind":"committee","quorum":"3 of 4","decisionRule":"simple majority"})


def material_ai_without_manifest(record):
    record["evaluators"].append({"evaluatorId":"ai-screen","displayName":"Illustrative AI evaluator","kind":"ai","role":"screening","participated":True,"recused":False,"recusalReason":None,"materiallyInformedDecision":True})


def final_without_challenge_process(record):
    make_approved(record)
    record["challenge"]["processDefined"] = False


def ineligible_without_failed_rule(record):
    record["eligibility"]["status"] = "ineligible"
    for rule in record["eligibility"]["rules"]:
        rule["result"] = "pass"
    record["decision"].update({"status":"ineligible","decidedAt":"2026-08-16T13:00:00Z","rationale":"Illustrative eligibility disposition.","awardedAmount":None})
    record["challenge"]["processDefined"] = True


def valid_ineligible(record):
    record["eligibility"]["status"] = "ineligible"
    record["eligibility"]["rationale"] = "Eligibility rule E1 failed."
    record["eligibility"]["rules"][0]["result"] = "fail"
    for rule in record["eligibility"]["rules"][1:]:
        rule["result"] = "not-applicable"
    record["evaluators"] = [{"evaluatorId":"human-gate","displayName":"Illustrative eligibility reviewer","kind":"human","role":"eligibility review","participated":True,"recused":False,"recusalReason":None}]
    record["decision"].update({"status":"ineligible","authority":"Illustrative eligibility reviewer","authorityKind":"human","decidedAt":"2026-08-16T13:00:00Z","rationale":"Returned without scoring after failing eligibility rule E1.","awardedAmount":None,"quorum":None,"decisionRule":None})
    record["challenge"].update({"scope":"Correction of factual or procedural eligibility errors.","processDefined":True})


def retrospective_final_record(record):
    make_approved(record)
    record["decision"]["decidedAt"] = "2026-08-10T13:00:00Z"
    record["timestamps"]["createdAt"] = "2026-08-15T13:00:00Z"
    record["timestamps"]["updatedAt"] = "2026-08-15T13:00:00Z"


expect("approval requires delivery conditions", "SCHEMA", approved_without_delivery)
expect("supported fact requires evidence", "SCHEMA", supported_fact_without_evidence)
expect("broken evidence reference is rejected", "REF101", broken_reference)
expect("eligible summary cannot contain a failed rule", "ELIG001", eligible_with_failed_rule)
expect("recused evaluator cannot participate", "COI002", recused_but_participating)
expect("adjudication requires conflict closure", "COI001", unresolved_conflict)
expect("committee decision requires participating human members", "AUTH001", committee_without_members)
expect("material AI use without manifest is surfaced", "AI001", material_ai_without_manifest)
expect("adjudication requires a correction path", "CHAL002", final_without_challenge_process)
expect("ineligible summary requires a failed rule", "ELIG002", ineligible_without_failed_rule)
expect_no_errors("valid ineligible hard-screen record", valid_ineligible)
expect_no_errors("retrospective finalized record", retrospective_final_record)

print("PASS adversarial conformance suite")
