#!/usr/bin/env python3
"""Cross-field conformance checks for ENS Grant Decision Integrity records.

JSON Schema checks structure. This module checks relations across fields that
encode the v0.1 decision-integrity profile.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "schema" / "grant-decision-record.schema.json"
SCHEMA_02_PATH = ROOT / "schema" / "grant-decision-record-0.2.schema.json"

DECIDED_STATUSES = {"ineligible", "approved", "rejected", "deferred", "suspended"}
SUBSTANTIVE_STATUSES = {"approved", "rejected", "suspended"}
ADJUDICATED_STATUSES = {"ineligible", "approved", "rejected", "suspended"}
AUTHORITY_KINDS = {"human", "committee", "dao-vote", "multisig", "other-human-authority"}
CONTENT_HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.severity.upper()} {self.code} {self.path}: {self.message}"


def _iso(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _ids(items: Iterable[dict], key: str) -> list[str]:
    return [item.get(key) for item in items if isinstance(item.get(key), str)]


def _check_unique(findings: list[Finding], items: list[dict], key: str, path: str, code: str) -> set[str]:
    seen: set[str] = set()
    for idx, value in enumerate(_ids(items, key)):
        if value in seen:
            findings.append(Finding("error", code, f"{path}[{idx}].{key}", f"duplicate identifier {value!r}"))
        seen.add(value)
    return seen


def check_semantics(record: dict) -> list[Finding]:
    findings: list[Finding] = []

    evaluators = record.get("evaluators", [])
    evidence = record.get("evidence", [])
    criteria = record.get("evaluation", {}).get("criteria", [])
    material_findings = record.get("evaluation", {}).get("materialFindings", [])
    disagreements = record.get("evaluation", {}).get("disagreements", [])
    conflicts = record.get("conflicts", [])
    delivery = record.get("deliveryConditions", [])
    eligibility_rules = record.get("eligibility", {}).get("rules", [])

    evaluator_ids = _check_unique(findings, evaluators, "evaluatorId", "evaluators", "REF001")
    evaluator_by_id = {evaluator.get("evaluatorId"): evaluator for evaluator in evaluators if isinstance(evaluator.get("evaluatorId"), str)}
    evidence_ids = _check_unique(findings, evidence, "evidenceId", "evidence", "REF002")
    finding_ids = _check_unique(findings, material_findings, "findingId", "evaluation.materialFindings", "REF003")
    _check_unique(findings, criteria, "criterionId", "evaluation.criteria", "REF004")
    _check_unique(findings, disagreements, "disagreementId", "evaluation.disagreements", "REF005")
    _check_unique(findings, conflicts, "conflictId", "conflicts", "REF006")
    _check_unique(findings, delivery, "conditionId", "deliveryConditions", "REF007")
    _check_unique(findings, eligibility_rules, "ruleId", "eligibility.rules", "REF008")

    for i, rule in enumerate(eligibility_rules):
        evidence_refs = rule.get("evidenceIds", [])
        for ref in evidence_refs:
            if ref not in evidence_ids:
                findings.append(Finding("error", "REF101", f"eligibility.rules[{i}].evidenceIds", f"unknown evidenceId {ref!r}"))
        if rule.get("result") == "fail" and not evidence_refs:
            findings.append(Finding("error", "EVID004", f"eligibility.rules[{i}].evidenceIds", "failed eligibility rule requires at least one evidence reference"))

    for i, item in enumerate(material_findings):
        for ref in item.get("evidenceIds", []):
            if ref not in evidence_ids:
                findings.append(Finding("error", "REF102", f"evaluation.materialFindings[{i}].evidenceIds", f"unknown evidenceId {ref!r}"))
        for ref in item.get("evaluatorIds", []):
            if ref not in evaluator_ids:
                findings.append(Finding("error", "REF103", f"evaluation.materialFindings[{i}].evaluatorIds", f"unknown evaluatorId {ref!r}"))
                continue
            evaluator = evaluator_by_id[ref]
            if not evaluator.get("participated") or evaluator.get("recused"):
                findings.append(Finding("error", "EVAL003", f"evaluation.materialFindings[{i}].evaluatorIds", f"finding is attributed to non-participating or recused evaluator {ref!r}"))
        if item.get("classification") == "supported-fact" and not item.get("evidenceIds"):
            findings.append(Finding("error", "EVID001", f"evaluation.materialFindings[{i}]", "supported-fact requires at least one evidence reference"))

    for i, item in enumerate(evidence):
        if item.get("disclosure") != "public" and not item.get("uri") and not item.get("contentHash"):
            findings.append(Finding("warning", "EVID003", f"evidence[{i}]", "non-public evidence has neither a retrievable URI nor a content hash"))

    for i, criterion in enumerate(criteria):
        for ref in criterion.get("findingIds", []):
            if ref not in finding_ids:
                findings.append(Finding("error", "REF104", f"evaluation.criteria[{i}].findingIds", f"unknown findingId {ref!r}"))

    for i, item in enumerate(disagreements):
        refs = item.get("evaluatorIds", [])
        if not refs:
            findings.append(Finding("error", "EVAL005", f"evaluation.disagreements[{i}].evaluatorIds", "recorded disagreement must identify at least one evaluator"))
        for ref in refs:
            if ref not in evaluator_ids:
                findings.append(Finding("error", "REF105", f"evaluation.disagreements[{i}].evaluatorIds", f"unknown evaluatorId {ref!r}"))
                continue
            evaluator = evaluator_by_id[ref]
            if not evaluator.get("participated") or evaluator.get("recused"):
                findings.append(Finding("error", "EVAL004", f"evaluation.disagreements[{i}].evaluatorIds", f"disagreement is attributed to non-participating or recused evaluator {ref!r}"))

    for i, item in enumerate(delivery):
        for ref in item.get("evidenceIds", []):
            if ref not in evidence_ids:
                findings.append(Finding("error", "REF106", f"deliveryConditions[{i}].evidenceIds", f"unknown evidenceId {ref!r}"))

    for i, conflict in enumerate(conflicts):
        subject_id = conflict.get("subjectId")
        if conflict.get("status") == "recused" and subject_id in evaluator_by_id:
            subject = evaluator_by_id[subject_id]
            if not subject.get("recused") or subject.get("participated"):
                findings.append(Finding("error", "COI009", f"conflicts[{i}].status", f"conflict records evaluator {subject_id!r} as recused but evaluator state is inconsistent with recusal"))

    for i, evaluator in enumerate(evaluators):
        evaluator_id = evaluator.get("evaluatorId")
        if evaluator.get("kind") == "ai" and evaluator.get("materiallyInformedRecommendation") and not evaluator.get("participated"):
            findings.append(Finding("error", "AI008", f"evaluators[{i}].materiallyInformedRecommendation", "an AI evaluator cannot materially inform the recommendation without participating"))
        if evaluator.get("recused") and evaluator.get("participated"):
            findings.append(Finding("error", "COI002", f"evaluators[{i}]", "recused evaluator cannot also be marked as participating"))
        if evaluator.get("recused"):
            linked = [conflict for conflict in conflicts if conflict.get("subjectId") == evaluator_id and conflict.get("status") in {"recused", "resolved"}]
            if not linked:
                findings.append(Finding("error", "COI003", f"evaluators[{i}]", "recusal requires a linked conflict record in recused or resolved state"))
                continue
            for conflict in linked:
                conflict_id = conflict.get("conflictId")
                if not conflict.get("affectedDecisionSurfaces"):
                    findings.append(Finding("error", "COI004", f"conflicts[{conflict_id!r}].affectedDecisionSurfaces", "recusal must identify the decision surface from which the evaluator was excluded"))
                if not isinstance(conflict.get("substitutionUsed"), bool):
                    findings.append(Finding("error", "COI005", f"conflicts[{conflict_id!r}].substitutionUsed", "recusal must state whether a substitute evaluator was used"))
                    continue
                substitute_id = conflict.get("substituteEvaluatorId")
                if conflict.get("substitutionUsed"):
                    if substitute_id not in evaluator_ids:
                        findings.append(Finding("error", "REF107", f"conflicts[{conflict_id!r}].substituteEvaluatorId", f"unknown substitute evaluatorId {substitute_id!r}"))
                    elif substitute_id == evaluator_id:
                        findings.append(Finding("error", "COI006", f"conflicts[{conflict_id!r}].substituteEvaluatorId", "recused evaluator cannot substitute for itself"))
                    else:
                        substitute = evaluator_by_id[substitute_id]
                        if not substitute.get("participated") or substitute.get("recused"):
                            findings.append(Finding("error", "COI007", f"conflicts[{conflict_id!r}].substituteEvaluatorId", "substitute evaluator must participate and must not be recused"))
                elif substitute_id is not None:
                    findings.append(Finding("error", "COI008", f"conflicts[{conflict_id!r}].substituteEvaluatorId", "substituteEvaluatorId is inconsistent with substitutionUsed=false"))

    weights = [criterion.get("weight") for criterion in criteria]
    populated_weights = [weight for weight in weights if weight is not None]
    if populated_weights and len(populated_weights) != len(weights):
        findings.append(Finding("error", "EVAL001", "evaluation.criteria", "criterion weights are partially specified"))
    elif populated_weights and abs(sum(populated_weights) - 1.0) > 1e-9:
        findings.append(Finding("error", "EVAL002", "evaluation.criteria", f"criterion weights sum to {sum(populated_weights)!r}, expected 1.0"))

    governing_policy = record.get("governingPolicy", {})
    policy_sources = set(governing_policy.get("sources", []))
    public_rules_uri = governing_policy.get("publicRulesUri")
    if public_rules_uri not in policy_sources:
        findings.append(Finding("error", "POL002", "governingPolicy.publicRulesUri", "publicRulesUri must also appear in governingPolicy.sources"))
    for surface, source_uri in governing_policy.get("surfaceSources", {}).items():
        if source_uri not in policy_sources:
            findings.append(Finding("error", "POL003", f"governingPolicy.surfaceSources.{surface}", "decision-surface source must also appear in governingPolicy.sources"))
    if governing_policy.get("changeDuringReview"):
        if governing_policy.get("previousVersion") == governing_policy.get("version"):
            findings.append(Finding("error", "POL004", "governingPolicy.previousVersion", "previousVersion must differ from the active governing-policy version"))
        if governing_policy.get("changeNoticeUri") not in policy_sources:
            findings.append(Finding("error", "POL005", "governingPolicy.changeNoticeUri", "changeNoticeUri must also appear in governingPolicy.sources"))
    else:
        stale_change_fields = [
            field
            for field in ("changeSummary", "previousVersion", "changeNoticeUri", "priorEvaluationsRerun")
            if governing_policy.get(field) not in (None, "")
        ]
        if stale_change_fields:
            findings.append(Finding("error", "POL006", "governingPolicy", f"changeDuringReview=false conflicts with populated change metadata: {', '.join(stale_change_fields)}"))

    decision = record.get("decision", {})
    status = decision.get("status")
    decided_at = decision.get("decidedAt")
    eligibility = record.get("eligibility", {}).get("status")
    eligibility_rationale = record.get("eligibility", {}).get("rationale")

    if status == "pending" and decided_at is not None:
        findings.append(Finding("error", "DEC001", "decision.decidedAt", "pending records must not claim a decision timestamp"))
    if status in DECIDED_STATUSES and not decided_at:
        findings.append(Finding("error", "DEC002", "decision.decidedAt", "non-pending decision requires a decision timestamp"))

    rule_results = [rule.get("result") for rule in eligibility_rules]
    if eligibility == "eligible" and any(result not in {"pass", "not-applicable"} for result in rule_results):
        findings.append(Finding("error", "ELIG001", "eligibility.rules", "eligibility.status='eligible' conflicts with a failed or pending eligibility rule"))
    if eligibility == "ineligible" and "fail" not in rule_results:
        findings.append(Finding("error", "ELIG002", "eligibility.rules", "eligibility.status='ineligible' requires at least one failed rule"))

    if status in SUBSTANTIVE_STATUSES and eligibility != "eligible":
        findings.append(Finding("error", "DEC003", "eligibility.status", f"{status} decision requires eligibility.status='eligible'"))
    if status == "ineligible" and eligibility != "ineligible":
        findings.append(Finding("error", "DEC009", "eligibility.status", "decision.status='ineligible' requires eligibility.status='ineligible'"))

    if status in SUBSTANTIVE_STATUSES:
        if not (decision.get("rationale") or "").strip():
            findings.append(Finding("error", "DEC007", "decision.rationale", f"{status} decision requires a substantive rationale"))
        if not material_findings:
            findings.append(Finding("error", "DEC008", "evaluation.materialFindings", f"{status} decision requires at least one attributable material finding"))

    if status == "deferred" and not (decision.get("rationale") or "").strip():
        findings.append(Finding("error", "DEC012", "decision.rationale", "deferred decision requires a rationale"))

    if status == "ineligible":
        if not ((decision.get("rationale") or "").strip() or (eligibility_rationale or "").strip()):
            findings.append(Finding("error", "DEC010", "decision.rationale", "ineligible decision requires a rationale identifying the failed eligibility gate"))
        if decision.get("awardedAmount") not in (None, 0):
            findings.append(Finding("error", "DEC011", "decision.awardedAmount", "ineligible decision cannot carry a positive award"))

    if status in {"pending", "deferred"} and decision.get("awardedAmount") not in (None, 0):
        findings.append(Finding("error", "DEC013", "decision.awardedAmount", f"{status} record cannot carry a positive award"))

    if status in {"approved", "suspended"}:
        if not isinstance(decision.get("awardedAmount"), (int, float)) or decision.get("awardedAmount", 0) <= 0:
            findings.append(Finding("error", "DEC004", "decision.awardedAmount", f"{status} decision requires a positive award amount"))
        if not delivery:
            findings.append(Finding("error", "DEL001", "deliveryConditions", f"{status} award requires at least one observable delivery condition"))
    elif status == "rejected" and decision.get("awardedAmount") not in (None, 0):
        findings.append(Finding("error", "DEC005", "decision.awardedAmount", "rejected decision cannot carry a positive award"))

    if status in ADJUDICATED_STATUSES:
        for i, conflict in enumerate(conflicts):
            if conflict.get("status") in {"unresolved", "disclosed"}:
                findings.append(Finding("error", "COI001", f"conflicts[{i}].status", "adjudicated decision cannot leave a material conflict in disclosed or unresolved state"))

    authority_kind = decision.get("authorityKind")
    if status in DECIDED_STATUSES and authority_kind not in AUTHORITY_KINDS:
        findings.append(Finding("error", "AUTH000", "decision.authorityKind", "non-pending decision must identify a permitted human decision-authority type"))

    committee_decision = authority_kind == "committee"
    if status in DECIDED_STATUSES and committee_decision:
        participating_humans = [evaluator for evaluator in evaluators if evaluator.get("kind") == "human" and evaluator.get("participated") and not evaluator.get("recused")]
        if not participating_humans:
            findings.append(Finding("error", "AUTH001", "evaluators", "non-pending committee decision must identify participating human members"))
        if not (decision.get("quorum") or "").strip():
            findings.append(Finding("error", "AUTH002", "decision.quorum", "non-pending committee decision must record quorum"))
        if not (decision.get("decisionRule") or "").strip():
            findings.append(Finding("error", "AUTH003", "decision.decisionRule", "non-pending committee decision must record the applicable voting or consensus rule"))

    material_ai = [
        evaluator
        for evaluator in evaluators
        if evaluator.get("kind") == "ai"
        and evaluator.get("participated")
        and evaluator.get("materiallyInformedRecommendation")
    ]
    manifest = record.get("evaluatorManifest")

    if material_ai and not isinstance(manifest, dict):
        findings.append(Finding("error", "AI001", "evaluatorManifest", "material AI use requires a versioned evaluator manifest"))

    if isinstance(manifest, dict):
        reveal_status = manifest.get("revealStatus")
        commitment = manifest.get("commitment")
        reveal_uri = manifest.get("revealUri")
        if reveal_status in {"committed", "partially-revealed", "revealed", "withheld"} and not commitment:
            findings.append(Finding("error", "AI002", "evaluatorManifest.commitment", f"revealStatus={reveal_status!r} requires a commitment"))
        if reveal_status == "revealed" and not reveal_uri:
            findings.append(Finding("error", "AI003", "evaluatorManifest.revealUri", "revealed manifest requires revealUri"))

    if material_ai:
        submission_deadline_raw = record.get("program", {}).get("submissionDeadline")
        if not submission_deadline_raw:
            findings.append(Finding("error", "AI004", "program.submissionDeadline", "material AI use requires the application deadline needed to verify pre-deadline commitment"))
        elif isinstance(manifest, dict):
            commitment = manifest.get("commitment")
            committed_at = _iso(commitment.get("committedAt")) if isinstance(commitment, dict) else None
            submission_deadline = _iso(submission_deadline_raw)
            if committed_at and submission_deadline and committed_at >= submission_deadline:
                findings.append(Finding("error", "AI005", "evaluatorManifest.commitment.committedAt", "evaluator manifest must be committed before applications close"))

    if decision.get("aiRecommendationOverridden"):
        if status == "pending":
            findings.append(Finding("error", "AI010", "decision.aiRecommendationOverridden", "pending decision cannot record an institutional departure from an AI recommendation"))
        if not material_ai:
            findings.append(Finding("error", "AI006", "decision.aiRecommendationOverridden", "AI recommendation cannot be marked as overridden when no AI evaluator materially informed the recommendation"))
        if not (decision.get("aiOverrideRationale") or "").strip():
            findings.append(Finding("error", "AI007", "decision.aiOverrideRationale", "AI recommendation departure requires a rationale"))
    elif (decision.get("aiOverrideRationale") or "").strip():
        findings.append(Finding("error", "AI009", "decision.aiOverrideRationale", "AI departure rationale cannot be populated when aiRecommendationOverridden=false"))

    challenge = record.get("challenge")
    if not isinstance(challenge, dict) or not (challenge.get("scope") or "").strip():
        findings.append(Finding("error", "CHAL001", "challenge", "record must state the scope of factual or procedural correction"))
    else:
        challenge_status = challenge.get("status")
        process_defined = challenge.get("processDefined")
        if status in ADJUDICATED_STATUSES and not process_defined:
            findings.append(Finding("error", "CHAL002", "challenge.processDefined", "adjudicated decision requires a defined factual or procedural correction process"))
        elif status == "pending" and not process_defined:
            findings.append(Finding("warning", "CHAL003", "challenge.processDefined", "no factual or procedural correction process is recorded; the reviewed public governing artifacts do not identify one"))
        if challenge_status in {"open", "submitted", "resolved", "expired"} and not process_defined:
            findings.append(Finding("error", "CHAL004", "challenge.processDefined", f"challenge status {challenge_status!r} requires a defined process"))
        if status == "pending" and challenge_status != "not-open":
            findings.append(Finding("error", "CHAL005", "challenge.status", "pending decision cannot claim an active or completed post-decision challenge"))
        if challenge_status == "resolved" and not (challenge.get("resolution") or "").strip():
            findings.append(Finding("error", "CHAL006", "challenge.resolution", "resolved challenge requires a resolution"))

    disclosure = record.get("disclosure", {})
    classification = disclosure.get("classification")
    public_record = disclosure.get("publicRecord")
    redactions = disclosure.get("redactions", [])
    if classification == "confidential" and public_record:
        findings.append(Finding("error", "DISC001", "disclosure.publicRecord", "confidential classification cannot be marked as a public record"))
    if classification == "public" and not public_record:
        findings.append(Finding("error", "DISC002", "disclosure.publicRecord", "public classification requires publicRecord=true"))
    if classification == "public" and redactions:
        findings.append(Finding("error", "DISC003", "disclosure.redactions", "fully public record cannot simultaneously declare redactions"))

    created = _iso(record.get("timestamps", {}).get("createdAt"))
    updated = _iso(record.get("timestamps", {}).get("updatedAt"))
    decided = _iso(decided_at)
    effective = _iso(governing_policy.get("effectiveAt"))
    eligibility_checked = _iso(record.get("eligibility", {}).get("checkedAt"))
    if created and updated and updated < created:
        findings.append(Finding("error", "TIME001", "timestamps.updatedAt", "updatedAt precedes createdAt"))
    if effective and decided and effective > decided:
        findings.append(Finding("error", "TIME003", "governingPolicy.effectiveAt", "governing policy became effective after the recorded decision"))
    if status in ADJUDICATED_STATUSES and eligibility_checked and decided and eligibility_checked > decided:
        findings.append(Finding("error", "TIME004", "eligibility.checkedAt", "eligibility check cannot occur after the adjudicated decision it supports"))
    if status in DECIDED_STATUSES and updated and decided and decided > updated:
        findings.append(Finding("error", "TIME005", "timestamps.updatedAt", "record cannot contain a non-pending decision that occurs after its last-update timestamp"))

    if governing_policy.get("changeDuringReview") and not (governing_policy.get("changeSummary") or "").strip():
        findings.append(Finding("error", "POL001", "governingPolicy.changeSummary", "policy change during review requires a change summary"))

    if record.get("program", {}).get("materialityTier") == "C-enhanced" and status in {"approved", "suspended"}:
        for i, condition in enumerate(delivery):
            if not (condition.get("verifier") or "").strip():
                findings.append(Finding("warning", "DEL002", f"deliveryConditions[{i}].verifier", "enhanced award should identify the verifier"))
            if condition.get("targetDate") is None and not (condition.get("reviewWindow") or "").strip():
                findings.append(Finding("warning", "DEL003", f"deliveryConditions[{i}]", "enhanced award should identify a target date or review window"))

    if status in {"approved", "suspended"}:
        award = decision.get("awardedAmount")
        decision_currency = decision.get("currency")
        payment_amounts = [condition.get("paymentAmount") for condition in delivery]
        for i, condition in enumerate(delivery):
            if condition.get("paymentAmount") is not None and condition.get("currency") not in {None, decision_currency}:
                findings.append(Finding("error", "PAY001", f"deliveryConditions[{i}].currency", "delivery payment currency differs from decision currency"))
        if payment_amounts and all(amount is not None for amount in payment_amounts) and isinstance(award, (int, float)):
            if abs(sum(payment_amounts) - award) > 1e-9:
                findings.append(Finding("warning", "PAY002", "deliveryConditions", f"specified delivery payments sum to {sum(payment_amounts)!r}, award amount is {award!r}"))
        requested = record.get("application", {}).get("requestedAmount")
        if isinstance(requested, (int, float)) and isinstance(award, (int, float)) and award > requested:
            findings.append(Finding("warning", "PAY003", "decision.awardedAmount", "award exceeds the recorded requested amount"))

    return findings


def load_schema_for_record(record: dict) -> dict:
    version = record.get("schemaVersion", "0.1")
    if version == "0.1":
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if version == "0.2":
        if isinstance(record.get("withheldCommitments"), dict) and record["withheldCommitments"]:
            return json.loads((ROOT / "schema" / "grant-decision-public-projection-0.2.schema.json").read_text(encoding="utf-8"))
        return json.loads(SCHEMA_02_PATH.read_text(encoding="utf-8"))
    raise ValueError(f"unsupported schemaVersion {version!r}")


def check_schema_02_extensions(record: dict) -> list[Finding]:
    findings: list[Finding] = []
    if record.get("schemaVersion") != "0.2":
        return findings

    governing_policy = record.get("governingPolicy", {})
    policy_sources = set(governing_policy.get("sources", []))
    surface_sources = governing_policy.get("surfaceSources", {})

    pinning = record.get("policyPinning")
    if isinstance(pinning, dict):
        pinned_uris: set[str] = set()
        for i, source in enumerate(pinning.get("sources", [])):
            uri = source.get("uri")
            content_hash = source.get("contentHash", "")
            if uri not in policy_sources:
                findings.append(
                    Finding(
                        "error",
                        "POL007",
                        f"policyPinning.sources[{i}].uri",
                        "pinned URI must also appear in governingPolicy.sources",
                    )
                )
            if not CONTENT_HASH_PATTERN.match(content_hash):
                findings.append(
                    Finding(
                        "error",
                        "POL008",
                        f"policyPinning.sources[{i}].contentHash",
                        "contentHash must match sha256:<64 lowercase hex>",
                    )
                )
            surface = source.get("surface")
            if surface and surface != "other" and surface_sources.get(surface) != uri:
                findings.append(
                    Finding(
                        "error",
                        "POL009",
                        f"policyPinning.sources[{i}].surface",
                        "pinned surface URI must match governingPolicy.surfaceSources for that surface",
                    )
                )
            if uri in pinned_uris:
                findings.append(
                    Finding("error", "POL010", f"policyPinning.sources[{i}].uri", f"duplicate pinned URI {uri!r}")
                )
            pinned_uris.add(uri)

    authority_identity = record.get("authorityIdentity")
    if isinstance(authority_identity, dict):
        decision = record.get("decision", {})
        identity_kind = authority_identity.get("authorityKind")
        if identity_kind != decision.get("authorityKind"):
            findings.append(
                Finding(
                    "error",
                    "AUTH004",
                    "authorityIdentity.authorityKind",
                    "structured authority kind must match decision.authorityKind",
                )
            )
        evaluators = record.get("evaluators", [])
        evaluator_by_id = {
            evaluator.get("evaluatorId"): evaluator
            for evaluator in evaluators
            if isinstance(evaluator.get("evaluatorId"), str)
        }
        human_members = 0
        for i, member in enumerate(authority_identity.get("members", [])):
            evaluator_id = member.get("evaluatorId")
            if evaluator_id not in evaluator_by_id:
                findings.append(
                    Finding(
                        "error",
                        "AUTH005",
                        f"authorityIdentity.members[{i}].evaluatorId",
                        f"unknown evaluatorId {evaluator_id!r}",
                    )
                )
                continue
            evaluator = evaluator_by_id[evaluator_id]
            if evaluator.get("kind") == "ai":
                findings.append(
                    Finding(
                        "error",
                        "AUTH006",
                        f"authorityIdentity.members[{i}].evaluatorId",
                        "AI evaluators cannot appear in structured authority identity",
                    )
                )
            if evaluator.get("kind") == "human" and evaluator.get("participated") and not evaluator.get("recused"):
                human_members += 1
        if identity_kind == "committee" and human_members == 0:
            findings.append(
                Finding(
                    "error",
                    "AUTH007",
                    "authorityIdentity.members",
                    "committee structured authority requires at least one participating human member link",
                )
            )

    return findings


def validate_schema(record: dict, schema: dict) -> list[Finding]:
    try:
        import jsonschema
    except ImportError as exc:
        raise SystemExit("jsonschema is required: python -m pip install jsonschema") from exc

    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    output: list[Finding] = []
    for error in sorted(validator.iter_errors(record), key=lambda item: list(item.absolute_path)):
        path = ".".join(str(part) for part in error.absolute_path) or "<root>"
        output.append(Finding("error", "SCHEMA", path, error.message))
    return output


def validate_record(record: dict, schema: dict | None = None) -> list[Finding]:
    schema = schema or load_schema_for_record(record)
    structural = validate_schema(record, schema)
    if structural:
        return structural
    findings = check_semantics(record)
    findings.extend(check_schema_02_extensions(record))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ENS Grant Decision Integrity records.")
    parser.add_argument("records", nargs="+", help="JSON decision record(s) to validate")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    failed = False
    for raw in args.records:
        path = Path(raw)
        record = json.loads(path.read_text(encoding="utf-8"))
        record_findings = validate_record(record)
        print(f"{path}:")
        if not record_findings:
            print("  PASS")
            continue
        for item in record_findings:
            print(f"  {item.render()}")
        if any(item.severity == "error" for item in record_findings):
            failed = True
        if args.strict and record_findings:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
