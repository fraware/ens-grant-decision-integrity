# v1.0.0 acceptance gate checklist (Gates A-L)

**Evaluated:** 2026-08-25 (local + repository tree on main after PR #19-#24 lineage)
**Tag decision:** **DO NOT TAG `v1.0.0`** — multiple blocking gates remain open.
**Scope note:** Status is evidence-bounded. Items marked `pass (local)` passed commands on this workstation; CI on Ubuntu/Python 3.12 remains authoritative for release.

Statuses: `pass` | `pass (local)` | `partial` | `fail` | `blocked` | `not-run`

## Gate A — Repository and version identity

| ID | Status | Evidence / notes |
|---|---|---|
| A1 | blocked | No release-candidate freeze of a single protected main SHA for v1.0.0 |
| A2 | blocked | No release-validation report bound to an exact candidate SHA |
| A3 | blocked | **v1.0.0 must not be tagged** until all blocking gates pass |
| A4 | partial | Software 0.4.0, schema 0.1/0.2, Phase II versions documented; full release manifest absent |
| A5 | pass | README distinguishes v0.3.2 from unreleased work |
| A6 | not-run | Branch-protection admin-bypass not independently audited (`docs/BRANCH-PROTECTION.md`) |

## Gate B — Core v0.1 semantics

| ID | Status | Evidence / notes |
|---|---|---|
| B1-B9 | pass (local) | validate.py, Marketplace conformance (CHAL003 warning only), test_conformance, test_regressions |
| B10 | partial | Relies on review discipline; no automated proof in this checklist |

## Gate C — Source and policy provenance

| ID | Status | Evidence / notes |
|---|---|---|
| C1-C3, C6-C7 | pass (local) | test_source_artifact, test_policy_pins |
| C4-C5 | blocked | Advertised SSRF-safe capture path not fully evidenced as release-complete |
| C8 | pass (local) | Profiles declare policySourceCapture (test_profiles) |

## Gate D — Phase II commitment and trust

| ID | Status | Evidence / notes |
|---|---|---|
| D1-D5, D7-D8, D13 | pass (local) | phase2/tests — 76 passed, 1 skipped |
| D6 | partial | Production C2 requires accepted trust policy + supported profile |
| D9 | pass (fail-closed) | Production rfc3161 remains fail-closed |
| D10-D12 | partial | Docs/claim registry present; authorized-signer only if advertised with tests |

## Gate E — Replay / reproducibility

| ID | Status | Evidence / notes |
|---|---|---|
| E1-E6 | pass (local) | Phase II replay tests / claim matrix; artifact recomputation only |
| E7 | n/a | Implementation re-execution not advertised |

## Gate F — Projection / privacy

| ID | Status | Evidence / notes |
|---|---|---|
| F1 | pass (local) | Projection v1 tests green |
| F2-F9 | partial | Projection v2 present on main post-PR #24; full adversarial suite still required for release claim |
| F10-F11 | partial | Docs warn on equality leakage; no Merkle/ZK claim |

## Gate G — Empirical corpus

| ID | Status | Evidence / notes |
|---|---|---|
| G1 | pass | PR #19 hard-eligibility disposition merged |
| G2 | fail | study_status: **4/8** minimum empirical cases |
| G3 | partial | Required strata covered for current 4 cases; count gate still open |
| G4-G8 | partial | Case contract tools exist; research dispositions incomplete |
| G9-G11 | blocked | Double-annotation: **0** completed independent seconds |
| G12-G13 | blocked | Final study report incomplete while gates open |

## Gate H — Unified assurance bundle / verifier

| ID | Status | Evidence / notes |
|---|---|---|
| H1-H8 | partial | gdi verify-bundle / claims / trust-policy present; full orchestration incomplete |
| H9-H10 | partial | Report schemas exist; full golden/CLI exit-code matrix not asserted here |

## Gate I — ENS operational adoption

| ID | Status | Evidence / notes |
|---|---|---|
| I1-I5 | pass (local) | Tier A/B/C + legacy profiles, templates, adapter provenance tests |
| I6-I7 | blocked | No authorized pilot / dry-run burden package yet |
| I8 | pass | Adopter docs avoid ENS endorsement claims |

## Gate J — Packaging / security / release

| ID | Status | Evidence / notes |
|---|---|---|
| J1-J2 | partial | python -m build succeeded locally; additive package CI job in this change set |
| J3 | partial | requirements.lock.txt present; regenerate under CI platform for release |
| J4 | pass (local) | pip-audit on direct pins: no known vulnerabilities |
| J5 | partial | Property/fuzz coverage incomplete vs release bar |
| J6 | not-run | Documented in docs/BRANCH-PROTECTION.md; settings not API-enforced here |
| J7-J11 | blocked | No v1.0.0 release assets / notes yet |
| J12 | pass | Explicitly **no** byte-reproducible claim without evidence |

## Gate K — Funding provenance

| ID | Status | Evidence / notes |
|---|---|---|
| K1 | pass | Aug24 snapshot preserved |
| K2 | blocked | Friday post-event capture only after authoritative artifact |
| K3-K5 | pass | Vocabulary / allocation!=payment discipline documented |
| K6 | partial | Pre-Friday checkpoint recorded; post-event baseline pending |

## Gate L — Documentation and assurance case

| Doc / topic | Status | Notes |
|---|---|---|
| README / Charter / CONFORMANCE | pass | Present |
| Claim registry / ASSURANCE-CASE | pass | Present |
| Adopter guide | pass | docs/ADOPTER-GUIDE.md |
| RELEASE-INTEGRITY / SECURITY | pass | Updated release-asset / SBOM / non-repro notes |
| Deferred / non-goals | pass | DEFERRED.md (+ phase2/DEFERRED.md) |
| Final study report | blocked | Study incomplete |

## Release blockers (summary)

1. Empirical corpus below 8-case minimum; double annotation incomplete.
2. No adoption pilot / burden evidence.
3. No exact-head v1.0.0 release validation package (assets, SBOM, SHA-256 manifest, notes).
4. Friday post-event funding provenance still pending authoritative artifact.
5. Branch-protection and full release red-team sign-off not completed.
6. Do **not** tag v1.0.0 until every blocking gate is satisfied or the corresponding capability is removed from advertised scope.
