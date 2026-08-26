# Final study report (draft)

Status: **incomplete draft**. Machine gates for `ready-for-final-review` are **not** met. Case-count and declared required-stratum coverage are currently satisfied; double annotation remains blocked. Do not treat this document as a completed empirical report.

The numeric tables below were last computed with `scripts/study_status.py` and `gdi.corpus.metrics.compute_metrics` against repository `main` `8728f9848673b19e349870b7e89fff1d97d8eef0` during an engineering refresh. The report text has since received methodological hardening on the release branch. **All metrics and status fields must be regenerated from the exact final empirical commit before any final-review or release claim.**

## 1. Objective, preregistration, and construct-validity boundary

**Original objective.** The retrospective study plan states an objective of testing whether the Grant Decision Integrity ontology and tooling improve reconstructability of real historical decision processes without disproportionate administrative burden (`corpus/study-plan.json`, studyPlanVersion `1`).

**What the present design can actually identify.** The checked-in study is a heterogeneous retrospective stress-test without an untreated, alternative-workflow, or before/after comparator. It can describe reconstructability under the GDI ontology, source-observability limits, ontology/tooling failure modes, annotation consistency, and bounded annotation-time observations for the sampled cases. It **cannot identify a comparative or causal “improvement” effect** relative to existing practice or another system.

Likewise, no predeclared administrative-burden comparator or proportionality threshold exists, and the legacy primary `elapsedMinutes` measurements were not prospectively standardized. The present study therefore **cannot establish that total administrative burden is proportionate, reduced, or lower than an alternative process**. Any such future claim requires a prospectively specified comparator, outcome definition, timing/cost protocol, and analysis plan; causal wording additionally requires a design that supports causal identification.

These interpretation rules are frozen in the post-start, pre-second-annotation addendum `corpus/analysis-plan-addendum-2026-08-26.json`. That addendum does not rewrite the original study plan and does not erase that primary-annotation outcomes were already known when it was written.

The study remains a heterogeneous stress-test, not a statistically representative estimate of all ENS decisions. Validator success is an outcome to record, not a target to force.

## 2. Study timeline, including post-start addenda

**Partially known.**

| Date / marker | Event |
| --- | --- |
| Study plan checked in | Predeclared infrastructure in `corpus/study-plan.json` |
| Baseline commit `00fb8231…` | Three empirical cases present; no second annotations recorded |
| `2026-08-25` | Post-start double-annotation addendum `corpus/double-annotation-plan-2026-08-25.json` selects all baseline cases |
| After PR #19 merge | Fourth empirical case: anonymous hard-eligibility disqualification |
| `2026-08-25` | Selection addendum `corpus/selection-log-2026-08-25.json` for additional candidates |
| `2026-08-25` | Source-only second-annotation handoffs prepared; human returns **pending** |
| `2026-08-25` (a3 encoding) | Five additional public-only cases encoded from the selection addendum (empirical count **9**) |
| `2026-08-26` | Post-start, pre-second-annotation analysis addendum freezes reliability/timing interpretation before any agreement outcome exists |
| `2026-08-26` | Second-annotation protocol hardened so a completed copy requires an explicit human-entered independence attestation in addition to `independent=true`; frozen source-only handoff hashes remain unchanged |

**Incomplete.** Exact annotation start/end calendar for each case, human second-annotator receipt dates, and final-review completion date are not filled here.

## 3. Sampling frame and case inclusion log

**Partially known.**

Sampling strategy (preregistered): heterogeneous stress-test covering required strata where evidence exists; target 8–12 counted empirical cases.

**Currently counted empirical cases (9):**

1. `ens-spp3-2026-namespace-award`
2. `ens-spp3-2026-ethid-withdrawal`
3. `ens-spp2-2025-agora-budget-rejection`
4. `ens-spp3-2026-anonymous-hard-eligibility-disqualification`
5. `ens-spp3-2026-goldsky-award`
6. `ens-spp2-2025-justaname-award`
7. `ens-spp2-2025-ep65-vote-amendment`
8. `ens-spp2-2025-unruggable-q4-delivery`
9. `ens-spp3-2026-marketplace-rfp-amendment`

**Selection addendum:** see `corpus/selection-log-2026-08-25.json`. Five preferred candidates encoded; Fluidkey remains selected-not-yet-encoded and held in reserve under the 12-case ceiling. It must not be added or omitted because of future second-annotation agreement outcomes.

**Machine study-status at the last recorded refresh:** `ok=true`, `readyForFinalReview=false`, `status=in-progress`, blocker `double-annotation: 0/9` (need ≥3 at current corpus size). Required strata declared coverage: met (`requiredUnresolved` empty). Conditional `ai-assisted-when-evidenced`: uncovered / not invented. Regenerate this status on the exact final empirical commit.

## 4. Case table

**Draft from checked-in cases.** Exact finding inventories are bound in each `case.json`.

| caseId | decisionClass | strata (declared) | sourceAccess | annotation count | record changed |
| --- | --- | --- | --- | --- | --- |
| ens-spp3-2026-namespace-award | approved-award | merit, award, quorum, recusal, policy, delivery, public-private, incomplete-public | public-only | 1 (second pending) | no |
| ens-spp3-2026-ethid-withdrawal | other | merit, policy, public-private, incomplete-public, other | public-only | 1 (second pending) | no |
| ens-spp2-2025-agora-budget-rejection | other | merit, policy, incomplete-public, other | public-only | 1 (second pending) | no |
| ens-spp3-2026-anonymous-hard-eligibility-disqualification | eligibility-failure | hard-eligibility, incomplete-public | public-only | 1 | yes (`record-reconciled.json`) |
| ens-spp3-2026-goldsky-award | approved-award | award, merit, delivery, incomplete-public | public-only | 1 | no |
| ens-spp2-2025-justaname-award | approved-award | award, merit, incomplete-public | public-only | 1 | no |
| ens-spp2-2025-ep65-vote-amendment | other | policy, incomplete-public | public-only | 1 | no |
| ens-spp2-2025-unruggable-q4-delivery | other | delivery, incomplete-public | public-only | 1 | no |
| ens-spp3-2026-marketplace-rfp-amendment | other | policy, delivery, incomplete-public | public-only | 1 | no |

## 5. Preregistered primary metrics

**Partial — primary annotations only.** Definitions come from `study-plan.json` `primaryMetrics`. Values below are per-case machine outputs from primary annotations. Aggregate medians/ranges were not preregistered primary analysis; if added later, they must be labeled post-hoc descriptive under the analysis addendum. Double-annotation agreement metrics are blocked (section 6).

| caseId | reconstructability | direct-source | unknown | interpretive share of reconstructable | elapsed min | source artifacts | initial findings | finding dispositions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ens-spp2-2025-agora-budget-rejection | 0.827586 | 0.241379 | 0.172414 | 0.583333 | 3.5 | 6 | 3 | unresolved:3 |
| ens-spp2-2025-ep65-vote-amendment | 0.833333 | 0.300000 | 0.166667 | 0.520000 | 4.0 | 4 | 3 | unresolved:3 |
| ens-spp2-2025-justaname-award | 0.843750 | 0.343750 | 0.156250 | 0.481481 | 5.2 | 6 | 3 | unresolved:3 |
| ens-spp2-2025-unruggable-q4-delivery | 0.818182 | 0.363636 | 0.181818 | 0.444444 | 4.5 | 4 | 3 | unresolved:3 |
| ens-spp3-2026-anonymous-hard-eligibility-disqualification | 0.758621 | 0.310345 | 0.241379 | 0.545455 | 3.3 | 3 | 6 | annotation-defect:2; unresolved:4 |
| ens-spp3-2026-ethid-withdrawal | 0.766667 | 0.233333 | 0.233333 | 0.608696 | 1.8 | 5 | 3 | model-defect:1; unresolved:2 |
| ens-spp3-2026-goldsky-award | 0.878788 | 0.363636 | 0.121212 | 0.482759 | 6.5 | 5 | 2 | unresolved:2 |
| ens-spp3-2026-marketplace-rfp-amendment | 0.812500 | 0.281250 | 0.187500 | 0.538462 | 5.0 | 3 | 3 | unresolved:3 |
| ens-spp3-2026-namespace-award | 0.878788 | 0.363636 | 0.121212 | 0.482759 | 8.4 | 5 | 2 | unresolved:2 |

**Primary-metric honesty notes:**

- Rates are over applicable required fields in the primary annotation, not over all schema fields.
- These values describe the sampled reconstructions; they do not identify an improvement effect relative to a comparator.
- Legacy primary `elapsedMinutes` values are observational metadata whose exact operational scope was not prospectively standardized. They are not a complete measure of administrative burden or adoption cost.
- These metrics do **not** establish source truth, merit, fairness, or institutional legitimacy.
- `agreement` / Cohen kappa: **not computable** until genuine independent second annotations exist.

## 6. Second-annotation agreement results

**Blocked / incomplete.**

Handoffs are under `corpus/second-annotation-handoffs/` (see `HANDOFF-STATUS.md` and `ANNOTATOR-CHECKLIST.md`). Human completed annotations have not been returned. `review.doubleAnnotation` remains `false` on counted cases. Agreement and kappa are **not** reported. Machine blocker at the last refresh: `0/9` cases below minimum fraction `0.25` (need at least 3 double-annotated cases at current corpus size).

The three cases are fixed by `double-annotation-plan-2026-08-25.json`; do not replace a case based on observed agreement. Agreement must be computed from the two frozen pre-reconciliation annotations. Report per-case compared-field count, raw classification agreement, Cohen's kappa when mathematically defined, and disagreement counts. Do not pool nested fields into a population-inferential kappa, do not attach qualitative reliability labels as if they were population categories, and do not suppress low or undefined results.

Completing three selected cases satisfies the study-plan 25% completion rule at the current corpus size. It does **not** support a strong population-level reliability claim.

The current verifier also requires the completed human copy to add the exact independence attestation specified by `ANNOTATOR-CHECKLIST.md`. The frozen source-only package itself does not contain that attestation key. Tool validation establishes that the returned artifact contains the required assertion; it still cannot prove the human's actual information exposure.

## 7. Recurring ontology/model defects

**Partially known.**

- Anonymous/publicly-unknown applicant identity collides with v0.1 required non-empty `application.applicantName` (hard-eligibility case).
- Procedural amendments and authorizations without settled applicant awards do not fit v0.1 `decision.status=approved` without inventing `awardedAmount` / non-empty `deliveryConditions`; EP6.5 and EP7.1 cases retain intentional non-vocabulary statuses (`amendment-passed`, `authorization-passed`) as reconstructability encodings.
- Disclosure serialization defects observed on the hard-eligibility initial record were treated as annotation/reconstruction defects in reconciliation.

**Incomplete.** Cross-case defect inventory after double annotation and human final review.

## 8. Recurring source observability gaps

**Partially known.**

- Many governing and decision sources are `reference-only` (no public byte-preserved capture claimed).
- Application IPFS URIs may fail retrieval; fields stay unknown rather than inferred.
- Individual committee scores, KYC, Award Notices, and private deliberations are routinely non-public.
- Exact schema-v0.1 timestamps (`effectiveAt`, `checkedAt`, sometimes `decidedAt`) often cannot be bound from rendered public clocks.
- Provider quarterly self-reports are not independent verification of every claimed deliverable.
- Missing public evidence is not treated as proof that private procedure did not exist.

## 9. Confirmed process gaps

**Incomplete / none asserted in this draft.**

Confirmed process gaps require source-bounded wording after review dispositions. Do not convert unresolved schema nulls or missing public evidence into confirmed process gaps without adjudication.

## 10. Annotation-time observations; administrative burden not identified

**Partial (primary only).**

Primary annotation `elapsedMinutes` values in section 5 range from 1.8 to 8.4 minutes in the currently recorded public reconstructions. Those values were captured before a prospectively standardized timing scope was defined. They may be reported as legacy observational metadata, but **must not be interpreted as total administrative burden, implementation cost, or adoption cost**.

For second annotations completed after the 2026-08-26 protocol clarification, `elapsedMinutes` is prospectively defined as active time spent inspecting the supplied source set and producing the annotation submission, excluding unrelated breaks, communication, engineering/package preparation, and post-submission reconciliation. These standardized second-annotation times must be reported separately from legacy primary times unless measurement-scope equivalence is independently established.

The present design has neither a burden comparator nor a predeclared proportionality threshold. It therefore cannot resolve whether administrative burden is “disproportionate.”

## 11. Limitations and non-claims

**Known (carry forward from the study plan, corpus protocol, and analysis addendum).**

- Heterogeneous stress-test, not a statistically representative population sample.
- No comparator or counterfactual: the design does not identify whether GDI improves reconstructability relative to an alternative workflow.
- No burden comparator or threshold: elapsed-time observations do not establish burden proportionality or reduction.
- Validator success does not establish substantive correctness, fairness, or institutional legitimacy.
- Missing public evidence does not prove absence of private/internal procedure.
- Double annotation measures classification reproducibility under the supplied evidence set, not correctness or source truth.
- Three double-annotated cases, if completed, satisfy a study-completion fraction but are too few for a strong population-level reliability claim.
- Explicit annotator attestation improves auditability but cannot prove the human process was independent.
- Primary timing was not prospectively standardized; standardized second-annotation timing has a narrower, explicit scope.
- Conditional stratum `ai-assisted-when-evidenced` is **not evidenced**; no AI-assisted case was invented.
- Meeting the 8–12 case-count band does not by itself make the study ready-for-final-review.

## 12. Implications for v1 profile design and future adoption

**Incomplete — placeholder only.**

Topics to revisit after corpus completion (not conclusions):

- whether anonymous/protected identity needs a versioned schema extension;
- whether governance amendments need a dedicated status/recordType distinct from applicant awards;
- whether reference-only-heavy corpora remain operationally useful;
- whether committee versus delegate-ranked processes stress different required fields;
- what prospective comparator would be appropriate for any future claim that GDI improves reconstructability or reduces burden;
- adoption/pilot implications only after machine gates and human final review.

---

## Draft control

| Item | State |
| --- | --- |
| Empirical case count vs 8–12 | **9 encoded; minimum met** |
| Required strata coverage (declared) | Machine `requiredUnresolved` empty at last refresh; regenerate at final empirical commit |
| Double annotation ≥ 25% | **Blocked** (last refresh 0/9; need ≥3) |
| Second-annotation agreement outcomes | **Not observed / not reported** |
| Improvement-effect identification | **Not identified by current design** |
| Administrative-burden proportionality | **Not identified by current design** |
| `scripts/study_status.py` ready-for-final-review | **false** at last refresh (`status: in-progress`); regenerate at final empirical commit |
| This report | Draft only; not final-review ready |
