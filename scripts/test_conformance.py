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


def expect(code, mutate):
    record = copy.deepcopy(BASE)
    mutate(record)
    got = codes(record)
    if code not in got:
        raise AssertionError(f"expected {code}, got {sorted(got)}")
    print(f"PASS rejects {code}")


if validate_record(BASE, SCHEMA):
    raise AssertionError("canonical example must pass")
print("PASS canonical example")

expect("SCHEMA", lambda r: r["decision"].update({"decidedAt": "2026-08-15T13:00:00Z"}))


def approved_without_delivery(r):
    r["eligibility"]["status"] = "eligible"
    for rule in r["eligibility"]["rules"]:
        rule["result"] = "pass"
    r["decision"].update({
        "status": "approved",
        "decidedAt": "2026-08-16T13:00:00Z",
        "awardedAmount": 100000,
        "currency": "USD",
    })
    r["deliveryConditions"] = []
expect("SCHEMA", approved_without_delivery)


def supported_fact_without_evidence(r):
    r["evaluation"]["materialFindings"] = [{
        "findingId": "F1",
        "statement": "Claim presented as fact.",
        "classification": "supported-fact",
        "evidenceIds": [],
        "evaluatorIds": ["committee"],
        "materiality": "high",
    }]
expect("SCHEMA", supported_fact_without_evidence)


def broken_reference(r):
    r["eligibility"]["rules"][0]["evidenceIds"] = ["DOES-NOT-EXIST"]
expect("REF101", broken_reference)


def unresolved_conflict(r):
    r["eligibility"]["status"] = "eligible"
    for rule in r["eligibility"]["rules"]:
        rule["result"] = "pass"
    r["decision"].update({
        "status": "approved",
        "decidedAt": "2026-08-16T13:00:00Z",
        "awardedAmount": 100000,
        "currency": "USD",
    })
    r["conflicts"] = [{
        "conflictId": "C1",
        "subjectId": "committee",
        "description": "Material relationship with applicant.",
        "status": "unresolved",
        "resolution": None,
    }]
expect("COI001", unresolved_conflict)


def committee_without_members(r):
    r["eligibility"]["status"] = "eligible"
    for rule in r["eligibility"]["rules"]:
        rule["result"] = "pass"
    r["evaluators"][0]["participated"] = True
    r["decision"].update({
        "status": "approved",
        "decidedAt": "2026-08-16T13:00:00Z",
        "awardedAmount": 100000,
        "currency": "USD",
        "quorum": "3 of 4",
        "decisionRule": "majority",
    })
expect("AUTH001", committee_without_members)


def material_ai_without_manifest(r):
    r["evaluators"].append({
        "evaluatorId": "automated-screen",
        "displayName": "Illustrative automated evaluator",
        "kind": "ai",
        "role": "screening",
        "participated": True,
        "recused": False,
        "recusalReason": None,
        "materiallyInformedDecision": True,
    })
expect("AI001", material_ai_without_manifest)

print("PASS adversarial conformance suite")
