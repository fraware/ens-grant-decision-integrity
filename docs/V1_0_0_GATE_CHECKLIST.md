# v1.0.0 acceptance gate checklist (Gates A-L)

**Evaluated:** 2026-08-26 against final-hardening PR #29 exact head `8c566a5f7827db92d815946e6e017ecb4f218750`.  
**Exact-head CI evidence:** workflow `validate`, run `32952179767`, completed successfully with all six jobs green: `conformance`, `phase2`, `schema-02`, `package`, `lint-type`, and `security`.  
**Tag decision:** **DO NOT TAG `v1.0.0` yet.** The PR head is machine-green, but the preregistered independent second-annotation research gate remains incomplete, the branch is not yet merged to the final release commit, and release assets have not been generated from a frozen release commit.  
**Evidence rule:** a gate is `pass` only when repository state or exact-head CI evidence supports it. A planned action is not evidence.

Statuses: `pass` | `partial` | `fail` | `blocked` | `not-applicable`

## Gate A — Repository and version identity

| ID | Status | Evidence / notes |
|---|---|---|
| A1 | partial | PR #29 exact head `8c566a5f…` is fully green in run `32952179767`; final release identity still requires merge and exact merged-commit validation |
| A2 | blocked | Final release-validation report must be bound to the eventual exact release commit |
| A3 | blocked | `v1.0.0` must not be tagged while any blocking gate remains |
| A4 | pass | Package 0.4.0 is distinguished from schema, Phase II, projection, and release-tag versions |
| A5 | pass | README and RELEASE-INTEGRITY distinguish historical `v0.3.2` from unreleased 0.4.0 work |
| A6 | partial | `main` is protected; currently enforced required contexts are `conformance`, `phase2`, and `schema-02`. Release procedure additionally requires all six jobs green on the exact candidate. |

## Gate B — Core v0.1 semantics

| ID | Status | Evidence / notes |
|---|---|---|
| B1-B9 | pass | Historical schema/conformance/regression suites passed in exact-head `conformance` job |
| B10 | pass | Final-hardening changes use additive/versioned wrappers; no silent v0.1 redesign |

## Gate C — Source and policy provenance

| ID | Status | Evidence / notes |
|---|---|---|
| C1-C3 | pass | Exact-byte metadata and policy-pin verification passed on exact PR head |
| C4 | pass | Capture provenance separation and duplicate-artifact fail-closed tests passed on exact PR head |
| C5 | pass (scope) | Network path is explicitly **SSRF-hardened**, not advertised as DNS-rebinding-proof or universally SSRF-safe |
| C6-C8 | pass | URI/hash/surface checks, source schema packaging, and profile declaration tests passed on exact PR head |

## Gate D — Phase II commitment and trust

| ID | Status | Evidence / notes |
|---|---|---|
| D1-D5, D7-D8, D13 | pass | Full Phase II suite passed on exact PR head |
| D6 | pass (scope) | C2 exists only for a supported profile under its explicit verifier trust boundary |
| D9 | pass (fail-closed) | Production RFC 3161 remains fail closed (`TS3178`) |
| D10 | pass (fail-closed) | Production Rekor v2 selector is reserved/fail-closed (`RKR263`) until native v2 inclusion semantics plus independent signed timestamp evidence exist |
| D11-D13 | pass | Run attribution, external signer-policy separation, and authority-separation regressions passed on exact PR head |

## Gate E — Replay / reproducibility

| ID | Status | Evidence / notes |
|---|---|---|
| E1-E6 | pass | Replay v2 artifact-recomputation semantics and historical-safe-read tests passed on exact PR head |
| E7 | not-applicable | Actual implementation re-execution is not advertised |

## Gate F — Projection / privacy

| ID | Status | Evidence / notes |
|---|---|---|
| F1 | pass | Projection v1 regression suite passed on exact PR head |
| F2-F9 | pass | Projection v2 adversarial and deterministic generative JSON-pointer/path tests passed in `schema-02` on exact PR head |
| F10-F11 | pass (scope) | Equality/dictionary leakage remains an explicit non-claim; no Merkle/ZK claim |

## Gate G — Empirical corpus

| ID | Status | Evidence / notes |
|---|---|---|
| G1 | pass | Corpus protocol and field-level annotation contract are versioned and checked in |
| G2 | pass | **9 empirical cases**, inside the preregistered 8–12 target |
| G3 | pass | Required declared strata are covered; `requiredUnresolved` is empty |
| G4-G8 | pass | Case validation, exact snapshot binding, finding binding, metrics, handoff tooling, and study-status computation passed on exact PR head |
| G9-G11 | **blocked** | Independent double annotation remains **0/9**; current preregistered minimum is **3 cases** |
| G12-G13 | **blocked** | Agreement/kappa and final research report cannot be finalized before genuine second annotations are frozen |

**Human-boundary rule:** software must not fabricate, copy, transform, or relabel primary annotations as independent annotations. The three frozen handoff packages under `corpus/second-annotation-handoffs/` are the inputs for genuine second annotators.

## Gate H — Unified assurance bundle / verifier

| ID | Status | Evidence / notes |
|---|---|---|
| H1 | pass | Required `not-run`, `unsupported`, or `not-applicable` checks force overall failure; regressions passed on exact PR head |
| H2 | pass | Bundle path traversal checks reject symlinked components as well as absolute/parent escapes; tests passed on exact PR head |
| H3 | pass | Record digest plus full schema/conformance runs through the packaged runtime; clean-wheel smoke passed |
| H4 | pass | Declared source metadata/bytes digests and exact source-byte verification are composed and tested |
| H5 | pass | Applicable policy pins are checked against the byte-verified source set and tested |
| H6 | pass | Phase II graph executes when present; unsupported production profiles fail closed and tests pass |
| H7 | pass | Projection v1/v2 deterministic recomputation paths are exercised and pass |
| H8 | pass (fail-closed) | Funding snapshots are not promoted to funding claims without a registered semantic verifier; required funding evidence therefore fails closed |
| H9-H10 | pass | Claim registry, report states, CLI exits, bundle verification, and clean-wheel behavior passed on exact PR head |

## Gate I — ENS operational adoption

| ID | Status | Evidence / notes |
|---|---|---|
| I1-I5 | pass | ENS-oriented Tier A/B/C, legacy profiles/templates, and adapters passed on exact PR head |
| I6-I7 | not-applicable | An authorized institutional pilot or independent governance program is not a software-release prerequisite for this repository boundary |
| I8 | pass | Documentation does not claim ENS endorsement or adoption |

## Gate J — Packaging / security / release

| ID | Status | Evidence / notes |
|---|---|---|
| J1 | pass | Wheel and sdist built successfully on CPython 3.12 on exact PR head |
| J2 | pass | Clean-wheel smoke ran away from the source checkout and exercised claims, profiles, record validation, trust policy, bundle verification, projection, and Phase II verification |
| J3 | pass | Runtime lock covers project runtime dependencies and clean `--require-hashes` installation plus `pip check` passed on exact PR head |
| J4 | pass | Development dependency audit and audit of the clean locked environment passed on exact PR head |
| J5 | pass | Adversarial and deterministic generative projection/capture/bundle tests are in the CI matrix and passed |
| J6 | partial | Three historical semantic contexts are branch-protected. `package`, `lint-type`, and `security` are verified release gates but are not currently enforced branch-protection contexts. |
| J7-J11 | blocked | Final tag/assets/SBOM/checksum manifest/release manifest/validation report can be generated only after the exact release commit is frozen |
| J12 | pass | No byte-reproducible-build claim without independent evidence |

## Gate K — Funding provenance

| ID | Status | Evidence / notes |
|---|---|---|
| K1 | pass | Existing dated provenance snapshot is preserved |
| K2 | not-applicable to release | A future funding event is captured only after an authoritative artifact exists; it is not a prerequisite for software correctness |
| K3-K5 | pass | Allocation, payment authorization, transfer, receipt, and settlement remain distinct propositions |
| K6 | pass | Release process must not infer a later financial state from current evidence |

## Gate L — Documentation and assurance case

| Doc / topic | Status | Notes |
|---|---|---|
| README / Charter / CONFORMANCE | pass | Present; v0.1 semantics remain frozen |
| Claim registry / ASSURANCE-CASE | pass | Machine claims and unresolved-required-check semantics are bounded |
| Source provenance | pass | Exact-byte, capture-event, SSRF-hardening, and DNS-rebinding non-claims documented |
| Phase II deferred profiles | pass | Production RFC 3161 and Rekor v2 timing remain explicit fail-closed boundaries |
| RELEASE-INTEGRITY / SECURITY | partial | Exact PR-head engineering evidence exists; final merged-commit validation and release assets remain to be generated |
| Citation metadata | pass | 0.4.0 is explicitly an unreleased checkpoint; no fictitious release date |
| Second-annotation protocol | pass | Frozen handoffs expose all five classifications; checklist and verifier agree; timing and reliability non-claims are explicit |
| Final study report | blocked | Genuine second annotation incomplete |

## Current release blockers

1. Three genuine independent second annotations must be completed and frozen before reconciliation; agreement metrics and the final empirical report must then be regenerated. Software must not manufacture this evidence.
2. After all pre-merge changes are frozen, PR #29 must be merged and the exact resulting `main` release commit must pass all six release jobs again before tag creation.
3. Final release assets, SBOM, checksum manifest, release manifest, and exact-commit validation report must be generated from that frozen release commit and verified before publication.
4. Branch protection currently enforces only the three historical semantic contexts. This is an explicit enforcement limitation; it must not be described as six-check branch protection unless repository settings are actually changed.

No adoption pilot and no future funding event are treated as hidden prerequisites for this software-release boundary.
