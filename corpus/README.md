# Retrospective decision corpus

This corpus is an empirical test of the Grant Decision Integrity ontology and tooling. It is not a benchmark of applicant merit and MUST NOT be constructed by editing records until validators pass.

## Research questions

For real historical decision processes, measure:

1. which required decision-integrity fields are recoverable from preserved public or authorized audit artifacts;
2. which fields require interpretive judgment rather than direct extraction;
3. which conformance findings correspond to genuine procedural gaps versus representation or annotation defects;
4. the administrative cost of constructing and independently reviewing a record;
5. whether policy pinning, conflict attribution, disagreement preservation, challenge representation, delivery conditions, and public projection remain proportionate in practice.

## Sampling

The first corpus SHOULD deliberately span heterogeneous decision states and mechanisms, including where source evidence permits:

- hard eligibility failure;
- merit rejection;
- approved award;
- committee/quorum decision;
- recusal or material conflict;
- policy-version ambiguity or change;
- delivery/milestone or payment condition;
- material public/private evidence separation;
- AI-assisted evaluation only where historical evidence actually establishes such use;
- an incomplete public case expected to retain unresolved warnings.

Do not invent missing process details to complete a case.

## Case directory contract

Each case directory SHOULD contain:

- `case.json` — study metadata and annotation metrics;
- `sources/` — preserved source bytes where redistribution is lawful;
- `source-artifacts/` — source-artifact metadata binding URIs to preserved bytes;
- `record.json` — canonical confidential or public decision record as applicable;
- `projection/` — projection spec/output when relevant;
- `phase2/` — only when historically justified;
- `verification.json` — machine-readable validator output;
- `review.md` — unresolved gaps, interpretive decisions, and explicit non-claims.

Protected applicant material MUST NOT be added to the public repository merely to improve corpus completeness.

## Annotation protocol

Annotators MUST classify each populated material field as one of:

- `direct-source` — directly represented by a cited artifact;
- `derived` — mechanically derived from directly represented data;
- `interpretive` — requires a documented mapping judgment;
- `unknown` — insufficient evidence;
- `not-applicable` — outside the decision process represented.

A missing public artifact is not evidence that the underlying procedure did not exist. Record `unknown` or the applicable validator warning unless authoritative evidence supports the stronger proposition.

## Measurements

For every case record:

- annotation start/end or elapsed minutes;
- source-artifact count;
- required-field observability rate;
- direct/derived/interpretive/unknown counts;
- validator errors and warnings before adjudication;
- validator findings confirmed as process gaps;
- validator findings resolved as annotation/model defects;
- projection preparation time where applicable;
- Phase II preparation time where historically applicable;
- reviewer disagreement count;
- unresolved questions after review.

On a subset, two reviewers SHOULD independently encode the same case before reconciliation. Report agreement by field classification and material proposition, not merely whether final JSON files match.

## Anti-circularity rule

Validator success is not the outcome variable. Preserve the pre-adjudication record, initial findings, changes made after review, and rationale for those changes. A record that passes only because undocumented facts were inferred is a failed corpus case, not a successful validation.

## Merit boundary

The corpus evaluates reconstructability and assurance mechanisms. It does not re-score historical applicants or decide whether a substantive funding judgment was correct.
