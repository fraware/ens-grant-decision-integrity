# Design Notes — ENS Grant Decision Integrity v0.1

## 1. Scope

Simocracy ballot reasoning repeatedly highlighted the Grants Charter and commit–reveal treatment of AI-assisted screening. Evidence-linked decision records were part of the same proposal mechanism. Marginal value declined after roughly the first $200 of cumulative funding.

v0.1 implements the proposal's $200 Charter and decision-record schema work item. It records the minimum evaluator-provenance envelope needed to represent the Charter's pre-deadline commitment rule. Commitment generation, external timestamp or publication anchoring, a complete evaluator-manifest format, selective disclosure proofs, and evaluator replay remain outside this release.

## 2. Existing ENS practices preserved

### Published decision policy

SPP3 publishes eligibility rules, evaluation criteria, program terms, and committee process. The Marketplace RFP adds a marketplace-specific hard eligibility gate and weighted rubric.

The record therefore identifies one public governing-policy URI and maps five normative decision surfaces—mandate, eligibility, evaluation criteria, conflict rules, and decision procedure—to declared source URIs. This permits reconstruction of which public artifact governed each surface without collapsing several documents into an invented single policy text.

### Committee attribution and voting

The ratified SPP3 committee model defines committee roles, quorum, and the decision rule. Voting or ranking requires three of four Member seats to be active and participating. Decisions use a simple majority of participating Members; the Chair votes only as a tiebreaker.

The schema therefore treats evaluator participation, recusals, quorum, and decision rule as first-class decision attributes. The conformance layer applies committee quorum and voting requirements only when `decision.authorityKind=committee`; advisory participation by a committee evaluator does not silently convert the final authority into a committee decision.

### Independent verification

The Marketplace RFP requires milestones to identify what ships, when it is expected, and how completion can be independently verified. Post-go-live traction gates use independently observable evidence, including on-chain activity.

The delivery-condition object models a target date or review window, verification method, verifier, evidence, dependencies, payment amount, and consequence.

### Eligibility and merit are distinct

The Marketplace RFP states that applications failing the hard eligibility gate are returned without scoring and that this is not a quality judgment. Its published gate contains seven conditions, including acknowledgment of the SPP3 Program Terms and Award Notice.

The record model therefore distinguishes `decision.status=ineligible` from `decision.status=rejected`. Substantive findings are required for approval, rejection, and suspension; an ineligible disposition is linked to a failed eligibility rule, and a failed rule must identify supporting evidence. An adjudicated decision cannot predate the eligibility check supporting it. The worked example maps all seven published eligibility conditions.

### Privacy and selective disclosure

The Marketplace RFP stores applications confidentially during review. The Charter distinguishes public decision records, selectively disclosed audit material, and confidential source material.

v0.1 does not define a deterministic public projection of a confidential canonical record. That boundary is retained as an explicit review question. Non-public evidence without a URI or content hash is surfaced as a warning, preserving privacy without treating an unlocatable evidence reference as fully auditable.

## 3. AI-assisted screening

The ENS screening experiment used frontier AI models to apply weighted rubrics, inspect evidence, surface discrepancies, and generate funding recommendations.

The same experiment identified two material risks:

1. publication of exact evaluator instructions can create a gaming surface;
2. AI evaluators can remain agreeable after identifying substantive red flags.

The Charter addresses the first by keeping public normative rules distinct from operational evaluator details and requiring a commitment to the versioned evaluator manifest before applications close whenever AI materially informs a recommendation. It addresses the second through evidence-linked findings, preserved disagreement, explicit human authority, and attributable departures from AI recommendations.

v0.1 does not define how a manifest is serialized or hashed, nor how a commitment is externally anchored. It records the manifest version, model identity, human-review policy, commitment metadata, and reveal state. The validator can compare the declared `committedAt` value with the submission deadline, but that comparison does not prove that the commitment existed at that time. Independently verifiable pre-deadline existence requires the later commitment protocol to specify a trustworthy timestamp or publication anchor.

## 4. Threat model

### T1 — Criteria or evaluator drift during review

**Risk:** criteria or AI evaluator configuration changes after applications are observed, or an in-round policy change is applied inconsistently to evaluations already completed.

**Control:** a public governing-policy URI, explicit source mapping for each normative decision surface, version and effective time, change summary, prior-version and change-notice traceability, explicit record of whether prior evaluations were rerun, and declared pre-deadline evaluator-manifest commitment metadata when AI materially informs a recommendation. External proof of the commitment's pre-deadline existence remains part of the later commit–reveal protocol.

### T2 — Unsupported or misattributed findings

**Risk:** a material finding cannot be traced to evidence, an explicit epistemic classification, or an evaluator who actually participated; or a hard-screen failure records ineligibility without evidence supporting the failed gate.

**Control:** failed eligibility rules require evidence; material findings are evidence-linked or explicitly classified as `judgment`, `uncertainty`, or `unverified-claim`; and evaluator-attribution checks enforce participation and recusal state. Risk can be the subject of a finding without functioning as an epistemic classification.

### T3 — Score aggregation obscures disagreement

**Risk:** an aggregate score conceals material disagreement, or a disagreement is recorded without an attributable evaluator.

**Control:** disagreement is recorded independently of aggregate scores. Every recorded disagreement identifies at least one participating, non-recused evaluator.

### T4 — Conflict disclosure without operational recusal

**Risk:** a disclosed material relationship continues to affect an adjudicated decision, a nominal recusal does not identify the decision surface or replacement reviewer, or the conflict record and evaluator record disagree about whether recusal occurred.

**Control:** adjudicated records cannot leave a material conflict in disclosed or unresolved state. A recusal identifies the affected decision surface, explicitly states whether substitution occurred, resolves any substitute identifier to an active, non-recused evaluator, and must agree with the recused evaluator's own participation state.

### T5 — AI recommendation acquires de facto authority

**Risk:** reviewers treat an AI score or recommendation as binding, or the record retrospectively represents a departure from AI advice before an institutional disposition exists.

**Control:** the decision authority is explicitly human-governed; AI systems cannot occupy the decision-authority type. An AI evaluator cannot materially inform a recommendation unless marked as participating. A departure requires materially influential AI evaluation, a rationale, and a non-pending institutional disposition.

### T6 — Award state outruns the decision

**Risk:** a pending or deferred record carries a positive award and thereby encodes funding before an approving disposition.

**Control:** positive `awardedAmount` is prohibited for pending, deferred, ineligible, and rejected states. Approval and suspension preserve the award amount; suspension also requires attributable findings and delivery conditions.

### T7 — Challenge state outruns the decision

**Risk:** a record claims a challenge is active or resolved without a defined process, represents a post-decision challenge while the decision is still pending, or marks a challenge resolved without recording the resolution.

**Control:** active/completed challenge states require a defined process; pending decisions cannot claim post-decision challenge activity; resolved challenges require a resolution.

### T8 — Milestones reduce to activity reports

**Risk:** funded work reports effort without establishing whether a delivery condition was met.

**Control:** delivery conditions identify observable outputs or outcomes and a verification method.

### T9 — Transparency exposes protected material

**Risk:** public auditability reveals private, security-sensitive, or commercially sensitive material.

**Control:** disclosure classification and selective audit access. Hash commitments remain descriptive unless their mechanism and anchor are specified.

### T10 — Administrative cost exceeds accountability value

**Risk:** full records impose disproportionate process cost on low-value or routine grants.

**Control:** program-defined materiality tiers and simplified records that preserve the Section 4 invariants.

### T11 — Nominal conformance

**Risk:** a schema-valid record contains cross-field contradictions such as undeclared governing-policy sources, unsupported hard-screen failures, unsupported or misattributed findings, inconsistent eligibility timing, a non-pending decision timestamp later than the record's own last-update time, contradictory recusal state, unresolved conflicts, incomplete recusal provenance, false committee-authority inference, premature award or challenge state, or a declared AI commitment time after applications close.

**Control:** a separate conformance layer checks cross-field relations and is exercised against adversarial and valid-edge cases in CI.

## 4.1 Phase II protocol controls (P1–P10)

These rows are additive. They do not rewrite T1–T11 above. v0.1 still does not, by itself, prove pre-deadline existence of a commitment.

| ID | Failure mode | Phase II control |
|---|---|---|
| P1 | Two serializers produce different bytes for one manifest. | RFC 8785 JCS, I-JSON only; T1 dual implementation. |
| P2 | A material manifest change after commitment still opens. | Digest opening; adversarial test T2. |
| P3 | Two salts are treated as one commitment. | 32-byte CSPRNG salt; T3. |
| P4 | Another object type verifies as an evaluator-manifest commitment. | Versioned domain string; T4. |
| P5 | programId, roundId, or deadline drift after commitment. | Those fields bind both manifest and envelope; T5. |
| P6 | A commitment at or after the deadline is treated as pre-deadline. | Profile-verified anchor time, strict inequality; T6. |
| P7 | A corrupted inclusion proof or substituted digest still verifies. | Offline SET, inclusion, checkpoint, and digest match; T7. |
| P8 | Withheld state is reported as manifest-content verification. | Reveal-status gate; T8. |
| P9 | A run attestation with the wrong commitment or output is accepted. | Predicate binding; T9. |
| P10 | Replay is taken as fairness, or Phase II objects become decision authority. | Layer outcomes including honest `not-replayable`; T10–T12. Authority remains on the v0.1 `decision` object. |

Details: `phase2/CLAIM-MATRIX.md` and `phase2/PROTOCOL.md`.

## 5. Marketplace RFP worked example

As of August 15, 2026, the Marketplace RFP submission window is closed. The published deadline was August 5 at 23:59 UTC; committee evaluation is scheduled for August 5–19, with the award announcement on or before August 28.

The RFP is a useful test case. It contains:

- seven hard eligibility conditions;
- a five-criterion weighted rubric (M1 25%, M2 20%, M3 35%, M4 10%, M5 10%);
- a named committee process with published quorum and voting rules;
- confidential application handling;
- milestone-gated payment;
- independently verifiable and on-chain traction requirements;
- a defined award threshold.

The example does not identify, score, recommend, or reject any real applicant. It maps the public process into a fictional pending record, including all seven eligibility gates, the published rubric weights, the public rules URI, and the source governing each of the five normative decision surfaces.

The reviewed public artifacts do not identify a post-decision factual/procedural correction process. The example records that documentation gap as `challenge.processDefined=false`. This does not assert that no internal or unpublished process exists, and it does not propose a rule change during the active review.

## 6. Structural validity and record conformance

JSON Schema validates representation. The conformance validator checks relations across fields: reference resolution, evidence requirements, evaluator and disagreement attribution, weight completeness, governing-policy source traceability, policy-change lineage, eligibility consistency and timing, decision-state transitions, conflict closure, reciprocal recusal state, recusal provenance, committee authority, challenge lifecycle, timestamp ordering, delivery conditions, and declared AI evaluator-manifest timing.

A validator pass establishes internal consistency with the v0.1 profile. It does not establish that cited evidence is true, that substantive judgment is sound, that a commitment existed at its declared time without an external anchor, that a committed evaluator configuration actually ran, or that ENS has adopted the Charter.

`CONFORMANCE.md` defines the checks and severity model.

## 7. Retrospective records

A decision record can be created after the decision it documents. v0.1 therefore permits `decision.decidedAt` to precede `timestamps.createdAt`.

The temporal invariants are narrower: the governing policy must have been effective by the time of an adjudicated decision; the eligibility check supporting that adjudication cannot postdate it; `updatedAt` cannot precede `createdAt`; and a non-pending `decision.decidedAt` cannot be later than `updatedAt`.

This permits retrospective testing of historical decisions without misrepresenting either record creation time or the record's last-update time.

## 8. Release integrity boundary

v0.1 does not define canonical JSON serialization, record signing, or proof binding. The optional record-level `integrity` object remains descriptive.

Release identity is anchored to the reviewed Git commit SHA. A release archive receives a published SHA-256 digest for that exact artifact. `RELEASE-INTEGRITY.md` defines the procedure and its limits.

## 9. Source map

- Marketplace RFP authorization: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP rubric and timeline: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 program authorization and committee model: https://discuss.ens.domains/t/social-spp3-program-authorization-and-committee-model/22086
- AI grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
