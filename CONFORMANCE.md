# Machine-Checkable Conformance

`schema/grant-decision-record.schema.json` validates record structure. `scripts/conformance.py` checks cross-field relations that encode the v0.1 decision-integrity profile.

A record passes the v0.1 profile when it has no schema or conformance errors. Warnings identify unresolved auditability or process questions and can be promoted to failures with `--strict`.

## Conformance checks

### Reference integrity

Identifiers for evaluators, evidence, findings, criteria, disagreements, conflicts, delivery conditions, and eligibility rules must be unique. Cross-references must resolve within the record.

### Evidence and finding integrity

A finding classified as `supported-fact` must reference evidence. Every material finding must identify at least one evaluator. A scored criterion must reference at least one finding. Public evidence must expose a retrievable URI.

### Evaluation integrity

Criterion weights must either be omitted consistently or be specified for every criterion and sum to `1.0`.

### Eligibility integrity

`eligibility.status=eligible` requires every rule to be `pass` or `not-applicable`. `eligibility.status=ineligible` requires at least one failed rule.

The decision model distinguishes a hard-screen ineligibility disposition from a merit rejection. `decision.status=ineligible` requires `eligibility.status=ineligible`, at least one failed eligibility rule, and a decision or eligibility rationale. It does not require merit findings.

### Decision-state integrity

A pending record cannot claim a decision timestamp. A non-pending decision requires one. Approval and rejection require an eligible application, a substantive rationale, and attributable material findings. An approved award requires a positive amount and at least one observable delivery condition.

Retrospective records are permitted: a decision can predate creation of the record that documents it.

### Conflict and recusal integrity

A recused evaluator cannot remain marked as participating. A recusal must link to a conflict record in `recused` or `resolved` state. An adjudicated decision cannot leave a material conflict in `disclosed` or `unresolved` state.

### Authority integrity

Decision authority is typed as `human`, `committee`, `dao-vote`, `multisig`, or `other-human-authority`. AI is intentionally absent from the authority types.

A non-pending committee decision must identify participating human members, quorum, and the applicable voting or consensus rule.

### AI evaluator provenance

If an AI evaluator materially informed a decision and no evaluator manifest is recorded, the validator emits `AI001` as a warning. Commitment and reveal states must remain internally consistent.

### Challenge integrity

The record states whether a factual or procedural correction process is defined. An adjudicated decision with `challenge.processDefined=false` is non-conformant. A pending record can expose the unresolved documentation question as warning `CHAL003`.

### Disclosure integrity

Public, mixed, and confidential classifications must agree with `publicRecord` and redaction state.

### Temporal integrity

`updatedAt` cannot precede `createdAt`. The governing policy cannot take effect after the decision it governed.

### Delivery and payment integrity

For Tier C approved awards, the validator warns when a delivery condition lacks a verifier or both a target date and review window. Delivery payment currencies must agree with the award currency. Fully specified tranche amounts are compared with the total award.

## Severity model

- **ERROR** — the record does not pass the v0.1 conformance profile.
- **WARNING** — the record exposes a material auditability or process question; `--strict` treats the warning as failure.

## Current worked example

The SPP3 Marketplace RFP example is intentionally pending. The reviewed public artifacts define eligibility, evaluation, committee quorum and voting, confidentiality, milestones, and award publication. They do not identify a post-decision process for correcting factual errors or procedural deviations.

The example therefore records `challenge.processDefined=false` and emits `CHAL003`. This maps the reviewed public process. It does not assert the absence of an internal or unpublished procedure and does not propose changing rules during the active review.

## Commands

```bash
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/conformance.py --strict examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
```

## Scope boundary

The validator checks record structure and declared cross-field consistency. It does not determine whether cited evidence is true, whether substantive judgment is correct, or whether the governing policy itself is legitimate.
