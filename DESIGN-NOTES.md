# Design Notes — ENS Grant Decision Integrity v0.1

## 1. Why this artifact is narrow

The Simocracy funding record strongly rewarded the adjudicative layer: a Grants Charter, evidence-linked decisions, and commit–reveal treatment of automated screening. It also showed diminishing marginal value after roughly the first $200 of funding.

This v0.1 therefore implements the funded core and deliberately stops short of a full cryptographic evaluator protocol.

## 2. Existing ENS practices preserved

### Published evaluation policy

SPP3 published its application format, eligibility screen, scoring rubric, program terms, and committee process before selection. The Marketplace RFP likewise publishes a marketplace-specific rubric and hard eligibility gate.

### Committee attribution and recusals

The SPP3 cohort process describes committee evaluation, conflict handling, and quorum expectations. The schema therefore treats evaluators, recusals, quorum, and decision rule as first-class decision attributes.

### Independent verification

The Marketplace RFP requires milestones to specify what ships and how completion can be independently verified. Post-go-live traction gates are designed around independently observable evidence, including on-chain activity.

The delivery-condition object directly models this structure.

### Privacy and selective disclosure

The SPP3 process uses confidential application handling during review. The Charter therefore separates public decision records, selectively disclosed audit material, and confidential source material.

## 3. Automated screening design

ENS's screening experiment found useful capabilities in detecting missing budget structure, non-falsifiable KPIs, undefined scope, repository inconsistencies, overlap, and conflict-of-interest problems.

The same experiment identified two material risks:

1. publishing exact evaluator instructions creates a gaming surface;
2. automated evaluators can remain overly agreeable after identifying substantive red flags.

The Charter's commit–reveal boundary addresses the first problem procedurally. Preserved disagreement, explicit human authority, and evidence-linked findings address the second.

## 4. Threat model

### T1 — Criteria drift during review

**Risk:** criteria or evaluator configuration changes after applications are observed.

**Control:** versioned policy + evaluator manifest + optional pre-deadline commitment.

### T2 — Unsupported evaluator findings

**Risk:** a score or recommendation rests on an assertion that cannot be traced to applicant or public evidence.

**Control:** evidence-linked material findings; unsupported claims must be labeled as judgment, uncertainty, or unverified claims.

### T3 — Score laundering

**Risk:** aggregation conceals a severe disagreement about security, eligibility, budget, or deliverability.

**Control:** material disagreement is recorded independently of aggregate scores.

### T4 — Conflict hidden behind disclosure

**Risk:** a reviewer discloses a relationship and still shapes the final decision.

**Control:** finalized records reject material conflicts left merely disclosed or unresolved; recusal and resolution remain attributable.

### T5 — Automation acquires de facto authority

**Risk:** reviewers treat automated scores as binding even where policy assigns authority to humans.

**Control:** explicit human disposition, attribution, and override/departure records.

### T6 — Milestones become activity reports

**Risk:** funded work reports effort without establishing completion.

**Control:** delivery conditions require observable outputs or outcomes and verification methods.

### T7 — Transparency harms applicants

**Risk:** public auditability exposes private, security-sensitive, or commercially sensitive material.

**Control:** disclosure classification, selective audit access, and integrity commitments for withheld artifacts.

### T8 — Administrative burden overwhelms small grants

**Risk:** full records cost more than the accountability value they create.

**Control:** proportionate materiality tiers.

### T9 — Compliance theater

**Risk:** a record satisfies the JSON Schema while encoding an institutionally invalid state: evidence-free factual claims, dangling references, unresolved conflicts, unattributed committee action, or approval without delivery conditions.

**Control:** a separate semantic conformance layer validates cross-field invariants and is exercised against adversarial negative tests in CI.

## 5. Why the current Marketplace RFP is a useful worked example

As of August 15, 2026, the Marketplace RFP submission window is closed and committee evaluation is scheduled for August 5–19, with an award announcement targeted by August 28.

The RFP is a useful test case because it contains:

- a hard eligibility gate;
- a five-criterion weighted rubric;
- explicit committee and conflict rules;
- confidential application handling;
- milestone-gated payment;
- independently verifiable and on-chain traction requirements;
- a defined award threshold.

The included example does **not** score any real applicant and does **not** imply committee endorsement. It demonstrates how public program rules can be represented as a pending decision record.

## 6. Structural validity and semantic conformance

JSON Schema validates representation. Institutional validity depends on relations across fields.

The semantic validator therefore checks identifier uniqueness, reference resolution, evidence requirements, weight completeness, decision-state consistency, conflict closure, committee attribution, challenge-path definition, timestamp ordering, and evaluator-manifest state consistency.

`CONFORMANCE.md` defines these checks and their severity model.

## 7. Deliberate Phase-II boundary

The schema includes an optional `evaluatorManifest` object with a manifest version, commitment digest, commit timestamp, reveal status, model descriptors, retrieval sources, and human-review policy.

v0.1 does not implement commitment generation, selective disclosure proofs, or evaluator replay. Those remain a distinct technical work package.

## 8. Source map

- Marketplace RFP authorization: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP rubric and timeline: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 cohort recommendation: https://discuss.ens.domains/t/ep-6-49-spp3-cohort-recommendation/22237
- Automated grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
