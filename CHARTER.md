# ENS Grant Decision Integrity Charter — Draft v0.1

## 1. Purpose

This Charter defines minimum procedural guarantees for material grant and service-provider funding decisions made on behalf of ENS.

Its purpose is to make material decisions reconstructable without displacing accountable human judgment. A conforming record identifies **which rules governed the decision, which evidence supported material findings, who exercised authority, where conflicts or disagreement existed, and which conditions govern challenge and delivery**.

The Charter is neutral on treasury custody, board composition, funding strategy, and the substantive merits of individual applicants. It governs the integrity of the adjudicative process.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

## 2. Scope

The Charter applies to a funding program, grant, service-provider award, or other discretionary allocation when the responsible ENS body determines that the decision is material by value, risk, strategic importance, or material use of AI-assisted evaluation.

A program MAY use a simplified record for low-value or routine awards. Simplification MUST preserve the core invariants in Section 4.

This Charter does not establish eligibility, scoring weights, program budgets, or selection thresholds. Those remain program-specific and MUST be identified through the governing decision policy.

## 3. Roles

Each covered decision MUST identify the following roles where applicable:

- **Policy authority** — the body authorized to establish the program mandate and evaluation rules.
- **Evaluator** — a human or AI system producing findings, scores, recommendations, or evidence summaries.
- **Decision authority** — the human-governed body authorized to approve, reject, defer, suspend, or modify an award.
- **Accountability authority** — the body authorized to verify delivery conditions or administer payment consequences.
- **Applicant** — the person or organization seeking funding.
- **Appeal authority** — the body or procedure authorized to correct factual or procedural errors.

One actor MAY hold more than one role only where the governing program permits it. Role concentration SHOULD be disclosed where it materially affects independence.

## 4. Decision-integrity invariants

Every covered material decision MUST satisfy the following invariants.

### 4.1 Fixed governing policy

The record MUST identify the exact version of the mandate, eligibility rules, evaluation criteria, conflict rules, and decision procedure governing the active review.

Material changes during an active review MUST be versioned and disclosed. A change affecting applicant treatment MUST state its effective time and whether prior evaluations were rerun.

### 4.2 Evidence-linked material findings

Each material finding used to support approval, rejection, ranking, suspension, or payment MUST either:

1. identify the evidence on which it relies; or
2. be explicitly labeled as judgment, uncertainty, or an unverified claim.

Evidence references SHOULD be independently retrievable where privacy, security, and law permit.

### 4.3 Attributable authority

A final disposition MUST identify the decision authority and decision time.

Where a committee acts collectively, the record MUST identify participating members, recusals, quorum status, and the applicable voting or consensus rule.

### 4.4 Conflict handling

Material conflicts of interest MUST be disclosed and resolved according to the governing conflict policy.

A recusal MUST identify the affected evaluator or decision-maker and the decision surface from which they were excluded. If a substitution or alternate reviewer is used, the record MUST identify that substitution.

### 4.5 Preserved disagreement

Material disagreement among evaluators SHOULD remain visible when it affects risk, eligibility, security, scope, budget, or delivery confidence.

An aggregate score MUST NOT be treated as evidence that disagreement did not exist.

### 4.6 Explicit human authority

An AI system MUST NOT exercise unilateral authority to approve, reject, suspend, or release material grant funding.

When an AI system materially informs a recommendation, the final decision record MUST identify the responsible human decision authority.

### 4.7 Challenge path

Applicants MUST have a defined process to identify factual errors or procedural deviations in an adjudicated decision.

The challenge process MAY be limited in scope and time. It need not create a right to relitigate substantive judgment, but it MUST distinguish factual correction from substantive disagreement.

### 4.8 Delivery conditions

A funded award MUST identify observable delivery conditions proportionate to the award.

Each material condition SHOULD specify:

- the expected output or outcome;
- the target date or review window;
- the verification method;
- the verifying authority;
- dependencies outside the grantee's control;
- the payment, remediation, or escalation consequence.

Experimental work MAY use learning gates, decision gates, or evidence-generation milestones when a fixed output would create false precision. The gate itself MUST remain observable.

## 5. AI-assisted evaluation

### 5.1 Permitted role

AI systems MAY assist with:

- eligibility screening;
- evidence collection;
- inconsistency detection;
- rubric application;
- comparative analysis;
- risk flagging;
- drafting;
- summarization.

AI outputs are recommendations or evidence-processing artifacts. They do not constitute institutional authority.

### 5.2 Evaluator manifest

When AI materially informs a covered decision, the program SHOULD maintain a versioned evaluator manifest containing, to the extent technically and legally practical:

- model provider and model identifier;
- model or endpoint version information;
- system and evaluation instructions;
- retrieval sources and data dependencies;
- tool permissions;
- aggregation or ensemble procedure;
- human-review rules;
- material configuration parameters;
- creation time and version identifier.

### 5.3 Commit–reveal boundary

Where publishing the exact evaluator configuration prior to the application deadline would create a material gaming surface, the program SHOULD separate:

**Public normative rules**
- mandate;
- eligibility;
- evaluation dimensions;
- evidence standards;
- conflict rules;
- appeal rights;
- human authority.

**Operational evaluator details**
- exact prompts;
- red-team queries;
- retrieval sequences;
- ensemble implementation;
- hidden consistency checks.

The program MAY cryptographically commit to the operational evaluator manifest prior to the review deadline and disclose it after the decision, subject to applicant privacy, security, licensing, and legal constraints.

A commitment can establish that a subsequently disclosed manifest matches the value committed at the recorded time, assuming the commitment and its time anchor are trustworthy. It does not establish that the evaluator used that manifest, that the review was complete, or that the resulting judgment was correct.

### 5.4 Overrides

A human decision that materially departs from an AI recommendation SHOULD record the departure and its rationale.

A human override is not presumptively an error. The record exists to preserve attribution and reviewability.

## 6. Privacy, security, and redaction

Decision transparency does not require indiscriminate disclosure.

A record MAY redact or withhold:

- personal data;
- security-sensitive implementation detail;
- protected commercial information;
- confidential applicant material;
- information restricted by law or contract.

A material redaction SHOULD identify the category and basis for withholding without revealing the protected content itself.

The program SHOULD distinguish:

1. public decision record;
2. selectively disclosed audit material;
3. confidential source material.

A hash commitment MAY support later integrity checks over a withheld artifact when the commitment mechanism and its anchor are specified. v0.1 does not define such a mechanism.

## 7. Proportionality

Recording requirements SHOULD scale with value and risk.

A program MAY define tiers such as:

- **Tier A — simplified**: low-value or routine grants;
- **Tier B — standard**: material grants requiring complete decision and delivery records;
- **Tier C — enhanced**: high-value, security-sensitive, strategically significant, or materially AI-assisted decisions requiring stronger evaluator provenance and auditability.

The thresholds are program-specific. A monetary threshold alone SHOULD NOT determine enhanced treatment where security or institutional risk is high.

## 8. Policy evolution

Programs MAY revise evaluation procedures between rounds.

A revision SHOULD include:

- new version identifier;
- effective date;
- change summary;
- reason for change;
- affected decision surfaces;
- migration treatment for active applications where relevant.

Material changes to eligibility, conflict rules, appeal rights, AI-assisted evaluation rules, or delivery enforcement SHOULD receive public notice under the program's governing process.

## 9. Minimum decision record

A conforming standard record SHOULD contain:

- record version;
- program and round identifier;
- applicant and application identifier;
- governing policy version;
- eligibility disposition;
- evaluation criteria and scores or findings;
- evidence references;
- evaluator identities or permitted pseudonymous identifiers;
- conflicts and recusals;
- material disagreement;
- AI evaluator provenance when applicable;
- final human-governed disposition;
- override rationale when applicable;
- challenge status;
- award amount if funded;
- delivery conditions;
- public/private disclosure classification;
- timestamps and provenance metadata.

The accompanying JSON Schema defines a machine-readable representation. `scripts/conformance.py` checks the v0.1 cross-field conformance profile.

## 10. Non-goals

This Charter does not:

- determine which projects ENS should fund;
- require AI scoring;
- require public disclosure of every applicant artifact;
- replace committee judgment with a formula;
- require every grant to use the same rubric;
- guarantee substantive correctness;
- make cryptographic commitment equivalent to procedural or institutional legitimacy;
- authorize an accountability body to reinterpret grant quality outside its delegated mandate.

## 11. Adoption and review

An ENS funding program adopting this Charter SHOULD publish:

1. the applicable materiality tiers;
2. the program-specific policy reference;
3. any permitted deviations;
4. the public decision-record location;
5. the responsible appeal and accountability authorities.

The Charter SHOULD be reviewed after each major funding cycle against observed administrative cost, appeals, unsupported findings, implementation failures, evaluator gaming, and stakeholder feedback.

## 12. Conformance statement

A program MAY state that a decision record is **“ENS Grant Decision Integrity Charter v0.1 compatible”** only when the record preserves the core invariants in Section 4 and identifies any deviations from the remaining provisions.

Passing the v0.1 schema and conformance validator establishes structural and declared cross-field consistency. It does not establish the truth of cited evidence, the quality of substantive judgment, or institutional adoption of this Charter.

This draft is an implementation proposal, not adopted ENS policy.
