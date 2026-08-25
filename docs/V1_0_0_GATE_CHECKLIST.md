# v1.0.0 acceptance gate checklist (Gates A-L)

**Evaluated:** 2026-08-26 against final-hardening PR #29.  
**Tag decision:** **DO NOT TAG `v1.0.0` yet.** Machine-release gates are being revalidated on the exact PR head; the preregistered independent second-annotation research gate remains incomplete.  
**Evidence rule:** a gate is `pass` only when the repository or exact-head CI evidence supports it. A planned action is not evidence.

Statuses: `pass` | `pending-ci` | `partial` | `fail` | `blocked` | `not-applicable`

## Gate A — Repository and version identity

| ID | Status | Evidence / notes |
|---|---|---|
| A1 | pending-ci | PR #29 is the release-hardening line; freeze only after its final head is fully green and merged |
| A2 | blocked | Final release-validation report must be bound to the eventual exact release commit |
| A3 | blocked | `v1.0.0` must not be tagged while any blocking gate remains |
| A4 | pass | Package 0.4.0 is distinguished from schema, Phase II, projection, and release-tag versions |
| A5 | pass | README and RELEASE-INTEGRITY distinguish historical `v0.3.2` from unreleased 0.4.0 work |
| A6 | partial | `main` is protected; current required contexts are the three historical semantic checks. Release procedure additionally requires all six CI jobs green on the exact candidate. |

## Gate B — Core v0.1 semantics

| ID | Status | Evidence / notes |
|---|---|---|
| B1-B9 | pending-ci | Historical suites are retained unchanged and rerun in `conformance` |
| B10 | pass | Final-hardening changes use additive/versioned wrappers; no silent v0.1 redesign |

## Gate C — Source and policy provenance

| ID | Status | Evidence / notes |
|---|---|---|
| C1-C3 | pending-ci | Exact-byte metadata and policy-pin verification retained and exercised |
| C4 | pending-ci | Capture provenance now separates immutable content bytes from artifact-scoped metadata/log events; duplicate artifact IDs fail closed |
| C5 | pass (scope) | Network path is explicitly **SSRF-hardened**, not advertised as DNS-rebinding-proof or universally SSRF-safe |
| C6-C8 | pending-ci | URI/hash/surface checks, source schema packaging, profile declaration tests rerun in CI |

## Gate D — Phase II commitment and trust

| ID | Status | Evidence / notes |
|---|---|---|
| D1-D5, D7-D8, D13 | pending-ci | Full Phase II suite reruns on PR #29 |
| D6 | pass (scope) | C2 exists only for a supported profile under its explicit verifier trust boundary |
| D9 | pass (fail-closed) | Production RFC 3161 remains fail closed (`TS3178`) |
| D10 | pass (fail-closed) | Production Rekor v2 selector is reserved/fail-closed (`RKR263`) until native v2 inclusion semantics plus independent signed timestamp evidence exist |
| D11-D13 | pending-ci | Run attribution, external signer-policy separation, and authority-separation regressions rerun |

## Gate E — Replay / reproducibility

| ID | Status | Evidence / notes |
|---|---|---|
| E1-E6 | pending-ci | Replay v2 exact artifact-recomputation semantics and historical-safe-read tests rerun |
| E7 | not-applicable | Actual implementation re-execution is not advertised |

## Gate F — Projection / privacy

| ID | Status | Evidence / notes |
|---|---|---|
| F1 | pending-ci | Projection v1 regression suite retained |
| F2-F9 | pending-ci | Projection v2 adversarial suite plus deterministic generative JSON-pointer/path tests run in `schema-02` |
| F10-F11 | pass (scope) | Equality/dictionary leakage remains an explicit non-claim; no Merkle/ZK claim |

## Gate G — Empirical corpus

| ID | Status | Evidence / notes |
|---|---|---|
| G1 | pass | Corpus protocol and field-level annotation contract are versioned and checked in |
| G2 | pass | **9 empirical cases**, inside the preregistered 8–12 target |
| G3 | pass | Required declared strata are covered; `requiredUnresolved` is empty |
| G4-G8 | pending-ci | Case validation, exact snapshot binding, findings, metrics, and study-status computation rerun |
| G9-G11 | **blocked** | Independent double annotation is **0/9**; current preregistered minimum is **3 cases** |
| G12-G13 | **blocked** | Agreement/kappa and final research report cannot be finalized before genuine second annotations are frozen |

**Human-boundary rule:** software must not fabricate, copy, transform, or relabel primary annotations as independent annotations. The three frozen handoff packages under `corpus/second-annotation-handoffs/` are the inputs for genuine second annotators.

## Gate H — Unified assurance bundle / verifier

| ID | Status | Evidence / notes |
|---|---|---|
| H1 | pending-ci | Required `not-run`, `unsupported`, or `not-applicable` checks now force overall failure |
| H2 | pending-ci | Bundle path traversal checks reject symlinked components as well as absolute/parent escapes |
| H3 | pending-ci | Record digest plus full schema/conformance run through the packaged runtime |
| H4 | pending-ci | Declared source metadata/bytes digests and exact source-byte verification are composed |
| H5 | pending-ci | Applicable policy pins are checked against the byte-verified source set |
| H6 | pending-ci | Phase II graph is executed when present; unsupported production profiles fail closed |
| H7 | pending-ci | Projection v1/v2 is deterministically recomputed when required inputs exist |
| H8 | pass (fail-closed) | Funding snapshots are not promoted to funding claims without a registered semantic verifier; required funding evidence therefore fails closed |
| H9-H10 | pending-ci | Claim registry, report states, CLI exits, and clean-wheel behavior rerun |

## Gate I — ENS operational adoption

| ID | Status | Evidence / notes |
|---|---|---|
| I1-I5 | pending-ci | ENS-oriented Tier A/B/C + legacy profiles/templates/adapters rerun |
| I6-I7 | not-applicable | An authorized institutional pilot or independent governance program is not a software-release prerequisite for this repository boundary |
| I8 | pass | Documentation does not claim ENS endorsement or adoption |

## Gate J — Packaging / security / release

| ID | Status | Evidence / notes |
|---|---|---|
| J1 | pending-ci | Wheel/sdist build on Python 3.12 |
| J2 | pending-ci | Clean-wheel smoke runs away from source checkout and exercises claims, profiles, record validation, trust policy, bundle verification, projection, and Phase II verification |
| J3 | pending-ci | Complete runtime hash lock is finalized from CI-platform artifacts, then installed with `--require-hashes` |
| J4 | pending-ci | Development and runtime dependency audits must be green on exact candidate |
| J5 | pending-ci | Adversarial + deterministic generative projection/capture/bundle tests are in the CI matrix |
| J6 | partial | Three historical semantic contexts are branch-protected. Release procedure independently requires all six CI jobs green before merge/tag. |
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
| RELEASE-INTEGRITY / SECURITY | partial | Final exact-commit evidence and assets remain to be generated |
| Citation metadata | pass | 0.4.0 is explicitly an unreleased checkpoint; no fictitious release date |
| Final study report | blocked | Genuine second annotation incomplete |

## Current release blockers

1. Exact PR #29 head must pass all six CI jobs after runtime-lock finalization and documentation freeze.
2. The final merged `main` release commit must pass all six jobs again before tag creation.
3. Three genuine independent second annotations must be completed and frozen before reconciliation; agreement metrics and the final empirical report must then be regenerated.
4. Final release assets, SBOM, checksum manifest, release manifest, and exact-commit validation report must be generated from the frozen release commit and verified before publication.

No adoption pilot and no future funding event are treated as hidden prerequisites for this software-release boundary.
