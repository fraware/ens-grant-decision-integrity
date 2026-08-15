# Design Notes — ENS Grant Decision Integrity v0.1

## 1. Why this artifact is narrow

The Simocracy funding record strongly rewarded the adjudicative layer: a Grants Charter, evidence-linked decisions, and commit–reveal treatment of AI-assisted screening. It also showed diminishing marginal value after roughly the first $200 of funding.

This v0.1 therefore implements the funded core and deliberately stops short of a full cryptographic evaluator protocol.

## 2. Existing ENS practices preserved

### Published evaluation policy

SPP3 published its application format, eligibility screen, scoring rubric, program terms, and committee process before selection. The Marketplace RFP likewise publishes a marketplace-specific rubric and hard eligibility gate.

### Committee attribution and recusals

The SPP3 cohort recommendation states that qualifying applications were evaluated by all members unless recused, discloses a recusal, and describes the quorum/process model. The schema therefore treats evaluators, recusals, and quorum as first-class fields.

### Independent verification

The Marketplace RFP requires milestones to state what ships, when, and how completion can be independently verified. Post-go-live traction gates are intended to use on-chain data such as attributable protocol revenue, active wallets, sales, and retention.

The delivery-condition object in the schema directly models this structure.

### Privacy and selective disclosure

The SPP3 process keeps applications confidential during review and gives applicants an opportunity to review/redact material before publication. The Charter therefore separates public decision records, selectively disclosed audit material, and confidential source material.

## 3. AI screening design

ENS's AI screening experiment found useful capabilities in detecting missing budget structure, non-falsifiable KPIs, undefined scope, repository inconsistencies, overlap, and conflict-of-interest problems.

The same experiment identified two risks:

1. publishing exact prompts creates a gaming surface;
2. evaluators can remain overly agreeable even after identifying red flags.

The Charter's commit–reveal boundary addresses the first problem procedurally. Preserved disagreement, explicit human authority, and evidence-linked findings address the second.

## 4. Threat model

### T1 — Criteria drift during review

**Risk:** criteria or model configuration changes after applications are observed.

**Control:** versioned policy + evaluator manifest + optional pre-deadline commitment.

### T2 — Unsupported evaluator findings

**Risk:** a score or recommendation rests on an assertion that cannot be traced to applicant evidence or public evidence.

**Control:** evidence-linked material findings; unsupported claims must be labeled as judgment or uncertainty.

### T3 — Score laundering

**Risk:** averaging conceals a severe disagreement about security, eligibility, or deliverability.

**Control:** material disagreement is recorded separately from aggregate scores.

### T4 — Conflict hidden behind process

**Risk:** a reviewer discloses a relationship but still shapes the evaluation.

**Control:** recusal records identify decision surface and substitute reviewer where applicable.

### T5 — Automation acquires de facto authority

**Risk:** reviewers treat model scores as binding even if policy calls them advisory.

**Control:** explicit human disposition and override/departure record.

### T6 — Milestones become activity reports

**Risk:** funded work reports effort without establishing completion.

**Control:** delivery conditions require observable outputs/outcomes and verification methods.

### T7 — Transparency harms applicants

**Risk:** public auditability exposes private, security-sensitive, or commercially sensitive material.

**Control:** disclosure classification, selective audit access, and integrity commitments for withheld artifacts.

### T8 — Administrative burden overwhelms small grants

**Risk:** full records cost more than the accountability value they create.

**Control:** proportionate materiality tiers.

## 5. Why the current Marketplace RFP is a useful worked example

As of August 15, 2026, the Marketplace RFP submission window is closed and committee evaluation is scheduled for August 5–19, with an award announcement on or before August 28.

The RFP is a useful test case because it already contains:

- a hard eligibility gate;
- a five-criterion weighted rubric;
- explicit conflict and quorum rules;
- confidential application handling;
- milestone-gated payment;
- independent/on-chain verification requirements;
- a defined award threshold.

The included example does **not** score any real applicant and does **not** imply committee endorsement. It demonstrates how a public program policy can be represented as a pending decision record.

## 6. Deliberate Phase-II boundary

The schema includes an optional `evaluatorManifest` object with a manifest version, commitment digest, commit timestamp, reveal status, model descriptors, retrieval sources, and human-review policy.

v0.1 does not implement commitment generation or replay. That is intentionally left as a distinct technical work package.

## 7. Source map

- Marketplace RFP authorization: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP rubric and timeline: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 cohort recommendation: https://discuss.ens.domains/t/ep-6-49-spp3-cohort-recommendation/22237
- AI grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
