# Final study report (draft)

Status: **incomplete draft**. Machine gates for `ready-for-final-review` are **not** met. Case-count and declared required-stratum coverage are currently satisfied; double annotation remains blocked. Do not treat this document as a completed empirical report.

## 1. Objective and preregistration reference

**Known.** The retrospective corpus tests whether the Grant Decision Integrity ontology and tooling improve reconstructability of real historical decision processes without disproportionate administrative burden, per `corpus/study-plan.json` (studyPlanVersion `1`).

The study is a heterogeneous stress-test, not a statistically representative estimate of all ENS decisions. Validator success is an outcome to record, not a target to force.

## 2. Study timeline, including post-start addenda

**Partially known.**

| Date / marker | Event |
| --- | --- |
| Study plan checked in | Predeclared infrastructure in `corpus/study-plan.json` |
| Baseline commit `00fb8231…` | Three empirical cases present; no second annotations recorded |
| `2026-08-25` | Post-start double-annotation addendum `corpus/double-annotation-plan-2026-08-25.json` selects baseline cases |
| After PR #19 merge | Fourth empirical case: anonymous hard-eligibility disqualification |
| `2026-08-25` | Selection addendum `corpus/selection-log-2026-08-25.json` for additional candidates |
| `2026-08-25` | Source-only second-annotation handoffs prepared; human returns **pending** |
| `2026-08-25` (a3 encoding) | Five additional public-only cases encoded from the selection addendum (empirical count **9**) |

**Incomplete.** Exact annotation start/end calendar for each case, human second-annotator receipt dates, and final-review completion date are not filled here.

## 3. Sampling frame and case inclusion log

**Partially known.**

Sampling strategy (preregistered): heterogeneous stress-test covering required strata where evidence exists; target 8–12 counted empirical cases.

**Currently counted empirical cases (9):**

1. `ens-spp3-2026-namespace-award`
2. `ens-spp3-2026-ethid-withdrawal`
3. `ens-spp2-2025-agora-budget-rejection`
4. `ens-spp3-2026-anonymous-hard-eligibility-disqualification`
5. `ens-spp3-2026-goldsky-award` (new)
6. `ens-spp2-2025-justaname-award` (new)
7. `ens-spp2-2025-ep65-vote-amendment` (new)
8. `ens-spp2-2025-unruggable-q4-delivery` (new)
9. `ens-spp3-2026-marketplace-rfp-amendment` (new)

**Selection addendum:** see `corpus/selection-log-2026-08-25.json`. Five preferred candidates encoded; Fluidkey remains selected-not-yet-encoded and held in reserve under the 12-case ceiling.

**Strata gaps / dispositions:**

| Stratum | Disposition |
| --- | --- |
| All required strata in study-plan | Represented by at least one counted case (machine `requiredUnresolved` empty) |
| `recusal-or-conflict` | Only Namespace discloses a distinct public recusal; no second recusal case invented |
| `committee-quorum` | Represented by Namespace; JustaName intended it at selection but did not claim it without a bound quorum figure |
| `ai-assisted-when-evidenced` | **Not evidenced** in selected historical decisions; not invented |
| `public-private-separation` | Covered by Namespace/EthID; Fluidkey optional for further stress |

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

**Incomplete.** Metrics must be computed from the final counted corpus using definitions in `study-plan.json` without redefining denominators. Per-case metrics are available via `scripts/corpus_metrics.py` / `scripts/validate_corpus_cases.py`. Aggregate medians/ranges/per-stratum breakdowns are **post-hoc secondary analysis** if added later.

## 6. Second-annotation agreement results

**Blocked / incomplete.**

Handoffs prepared under `corpus/second-annotation-handoffs/` (see `HANDOFF-STATUS.md`). Human completed annotations have not been returned. `review.doubleAnnotation` remains `false` on counted cases. Agreement and kappa are **not** reported. Machine blocker: `0/9` cases below minimum fraction `0.25` (need at least 3 double-annotated cases at current corpus size).

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

## 10. Administrative-burden measurements

**Incomplete.**

Primary annotation elapsed minutes exist per case in `case.json` annotations. Aggregate burden (including second annotation time) awaits human second-annotation completion.

## 11. Limitations and non-claims

**Known (carry forward from study plan and corpus docs).**

- Heterogeneous stress-test, not representative causal estimate.
- Validator success does not establish substantive correctness, fairness, or institutional legitimacy.
- Missing public evidence does not prove absence of private/internal procedure.
- Double annotation measures classification reproducibility under the supplied evidence set, not correctness or source truth.
- Handoff tooling cannot prove human independence.
- Conditional stratum `ai-assisted-when-evidenced` is **not evidenced**; no AI-assisted case was invented.
- Meeting the 8–12 case-count band does not by itself make the study ready-for-final-review.

## 12. Implications for v1 profile design and future adoption

**Incomplete — placeholder only.**

Topics to revisit after corpus completion (not conclusions):

- whether anonymous/protected identity needs a versioned schema extension;
- whether governance amendments need a dedicated status/recordType distinct from applicant awards;
- whether reference-only heavy corpora remain operationally useful;
- whether committee versus delegate-ranked processes stress different required fields;
- adoption/pilot implications only after machine gates and human final review.

---

## Draft control

| Item | State |
| --- | --- |
| Empirical case count vs 8–12 | **9 encoded; minimum met** |
| Required strata coverage (declared) | Machine `requiredUnresolved` empty |
| Double annotation ≥ 25% | **Blocked** (0/9; need ≥3) |
| `scripts/study_status.py` ready-for-final-review | **false** (`status: in-progress`) |
| This report | Draft only; not final-review ready |
