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
    record["decision"].update({"status":"approved","authority":"Illustrative decision-maker","authorityKind":"human","decidedAt":"2026-08-16T13:00:00Z","awardedAmount":100000,"currency":"USD","rationale":"Illustrative decision rationale.","aiRecommendationOverridden":False,"aiOverrideRationale":None,"quorum":None,"decisionRule":None})
    record["challenge"].update({"status":"not-open","scope":"Factual and procedural correction only.","processDefined":True})


def add_material_ai(record):
    record["evaluators"].append({"evaluatorId":"ai-screen","displayName":"Illustrative AI evaluator","kind":"ai","role":"screening","participated":True,"recused":False,"recusalReason":None,"materiallyInformedRecommendation":True})


def add_valid_manifest(record):
    record["evaluatorManifest"] = {
        "manifestVersion": "illustrative-v1",
        "commitment": {
            "algorithm": "sha256",
            "digest": "illustrative-commitment-digest",
            "committedAt": "2026-08-05T20:00:00Z",
        },
        "revealStatus": "committed",
        "revealUri": None,
        "models": [{"provider": "Illustrative Provider", "model": "Illustrative Model", "version": "v1"}],
        "retrievalSources": ["public ENS artifacts"],
        "humanReviewPolicy": "AI outputs are advisory; the identified human authority makes the funding decision.",
    }


def approved_without_delivery(record):
    make_approved(record)
    record["deliveryConditions"] = []


def supported_fact_without_evidence(record):
    record["evaluation"]["materialFindings"] = [{"findingId":"F1","statement":"Claim presented as fact.","classification":"supported-fact","evidenceIds":[],"evaluatorIds":["committee"],"materiality":"high"}]


def invalid_risk_classification(record):
    make_approved(record)
    record["evaluation"]["materialFindings"][0]["classification"] = "risk"


def finding_from_nonparticipant(record):
    record["evaluation"]["materialFindings"] = [{"findingId":"F1","statement":"Illustrative judgment.","classification":"judgment","evidenceIds":[],"evaluatorIds":["committee"],"materiality":"high"}]


def nonpublic_evidence_without_locator(record):
    record["evidence"][0]["disclosure"] = "confidential"
    record["evidence"][0].pop("uri", None)
    record["evidence"][0].pop("contentHash", None)


def nonpublic_evidence_with_uri(record):
    record["evidence"][0]["disclosure"] = "confidential"


def broken_reference(record):
    record["eligibility"]["rules"][0]["evidenceIds"] = ["DOES-NOT-EXIST"]


def eligible_with_failed_rule(record):
    record["eligibility"]["status"] = "eligible"
    record["eligibility"]["rules"][0]["result"] = "fail"


def recused_but_participating(record):
    record["evaluators"].append({"evaluatorId":"human-1","displayName":"Illustrative reviewer","kind":"human","role":"reviewer","participated":True,"recused":True,"recusalReason":"Illustrative conflict."})


def recusal_without_surface(record):
    record["evaluators"].append({"evaluatorId":"human-recused","displayName":"Illustrative reviewer","kind":"human","role":"reviewer","participated":False,"recused":True,"recusalReason":"Illustrative conflict."})
    record["conflicts"] = [{"conflictId":"C-recusal","subjectId":"human-recused","description":"Illustrative conflict.","status":"recused","resolution":"Reviewer recused."}]


def valid_recusal_without_substitute(record):
    record["evaluators"].append({"evaluatorId":"human-recused","displayName":"Illustrative reviewer","kind":"human","role":"reviewer","participated":False,"recused":True,"recusalReason":"Illustrative conflict."})
    record["conflicts"] = [{"conflictId":"C-recusal","subjectId":"human-recused","description":"Illustrative conflict.","status":"recused","resolution":"Reviewer recused.","affectedDecisionSurfaces":["application scoring"],"substitutionUsed":False,"substituteEvaluatorId":None}]


def recusal_with_unknown_substitute(record):
    record["evaluators"].append({"evaluatorId":"human-recused","displayName":"Illustrative reviewer","kind":"human","role":"reviewer","participated":False,"recused":True,"recusalReason":"Illustrative conflict."})
    record["conflicts"] = [{"conflictId":"C-recusal","subjectId":"human-recused","description":"Illustrative conflict.","status":"recused","resolution":"Reviewer recused and replaced.","affectedDecisionSurfaces":["application scoring"],"substitutionUsed":True,"substituteEvaluatorId":"missing-reviewer"}]


def valid_recusal_with_substitute(record):
    record["evaluators"].extend([
        {"evaluatorId":"human-recused","displayName":"Illustrative reviewer","kind":"human","role":"reviewer","participated":False,"recused":True,"recusalReason":"Illustrative conflict."},
        {"evaluatorId":"human-substitute","displayName":"Illustrative substitute","kind":"human","role":"reviewer","participated":True,"recused":False,"recusalReason":None},
    ])
    record["conflicts"] = [{"conflictId":"C-recusal","subjectId":"human-recused","description":"Illustrative conflict.","status":"recused","resolution":"Reviewer recused and replaced.","affectedDecisionSurfaces":["application scoring"],"substitutionUsed":True,"substituteEvaluatorId":"human-substitute"}]


def unresolved_conflict(record):
    make_approved(record)
    record["conflicts"] = [{"conflictId":"C1","subjectId":"human-final","description":"Material relationship with applicant.","status":"unresolved","resolution":None}]


def committee_without_members(record):
    make_approved(record)
    record["evaluators"] = [{"evaluatorId":"committee","displayName":"Illustrative committee","kind":"committee","role":"decision authority","participated":True,"recused":False,"recusalReason":None}]
    record["evaluation"]["materialFindings"][0]["evaluatorIds"] = ["committee"]
    record["decision"].update({"authority":"Illustrative committee","authorityKind":"committee","quorum":"3 of 4","decisionRule":"simple majority"})


def material_ai_without_manifest(record):
    add_material_ai(record)


def material_ai_without_participation(record):
    record["evaluators"].append({"evaluatorId":"ai-screen","displayName":"Illustrative AI evaluator","kind":"ai","role":"screening","participated":False,"recused":False,"recusalReason":None,"materiallyInformedRecommendation":True})


def material_ai_with_empty_manifest(record):
    add_material_ai(record)
    record["evaluatorManifest"] = {}


def valid_material_ai(record):
    add_material_ai(record)
    add_valid_manifest(record)


def material_ai_without_deadline(record):
    valid_material_ai(record)
    record["program"].pop("submissionDeadline")


def late_ai_commitment(record):
    valid_material_ai(record)
    record["evaluatorManifest"]["commitment"]["committedAt"] = record["program"]["submissionDeadline"]


def override_without_material_ai(record):
    record["decision"]["aiRecommendationOverridden"] = True
    record["decision"]["aiOverrideRationale"] = "Illustrative departure rationale."


def valid_ai_override(record):
    valid_material_ai(record)
    record["decision"]["aiRecommendationOverridden"] = True
    record["decision"]["aiOverrideRationale"] = "Human reviewers disagreed with the AI recommendation for documented reasons."


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


def pending_with_positive_award(record):
    record["decision"]["awardedAmount"] = 100


def deferred_with_positive_award(record):
    record["evaluators"] = [{"evaluatorId":"human-defer","displayName":"Illustrative decision-maker","kind":"human","role":"decision authority","participated":True,"recused":False,"recusalReason":None}]
    record["decision"].update({"status":"deferred","authority":"Illustrative decision-maker","authorityKind":"human","decidedAt":"2026-08-16T13:00:00Z","rationale":"Decision deferred pending additional evidence.","awardedAmount":100,"quorum":None,"decisionRule":None})


def retrospective_final_record(record):
    make_approved(record)
    record["decision"]["decidedAt"] = "2026-08-10T13:00:00Z"
    record["timestamps"]["createdAt"] = "2026-08-15T13:00:00Z"
    record["timestamps"]["updatedAt"] = "2026-08-15T13:00:00Z"


def suspended_without_findings(record):
    make_approved(record)
    record["decision"]["status"] = "suspended"
    record["decision"]["rationale"] = "Illustrative suspension rationale."
    record["evaluation"]["materialFindings"] = []


def deferred_without_rationale(record):
    record["evaluators"] = [{"evaluatorId":"human-defer","displayName":"Illustrative decision-maker","kind":"human","role":"decision authority","participated":True,"recused":False,"recusalReason":None}]
    record["decision"].update({"status":"deferred","authority":"Illustrative decision-maker","authorityKind":"human","decidedAt":"2026-08-16T13:00:00Z","rationale":None,"quorum":None,"decisionRule":None})


def undeclared_public_rules_uri(record):
    record["governingPolicy"]["publicRulesUri"] = "https://example.invalid/undeclared-policy"


def missing_surface_source(record):
    record["governingPolicy"]["surfaceSources"].pop("conflictRules")


def undeclared_surface_source(record):
    record["governingPolicy"]["surfaceSources"]["evaluationCriteria"] = "https://example.invalid/undeclared-rubric"


def policy_change_without_rerun_statement(record):
    record["governingPolicy"].update({
        "changeDuringReview": True,
        "changeSummary": "Illustrative in-round policy correction.",
        "previousVersion": "public-artifacts-2026-07-19",
        "changeNoticeUri": record["governingPolicy"]["publicRulesUri"],
    })


def self_referential_previous_version(record):
    valid_policy_change(record)
    record["governingPolicy"]["previousVersion"] = record["governingPolicy"]["version"]


def undeclared_change_notice(record):
    valid_policy_change(record)
    record["governingPolicy"]["changeNoticeUri"] = "https://example.invalid/undeclared-change-notice"


def valid_policy_change(record):
    record["governingPolicy"].update({
        "changeDuringReview": True,
        "changeSummary": "Illustrative in-round policy correction.",
        "priorEvaluationsRerun": False,
        "previousVersion": "public-artifacts-2026-07-19",
        "changeNoticeUri": record["governingPolicy"]["publicRulesUri"],
    })


expect("approval requires delivery conditions", "SCHEMA", approved_without_delivery)
expect("supported fact requires evidence", "SCHEMA", supported_fact_without_evidence)
expect("risk is not an epistemic finding classification", "SCHEMA", invalid_risk_classification)
expect("finding cannot be attributed to a non-participant", "EVAL003", finding_from_nonparticipant)
expect("non-public evidence without locator is surfaced", "EVID003", nonpublic_evidence_without_locator)
expect_no_errors("non-public evidence with a URI remains usable", nonpublic_evidence_with_uri)
expect("broken evidence reference is rejected", "REF101", broken_reference)
expect("eligible summary cannot contain a failed rule", "ELIG001", eligible_with_failed_rule)
expect("recused evaluator cannot participate", "COI002", recused_but_participating)
expect("recusal requires affected decision surface", "COI004", recusal_without_surface)
expect_no_errors("valid recusal without substitute", valid_recusal_without_substitute)
expect("recusal substitute must resolve", "REF107", recusal_with_unknown_substitute)
expect_no_errors("valid recusal with substitute", valid_recusal_with_substitute)
expect("adjudication requires conflict closure", "COI001", unresolved_conflict)
expect("committee decision requires participating human members", "AUTH001", committee_without_members)
expect("AI cannot materially inform recommendation without participating", "AI008", material_ai_without_participation)
expect("material AI use requires a manifest", "AI001", material_ai_without_manifest)
expect("empty AI manifest cannot satisfy provenance", "SCHEMA", material_ai_with_empty_manifest)
expect("material AI use requires a submission deadline", "AI004", material_ai_without_deadline)
expect("AI manifest commitment must precede the deadline", "AI005", late_ai_commitment)
expect("AI departure requires material AI use", "AI006", override_without_material_ai)
expect_no_errors("valid material AI provenance", valid_material_ai)
expect_no_errors("valid AI recommendation departure", valid_ai_override)
expect("adjudication requires a correction path", "CHAL002", final_without_challenge_process)
expect("ineligible summary requires a failed rule", "ELIG002", ineligible_without_failed_rule)
expect_no_errors("valid ineligible hard-screen record", valid_ineligible)
expect("pending record cannot carry a positive award", "DEC013", pending_with_positive_award)
expect("deferred record cannot carry a positive award", "DEC013", deferred_with_positive_award)
expect_no_errors("retrospective finalized record", retrospective_final_record)
expect("suspension requires attributable findings", "DEC008", suspended_without_findings)
expect("deferral requires a rationale", "DEC012", deferred_without_rationale)
expect("public governing-policy URI must be declared", "POL002", undeclared_public_rules_uri)
expect("all five governing-policy surfaces are required", "SCHEMA", missing_surface_source)
expect("decision-surface source must be declared", "POL003", undeclared_surface_source)
expect("in-round policy change requires rerun statement", "SCHEMA", policy_change_without_rerun_statement)
expect("previous policy version must differ from active version", "POL004", self_referential_previous_version)
expect("policy change notice must be a declared source", "POL005", undeclared_change_notice)
expect_no_errors("valid in-round policy change record", valid_policy_change)

print("PASS adversarial conformance suite")
