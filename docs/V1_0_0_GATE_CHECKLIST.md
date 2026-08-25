# v1.0.0 Gate Checklist (Gates A–L)

**Document role:** engineering gate tracker for a *future* `v1.0.0` assurance boundary.  
**This file is not a `v1.0.0` release claim**, not a tag, and not ENS endorsement. Current package: `ens-gdi` / `gdi` **0.4.0**.

**Date:** 2026-08-25 (local engineering refresh)  
**Repository SHA evaluated:** `8728f9848673b19e349870b7e89fff1d97d8eef0` (`main` = `origin/main`)  
**Package version:** `ens-gdi` / `gdi` **0.4.0** (not a v1.0.0 candidate)  
**Tag decision:** **DO NOT TAG v1.0.0** — blocking items remain (corpus double-annotation, Friday provenance, pilot/adoption evidence, release assets).

Gate letters follow the Final Acceptance Test Matrix (Gates A–L), not informal earlier labels.

## Local suite evidence (this refresh)

| Suite | Result |
| --- | --- |
| `pytest scripts/test_conformance.py scripts/test_schema_02.py scripts/test_regressions.py scripts/test_policy_pins.py scripts/test_source_artifact.py` | **24 passed** |
| `pytest phase2/tests projection/tests` | **104 passed, 1 skipped** (`test_t7_inclusion_proof`: no recorded-from-live Rekor fixture) |
| `pytest scripts/test_corpus.py scripts/test_corpus_adversarial_ws01.py scripts/test_corpus_validator_binding.py scripts/test_study_status.py scripts/test_second_annotation.py` | **59 passed** |
| `pytest scripts/test_gdi_bundle.py scripts/test_claims_registry.py scripts/test_profiles.py scripts/test_adapters.py` | **22 passed** |
| `gdi verify-bundle examples/verification-bundle --json` | **ok=true** (warnings include expected CHAL003; trust.policy / C4A `not-run` without `--trust-policy`) |
| `python scripts/study_status.py` | **ok=true**, `readyForFinalReview=false`, blocker: double-annotation 0/9 |

Total automated checks run above: **209 passed, 1 skipped**. No `v1.0.0` tag created.

---

## Gate matrix

| Gate | Status | Evidence / notes |
| --- | --- | --- |
| **A** Repository and version identity | **blocked** for v1.0.0 | Exact SHA known; package still `0.4.0`; no annotated `v1.0.0` tag (A3). Do not conflate with `v0.3.2`. |
| **B** Core v0.1 semantics | **pass** (local) | Conformance / schema / regression suites green (24 tests in core group). |
| **C** Source and policy provenance | **pass / partial** | Source-artifact + policy-pin tests green; `gdi.source.capture` module present. Full `gdi source capture` CLI surface not advertised in root `gdi --help` — treat capture operationalization as partial unless release notes narrow the claim. |
| **D** Phase II commitment and trust | **pass / partial** | Phase II + projection suite 104 pass; production RFC3161 remains fail-closed by design (acceptable if Rekor v2 is the advertised C2). T7 live Rekor inclusion **skipped** (no live fixture). Rekor v2 module present (`phase2/src/anchors/rekor_v2.py`). |
| **E** Replay / reproducibility | **pass** (local) | Covered by phase2 replay tests in the 104-pass run; C5 remains artifact recomputation, not re-execution. |
| **F** Projection / privacy | **pass** (local) | Projection tests in suite; v2 schema present. Low-entropy leakage must remain documented (red-team). |
| **G** Empirical corpus | **blocked** | Case count 9/8–12 **met**; required strata declared coverage **met**; PR #19 disposition merged. **G9–G11 blocked:** genuine independent second annotations not returned. Final report is draft (`corpus/FINAL-STUDY-REPORT.md`). `ready-for-final-review=false`. |
| **H** Unified assurance bundle / verifier | **pass / partial** | `gdi verify-bundle` smoke ok; bundle/claims tests 22 pass. Some profile checks correctly `not-run`/`not-applicable` without trust policy — must not be marketed as full production trust verification. |
| **I** ENS operational adoption | **blocked** | Tier A/B/C profiles + templates present; adapter tests pass. **I6–I7 blocked:** no authorized pilot / operator dry-run evidence with predeclared burden metrics. |
| **J** Packaging / security / release | **partial / blocked** for v1 | Lockfile + packaging docs present; wheel/sdist/SBOM/release-asset matrix for a `v1.0.0` publish **not** evidenced here. Branch-protection docs exist; live GitHub protection settings not re-audited in this refresh. |
| **K** Funding provenance | **blocked** | Aug 24 snapshot preserved. Pre-Friday checkpoint historical at `757d35e…`. Current main noted in `FRIDAY-CAPTURE-STATUS.md`. **No** `simocracy-status-2026-08-28.json` invented; template + checklist only. |
| **L** Documentation and assurance case | **partial** | Claim registry, `ASSURANCE-CASE.md`, `DEFERRED.md`, adopter/profile docs exist. Final study report **not** final-review ready. Version/status constants still reflect pre-v1. |

---

## Red-team review (Workstream 09 §15) — findings only

Written adversarial review against current tree. **No fake passes.** Material issues are either mitigated by existing fail-closed behavior, documented limitations, or remain release blockers.

| Prompt | Finding |
| --- | --- |
| Can untrusted bundle material choose a trust root or authorized signer? | **Mitigated / watch:** bundles without `--trust-policy` leave trust checks `not-run`; docs/nonClaims state bundles cannot appoint trust roots. Do not advertise C4A/production trust without external policy input. |
| Can any automated object imply grant authority? | **Mitigated in claims:** Phase II / signatures are technical; adapters must not score merit. Residual risk is documentation overclaim — keep non-claims in release notes. |
| Can a source disappear from public projection without a disposition? | **Mitigated if v2 rules enforced:** projection v2 requires explicit dispositions; keep fail-closed on incomplete rules. |
| Can a low-entropy hidden field be guessed from its public commitment, and is that documented? | **Residual risk / document:** deterministic path-bound commitments leak equality for low-entropy values; must remain explicit in privacy docs before any v1 claim. |
| Can an invalid initial corpus record be sanitized out of history? | **Mitigated by corpus contract:** initial bytes/findings bound (CORP020/CORP026-style tests green). Hard-eligibility case keeps reconciled record separate. |
| Can an annotation be called independent when it reused primary material? | **Open process risk / blocked:** tooling checks attestation + field-set; cannot prove human independence. Handoffs prepared; **do not** set `independent=true` falsely. |
| Can a fixture establish a production claim? | **Mitigated / watch:** fixture Rekor profiles must stay non-production; T7 live path skipped. Label clearly in claim registry / release notes. |
| Can a release note claim behavior from a different commit/tag? | **Open until release discipline:** package still `0.4.0`; do not describe `8728f98` behavior as `v0.3.2` or as tagged `v1.0.0`. |
| Can an allocation be misreported as payment? | **Mitigated in provenance model:** Axis A vs Axis B separation; Aug 24 financial fields null; Friday status **not invented**. |
| Can the verifier return success while a profile-required check is not run? | **Watch:** `ok=true` with `unverified` / `not-run` entries is allowed by design; marketing must not equate `ok` with full-profile assurance. |
| Can path traversal/symlink/SSRF make verifier/capture read unintended resources? | **Partial evidence:** bundle path-safety tests present; capture SSRF module exists. Keep capture claims bounded to tested surfaces. |
| Can current replay language be misread as actual model re-execution? | **Mitigated if claims stay tight:** C5 is artifact recomputation; claim registry / ASSURANCE-CASE must keep that wording. |
| Can a public bundle leak protected content in metadata, errors, logs, or auxiliary files? | **Residual risk:** projection canary/leak tests should remain in release suite; public examples must stay free of protected payloads. |

**Red-team verdict:** several controls look directionally correct under local tests, but **corpus independence (human)**, **Friday funding capture**, **pilot evidence**, and **release-asset/tag identity** remain material blockers. Narrowing advertised claims is acceptable; tagging `v1.0.0` is not.

---

## Go / no-go

**NO-GO for `v1.0.0`.**

Minimum remaining blockers before any tag discussion:

1. Genuine independent second annotations for the three baseline cases (verify + integrate; agreement before reconciliation).
2. Authoritative Friday (or actual-date) funding snapshot with Axis A/B split — only after public artifact exists.
3. Pilot or realistic operator dry-run evidence with predeclared burden metrics (or explicitly drop I6–I7 from advertised scope).
4. Release candidate SHA + assets + version sync + signed checklist for every blocking row above.
