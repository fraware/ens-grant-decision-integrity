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
- `record-initial.json` — exact initial record bytes before adjudication/reconciliation;
- `record-reconciled.json` — exact reconciled record bytes only if review changes the record;
- `projection/` — projection spec/output when relevant;
- `phase2/` — only when historically justified;
- `review.md` — residual gaps and case-specific interpretation notes.

Every source entry carries an exact `sourceUri`. A `redistributable` source also declares relative `metadataPath` and `bytesPath`; the corpus CLI re-runs `source_artifact.py` verification and requires the case artifact ID and source URI to match the verified metadata. `reference-only` and `authorized-audit-only` entries require an explanatory note and are not represented as publicly byte-verified.

A `public-only` case cannot contain an `authorized-audit-only` source. Protected applicant material must not be added to the public repository merely to improve completeness.

Checked-in empirical cases live under `corpus/cases/<case-id>/`. CI runs `scripts/validate_corpus_cases.py`, discovers every `case.json` in that directory, re-verifies its exact record snapshot and validator-output binding, and fails if any checked-in case violates the corpus contract. A case may legitimately contain recorded validator errors; CI requires those errors to match the exact validator output rather than requiring the historical reconstruction itself to be green.

## Record snapshot identity

`recordHash` is `sha256:<hex>` over the exact file bytes identified by the snapshot's relative `path`. It is not a JCS or semantic-content hash. The case CLI resolves the path inside the case directory, rejects absolute/path-escape references, re-hashes the file, and compares it with the declared digest.

Real cases cannot use the template zero hash. If review changes a record, both initial and reconciled bytes remain addressable, their hashes must differ, `review.reconciled` must be true, and reconciliation notes plus a change rationale are retained.

The file hash proves identity of the supplied bytes only. It does not prove that the annotation was correct or that the file contains every fact that existed historically.

## Validator-output binding

For a real case, the corpus CLI does not trust `verification.initialFindings` as self-authenticating bookkeeping. After verifying the exact initial record bytes, it parses that file and runs the repository decision-record validator on those bytes. The complete machine finding multiset must match the recorded initial findings by severity, code, path, and message. An omitted finding, an invented finding, or a nearby-but-different path/message fails closed.

A schema-invalid initial record is admissible evidence. The corpus should preserve that exact initial state and its `SCHEMA` finding rather than repair the record before measuring it. This keeps validator success from becoming the study outcome.

For the final state, the CLI validates `record-reconciled.json` when review changed the record and otherwise reuses the initial validator result. `verification.finalErrors` and `verification.finalWarnings` must equal the validator's rendered final output in validator order. The metrics output reports whether initial and final validator findings were actually verified. Without case-directory context, those verification flags remain false rather than implying that a record was checked.

This binding establishes consistency between the supplied record bytes, the repository validator, and the recorded finding inventory. It does not establish that the validator is correct, that the record is complete, or that a finding corresponds to a real-world procedural defect.

## Annotation classes

Each material field is classified as:

- `direct-source` — directly represented by cited source evidence;
- `derived` — mechanically derived from cited source evidence; document the derivation;
- `interpretive` — requires a documented mapping judgment over cited source evidence;
- `unknown` — insufficient evidence;
- `not-applicable` — outside the represented process/profile; document why.

Every field counted as reconstructable (`direct-source`, `derived`, or `interpretive`) requires at least one declared case source ID. Derived and interpretive fields also require a rationale. A source linkage does not by itself mean the source bytes were publicly preserved or verified; source availability and byte-verification status are reported separately. `unknown` is an admissible result. Missing public evidence is not proof that the underlying procedure did not exist.

## Metrics

Run:

```bash
python scripts/corpus_metrics.py corpus/path/to/case.json
```

For real cases the CLI verifies declared record-snapshot bytes, the corresponding initial/final decision-record validator output, and any redistributable source artifacts before emitting metrics. It reports source counts, byte-verification status, validator-binding status, required-field reconstructability, direct-source and unknown rates, interpretive share, elapsed minutes, and finding dispositions. For exactly two independent annotations over the same material field set, it also reports raw classification agreement and Cohen's kappa.

To validate all checked-in empirical cases in one pass, run:

```bash
python scripts/validate_corpus_cases.py
```

Kappa is descriptive agreement evidence, not proof that either annotation is substantively correct. It is undefined when expected agreement is 1. Small-case results must not be generalized as population estimates.

## Anti-circularity

Validator success is not the outcome variable. Preserve the initial record bytes/hash and the exact initial validator findings. If review changes a record, preserve reconciled bytes/hash, the exact final validator output, and a non-empty rationale. Findings are classified after review as confirmed process gaps, annotation defects, model defects, expected warnings, unresolved, or other.

A case that cannot be completed from available artifacts remains informative. Do not infer undocumented facts to turn it green.

## Merit and legitimacy boundary

The corpus evaluates reconstructability, claim discipline, and operational burden. It does not rescore historical applicants, certify the quality of substantive judgment, prove source truth, or determine institutional legitimacy.
