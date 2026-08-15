# Machine-Checkable Conformance

`schema/grant-decision-record.schema.json` validates record structure. `scripts/conformance.py` checks cross-field relations that encode the v0.1 decision-integrity profile.

A record passes the v0.1 profile when it has no schema or conformance errors. Warnings identify unresolved auditability or process questions and can be promoted to failures with `--strict`.

## Conformance checks

### Reference and attribution integrity

Identifiers for evaluators, evidence, findings, criteria, disagreements, conflicts, delivery conditions, and eligibility rules must be unique. Cross-references must resolve within the record.

A material finding can be attributed only to an evaluator marked as participating and not recused. A finding attributed to a known evaluator who did not participate, or who was recused, fails as `EVAL003`.

A disagreement follows the same attribution rule. A disagreement attributed to a known evaluator who did not participate, or who was recused, fails as `EVAL004`. This prevents a record from manufacturing apparent dissent from an actor who was outside the review surface.

### Evidence integrity

A finding classified as `supported-fact` must reference evidence. Every material finding must identify at least one evaluator. A scored criterion must reference at least one finding. Public evidence must expose a retrievable URI.

A failed eligibility rule must also reference evidence. A hard-screen failure with an empty `evidenceIds` array fails as `EVID004`; this prevents an ineligible disposition from bypassing the evidence-linkage requirement simply because merit scoring never occurred.

Non-public evidence can remain confidential. If it has neither a retrievable URI nor a content hash, the validator emits `EVID003` as an auditability warning. A private URI is sufficient to avoid this warning; v0.1 does not require every confidential artifact to be publicly disclosed or cryptographically committed.

### Evaluation integrity

Criterion weights must either be omitted consistently or be specified for every criterion and sum to `1.0`.

Material-finding classification is epistemic. The allowed values are `supported-fact`, `judgment`, `uncertainty`, and `unverified-claim`. A risk statement can be recorded as a finding, but `risk` is not itself an epistemic classification.

### Governing-policy traceability

The governing policy must identify a public rules URI and a source map for five decision surfaces: mandate, eligibility, evaluation criteria, conflict rules, and decision procedure.

`governingPolicy.publicRulesUri` must also appear in `governingPolicy.sources`; otherwise the record fails as `POL002`. Every URI in `surfaceSources` must resolve to the same declared source set; an undeclared decision-surface source fails as `POL003`.

If `changeDuringReview=true`, schema validation requires a change summary, prior version, disclosure URI, and a statement of whether prior evaluations were rerun. The prior version must differ from the active version (`POL004`), and the change notice URI must appear in the declared source set (`POL005`).

If `changeDuringReview=false`, the change summary, prior version, change-notice URI, and rerun state must remain empty. Populated change metadata under a no-change declaration fails as `POL006`.

These checks establish declared traceability. They do not establish that the published rule was substantively legitimate or correctly interpreted.

### Eligibility integrity

`eligibility.status=eligible` requires every rule to be `pass` or `not-applicable`. `eligibility.status=ineligible` requires at least one failed rule.

The decision model distinguishes a hard-screen ineligibility disposition from a merit rejection. `decision.status=ineligible` requires `eligibility.status=ineligible`, at least one failed eligibility rule, and a decision or eligibility rationale. It does not require merit findings. The failed rule itself must carry evidence under `EVID004`.

### Decision-state integrity

A pending record cannot claim a decision timestamp. A non-pending decision requires one.

Approval, rejection, and suspension require an eligible application, substantive rationale, and attributable material findings. Approval and suspension also require a positive award amount and observable delivery conditions. A deferral requires a rationale but does not imply a merit judgment.

Pending and deferred records cannot carry a positive `awardedAmount`. The requested amount belongs in `application.requestedAmount`; an award is recorded only after an approving disposition.

Retrospective records are permitted: a decision can predate creation of the record that documents it.

### Conflict and recusal integrity

A recused evaluator cannot remain marked as participating. A recusal must link to a conflict record in `recused` or `resolved` state.

For each recused evaluator, the linked record must identify:

- at least one affected decision surface;
- whether a substitute evaluator was used;
- the substitute evaluator identifier when substitution occurred.

A substitute identifier must resolve to a distinct evaluator who participated and was not recused. If `substitutionUsed=false`, a substitute identifier must not be present.

Recusal state is reciprocal for known evaluators. If a conflict record marks a known evaluator as `recused` but that evaluator remains participating or is not itself marked recused, the record fails as `COI009`.

An adjudicated decision cannot leave a material conflict in `disclosed` or `unresolved` state.

### Authority integrity

Decision authority is typed as `human`, `committee`, `dao-vote`, `multisig`, or `other-human-authority`. AI is intentionally absent from the authority types.

A non-pending committee decision must identify participating human members, quorum, and the applicable voting or consensus rule.

### AI evaluator provenance

AI materiality is recorded against the **grant recommendation**, not the institutional decision.

An AI evaluator cannot claim to have materially informed a recommendation unless it is also marked as participating (`AI008`).

If a participating AI evaluator materially informed the recommendation:

- a versioned evaluator manifest is mandatory;
- the manifest must contain the v0.1 minimum provenance envelope: version, commitment, reveal state, model identity, and human-review policy;
- the program must record the submission deadline;
- the declared manifest commitment time must be strictly earlier than that deadline.

An empty manifest fails schema validation. A missing manifest produces `AI001`. A missing submission deadline produces `AI004`. A declared commitment time at or after the deadline produces `AI005`.

If the final human decision departs from a materially influential AI recommendation, `decision.aiRecommendationOverridden=true` records that fact and requires `aiOverrideRationale`. Marking an AI departure when no AI evaluator materially informed the recommendation produces `AI006`. Conversely, populating `aiOverrideRationale` when `aiRecommendationOverridden=false` fails as `AI009`; the rationale cannot exist without the event it purports to explain.

The validator checks the internal ordering of the declared `committedAt` timestamp and submission deadline. v0.1 does not define or verify an external timestamp/publication anchor, verify the commitment digest, prove that the committed configuration was executed, or replay the evaluator. A later commitment protocol is required to establish independently verifiable pre-deadline existence.

### Challenge integrity

The record states whether a factual or procedural correction process is defined. An adjudicated decision with `challenge.processDefined=false` is non-conformant. A pending record can expose the unresolved documentation question as warning `CHAL003`.

### Disclosure integrity

Public, mixed, and confidential classifications must agree with `publicRecord` and redaction state.

### Temporal integrity

`updatedAt` cannot precede `createdAt`. The governing policy cannot take effect after the decision it governed.

The active policy version's `effectiveAt` records the effective time of that version; in-round change traceability is checked separately under Governing-policy traceability.

### Delivery and payment integrity

For Tier C approved or suspended awards, the validator warns when a delivery condition lacks a verifier or both a target date and review window. Delivery payment currencies must agree with the award currency. Fully specified tranche amounts are compared with the total award.

## Severity model

- **ERROR** — the record does not pass the v0.1 conformance profile.
- **WARNING** — the record exposes a material auditability or process question; `--strict` treats the warning as failure.

## Current worked example

The SPP3 Marketplace RFP example is intentionally pending. The reviewed public artifacts define seven hard eligibility gates, the M1–M5 weighted rubric, committee quorum and voting, confidentiality, milestones, the August 5, 2026 23:59 UTC submission deadline, and award publication. The example maps all seven eligibility gates, preserves the published rubric weights, and maps the public governing-policy URI and each of the five normative decision surfaces to declared sources.

The reviewed public artifacts do not identify a post-decision process for correcting factual errors or procedural deviations. The example therefore records `challenge.processDefined=false` and emits `CHAL003`. This maps the reviewed public process. It does not assert the absence of an internal or unpublished procedure and does not propose changing rules during the active review.

## Commands

```bash
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/conformance.py --strict examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_final_consistency.py
```

## Scope boundary

The validator checks record structure and declared cross-field consistency. It does not determine whether cited evidence is true, whether substantive judgment is correct, whether a commitment existed at the declared time without an external anchor, whether a committed evaluator configuration actually ran, or whether the governing policy itself is legitimate.
