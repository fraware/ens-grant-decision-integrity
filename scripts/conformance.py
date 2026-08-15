#!/usr/bin/env python3
"""Semantic conformance checks for ENS Grant Decision Integrity records.

JSON Schema proves shape. This module enforces cross-field institutional
invariants that are awkward or impossible to express cleanly in JSON Schema.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "grant-decision-record.schema.json"

FINAL_STATUSES = {"approved", "rejected", "deferred", "withdrawn", "suspended"}


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
    f: list[Finding] = []

    evaluators = record.get("evaluators", [])
    evidence = record.get("evidence", [])
    criteria = record.get("evaluation", {}).get("criteria", [])
    material_findings = record.get("evaluation", {}).get("materialFindings", [])
    disagreements = record.get("evaluation", {}).get("disagreements", [])
    conflicts = record.get("conflicts", [])
    delivery = record.get("deliveryConditions", [])
    eligibility_rules = record.get("eligibility", {}).get("rules", [])

    evaluator_ids = _check_unique(f, evaluators, "evaluatorId", "evaluators", "REF001")
    evidence_ids = _check_unique(f, evidence, "evidenceId", "evidence", "REF002")
    finding_ids = _check_unique(f, material_findings, "findingId", "evaluation.materialFindings", "REF003")
    _check_unique(f, criteria, "criterionId", "evaluation.criteria", "REF004")
    _check_unique(f, disagreements, "disagreementId", "evaluation.disagreements", "REF005")
    _check_unique(f, conflicts, "conflictId", "conflicts", "REF006")
    _check_unique(f, delivery, "conditionId", "deliveryConditions", "REF007")
    _check_unique(f, eligibility_rules, "ruleId", "eligibility.rules", "REF008")

    for i, rule in enumerate(eligibility_rules):
        for ref in rule.get("evidenceIds", []):
            if ref not in evidence_ids:
                f.append(Finding("error", "REF101", f"eligibility.rules[{i}].evidenceIds", f"unknown evidenceId {ref!r}"))

    for i, item in enumerate(material_findings):
        for ref in item.get("evidenceIds", []):
            if ref not in evidence_ids:
                f.append(Finding("error", "REF102", f"evaluation.materialFindings[{i}].evidenceIds", f"unknown evidenceId {ref!r}"))
        for ref in item.get("evaluatorIds", []):
            if ref not in evaluator_ids:
                f.append(Finding("error", "REF103", f"evaluation.materialFindings[{i}].evaluatorIds", f"unknown evaluatorId {ref!r}"))
        if item.get("classification") == "supported-fact" and not item.get("evidenceIds"):
            f.append(Finding("error", "EVID001", f"evaluation.materialFindings[{i}]", "supported-fact requires at least one evidence reference"))

    for i, criterion in enumerate(criteria):
        for ref in criterion.get("findingIds", []):
            if ref not in finding_ids:
                f.append(Finding("error", "REF104", f"evaluation.criteria[{i}].findingIds", f"unknown findingId {ref!r}"))

    for i, item in enumerate(disagreements):
        for ref in item.get("evaluatorIds", []):
            if ref not in evaluator_ids:
                f.append(Finding("error", "REF105", f"evaluation.disagreements[{i}].evaluatorIds", f"unknown evaluatorId {ref!r}"))

    for i, item in enumerate(delivery):
        for ref in item.get("evidenceIds", []):
            if ref not in evidence_ids:
                f.append(Finding("error", "REF106", f"deliveryConditions[{i}].evidenceIds", f"unknown evidenceId {ref!r}"))

    for i, item in enumerate(evidence):
        if item.get("disclosure") == "public" and not item.get("uri"):
            f.append(Finding("error", "EVID002", f"evidence[{i}]", "public evidence requires a retrievable URI"))
        if item.get("disclosure") != "public" and not item.get("contentHash"):
            f.append(Finding("warning", "EVID003", f"evidence[{i}]", "non-public evidence has no content hash; later integrity verification will be impossible"))

    weights = [c.get("weight") for c in criteria]
    populated = [w for w in weights if w is not None]
    if populated and len(populated) != len(weights):
        f.append(Finding("error", "EVAL001", "evaluation.criteria", "criterion weights are partially specified"))
    elif populated and abs(sum(populated) - 1.0) > 1e-9:
        f.append(Finding("error", "EVAL002", "evaluation.criteria", f"criterion weights sum to {sum(populated)!r}, expected 1.0"))

    decision = record.get("decision", {})
    status = decision.get("status")
    decided_at = decision.get("decidedAt")
    eligibility = record.get("eligibility", {}).get("status")

    if status == "pending" and decided_at is not None:
        f.append(Finding("error", "DEC001", "decision.decidedAt", "pending records must not claim a decision timestamp"))
    if status in FINAL_STATUSES and not decided_at:
        f.append(Finding("error", "DEC002", "decision.decidedAt", "finalized decision requires a decision timestamp"))
    if status in {"approved", "rejected"} and eligibility != "eligible":
        f.append(Finding("error", "DEC003", "eligibility.status", f"{status} decision requires eligibility.status='eligible'"))

    if status == "approved":
        if not isinstance(decision.get("awardedAmount"), (int, float)) or decision.get("awardedAmount", 0) <= 0:
            f.append(Finding("error", "DEC004", "decision.awardedAmount", "approved decision requires a positive award amount"))
        if not delivery:
            f.append(Finding("error", "DEL001", "deliveryConditions", "approved award requires at least one observable delivery condition"))
    elif status == "rejected" and decision.get("awardedAmount") not in (None, 0):
        f.append(Finding("error", "DEC005", "decision.awardedAmount", "rejected decision cannot carry a positive award"))

    if decision.get("humanOverride") and not (decision.get("overrideRationale") or "").strip():
        f.append(Finding("error", "DEC006", "decision.overrideRationale", "human override requires a rationale"))

    if status in FINAL_STATUSES:
        for i, conflict in enumerate(conflicts):
            if conflict.get("status") in {"unresolved", "disclosed"}:
                f.append(Finding("error", "COI001", f"conflicts[{i}].status", "final decision cannot leave a material conflict merely disclosed or unresolved"))

    committee_present = any(e.get("kind") == "committee" and e.get("participated") for e in evaluators)
    if status in FINAL_STATUSES and committee_present:
        humans = [e for e in evaluators if e.get("kind") == "human" and e.get("participated") and not e.get("recused")]
        if not humans:
            f.append(Finding("error", "AUTH001", "evaluators", "final committee decision must identify participating human members"))
        if not (decision.get("quorum") or "").strip():
            f.append(Finding("error", "AUTH002", "decision.quorum", "final committee decision must record quorum status or rule"))
        if not (decision.get("decisionRule") or "").strip():
            f.append(Finding("error", "AUTH003", "decision.decisionRule", "final committee decision must record the applicable voting or consensus rule"))

    material_ai = [e for e in evaluators if e.get("kind") == "ai" and e.get("participated") and e.get("materiallyInformedDecision")]
    if material_ai and record.get("evaluatorManifest") is None:
        f.append(Finding("warning", "AI001", "evaluatorManifest", "an automated evaluator materially informed the decision but no evaluator manifest is recorded"))

    manifest = record.get("evaluatorManifest")
    if isinstance(manifest, dict):
        reveal = manifest.get("revealStatus")
        commitment = manifest.get("commitment")
        reveal_uri = manifest.get("revealUri")
        if reveal in {"committed", "partially-revealed", "revealed", "withheld"} and not commitment:
            f.append(Finding("error", "AI002", "evaluatorManifest.commitment", f"revealStatus={reveal!r} requires a commitment"))
        if reveal == "revealed" and not reveal_uri:
            f.append(Finding("error", "AI003", "evaluatorManifest.revealUri", "revealed manifest requires revealUri"))

    challenge = record.get("challenge")
    if not isinstance(challenge, dict) or not (challenge.get("scope") or "").strip():
        f.append(Finding("error", "CHAL001", "challenge", "record must define the scope of the factual or procedural challenge path"))

    created = _iso(record.get("timestamps", {}).get("createdAt"))
    updated = _iso(record.get("timestamps", {}).get("updatedAt"))
    decided = _iso(decided_at)
    effective = _iso(record.get("governingPolicy", {}).get("effectiveAt"))
    if created and updated and updated < created:
        f.append(Finding("error", "TIME001", "timestamps.updatedAt", "updatedAt precedes createdAt"))
    if created and decided and decided < created:
        f.append(Finding("error", "TIME002", "decision.decidedAt", "decidedAt precedes record creation"))
    if effective and decided and effective > decided:
        f.append(Finding("error", "TIME003", "governingPolicy.effectiveAt", "governing policy became effective after the recorded decision"))

    gp = record.get("governingPolicy", {})
    if gp.get("changeDuringReview") and not (gp.get("changeSummary") or "").strip():
        f.append(Finding("error", "POL001", "governingPolicy.changeSummary", "policy change during review requires a change summary"))

    if record.get("program", {}).get("materialityTier") == "C-enhanced":
        if status in FINAL_STATUSES and record.get("integrity") is None:
            f.append(Finding("warning", "INT001", "integrity", "enhanced finalized record has no integrity metadata"))
        for i, condition in enumerate(delivery):
            if status == "approved" and not (condition.get("verifier") or "").strip():
                f.append(Finding("warning", "DEL002", f"deliveryConditions[{i}].verifier", "enhanced approved award should identify the verifier"))
            if status == "approved" and condition.get("targetDate") is None:
                f.append(Finding("warning", "DEL003", f"deliveryConditions[{i}].targetDate", "enhanced approved award should identify a target date or encode a review window elsewhere"))

    return f


def validate_schema(record: dict, schema: dict) -> list[Finding]:
    try:
        import jsonschema
    except ImportError as exc:
        raise SystemExit("jsonschema is required: python -m pip install jsonschema") from exc

    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    out: list[Finding] = []
    for err in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path)):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        out.append(Finding("error", "SCHEMA", path, err.message))
    return out


def validate_record(record: dict, schema: dict) -> list[Finding]:
    structural = validate_schema(record, schema)
    if structural:
        return structural
    return check_semantics(record)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ENS Grant Decision Integrity records.")
    parser.add_argument("records", nargs="+", help="JSON decision record(s) to validate")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    failed = False
    for raw in args.records:
        path = Path(raw)
        record = json.loads(path.read_text(encoding="utf-8"))
        findings = validate_record(record, schema)
        print(f"{path}:")
        if not findings:
            print("  PASS")
            continue
        for item in findings:
            print(f"  {item.render()}")
        if any(item.severity == "error" for item in findings):
            failed = True
        if args.strict and findings:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
