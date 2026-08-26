# v1.0.0 acceptance gate checklist (Gates A-L)

**Evaluated:** 2026-08-26 against final-hardening PR #29.  
**Tag decision:** **DO NOT TAG `v1.0.0` yet.** Genuine independent second annotation is incomplete, active `main` protection does not yet require all six release-critical contexts, the final release commit has not been frozen/validated on `main`, and final release assets have not been produced and post-run verified.  
**Exact-head evidence rule:** this file cannot self-certify its own containing commit. The controlling engineering evidence is the externally recorded GitHub `validate` run for the exact current PR head. Every release-facing job must explicitly check out `VALIDATION_SHA` and pass `git rev-parse HEAD == VALIDATION_SHA`. PR #29 records the current exact-head SHA/run after each tree change.  
**Historical evidence correction:** earlier pull-request runs that used GitHub's synthetic merge checkout remain integration evidence only; they are not proof of raw PR-head execution.  
**Evidence rule:** a gate is `pass` only when repository state or machine evidence supports it. A planned action is not evidence.

Statuses: `pass` | `partial` | `fail` | `blocked` | `not-applicable`

## Gate A — Repository and version identity

| ID | Status | Evidence / notes |
|---|---|---|
| A1 | partial | PR #29 is the final-hardening change set. Final release identity still requires a frozen merged `main` commit and exact merged-commit validation. |
| A2 | blocked | Final release-validation evidence must bind the eventual exact release commit to same-run six-job `main` validation and post-run GitHub API verification. |
| A3 | blocked | `v1.0.0` must not be tagged while any blocking/failing release gate remains. |
| A4 | pass | Package `0.4.0` is distinguished from schema, Phase II, projection, evidence-format, and repository release-tag versions. |
| A5 | pass | README/CITATION/RELEASE-INTEGRITY distinguish historical `v0.3.2` from unreleased package-line `0.4.0` work. |
| A6 | **fail** | Point-in-time GitHub evidence on 2026-08-26 shows `main` protected but requiring only `conformance`, `phase2`, and `schema-02`; repository Rulesets are empty. The v1.0.0 target additionally requires `package`, `lint-type`, and `security`. Full protection details remain unreadable through the integration (403). |

## Gate B — Core v0.1 semantics

| ID | Status | Evidence / notes |
|---|---|---|
| B1-B9 | pass | Schema/conformance/regression suites preserve the historical v0.1 contract. |
| B10 | pass | Final-hardening changes use additive/versioned wrappers; no silent v0.1 redesign. |
| B11 | pass | Public runtime validation rejects non-finite numeric values before schema/semantic comparisons, preventing `NaN`/infinity from bypassing amount/weight relations. |

## Gate C — Source and policy provenance

| ID | Status | Evidence / notes |
|---|---|---|
| C1-C3 | pass | Exact-byte metadata and policy-pin verification are machine checked. |
| C4 | pass | Capture provenance separates immutable content bytes from artifact-scoped capture events; duplicate artifact IDs fail closed. |
| C5 | pass (scope) | Network capture is SSRF-hardened, not DNS-rebinding-proof. Default urllib automatic redirects are disabled so every redirect destination returns through explicit URL/IP revalidation before the next request; a local-server regression proves the redirected endpoint is not contacted first. |
| C6-C8 | pass | URI/hash/surface checks, source schema packaging, and profile declaration paths are tested. |

## Gate D — Phase II commitment and trust

| ID | Status | Evidence / notes |
|---|---|---|
| D1-D5, D7-D8, D13 | pass | Full Phase II graph/commitment/replay/linkage machinery remains in the required suite. |
| D6 | pass (scope) | C2 exists only for a supported profile under its explicit verifier trust boundary. |
| D9 | pass (fail-closed) | Production RFC 3161 remains fail closed (`TS3178`). |
| D10 | pass (fail-closed) | Production Rekor v2 selector remains reserved/fail-closed (`RKR263`) until native v2 inclusion semantics plus independent signed timestamp evidence exist. |
| D11-D13 | pass | Run attribution, external signer-policy separation, and authority-separation regressions are present. |
| D14 | pass | External trust-policy `date-time` formats are actively checked; policy/signer validity intervals must be positive; signer authorization is bounded by both policy-wide and signer-specific validity windows. |

## Gate E — Replay / reproducibility

| ID | Status | Evidence / notes |
|---|---|---|
| E1-E6 | pass | Replay v2 artifact-recomputation semantics and historical-safe-read tests are in the required Phase II suite. |
| E7 | not-applicable | Actual evaluator implementation re-execution is not advertised by the current replay claim. |

## Gate F — Projection / privacy

| ID | Status | Evidence / notes |
|---|---|---|
| F1 | pass | Projection v1 regression suite remains required. |
| F2-F9 | pass | Projection v2 adversarial and deterministic generative JSON-pointer/path tests remain required in `schema-02`. |
| F10-F11 | pass (scope) | Equality/dictionary leakage remains an explicit non-claim; no Merkle/ZK confidentiality claim is made. |

## Gate G — Empirical corpus

| ID | Status | Evidence / notes |
|---|---|---|
| G1 | pass | Corpus protocol and field-level annotation contract are versioned and checked in. |
| G2 | pass | **9 empirical cases**, inside the predeclared 8–12 target. |
| G3 | pass | Required declared strata are covered; machine `requiredUnresolved` is empty at the current corpus state. |
| G4-G8 | pass | Case validation, exact snapshot/finding binding, metrics, frozen handoffs, study-status computation, distinct second-annotation identity, exact human attestation, complete field-set enforcement, and finite annotation timing are machine checked. |
| G9-G11 | **blocked** | Genuine independent double annotation remains **0/9**; the study-plan minimum is **3 cases**. |
| G12-G13 | **blocked** | Agreement results, reconciliation-dependent conclusions, and the final empirical report cannot be finalized before genuine second annotations are frozen. |

**Human-boundary rule:** software must not fabricate, copy, transform, simulate, or relabel primary annotations as independent annotations. The three frozen source-only handoff packages are inputs for genuine human second annotators. Tool verification can establish handoff consistency and the presence of an explicit human assertion; it cannot prove the human's actual information exposure.

### Empirical construct-validity boundary

The original study objective uses the terms “improve reconstructability” and “without disproportionate administrative burden.” The current retrospective stress-test has no untreated/alternative-workflow/before-after comparator and no predeclared burden comparator or proportionality threshold. Therefore:

- the current study **does not identify a comparative or causal improvement effect**;
- legacy primary `elapsedMinutes` values **do not identify total administrative burden or proportionality**;
- three independently annotated cases, when completed, satisfy the 25% study-completion rule but do **not** establish population-level inter-rater reliability;
- valid current outputs are descriptive reconstructability, source-observability, ontology/model failure modes, bounded annotation-time observations, and descriptive agreement for the selected cases.

These pre-second-annotation interpretation rules are frozen in `corpus/analysis-plan-addendum-2026-08-26.json`, explicitly labeled as a post-start addendum rather than a preregistration rewrite.

## Gate H — Unified assurance bundle / verifier

| ID | Status | Evidence / notes |
|---|---|---|
| H1 | pass | Required `not-run`, `unsupported`, or `not-applicable` checks force overall failure. |
| H2 | pass | Bundle path traversal checks reject symlinked components as well as absolute/parent escapes. |
| H3 | pass | Record digest plus schema/conformance executes through the packaged guarded runtime; clean-wheel smoke is release-critical. |
| H4 | pass | Declared source metadata/bytes digests and exact source-byte verification are composed. |
| H5 | pass | Applicable policy pins are checked against the byte-verified source set. |
| H6 | pass | Phase II graph executes when present; unsupported production profiles fail closed. |
| H7 | pass | Projection v1/v2 deterministic recomputation paths are exercised. |
| H8 | pass (fail-closed) | Funding snapshots are not promoted to funding claims without a registered semantic verifier. |
| H9-H10 | pass | Claim registry, report states, CLI exits, bundle verification, and clean-wheel behavior are required validation surfaces. |

## Gate I — ENS operational adoption

| ID | Status | Evidence / notes |
|---|---|---|
| I1-I5 | pass | ENS-oriented Tier A/B/C, legacy profiles/templates, and adapters are validation surfaces. |
| I6-I7 | not-applicable | An authorized institutional pilot or independent governance program is not a software-release prerequisite for this repository boundary. |
| I8 | pass | Documentation does not claim ENS endorsement or adoption. |

## Gate J — Packaging / security / release

| ID | Status | Evidence / notes |
|---|---|---|
| J1 | pass | Wheel/sdist build on the supported CI platform; PEP 517 backend requirements are exact pins and distribution assembly uses a separate hash-locked build toolchain with `--no-isolation`. |
| J2 | pass | `package` assembles/re-verifies a non-release candidate and installs the assembled wheel into a locked clean venv before substantive CLI smoke. |
| J3 | pass (machinery) | Runtime/validation and build lock coverage/installability are enforced with `--require-hashes` and `pip check`. |
| J4 | pass (machinery) | Development pins, validation lock, and build lock are all in the security audit path; the vulnerable historical `wheel==0.45.1` pin was replaced with audited `wheel==0.46.2`. |
| J5 | pass | Adversarial/generative projection, capture, bundle, corpus, release-integrity, trust-window, and non-finite-number regressions are included in required CI surfaces. |
| J6 | **fail** | Active `main` protection currently requires only three of the six release-critical contexts; remaining protection controls are partially unverified because the full endpoint returns 403. |
| J7 | blocked | Annotated `v1.0.0` tag must be created only after empirical/release gates, exact merged-`main` validation, and post-run candidate verification. |
| J8 | pass (machinery) / blocked (final asset) | CycloneDX SBOM generation is implemented/exercised; final SBOM must be generated from the frozen release commit. |
| J9 | pass (machinery) / blocked (final asset) | Acyclic `SHA256SUMS` generation/verification is implemented/tested; final checksum manifest must come from the frozen release commit. |
| J10 | pass (machinery) / blocked (final asset) | `release-manifest.json` records commit/package/toolchain identity and exact required payload hashes/sizes; verifier rejects missing, unexpected, unsafe, symlinked, nested, or inconsistent assets. |
| J11 | pass (machinery) / blocked (final evidence) | Manual `main`-only `release-assets` requires same-run six-job success and `studyStatus.readyForFinalReview=true`; `verify-github` independently authenticates the cited Actions run/job state. |
| J12 | pass (machinery) / blocked (final evidence) | The sole candidate artifact name binds SHA-256 of the local release manifest to the exact Actions run. |
| J13 | pass | No byte-reproducible-build, signed-commit, or GitHub-signed-artifact claim is made without corresponding evidence. |

### Release-asset integrity and provenance graph

`scripts/release_artifacts.py` builds an exact-commit source archive, wheel, sdist, validation report, SBOM, build lock, and validation lock; writes a release manifest over those seven payloads; then writes `SHA256SUMS` **last** over all seven plus the release manifest. The checksum manifest excludes itself, avoiding a circular self-hash. Offline verification rejects missing/unexpected payloads, path escapes, symlinks, nested/non-regular entries, duplicate checksum entries, hash/size mismatches, invalid manifest/toolchain identity, control-file self-reference, and cross-file commit disagreement.

For `releaseEligible=true`, the embedded report must declare the expected repository/workflow/event/run/ref identity, exactly six successful prerequisite jobs, and `studyStatus.readyForFinalReview=true`. This report is still self-declared bytes; offline verification does not authenticate GitHub Actions state.

Post-run `verify-github` requires a completed/successful `workflow_dispatch` run on the exact `main` commit; exactly the six prerequisite jobs plus successful `release-assets`; successful exact-SHA and main-binding steps; and exactly one non-expired artifact named `release-candidate-<tag>-<commit>-<manifest-sha256>`, where the manifest digest is recomputed from the downloaded candidate. This is an API-state/SHA-256 trust claim, not a signed-attestation claim.

## Gate K — Funding provenance

| ID | Status | Evidence / notes |
|---|---|---|
| K1 | pass | Existing dated provenance snapshot is preserved. |
| K2 | not-applicable to release | A future funding event is captured only after an authoritative artifact exists; it is not a prerequisite for software correctness. |
| K3-K5 | pass | Allocation, payment authorization, transfer, receipt, and settlement remain distinct propositions. |
| K6 | pass | Release process must not infer a later financial state from current evidence. |

## Gate L — Documentation and assurance case

| Doc / topic | Status | Notes |
|---|---|---|
| README / Charter / CONFORMANCE | pass | Present; v0.1 semantics remain frozen and claims remain bounded. |
| Claim registry / ASSURANCE-CASE | pass | Machine claims and unresolved-required-check semantics are explicit. |
| Source provenance | pass | Exact-byte, capture-event, redirect revalidation, SSRF-hardening, and DNS-rebinding non-claims are documented. |
| Phase II trust | pass | Unsupported production profiles fail closed; external trust-policy temporal validity is enforced. |
| RELEASE-INTEGRITY / packaging-security | pass (procedure) | Exact-head CI, separate build/validation locks, offline candidate integrity, online GitHub evidence verification, and manifest-digest Actions artifact binding are documented. |
| Branch protection | **fail / partial evidence** | Live summary proves only three required contexts and no repository Rulesets; full classic-protection details remain inaccessible. |
| Citation metadata | pass | Package `0.4.0` is explicitly an unreleased checkpoint, separate from a future repository release tag. |
| Second-annotation protocol | pass | Five-class vocabulary, distinct identity, explicit human attestation, frozen-package compatibility, finite timing, and reliability non-claims are documented/tested. |
| Empirical analysis plan | pass (scope) | Pre-second-annotation interpretation rules bind the study to descriptive claims and record non-identification of improvement/burden effects. |
| Final study report | blocked | Genuine second annotation is incomplete; metrics/report must be regenerated from the exact final empirical commit. |

## Current release blockers

1. Complete and freeze the three genuine independent second annotations before reconciliation; then regenerate agreement metrics, study status, and the final empirical report. Software must not manufacture this evidence.
2. Strengthen `main` protection so GitHub requires `package`, `lint-type`, and `security` in addition to the currently observed `conformance`, `phase2`, and `schema-02`; use authorized settings access to verify PR, up-to-date, force-push, deletion, review, and bypass controls that remain hidden from this integration.
3. After empirical completion and any resulting reviewed changes are frozen, the exact current PR head must pass all six explicit-SHA release jobs; PR #29 must be made ready/reviewed and merged; the exact resulting `main` commit must pass all six jobs again.
4. On that exact eligible `main` commit, manually dispatch `validate`. `release-assets` must see same-run six-job success plus `studyStatus.readyForFinalReview=true` and produce the manifest-digest-bound candidate.
5. After workflow completion, download the candidate; run both offline `verify` and online `verify-github`; inspect the results; only then create the annotated repository tag and attach the verified individual assets. Re-verify published hashes after upload.

No adoption pilot and no future funding event are hidden prerequisites for this software-release boundary.
