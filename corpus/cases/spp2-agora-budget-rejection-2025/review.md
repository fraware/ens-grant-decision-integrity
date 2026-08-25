# SPP2 Agora budget-constrained no-award retrospective case review

## Scope

This case reconstructs Agora's SPP2 eligibility and final no-award outcome from public sources only. It was selected because it exercises a materially different decision mechanism from the first two corpus cases: an eligible applicant ranks above the final `NONE BELOW` cutoff but receives no funding under a fixed program envelope. The case does not rescore Agora, treat Copeland rank as a scalar merit score, or infer private voting rationale.

## Source basis

1. **Original SPP2 facilitation plan** — `https://discuss.ens.domains/t/metagov-s-facilitation-plan-for-spp2/20340`. Used for the original program structure, eligibility rules, and MetaGov facilitation role.
2. **EP6.5 governance documentation** — `https://docs.ens.domains/dao/proposals/6.5/`. Used for the passed amendment, Copeland ranking, average-support tiebreaker, budget-option handling, and the $4.5 million allocation procedure.
3. **Amended SPP2 facilitation plan** — `https://discuss.ens.domains/t/6-5-amendment-metagovs-facilitation-plan-for-spp2/20638/1`. Used for the post-application voting-method change, final-vote eligibility statement, and limited application edit window.
4. **Agora application** — `https://discuss.ens.domains/t/spp2-agora-application/20443`. Used for applicant identity, the $300,000 basic and $400,000 extended one-year scopes, public disclosures, and MetaGov's explicit eligibility confirmation.
5. **Final SPP2 selection proposal** — `https://discuss.ens.domains/t/6-10-social-select-providers-for-service-provider-program-season-ii/20741`. Used for the final selection mechanism and the separation between candidate ranking, `NONE BELOW`, and budget options.
6. **SPP2 result interface** — `https://spp.vote/`. Used for the published final rank, support figure, funded/not-funded label, `NONE BELOW` position, and total allocated budget.

All six sources are `reference-only`. This case therefore does not claim an exact byte-preserved capture of any remote page and does not independently recompute the full election from raw ballots.

## Decision reconstruction

Agora publicly proposed a $300,000 basic one-year scope and a $400,000 extended one-year scope. MetaGov explicitly confirmed eligibility. The final result interface reports `Agora Basic` at rank 10 with 26 Copeland wins and average ENS support of 1,490,652. `NONE BELOW` is rank 11. The same result interface marks Agora Basic `Not funded` and reports $4.5 million of $4.5 million allocated.

The case therefore preserves two distinct propositions: Agora Basic finished above `NONE BELOW`, and Agora received no allocation. It does not translate the first proposition into a funded award or the second into a claim that Agora failed the electorate's cutoff.

Schema v0.1 has one terminal institutional `decision.status` surface and no separate allocation-disposition field. This reconstruction uses `rejected` as the nearest terminal no-award mapping while documenting that the public result was budget-constrained and above the cutoff. Whether a future version should separate preference/selection approval from allocation disposition is a corpus research question, not a v0.1 change made by this case.

## Policy change

Agora's application and public eligibility confirmation predate the final EP6.5 selection procedure. EP6.5 changed the voting and allocation mechanism before the final selection vote, and the amended facilitation plan reopened a limited application edit window. The record therefore represents `governingPolicy.changeDuringReview = true`.

`priorEvaluationsRerun = false` is a bounded reconstruction of the public material: the amendment is described as changing the final selection mechanism while the amended plan continues to treat the final pool as eligible. It is not represented as proof of every internal eligibility or review action.

## Deliberately unresolved timestamps

Three schema-v0.1 exact historical instants remain unresolved:

- `governingPolicy.effectiveAt`;
- `eligibility.checkedAt`;
- `decision.decidedAt`.

The reviewed sources establish the relevant sequence and display dates or times, but this reconstruction does not elevate a UI-rendered or forum-rendered clock value into a timezone-qualified RFC 3339 instant without sufficient source support. The fields remain `null` instead of receiving estimated timestamps.

Because structural schema findings short-circuit semantic conformance in the current validator, absence of semantic findings in this case would not establish that challenge, policy-change, authority, or other semantic obligations passed.

## Conflict and disclosure boundary

The Agora application publicly disclosed investor relationships involving ENS delegates. This case does not convert an applicant disclosure into an evaluator conflict, recusal, or substitution without a source-supported program adjudication connecting a named evaluator and a decision surface. No conflict object is invented for that purpose.

## Measurement boundary

`elapsedMinutes = 3.5` measures the timed structured record construction and field-classification pass after the principal source research had already been completed. It is not an end-to-end burden measurement. Source discovery, source reading, interpretation, record construction, reconciliation, and independent review must be measured separately when the full study evaluates administrative burden.

## Intended validator state before hosted validation

The construction-time record hash is:

`sha256:ba89fa6237c90a5c0adaf72776fc8b830738a4ba12524ec0814efbf176c1ed15`

The case declares three expected unresolved `SCHEMA` findings corresponding to the three unsupported exact timestamps. These are construction-time expectations only until the exact branch bytes and validator output are checked by hosted validation. If the observed hash or validator output differs, the case metadata must be corrected to the observed state without weakening the corpus contract or inventing historical values.

No v0.1 schema or semantic conformance rule is changed by this case.
