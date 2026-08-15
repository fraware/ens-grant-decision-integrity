# Machine-Checkable Conformance

`grant-decision-record.schema.json` validates record structure. `scripts/conformance.py` validates cross-field decision-integrity invariants that JSON Schema cannot express cleanly.

A record is **core-conformant** only when both layers pass without errors.

## Core invariants

### Reference integrity

Identifiers for evaluators, evidence, findings, criteria, disagreements, conflicts, delivery conditions, and eligibility rules must be unique. Every cross-reference must resolve within the same record.

### Evidence and finding integrity

A finding classified as `supported-fact` must reference evidence. Every material finding must identify at least one evaluator. A scored criterion must reference at least one finding. Public evidence must expose a retrievable URI. Non-public evidence without a content hash produces a warning.

### Evaluation integrity

Criterion weights must either be omitted consistently or be specified for every criterion and sum to `1.0`.

### Eligibility integrity

`eligibility.status=eligible` is valid only when every rule is `pass` or `not-applicable`. `eligibility.status=ineligible` requires at least one failed rule. Approval and rejection require an eligible application.

### Decision-state integrity

A pending record cannot claim a decision timestamp. Final dispositions require one. Approval or rejection requires a substantive rationale and at least one attributable material finding. Approved awards require a positive amount and at least one observable delivery condition. Rejected decisions cannot retain a positive award.

### Conflict and recusal integrity

A recused evaluator cannot remain marked as participating. Each recusal must link to a conflict record in `recused` or `resolved` state. A finalized decision cannot leave a material conflict merely `disclosed` or `unresolved`.

### Authority integrity

Every decision has a typed human-governed authority: `human`, `committee`, `dao-vote`, `multisig`, or `other-human-governed`. A finalized committee decision must identify participating human members, record quorum, and record the applicable voting or consensus rule.

### Automated-evaluator provenance

If an automated evaluator materially informed the decision, absence of an evaluator manifest produces a warning. Manifest commitment and reveal states must remain internally consistent.

### Challenge integrity

The record states whether a factual or procedural correction process is actually defined. A finalized decision with `challenge.processDefined=false` is non-conformant. A pending record may expose the missing process as warning `CHAL003` so the gap can be repaired before finalization.

### Disclosure integrity

Public, mixed, and confidential disclosure classifications must agree with `publicRecord` and redaction state.

### Temporal integrity

`updatedAt` cannot precede `createdAt`. A finalized decision cannot predate record creation. A governing policy cannot take effect after the decision it governed.

### Delivery and payment integrity

Enhanced approved awards should identify verifiers and target dates. Delivery payment currencies must agree with the award currency. Fully specified tranche amounts are compared with the total award and discrepancies are surfaced.

## Severity model

- **ERROR** — the record cannot claim core conformance.
- **WARNING** — the record has a material auditability or process gap. It remains usable as a diagnostic record, and `--strict` treats the warning as failure.

## Current worked example

The SPP3 Marketplace RFP example is intentionally pending. Public RFP artifacts reviewed on August 15, 2026 specify eligibility, evaluation, committee process, confidentiality, milestones, and publication of the winning rationale, but they do not specify a post-decision factual/procedural correction process. The example therefore records `challenge.processDefined=false` and emits `CHAL003`.

This is deliberate: the example maps the public process and exposes a Charter gap instead of manufacturing conformance.

## Commands

```bash
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/conformance.py --strict examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
```

## Design principle

Syntactic validity is insufficient for institutional conformance. A record can parse correctly and still contain an unsupported factual claim, a broken reference, an unresolved conflict, a contradictory recusal, or an unattributed decision. The semantic layer rejects those states explicitly.

## Scope boundary

The validator checks internal consistency and declared process invariants. It does not determine whether substantive judgment is correct, whether cited evidence is truthful, or whether the governing policy itself is legitimate.
