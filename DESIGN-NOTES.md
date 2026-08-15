# Design Notes — ENS Grant Decision Integrity v0.1

## 1. Scope

Simocracy ballot reasoning repeatedly highlighted the Grants Charter and commit–reveal treatment of AI-assisted screening. Evidence-linked decision records were part of the same funded mechanism. Marginal value declined after roughly the first $200 of cumulative funding.

v0.1 therefore implements the funded core. Commitment generation, selective disclosure proofs, and evaluator replay remain outside this release.

## 2. Existing ENS practices preserved

### Published decision policy

SPP3 publishes eligibility rules, evaluation criteria, program terms, and committee process. The Marketplace RFP adds a marketplace-specific hard eligibility gate and weighted rubric.

### Committee attribution and voting

The ratified SPP3 committee model defines committee roles, quorum, and the decision rule. Voting or ranking requires three of four Member seats to be active and participating. Decisions use a simple majority of participating Members; the Chair votes only as a tiebreaker.

The schema therefore treats evaluator participation, recusals, quorum, and decision rule as first-class decision attributes.

### Independent verification

The Marketplace RFP requires milestones to identify what ships, when it is expected, and how completion can be independently verified. Post-go-live traction gates use independently observable evidence, including on-chain activity.

The delivery-condition object models a target date or review window, verification method, verifier, evidence, dependencies, payment amount, and consequence.

### Eligibility and merit are distinct

The Marketplace RFP states that applications failing the hard eligibility gate are returned without scoring and that this is not a quality judgment.

The record model therefore distinguishes `decision.status=ineligible` from `decision.status=rejected`. Merit findings are required for approval and rejection; an ineligible disposition is linked to the failed eligibility rule.

### Privacy and selective disclosure

The Marketplace RFP stores applications confidentially during review. The Charter distinguishes public decision records, selectively disclosed audit material, and confidential source material.

v0.1 does not define a deterministic public projection of a confidential canonical record. That boundary is retained as an explicit review question.

## 3. AI-assisted screening

The ENS screening experiment used frontier AI models to apply weighted rubrics, inspect evidence, surface discrepancies, and generate funding recommendations.

The same experiment identified two material risks:

1. publication of exact evaluator instructions can create a gaming surface;
2. AI evaluators can remain agreeable after identifying substantive red flags.

The Charter addresses the first through a public-rule / operational-manifest boundary and optional commit–reveal. It addresses the second through evidence-linked findings, preserved disagreement, and explicit human authority.

## 4. Threat model

### T1 — Criteria drift during review

**Risk:** criteria or AI evaluator configuration changes after applications are observed.

**Control:** versioned policy, evaluator manifest, and optional pre-deadline commitment.

### T2 — Unsupported findings

**Risk:** a material finding cannot be traced to evidence or an explicit judgment classification.

**Control:** evidence-linked material findings and explicit classification of judgment, uncertainty, risk, or unverified claims.

### T3 — Score aggregation obscures disagreement

**Risk:** an aggregate score conceals material disagreement about security, eligibility, scope, budget, or delivery confidence.

**Control:** disagreement is recorded independently of aggregate scores.

### T4 — Conflict disclosure without resolution

**Risk:** a disclosed material relationship continues to affect an adjudicated decision.

**Control:** adjudicated records cannot leave a material conflict in disclosed or unresolved state; recusals remain attributable.

### T5 — AI recommendation acquires de facto authority

**Risk:** reviewers treat an AI score or recommendation as binding despite a policy that reserves authority to humans.

**Control:** the decision authority is explicitly human-governed; AI systems cannot occupy the decision-authority type.

### T6 — Milestones reduce to activity reports

**Risk:** funded work reports effort without establishing whether a delivery condition was met.

**Control:** delivery conditions identify observable outputs or outcomes and a verification method.

### T7 — Transparency exposes protected material

**Risk:** public auditability reveals private, security-sensitive, or commercially sensitive material.

**Control:** disclosure classification and selective audit access. Hash commitments remain optional and are not treated as cryptographic guarantees unless their mechanism and anchor are specified.

### T8 — Administrative cost exceeds accountability value

**Risk:** full records impose disproportionate process cost on low-value or routine grants.

**Control:** program-defined materiality tiers and simplified records that preserve the Section 4 invariants.

### T9 — Nominal conformance

**Risk:** a schema-valid record contains cross-field contradictions such as unsupported factual findings, dangling references, inconsistent eligibility, unresolved conflicts, or unattributed committee action.

**Control:** a separate conformance layer checks cross-field relations and is exercised against adversarial cases in CI.

## 5. Marketplace RFP worked example

As of August 15, 2026, the Marketplace RFP submission window is closed. Committee evaluation is scheduled for August 5–19, with the award announcement on or before August 28.

The RFP is a useful test case. It contains:

- a hard eligibility gate;
- a five-criterion weighted rubric;
- a named committee process with published quorum and voting rules;
- confidential application handling;
- milestone-gated payment;
- independently verifiable and on-chain traction requirements;
- a defined award threshold.

The example does not identify, score, recommend, or reject any real applicant. It maps the public process into a fictional pending record.

The reviewed public artifacts do not identify a post-decision factual/procedural correction process. The example records that documentation gap as `challenge.processDefined=false`. This does not assert that no internal or unpublished process exists, and it does not propose a rule change during the active review.

## 6. Structural validity and record conformance

JSON Schema validates representation. The conformance validator checks relations across fields: reference resolution, evidence requirements, weight completeness, eligibility consistency, decision-state transitions, conflict closure, committee attribution, correction-path declaration, timestamp ordering, delivery conditions, and AI evaluator-manifest state.

A validator pass establishes internal consistency with the v0.1 profile. It does not establish that cited evidence is true, that substantive judgment is sound, or that ENS has adopted the Charter.

`CONFORMANCE.md` defines the checks and severity model.

## 7. Retrospective records

A decision record can be created after the decision it documents. v0.1 therefore permits `decision.decidedAt` to precede `timestamps.createdAt`.

The temporal invariant is narrower: the governing policy must have been effective by the time of the decision, and `updatedAt` cannot precede `createdAt`.

This permits retrospective testing of historical decisions without misrepresenting record creation time.

## 8. Release integrity boundary

v0.1 does not define canonical JSON serialization, record signing, or proof binding. The optional record-level `integrity` object remains descriptive.

Release identity is anchored to the reviewed Git commit SHA. A release archive receives a published SHA-256 digest for that exact artifact. `RELEASE-INTEGRITY.md` defines the procedure and its limits.

## 9. Source map

- Marketplace RFP authorization: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP rubric and timeline: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 program authorization and committee model: https://discuss.ens.domains/t/social-spp3-program-authorization-and-committee-model/22086
- AI grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
