# Final study report (draft)

Status: **incomplete draft structure**. Machine gates for `ready-for-final-review` are **not** claimed. Double annotation and additional case encoding remain blocked or unfinished. Do not treat this document as a completed empirical report.

## 1. Objective and preregistration reference

**Known.** The retrospective corpus tests whether the Grant Decision Integrity ontology and tooling improve reconstructability of real historical decision processes without disproportionate administrative burden, per `corpus/study-plan.json` (studyPlanVersion `1`).

The study is a heterogeneous stress-test, not a statistically representative estimate of all ENS decisions. Validator success is an outcome to record, not a target to force.

## 2. Study timeline, including post-start double-annotation addendum

**Partially known.**

| Date / marker | Event |
| --- | --- |
| Study plan checked in | Predeclared infrastructure in `corpus/study-plan.json` |
| Baseline commit `00fb8231…` | Three empirical cases present; no second annotations recorded |
| `2026-08-25` | Post-start double-annotation addendum `corpus/double-annotation-plan-2026-08-25.json` selects all three baseline cases |
| After PR #19 merge | Fourth empirical case: anonymous hard-eligibility disqualification |
| `2026-08-25` | Selection addendum `corpus/selection-log-2026-08-25.json` for additional candidates (does not rewrite study-plan) |
| `2026-08-25` | Source-only second-annotation handoffs prepared; human returns **pending** |

**Incomplete.** Exact annotation start/end calendar for each case, human second-annotator receipt dates, and final-review completion date are not filled here.

## 3. Sampling frame and case inclusion log

**Partially known.**

Sampling strategy (preregistered): heterogeneous stress-test covering required strata where evidence exists; target 8–12 counted empirical cases.

**Currently counted empirical cases (4):**

1. `ens-spp3-2026-namespace-award`
2. `ens-spp3-2026-ethid-withdrawal`
3. `ens-spp2-2025-agora-budget-rejection`
4. `ens-spp3-2026-anonymous-hard-eligibility-disqualification`

**Selection addendum candidates (not yet encoded):** see `corpus/selection-log-2026-08-25.json` (six source-bounded candidates). Encoding of at least four remains required for the case-count gate.

**Incomplete.** Final inclusion/exclusion table after encoding all additional cases; research disposition text for any still-uncovered required stratum after evidence search.

## 4. Case table

**Incomplete — draft from checked-in cases only.**

| caseId | decisionClass | strata (declared) | sourceAccess | annotation count | initial findings | final findings | record changed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ens-spp3-2026-namespace-award | approved-award | merit, award, quorum, recusal, policy, delivery, public-private, incomplete-public | public-only | 1 (second pending) | see case.json | see case.json | no reconciled snapshot in baseline layout |
| ens-spp3-2026-ethid-withdrawal | other | merit, policy, public-private, incomplete-public, other | public-only | 1 (second pending) | see case.json | see case.json | no |
| ens-spp2-2025-agora-budget-rejection | other | merit, policy, incomplete-public, other | public-only | 1 (second pending) | see case.json | see case.json | no |
| ens-spp3-2026-anonymous-hard-eligibility-disqualification | eligibility-failure | hard-eligibility, incomplete-public | public-only | 1 | preserved full initial set | reconciled retains unresolved nulls | yes (`record-reconciled.json`) |

Exact finding counts and messages are bound in each `case.json` and must be taken from validator output, not paraphrased here until the metrics pass is finalized.

## 5. Preregistered primary metrics

**Incomplete.** Metrics must be computed from the final counted corpus using definitions in `study-plan.json` without redefining denominators:

- required-field reconstructability rate
- required-field direct-source rate
- required-field unknown rate
- interpretive share among reconstructable required fields
- annotation elapsed minutes
- source-artifact count
- initial validator errors and warnings
- finding dispositions after review
- raw classification agreement on double-annotated cases
- Cohen kappa on classification for double-annotated cases

Any medians/ranges/per-stratum breakdowns added later must be labeled **post-hoc secondary analysis**.

## 6. Second-annotation agreement results

**Blocked / incomplete.**

Handoffs prepared and hashed under `corpus/second-annotation-handoffs/` (see `HANDOFF-STATUS.md`). Human completed annotations have not been returned. `review.doubleAnnotation` remains `false` on the three selected cases. Agreement and kappa are **not** reported.

## 7. Recurring ontology/model defects

**Partially known (early).**

- Anonymous/publicly-unknown applicant identity collides with v0.1 required non-empty `application.applicantName` (hard-eligibility case). Unit-of-analysis question deferred per Workstream 01; no v0.1 schema change claimed here.
- Disclosure serialization defects observed on the hard-eligibility initial record were treated as annotation/reconstruction defects in reconciliation, not as historical process gaps.

**Incomplete.** Cross-case defect inventory after all cases are encoded and reviewed.

## 8. Recurring source observability gaps

**Partially known (early).**

- Many governing and decision sources are `reference-only` (no public byte-preserved capture claimed).
- Application IPFS URIs may fail retrieval; fields stay unknown rather than inferred.
- Individual committee scores, KYC, Award Notices, and private deliberations are routinely non-public.
- Missing public evidence is not treated as proof that private procedure did not exist.

**Incomplete.** Final gap taxonomy after additional cases.

## 9. Confirmed process gaps

**Incomplete / none asserted in this draft.**

Confirmed process gaps require source-bounded wording after review dispositions. Do not convert unresolved schema nulls or missing public evidence into confirmed process gaps without adjudication.

## 10. Administrative-burden measurements

**Incomplete.**

Primary annotation elapsed minutes exist per case in `case.json` annotations. Aggregate burden (including second annotation time) awaits human second-annotation completion and remaining case encoding.

## 11. Limitations and non-claims

**Known (carry forward from study plan and corpus docs).**

- Heterogeneous stress-test, not representative causal estimate.
- Validator success does not establish substantive correctness, fairness, or institutional legitimacy.
- Missing public evidence does not prove absence of private/internal procedure.
- Double annotation measures classification reproducibility under the supplied evidence set, not correctness or source truth.
- Handoff tooling cannot prove human independence.
- Conditional stratum `ai-assisted-when-evidenced` is **not evidenced** in the selected historical decisions; no AI-assisted case was invented.

## 12. Implications for v1 profile design and future adoption

**Incomplete — placeholder only.**

Topics to revisit after corpus completion (not conclusions):

- whether anonymous/protected identity needs a versioned schema extension;
- whether reference-only heavy corpora remain operationally useful;
- whether committee versus delegate-ranked processes stress different required fields;
- adoption/pilot implications only after machine gates and human final review.

---

## Draft control

| Item | State |
| --- | --- |
| Empirical case count vs 8–12 | 4 encoded; below minimum |
| Required strata coverage | Not claimed complete in this draft |
| Double annotation ≥ 25% | Blocked on human returns |
| `scripts/study_status.py` ready-for-final-review | **Not claimed** |
| This report | Draft structure only |
