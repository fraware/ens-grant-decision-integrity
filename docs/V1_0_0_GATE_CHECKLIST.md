# v1.0.0 acceptance gate checklist (Gates A–L)

**Evaluated:** 2026-08-26 after merge of PR #29.  
**Current `main`:** `675ce12b69309b4eee455eb661d316c53c106333`.  
**Merged-main validation:** workflow `validate`, run `32995711485`, `success`.  
**Tag decision:** **DO NOT TAG `v1.0.0` yet.** The engineering hardening is integrated and exact-`main` validation is green, but the genuine independent second-annotation study gate is incomplete, active `main` protection still requires only three of six release-critical checks, and no eligible final release candidate has been produced and post-run verified.  
**Evidence rule:** a gate is `pass` only when repository state or machine evidence supports it. A plan, checklist entry, stale workflow, or documentation statement is not evidence.

Statuses: `pass` | `partial` | `fail` | `blocked` | `not-applicable`.

## Engineering integration baseline

PR #29 was merged and closed at merge commit `675ce12b69309b4eee455eb661d316c53c106333`. Its exact pre-merge head `db1b4a782e7f41a63366a71029d7e99fe253aa5a` passed all six release-critical jobs in run `32995144501`.

The exact merged `main` commit then passed all six jobs again in push run `32995711485`:

- `conformance`: success
- `phase2`: success
- `schema-02`: success
- `package`: success
- `lint-type`: success
- `security`: success

Every release-critical job passed the explicit exact-SHA assertion before substantive validation. `release-assets` was skipped, correctly, because the merged-main run was a normal push run rather than the guarded manual release workflow.

The conformance job executed corpus validation and `scripts/study_status.py`. That machine report is valid but intentionally reports the study as incomplete: 9 counted cases, required declared strata covered, 0 independently double-annotated cases, minimum required at the current corpus size 3, `doubleAnnotationFractionMet=false`, `readyForFinalReview=false`, and `status="in-progress"`.

This merged-main result is the current engineering baseline. It is not the final release commit because genuine human annotation work in Gate G must still change empirical artifacts before `v1.0.0` can be eligible.

## Gate A — Repository and version identity

| ID | Status | Evidence / notes |
|---|---|---|
| A1 | partial | The engineering integration identity is frozen and validated on `main` at `675ce12b...`. The final release identity is not yet frozen because Gate G requires future verified human evidence and regenerated empirical outputs. |
| A2 | blocked | Final release-validation evidence must bind the eventual exact eligible `main` commit to same-run six-job validation, successful `release-assets`, and post-run API verification of the candidate artifact identity. |
| A3 | blocked | `v1.0.0` must not be tagged while Gate G, Gate J branch protection, or final candidate verification remains blocking/failing. |
| A4 | pass | Package `0.4.0` is distinguished from schema, Phase II, projection, evidence-format, and repository release-tag versions. |
| A5 | pass | README/CITATION/release documentation distinguish historical `v0.3.2` from the unreleased package-line `0.4.0` work. |
| A6 | **fail** | Machine-readable GitHub state shows `main` protected but requiring only `conformance`, `phase2`, and `schema-02`; repository Rulesets are empty. The `v1.0.0` target additionally requires `package`, `lint-type`, and `security`. Full protection details remain unreadable through the available integration. |

## Gate B — Core v0.1 semantics

| ID | Status | Evidence / notes |
|---|---|---|
| B1–B9 | pass | Schema, conformance, and regression suites preserve the historical v0.1 contract. |
| B10 | pass | New behavior is additive/versioned or wrapped; no silent v0.1 semantic redesign is promoted. |
| B11 | pass | Public validation rejects non-finite numeric values before schema/semantic comparisons, preventing `NaN`/infinity from bypassing amount or weight relations. |

## Gate C — Source and policy provenance

| ID | Status | Evidence / notes |
|---|---|---|
| C1–C3 | pass | Exact-byte source metadata and policy-pin verification are machine checked. |
| C4 | pass | Capture provenance separates immutable content bytes from artifact-scoped capture events; duplicate artifact IDs fail closed. |
| C5 | pass (scope) | Network capture implements the documented SSRF-hardening and redirect revalidation boundary; it does not claim DNS-rebinding resistance. |
| C6–C8 | pass | URI/hash/surface binding, source-schema packaging, and profile declaration paths are tested. |

## Gate D — Phase II commitment and trust

| ID | Status | Evidence / notes |
|---|---|---|
| D1–D5, D7–D8, D13 | pass | Phase II graph, commitment, replay, linkage, and authority-separation machinery is in required CI. |
| D6 | pass (scope) | C2 exists only for supported profiles under explicit verifier trust assumptions. |
| D9 | pass (fail-closed) | Unsupported production RFC 3161 operation remains fail closed. |
| D10 | pass (fail-closed) | The reserved production Rekor-v2 selector remains fail closed until its stated evidence requirements exist. |
| D11–D13 | pass | Run attribution, external signer-policy separation, and authority separation are regression tested. |
| D14 | pass | Trust-policy datetime formats and positive validity windows are enforced; signer authorization is bounded by both policy-wide and signer-specific intervals. |

## Gate E — Replay / reproducibility

| ID | Status | Evidence / notes |
|---|---|---|
| E1–E6 | pass | Replay-v2 artifact recomputation and historical-safe-read semantics remain in required Phase II validation. |
| E7 | not-applicable | Re-execution of an external evaluator implementation is not advertised by the present replay claim. |

## Gate F — Projection / privacy

| ID | Status | Evidence / notes |
|---|---|---|
| F1 | pass | Projection-v1 compatibility remains regression tested. |
| F2–F9 | pass | Projection-v2 deterministic and adversarial JSON-pointer/path behavior is in the required `schema-02` surface. |
| F10–F11 | pass (scope) | Equality/dictionary leakage is an explicit limitation; no Merkle, zero-knowledge, or stronger confidentiality claim is made. |

## Gate G — Empirical corpus

| ID | Status | Evidence / notes |
|---|---|---|
| G1 | pass | Corpus protocol and field-level annotation contract are versioned and checked in. |
| G2 | pass | 9 empirical cases, inside the predeclared 8–12 target. |
| G3 | pass | Required declared strata are covered; the machine report has no unresolved required stratum. |
| G4–G8 | pass | Case validation, exact snapshot/finding binding, metrics, frozen handoffs, study-status computation, second-annotator identity rules, explicit independence attestation, field-set enforcement, and finite timing are machine checked. |
| G9–G11 | **blocked** | Genuine independent double annotation remains **0/9**; the current study-plan minimum is **3 cases**. |
| G12–G13 | **blocked** | Agreement, reconciliation-dependent interpretation, and the final empirical report cannot be finalized before the three genuine second annotations are frozen and integrated. |

**Human-boundary rule:** software must not fabricate, copy, transform, infer, simulate, or relabel primary annotations as independent observations. The frozen source-only handoff packages are inputs for genuine human second annotators. Tool verification can establish package consistency and the presence of an explicit human assertion; it cannot prove the annotator's actual information exposure.

### Empirical construct-validity boundary

The current retrospective design has no untreated/alternative-workflow/before-after comparator and no predeclared administrative-burden comparator or proportionality threshold. Therefore:

- it does **not** identify a comparative or causal reconstructability-improvement effect;
- legacy primary `elapsedMinutes` values do **not** identify total administrative burden or proportionality;
- three independently annotated cases, once completed, satisfy the study-completion fraction but do **not** establish population-level inter-rater reliability;
- valid current outputs are descriptive reconstructability, source observability, ontology/model failure modes, bounded annotation-time observations, and descriptive agreement for the selected cases.

These interpretation constraints were frozen before second-annotation outcomes in `corpus/analysis-plan-addendum-2026-08-26.json` and are explicitly presented as a post-start addendum rather than a rewritten preregistration.

## Gate H — Unified assurance bundle / verifier

| ID | Status | Evidence / notes |
|---|---|---|
| H1 | pass | Required `not-run`, `unsupported`, or `not-applicable` checks force overall failure. |
| H2 | pass | Bundle path safety rejects absolute paths, parent escapes, and symlink traversal. |
| H3 | pass | Record digest plus schema/conformance executes through the packaged guarded runtime; clean-wheel smoke is release critical. |
| H4 | pass | Source metadata/byte digests and exact source-byte verification are composed. |
| H5 | pass | Applicable policy pins are checked against byte-verified source artifacts. |
| H6 | pass | Phase II executes when present; unsupported production profiles fail closed. |
| H7 | pass | Projection-v1/v2 deterministic recomputation paths are exercised. |
| H8 | pass (fail-closed) | Funding snapshots are not promoted to funding claims without a registered semantic verifier. |
| H9–H10 | pass | Claim registry, report states, CLI exits, bundle verification, and clean-wheel behavior are required validation surfaces. |

## Gate I — Operational adoption

| ID | Status | Evidence / notes |
|---|---|---|
| I1–I5 | pass | Tier A/B/C, legacy profiles/templates, and adapters are validation surfaces. |
| I6–I7 | not-applicable | An authorized institutional pilot or independent governance program is not a software-release prerequisite for this repository boundary. |
| I8 | pass | Documentation does not claim institutional endorsement or adoption. |

## Gate J — Packaging / security / release

| ID | Status | Evidence / notes |
|---|---|---|
| J1 | pass | Wheel/sdist assembly is exercised on the supported CI platform; build-system requirements are exact pins and distribution assembly uses the hash-locked build toolchain with `--no-isolation`. |
| J2 | pass | `package` assembles and verifies a non-release candidate and installs the assembled wheel into a locked clean environment before substantive CLI smoke. |
| J3 | pass | Runtime/validation and build locks are enforced with `--require-hashes` and `pip check`. |
| J4 | pass | Development pins, validation lock, and build lock are in dependency-audit paths. |
| J5 | pass | Adversarial/generative projection, capture, bundle, corpus, release-integrity, trust-window, strict-JSON, and non-finite-number regressions are in required CI. |
| J6 | **fail** | Active `main` protection currently requires only three of the six release-critical contexts; remaining protection controls are partially unverified because the full endpoint is inaccessible. |
| J7 | blocked | The final `v1.0.0` tag is prohibited until empirical and release-control gates pass and the eligible final candidate is verified. |
| J8–J10 | pass (machinery) / blocked (final asset) | SBOM, acyclic checksum manifest, release manifest, exact payload-set enforcement, and artifact integrity checks are implemented and exercised; final assets must come from the eventual eligible release commit. |
| J11–J12 | pass (machinery) / blocked (final evidence) | Manual `main`-only `release-assets` requires same-run six-job success and `studyStatus.readyForFinalReview=true`; post-run verification binds the downloaded candidate manifest digest to the authoritative workflow/artifact identity. |
| J13 | pass | No byte-reproducible-build, signed-commit, or platform-signed-artifact claim is made without corresponding evidence. |

### Release provenance graph

`scripts/release_artifacts.py` builds the exact-commit source archive, wheel, sdist, validation report, SBOM, build lock, and validation lock; writes a release manifest over the payload set; then writes `SHA256SUMS` last. Offline verification rejects missing/unexpected payloads, unsafe paths, symlinks, nested/non-regular entries, duplicate checksum entries, digest/size mismatch, invalid manifest/toolchain identity, control-file self-reference, and cross-file commit disagreement.

For `releaseEligible=true`, the embedded report must name the expected repository/workflow/event/run/ref identity, exactly six successful prerequisite jobs, and `studyStatus.readyForFinalReview=true`. Offline byte verification alone does not authenticate the workflow service. Post-run verification therefore separately requires the completed successful manual run on the exact `main` commit, the required jobs plus successful `release-assets`, successful SHA/main binding steps, and exactly one non-expired candidate artifact whose name binds the recomputed local release-manifest digest.

## Gate K — Funding provenance

| ID | Status | Evidence / notes |
|---|---|---|
| K1 | pass | Existing dated provenance snapshots are preserved. |
| K2 | not-applicable to release | A future funding event is captured only after authoritative evidence exists; it is not a prerequisite for software correctness. |
| K3–K5 | pass | Allocation, payment authorization, transfer, receipt, and settlement remain distinct propositions. |
| K6 | pass | Release logic must not infer a later financial state from present evidence. |

As of 2026-08-26, future-dated August 28 material in `provenance/` consists of a capture checklist/status planning record and a `.template.json`; there is no non-template August 28 status artifact claiming a future observation has already occurred.

## Gate L — Documentation and assurance case

| Doc / topic | Status | Notes |
|---|---|---|
| README / Charter / CONFORMANCE | pass | Present; v0.1 semantics remain frozen and claims remain bounded. |
| Claim registry / assurance case | pass | Machine claims and unresolved-required-check semantics are explicit. |
| Source provenance | pass | Exact-byte, capture-event, redirect-revalidation, SSRF-hardening, and DNS-rebinding non-claims are documented. |
| Phase II trust | pass | Unsupported production profiles fail closed; external trust-policy temporal validity is enforced. |
| Release integrity / packaging-security | pass (procedure) | Exact-SHA CI, separate locks, offline candidate integrity, online workflow-state verification, and manifest-digest artifact binding are documented. |
| Branch protection | **fail / partial evidence** | Live summary proves only three required contexts and no repository Rulesets; full classic-protection details remain inaccessible. |
| Citation metadata | pass | Package `0.4.0` is explicitly distinct from the eventual repository release tag. |
| Second-annotation protocol | pass | Five-class vocabulary, distinct identity, explicit human attestation, frozen-package compatibility, finite timing, and reliability non-claims are documented/tested. |
| Empirical analysis plan | pass (scope) | The study is bound to descriptive claims and explicitly records non-identification of improvement/burden effects. |
| Final study report | blocked | Genuine second annotation is incomplete; the report must be regenerated from the exact final empirical commit. |

## Current release blockers

1. **Human empirical evidence:** complete and freeze the three genuine independent second annotations selected prospectively; verify each return; integrate without rewriting primaries; compute pre-reconciliation agreement honestly; then regenerate corpus validation, study status, metrics, and the final empirical report.
2. **Branch protection:** require `package`, `lint-type`, and `security` in addition to the currently required `conformance`, `phase2`, and `schema-02`; independently verify the effective PR/up-to-date/review/force-push/deletion/bypass controls or explicitly document and deliberately accept any release deviation.
3. **Final empirical commit:** after verified human evidence and any reconciliation/report changes are reviewed and merged, run all six exact-SHA jobs on the resulting exact `main` commit. The current green engineering baseline cannot substitute for validation of that future changed commit.
4. **Final candidate:** manually dispatch `validate` on that exact eligible `main` commit. `release-assets` must see same-run six-job success plus `studyStatus.readyForFinalReview=true` and produce the manifest-digest-bound candidate.
5. **Publication verification:** download the candidate; run offline verification and post-run workflow/artifact verification; inspect the evidence; only then create the annotated repository tag and publish the verified asset set. Re-verify published hashes after upload.

## Completed integration actions on 2026-08-26

- PR #29 exact head passed all six release-critical jobs.
- PR #29 was merged and closed into `main` with an expected-head SHA lock.
- The hardening branch was automatically removed after merge.
- The exact merged `main` commit `675ce12b69309b4eee455eb661d316c53c106333` passed all six release-critical jobs in run `32995711485`.
- There are no open pull requests.
- No `v1.0.0` release has been published; the published release line remains at `v0.3.2`.

No adoption pilot and no future funding event are hidden prerequisites for this software-release boundary. No merge, green workflow, or documentation update overrides the remaining human evidence and release-control gates.
