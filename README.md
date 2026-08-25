# ENS Grant Decision Integrity

A versioned draft Charter and machine-readable decision-record profile for making material ENS grant and service-provider decisions reconstructable.

The project originated in the Simocracy proposal **"No Black-Box Grants: Ratify the Rules Before SPP Is Absorbed."** Five ENS Governance funding rounds assigned a cumulative **$219** to that proposal. A dated public-status snapshot for 2026-08-24 records the first three relevant rounds as `ratified` and the August 3 and August 4 rounds as `provisional`. The repository does not treat those decision states as payment, transfer, receipt, or settlement evidence. Allocation is not payment.

**Package / development line:** `ens-gdi` **0.4.0** (`gdi` CLI). This is an engineering checkpoint on `main`, not a claim that `v1.0.0` gates are closed, and not ENS endorsement.

**Latest annotated Git tag:** [v0.3.2](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.3.2). Earlier tags: [v0.3.1](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.3.1) · [v0.3.0](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.3.0) · [v0.2.0](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.2.0) · [v0.1.0](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.1.0).

Do not attribute unreleased `0.4.0` tree behavior to tag `v0.3.2`. Do not describe this checkpoint as `v1.0.0`.

Release lineage in short: v0.1 Charter and schema; v0.2 Phase II evaluator-manifest commitment and anchoring; v0.3 schema 0.2 extensions, projection, and alternate anchor fixtures; post-v0.3.2 / package 0.4.0 hardening includes unified `gdi` verifier, claim registry, profiles/adapters, corpus expansion, projection v2, and Rekor v2 module surfaces (see `RELEASE-INTEGRITY.md` and `docs/V1_0_0_GATE_CHECKLIST.md`).

## What this repository provides

The profile records enough information for a third party to reconstruct the procedural basis of a material funding decision:

- the versioned public rules governing the review;
- eligibility results and evidence for failed gates;
- evaluation criteria, material findings, and evidence references;
- evaluator participation, disagreement, conflicts, recusals, and substitutions;
- the human-governed decision authority and decision state;
- a factual/procedural correction path;
- delivery conditions for funded awards;
- minimum provenance when AI materially informs a recommendation.

JSON Schema validates record structure. A separate conformance validator checks cross-field relations that JSON Schema alone cannot express. Additive modules cover evaluator-manifest commitment (Phase II), optional schema 0.2 pinning and authority identity, deterministic confidential-to-public projection (v1 and v2), exact-byte source-artifact verification for policy-pin evidence, a unified `gdi` verifier and claim registry, ENS-oriented profiles/adapters, and a predeclared retrospective-corpus protocol for empirical reconstructability testing.

## Repository layout

| Path | Purpose |
|---|---|
| `CHARTER.md` | Normative decision-integrity requirements (draft governance proposal — not adopted ENS policy) |
| `schema/grant-decision-record.schema.json` | JSON Schema Draft 2020-12 record format (default `schemaVersion` `"0.1"`) |
| `schema/grant-decision-record-0.2.schema.json` | Optional schema 0.2 extensions (`policyPinning`, `authorityIdentity`) |
| `schema/grant-decision-public-projection-0.2.schema.json` | Relaxed schema for projected public records with `withheldCommitments` |
| `schema/source-artifact.schema.json` | Metadata contract binding an exact source URI to preserved raw bytes |
| `CONFORMANCE.md` | Cross-field conformance rules, severity model, and rule-ID index |
| `scripts/conformance.py` | Semantic conformance validator |
| `scripts/source_artifact.py` | Build/verify SHA-256 metadata over exact preserved source bytes |
| `scripts/verify_policy_pins.py` | Verify schema 0.2 policy pins against byte-verified source artifacts |
| `SOURCE-ARTIFACTS.md` | Source-capture assurance chain, CLI, and non-claims |
| `src/gdi/` | Packaged unified verifier (`gdi` entry point) |
| `claims/` | Machine-readable claim registry |
| `profiles/` | ENS-oriented profile definitions |
| `adapters/` | Operator-facing mapping adapters (do not score merit) |
| `templates/` | Operator worksheets |
| `corpus/` | Predeclared retrospective study plan, case schema/template, empirical cases, and protocol |
| `scripts/corpus_metrics.py` | Validate corpus cases and compute descriptive reconstructability/agreement metrics |
| `scripts/study_status.py` | Revalidate empirical cases and report progress against predeclared gates |
| `corpus/STUDY-STATUS.md` | Semantics and claim boundaries for machine-readable study-progress reporting |
| `phase2/` | Evaluator-manifest commitment, anchoring (incl. Rekor v1/v2 modules), run attestation, replay, evidence bundles |
| `projection/` | Deterministic confidential-to-public record projection (v1 and v2) |
| `examples/` | Fictional worked examples and a verification-bundle smoke fixture |
| `methodology/GRANT-DECISION-INTEGRITY.md` | Draft twelve-step review methodology |
| `docs/ADOPTER-GUIDE.md` | Short operator-facing adoption guide |
| `docs/V1_0_0_GATE_CHECKLIST.md` | Engineering gate tracker for a future `v1.0.0` — **not** a release claim |
| `ADOPTION.md` | Adoption pathway for ENS grant programs |
| `VALIDATION.md` | Validation contract and expected outcomes |
| `DESIGN-NOTES.md` | Design rationale, threat model, and scope boundaries |
| `RELEASE-INTEGRITY.md` | Release-identity and archive-integrity procedure |
| `ASSURANCE-CASE.md` | Bounded assurance map to the claim registry |
| `DEFERRED.md` | Explicit non-goals and deferred work at the v1.0.0 boundary |
| `REVIEW.md` | Adversarial review guide |
| `CONTRIBUTING.md` | Contribution preferences and pre-change validation |
| `SECURITY.md` | Sensitive-disclosure reporting |
| `CITATION.cff` | Citation metadata aligned with package version `0.4.0` |
| `provenance/simocracy-funding.json` | Recorded historical allocation amounts and source identifiers |
| `provenance/simocracy-status-2026-08-24.json` | Dated platform decision-status snapshot; financial evidence kept separate |
| `provenance/ALLOCATION-CAPTURE.md` | Friday/post-event provenance procedure without status conflation |

## Quickstart

Install the package (editable) and run the unified CLI, or use the script-based validation contract:

```bash
python -m pip install -e ".[dev]"
gdi --version
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_regressions.py
```

Useful `gdi` surfaces (see `--help` for full options):

```bash
gdi verify-record examples/spp3-marketplace-rfp.example.json
gdi verify-bundle examples/verification-bundle --json
gdi claims --id C2
gdi profiles
```

The Marketplace example is intentionally pending. It should produce no conformance errors and one warning, `CHAL003`, which records that the reviewed public process artifacts do not identify a post-decision route for correcting factual or procedural errors. See `VALIDATION.md` for the full contract, including source-artifact, corpus, Phase II, schema 0.2, projection, and bundle suites.

## Phase II (evaluator provenance)

`phase2/` is an additive protocol for evaluator-manifest commitment, anchor-profile verification, run attestation, replay evidence, and graph verification. Grant-decision `schemaVersion` remains `"0.1"`. Phase II does not change v0.1 Charter, schema, or conformance behavior.

A Phase II graph pass establishes only the claims in `phase2/CLAIM-MATRIX.md`. A valid commitment is not execution. A signed run is an assertion. Artifact replay agreement is not proof that the recorded implementation was re-executed and is not correctness, fairness, or legitimacy. Hosted models may be `not-replayable`. Hashes are not institutional authority. AI systems cannot approve, reject, suspend, or release funding.

```bash
python -m pip install -r phase2/requirements.txt
python -m pytest phase2/tests
python phase2/src/cli.py verify-graph --bundle phase2/examples/retrospective-public.bundle.json
```

Public examples and many tests use recorded-fixture receipts under shipped test-log keys. Fixture profiles do **not** establish inclusion in a production public log. Rekor v1 remains a historical compatibility profile. A Rekor v2 module exists (`phase2/src/anchors/rekor_v2.py`); live Sigstore TUF TrustedRoot / SigningConfig online issuance remains fail-closed until an official client integration is pinned. Production `rfc3161` fails closed until standards-conformant CMS/RFC 3161 verification is implemented. See `phase2/ADMIN-BURDEN.md`, `phase2/CLAIM-MATRIX.md`, and `phase2/DEFERRED.md`.

Current replay generation emits replay-report v2 (`exact-match`, `diverged`, `not-replayable`) from canonical artifact recomputation. Historical replay-report v1 remains schema-frozen for compatibility; its `bounded-match` digest-distance mechanism is rejected by the current verifier. New evidence carrying replay-report v2 uses evidence-bundle v2.

## Schema 0.2 extensions and projection

Optional schema `0.2` extensions do not mutate v0.1 behavior:

- `schema/grant-decision-record-0.2.schema.json` — optional `policyPinning` and `authorityIdentity`
- `schema/grant-decision-public-projection-0.2.schema.json` — relaxed requirements for projected public records
- `projection/` — deterministic confidential-to-public record projection with withheld commitments
  - **v1:** top-level redaction paths; fails closed on silent top-level omission or ambiguous publish/withhold disposition; refuses to overwrite non-null source integrity metadata
  - **v2:** RFC 6901 path disposition rules; arrays treated atomically; explicit dispositions required
- `phase2/src/anchors/rfc3161.py` — reserved production RFC 3161 profile plus recorded test fixture; production `rfc3161` fails closed
- `phase2/src/anchors/ethereum.py` — Ethereum calldata fixture profile; live mainnet anchoring is not implemented
- `examples/tier-a-simplified-grant.example.json` — fictional Tier A approved grant with pinning and structured authority

```bash
python scripts/conformance.py examples/tier-a-simplified-grant.example.json
python -m pytest scripts/test_schema_02.py
python -m pytest projection/tests
python projection/src/cli.py --confidential examples/tier-a-simplified-grant.example.json --spec projection/examples/tier-a-projection-spec.json --out /tmp/tier-a-public.json
```

Cryptographic selective disclosure remains deferred; see `phase2/DEFERRED.md`.

## Source artifacts and policy pins

Schema 0.2 can declare `policyPinning` content hashes. The source-artifact module supplies the missing operational check from that declaration to exact preserved bytes:

```bash
python -m pytest scripts/test_source_artifact.py scripts/test_policy_pins.py
python scripts/source_artifact.py verify --metadata policy.artifact.json --file policy.bytes
python scripts/verify_policy_pins.py --record record.json --artifact policy.artifact.json policy.bytes
```

The source verifier re-hashes the supplied raw bytes and checks byte length and SHA-256. The policy-pin verifier then requires exact URI and hash equality against a byte-verified artifact. It does not retrieve the source, normalize it, authenticate source ownership, decide whether the source was institutionally adopted, or prove that the bytes existed at `capturedAt` or `policyPinning.pinnedAt`. Decision-surface semantics remain in the record and the conformance layer. See `SOURCE-ARTIFACTS.md`.

## Retrospective empirical corpus

`corpus/` defines the empirical test before real cases are counted. `study-plan.json` predeclares the heterogeneous sampling strata, primary metrics, double-annotation rule, anti-circularity rule, merit boundary, and privacy boundary. `schema/case.schema.json` defines the machine-readable case contract. `case-template.json` is explicitly marked `template: true` and is not empirical evidence.

The development tree currently contains **nine** checked-in public-only empirical reconstructions (SPP2 and SPP3). Machine `study_status` reports:

- `status`: `in-progress`
- case count: **9** (predeclared target 8–12) — minimum and maximum gates met
- required strata declared coverage: **met** (`requiredUnresolved` empty)
- double annotation: **0/9** (need ≥3 at current corpus size; minimum fraction 0.25) — **blocked**
- `readyForFinalReview`: **false**

This status is descriptive study-progress evidence only. Second-annotation handoffs are prepared under `corpus/second-annotation-handoffs/`; human independent annotations have not been returned. Do not fabricate second annotations.

```bash
python -m pytest scripts/test_corpus.py scripts/test_corpus_validator_binding.py scripts/test_study_status.py
python scripts/corpus_metrics.py corpus/case-template.json
python scripts/validate_corpus_cases.py
python scripts/study_status.py
```

For a real case, the corpus CLI requires a traceable source record, re-hashes the exact initial record file identified by the case, and—when review changes the record—re-hashes the reconciled record file as well. Paths are case-relative and cannot escape the case directory. Redistributable source entries must carry source-artifact metadata and preserved bytes; the CLI re-runs source-artifact verification and requires the case artifact ID and source URI to match the verified metadata. Reference-only and authorized-audit-only entries remain explicitly outside the public byte-verification claim.

The metrics are descriptive: required-field reconstructability, direct-source and unknown rates, interpretive share, annotation time, finding dispositions, and—when exactly two independent annotations cover the same material field set—raw classification agreement and Cohen's kappa. Neither high validator success nor high annotator agreement establishes substantive correctness, fairness, source truth, or institutional legitimacy.

The corpus must preserve exact initial record bytes/hash and initial findings. If review changes a record, reconciled bytes/hash, the change rationale, reconciliation state, and reconciliation notes are retained. `unknown` is an admissible result; undocumented facts must not be inferred merely to make a case validate. See `corpus/README.md` and `corpus/STUDY-STATUS.md`.

## What validators prove and do not prove

**Prove:** record structure and declared cross-field consistency under the selected profile; exact byte identity for a supplied source artifact when the source-artifact verifier succeeds; exact policy-pin URI/hash linkage to a byte-verified artifact when the policy-pin verifier succeeds; Phase II graph claims bounded by `phase2/CLAIM-MATRIX.md` when a version-compatible bundle is present; deterministic projection from the supplied confidential input under a declared projection spec; corpus-case structural/protocol consistency, exact-byte agreement for declared record snapshots and redistributable sources when those checks apply, and the arithmetic of its descriptive metrics when the corpus validator succeeds; claim-registry–bounded results from `gdi verify-bundle` for checks that actually ran.

**Do not prove:** truth or completeness of cited evidence; source ownership or institutional adoption; byte verification of reference-only or authorized-audit-only corpus sources; quality of substantive judgment; legitimacy of the governing policy; representativeness of the retrospective corpus; correctness of an annotation merely because annotators agree; independently verifiable existence of an AI manifest commitment without verifying a supported anchor profile; execution or re-execution of a committed evaluator implementation unless a separate execution protocol establishes that fact; funding authority; payment, transfer, receipt, or settlement of Simocracy allocations; ENS DAO / Foundation / SPP committee endorsement.

`ok=true` with `not-run` or `not-applicable` checks must not be marketed as full-profile production assurance.

## AI provenance boundary

When AI materially informs a grant recommendation, v0.1 requires a versioned evaluator manifest and records a minimum provenance envelope: model identity, human-review policy, commitment metadata, reveal state, and the application deadline used for the timing check.

The v0.1 validator checks only that the declared commitment time precedes the declared submission deadline. v0.1 does not define canonical manifest serialization, commitment generation, an independently verifiable timestamp or publication anchor, proof verification, selective-disclosure proofs, or evaluator replay. A schema 0.1 record without a Phase II evidence bundle therefore does not prove that a commitment existed at the declared time or that the committed configuration was actually used.

## ENS process mapping

The worked example maps the public SPP3 Marketplace process without evaluating any applicant. It records all seven published hard eligibility conditions, the published M1–M5 weights, the public rules and sources governing mandate, eligibility, evaluation criteria, conflict rules, and decision procedure, the published committee quorum and decision rule, and milestone and traction-verification requirements.

The example is a dated snapshot of the published process. It is fictional, does not identify, score, recommend, or reject a real applicant, and does not need to be rewritten when the underlying RFP later reaches an award state.

## Scope and status

This project governs the integrity of the decision record. It does not determine which projects ENS should fund, replace substantive committee judgment, establish the truth of cited evidence, or create authority for AI systems to approve, reject, suspend, or release funding.

| Item | Value |
|---|---|
| Package version (`ens-gdi` / `gdi`) | `0.4.0` (engineering checkpoint; unreleased as an annotated tag unless/until tagged) |
| Latest annotated repository tag | `v0.3.2` |
| Default grant-decision `schemaVersion` | `"0.1"` |
| Optional extensions | schema `"0.2"` (additive) |
| Phase II versions | manifest/envelope/anchor/run predicate v1; replay report v1 historical and v2 current; evidence bundle v1 historical and v2 current |
| Projection | v1 (top-level) and v2 (RFC 6901 path dispositions) |
| Charter status | Draft governance proposal — not adopted ENS policy |
| Methodology status | Draft — not a frozen ENS standard |
| Retrospective corpus | In progress: 9 empirical cases; required strata coverage met; 0/9 double annotated; `readyForFinalReview=false` |
| Simocracy decision-status snapshot | $219 across five relevant rounds; 3 ratified and 2 provisional as observed 2026-08-24 |
| Financial evidence | no payment, transfer, receipt, or settlement evidence recorded in the dated 2026-08-24 snapshot |
| Friday / post-event capture | blocked until an authoritative artifact exists; template/checklist only — no invented outcomes |
| Endorsement | Does not claim endorsement by ENS DAO, the ENS Foundation, or any SPP committee |
| `v1.0.0` | Not claimed; see `docs/V1_0_0_GATE_CHECKLIST.md` for remaining blockers |

For adoption guidance, see `docs/ADOPTER-GUIDE.md` and `ADOPTION.md`. For security-sensitive reports, see `SECURITY.md`.

## Sources

- ENS SPP3 Marketplace RFP: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP submission timeline and rubric: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 program authorization and committee model: https://discuss.ens.domains/t/social-spp3-program-authorization-and-committee-model/22086
- ENS AI grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
- Simocracy funding status surface: https://www.simocracy.org/funding
