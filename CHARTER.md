# ENS Grant Decision Integrity Charter — Draft v0.1

## 1. Purpose

This Charter defines minimum procedural guarantees for material grant and service-provider funding decisions made on behalf of ENS.

Its purpose is to preserve accountable human judgment as grant evaluation becomes more technical, evidence-intensive, and increasingly assisted by automated systems. It establishes a record of **which rules governed a decision, which evidence supported material findings, who exercised authority, where conflicts or disagreement existed, and how the resulting award is verified after selection**.

The Charter is neutral on treasury custody, board composition, funding strategy, and the substantive merits of individual applicants. It governs the integrity of the adjudicative process.

## 2. Scope

The Charter applies to a funding program, grant, service-provider award, or other discretionary allocation when the responsible ENS body determines that the decision is material by value, risk, strategic importance, or use of automated evaluation.

A program MAY use a simplified record for low-value or routine awards. Simplification MUST preserve the core invariants in Section 4.

This Charter does not itself establish eligibility, scoring weights, program budgets, or selection thresholds. Those remain program-specific and must be referenced through the applicable decision policy.

## 3. Roles

Each covered decision MUST identify the following roles where applicable:

- **Policy authority** — the body authorized to establish the program mandate and evaluation rules.
- **Evaluator** — a human or automated system producing findings, scores, recommendations, or evidence summaries.
- **Decision authority** — the human body authorized to approve, reject, defer, suspend, or modify an award.
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

The final disposition MUST identify the decision authority and the date of the decision.

Where a committee acts collectively, the record MUST identify participating members, recusals, quorum status, and the applicable voting or consensus rule.

### 4.4 Conflict handling

Material conflicts of interest MUST be disclosed and resolved according to the governing conflict policy.

A recusal MUST identify the affected evaluator or decision-maker and the decision surface from which they were excluded. If a substitution or alternate reviewer is used, the record MUST identify that substitution.

### 4.5 Preserved disagreement

Material disagreement among evaluators SHOULD remain visible when it affects risk, eligibility, security, scope, budget, or delivery confidence.

An aggregate score MUST NOT be treated as evidence that disagreement did not exist.

### 4.6 Explicit human authority

An automated system MUST NOT possess unilateral authority to approve, reject, suspend, or release material grant funding.

When an automated system materially informs a recommendation, the final decision record MUST identify the responsible human decision authority.

### 4.7 Challenge path

Applicants MUST have a defined process to identify factual errors or procedural deviations.

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

Experimental work MAY use learning gates, decision gates, or evidence-generation milestones when output cannot responsibly be fixed in advance. The gate itself must remain observable.

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

AI outputs are recommendations or evidence-processing artifacts. They are not institutional authority.

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

Where publishing the exact evaluator configuration before applications close would create a material gaming surface, the program SHOULD separate:

**Public normative rules**
- mandate;
- eligibility;
- evaluation dimensions;
- evidence standards;
- conflict rules;
- appeal rights;
- human authority.

from:

**Operational evaluator details**
- exact prompts;
- red-team queries;
- retrieval sequences;
- ensemble implementation;
- hidden consistency checks.

The program MAY cryptographically commit to the operational evaluator manifest before the review deadline and disclose it after the decision, subject to applicant privacy, security, licensing, and legal constraints.

A commitment proves that a configuration existed in a fixed form. It does not prove that the resulting judgment was substantively correct.

### 5.4 Overrides

A human decision that materially departs from an automated recommendation SHOULD record the departure and its rationale.

A human override is not presumptively an error. The purpose of the record is attribution and reviewability.

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

Hash commitments MAY be used to prove the existence or integrity of withheld artifacts without publishing their contents.

## 7. Proportionality

The record burden SHOULD scale with value and risk.

A program MAY define tiers such as:

- **Tier A — simplified**: low-value or routine grants;
- **Tier B — standard**: material grants requiring complete decision and delivery records;
- **Tier C — enhanced**: high-value, security-sensitive, strategically significant, or AI-material decisions requiring evaluator provenance and stronger auditability.

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

Material changes to eligibility, conflict rules, appeal rights, automated authority, or delivery enforcement SHOULD receive public notice under the program's governing process.

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
- automated evaluator provenance when applicable;
- final human disposition;
- override rationale when applicable;
- challenge status;
- award amount if funded;
- delivery conditions;
- public/private disclosure classification;
- timestamps and integrity metadata.

The accompanying JSON Schema defines a machine-readable representation.

## 10. Non-goals

This Charter does not:

- determine which projects ENS should fund;
- require automated scoring;
- require public disclosure of every applicant artifact;
- replace committee judgment with a formula;
- require every grant to use the same rubric;
- guarantee substantive correctness;
- make cryptographic commitment equivalent to institutional legitimacy;
- authorize an accountability body to reinterpret grant quality outside its delegated mandate.

## 11. Adoption and review

An ENS funding program adopting this Charter SHOULD publish:

1. the applicable materiality tiers;
2. the program-specific policy reference;
3. any permitted deviations;
4. the public decision-record location;
5. the responsible appeal and accountability authorities.

The Charter SHOULD be reviewed after each major funding cycle against observed administrative cost, appeals, false or unsupported findings, implementation failures, evaluator gaming, and stakeholder feedback.

## 12. Conformance statement

A program may state that a decision record is **“ENS Grant Decision Integrity Charter v0.1 compatible”** only when the record preserves the core invariants in Section 4 and identifies any deviations from the remaining provisions.

This draft is an implementation proposal, not adopted ENS policy.
