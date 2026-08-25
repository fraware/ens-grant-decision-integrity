# SPP3 EthID withdrawal retrospective case review

## Scope and selection rationale

This case reconstructs the EthID SPP3 selection-and-withdrawal lifecycle using public sources only. It was selected after the first approved-award case because it contains an observed terminal state that the v0.1 decision-status vocabulary cannot represent without distortion: EthID was initially selected by the committee, publicly declined SPP3 funding, and was excluded from the final four-provider cohort before DAO ratification.

The purpose is construct-validity testing. The case does not rescore EthID, infer private applicant facts, or change v0.1 to make the record fit.

## Source basis

1. **Program authorization and committee model** — `https://discuss.ens.domains/t/6-42-social-spp3-program-authorization-and-committee-model/22086`. The authorization separates committee cohort selection/recommendation from final DAO ratification. Cohort voting/ranking requires 3 of 4 Member seats active and participating; decisions require a simple majority of participating Members; the Chair votes only as a tiebreaker. The cohort recommendation is submitted as a take-it-or-leave-it executable proposal.
2. **Submission timeline and rubric** — `https://discuss.ens.domains/t/spp3-submission-timeline-and-artifacts/22124`. Before scoring, applications pass a hard eligibility screen. Qualifying applications are scored on Prior Delivery 25%, Scope Clarity 15%, Milestone Structure 15%, Adoption/Revenue/Ecosystem Utility 40%, and Team/Budget Fit 5%.
3. **Cohort recommendation and discussion** — `https://discuss.ens.domains/t/ep-6-49-spp3-cohort-recommendation/22237`. The initial report states that five providers were selected and EthID declined the offer. EthID publicly states that it decided to decline SPP3 funding. The committee later states that the withdrawal removes $1,200,000 from the recommended cohort and that the cohort will proceed with Namespace, Goldsky, Unruggable, and Fluidkey at $1,690,000. The same update states that EthID applied and was evaluated as a whole team. Individual scoring records remain internal, and applicant-specific aggregate rubric scores are available privately on request rather than published in the reviewed source.
4. **Marketplace RFP** — `https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263`. This later proposal states that the provider selected for the marketplace and revenue vertical declined its award, leaving the vertical unfilled, and that the standalone cohort proposal ratifies the four remaining providers.
5. **Final cohort proposal mirror** — `https://dao.ens.gregskril.com/proposal/30153206728472299340257495645753485226870528642942223493225654414745632348879`. Used only as a public reconstruction source showing the executed final cohort excludes EthID. It is not represented as an independent cryptographic proof.

All five source entries are `reference-only`; this case therefore makes no exact-byte preservation claim for the remote pages.

## Observed lifecycle and model gap

The public evidence supports the following sequence: EthID qualified for review, was evaluated, was one of five initially selected providers, publicly declined funding, and was removed before the final four-provider executable cohort. The committee states that the withdrawal removed $1,200,000 from the recommended cohort.

v0.1 permits `decision.status` values `pending`, `ineligible`, `approved`, `rejected`, `deferred`, and `suspended`. None is an accurate description of this terminal applicant lifecycle state. Encoding `approved` would imply a final award that never occurred. Encoding `rejected` would turn an applicant withdrawal into an institutional rejection. `pending`, `deferred`, and `suspended` would incorrectly imply the candidacy remained live.

The record therefore uses the literal value `withdrawn` and intentionally violates the v0.1 status enum. The resulting `SCHEMA` finding is classified `model-defect`. This is a case-specific representational result. It does not by itself justify adding `withdrawn` to the institutional decision-status enum: a better future design may separate institutional decision state from applicant disposition or lifecycle events.

`decision.authorityKind = committee` identifies the last documented institutional selection surface before withdrawal. It does not classify EthID's withdrawal as a committee act and does not imply that ENS DAO made a final award decision for EthID.

## Financial boundary

The public committee update says EthID's withdrawal removed $1,200,000 from the recommended cohort. The record does not store this as `decision.awardedAmount`, because no final EthID award was ratified. It is retained only as an evidence-linked material finding and explanatory rationale. No payment, receipt, or settlement is claimed.

## Preserved unknowns

`governingPolicy.effectiveAt` and `eligibility.checkedAt` remain null because the reviewed public sources do not establish the exact timestamps required by schema v0.1. EthID-specific aggregate scores are also not public in the reviewed source set. No conflict or internal disagreement is inferred from silence in the public record.

The May 14 timeline says provider submissions close June 9, while the later cohort process narrative says submissions closed June 4. This discrepancy is preserved rather than silently resolved.

## Measurement boundary

`annotations[0].elapsedMinutes = 1.8` measures the timed structured record-and-field-classification pass after the source set had already been researched and reviewed. It does not include earlier source discovery or reading and must not be interpreted as end-to-end reconstruction effort. Future burden measurement should separately time source acquisition, source review, record construction, annotation, reconciliation, and independent review.

## Expected validator state

The case intentionally expects three structural findings:

1. `decision.status` uses the source-faithful but out-of-vocabulary value `withdrawn` — disposition `model-defect`.
2. `eligibility.checkedAt` is null — disposition `unresolved`.
3. `governingPolicy.effectiveAt` is null — disposition `unresolved`.

The exact record-byte hash declared in `case.json` is `sha256:4ed7dfc475b66532893bb17eed009d8e41b94111fa6761888a7be3adb1a7c982`. This hash and the exact validator finding inventory are expectations until hosted validation runs on the exact PR head. They are not represented as validated merely because they were computed during construction.

Because structural validation short-circuits semantic conformance, absence of semantic findings in this structurally invalid record is not evidence that all semantic obligations were satisfied. No reconciliation has been performed.
