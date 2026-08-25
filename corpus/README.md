# Retrospective decision corpus

This corpus is an empirical test of the Grant Decision Integrity ontology and tooling. It is not a benchmark of applicant merit, a leaderboard, or a collection to be edited until validators pass.

The predeclared study design is `study-plan.json`. Case structure is defined by `schema/case.schema.json`. The checked-in `case-template.json` is marked `template: true` and must not be counted as empirical evidence.

## Research questions

For real historical decision processes, measure:

1. which material and required decision-integrity fields are reconstructable from preserved public or authorized audit artifacts;
2. which fields require mechanical derivation or interpretive mapping rather than direct extraction;
3. which conformance findings correspond to genuine procedural gaps versus annotation/model defects or unresolved evidence limits;
4. the administrative cost of constructing and independently reviewing a record;
5. whether policy pinning, conflict attribution, disagreement preservation, challenge representation, delivery conditions, AI provenance where historically evidenced, and public projection remain proportionate in practice.

## Sampling discipline

The first corpus is a heterogeneous stress-test, not a statistically representative sample. Cover the predeclared strata in `study-plan.json` before considering validator outcomes. Do not add a case because it is easy to make pass, and do not drop a case because public evidence is incomplete.

AI-assisted evaluation belongs in the corpus only where historical evidence actually establishes material AI use. Do not manufacture an AI case to exercise Phase II.

## Case directory contract

A real case directory should contain, where lawful and applicable:

- `case.json` — study metadata conforming to `schema/case.schema.json`;
- `sources/` — preserved source bytes when redistribution is lawful;
- `source-artifacts/` — exact-byte source-artifact metadata;
- `record-initial.json` — record before adjudication/reconciliation;
- `record-reconciled.json` — only if review changes the record;
- `projection/` — projection spec/output when relevant;
- `phase2/` — only when historically justified;
- `review.md` — residual gaps and case-specific interpretation notes.

Protected applicant material must not be added to the public repository merely to improve completeness. Reference-only or authorized-audit-only source entries can remain metadata references without redistributing protected bytes.

## Annotation classes

Each material field is classified as:

- `direct-source` — directly represented by a cited source artifact;
- `derived` — mechanically derived from directly represented information; document the derivation;
- `interpretive` — requires a documented mapping judgment;
- `unknown` — insufficient evidence;
- `not-applicable` — outside the represented process/profile; document why.

`unknown` is an admissible result. Missing public evidence is not proof that the underlying procedure did not exist.

## Metrics

Run:

```bash
python scripts/corpus_metrics.py corpus/path/to/case.json
```

For each annotation, the tool reports required-field reconstructability, direct-source and unknown rates, interpretive share, elapsed minutes, source-artifact count, and finding dispositions. For exactly two independent annotations over the same field set, it also reports raw classification agreement and Cohen's kappa.

Kappa is descriptive agreement evidence, not proof that either annotation is substantively correct. Small-case results must not be generalized as population estimates.

## Anti-circularity

Validator success is not the outcome variable. Preserve the initial record hash and initial findings. If review changes a record, preserve a reconciled hash and a non-empty rationale. Findings are classified after review as confirmed process gaps, annotation defects, model defects, expected warnings, unresolved, or other.

A case that cannot be completed from available artifacts remains informative. Do not infer undocumented facts to turn it green.

## Merit and legitimacy boundary

The corpus evaluates reconstructability, claim discipline, and operational burden. It does not rescore historical applicants, certify the quality of substantive judgment, or determine institutional legitimacy.
