# Review Guide — v0.1

## Objective

Test whether the Charter and decision-record schema improve an actual ENS funding workflow without creating disproportionate process cost.

A useful review is adversarial: identify concrete failure modes, unnecessary requirements, missing invariants, and implementation cost. Review does not imply endorsement, funding, or a decision on any applicant.

## Scope

v0.1 contains a draft Grants Charter, a machine-readable decision-record schema, a conformance validator, and a fictional mapping of the public SPP3 Marketplace process.

It does not implement a complete evaluator-manifest protocol, independently verifiable commitment anchoring, selective-disclosure proofs, evaluator replay, or a deterministic confidential-to-public record projection.

The worked Marketplace record is a dated, fictional process snapshot. It does not identify, score, recommend, or reject a real applicant, and it does not prescribe changes to the mapped process.

## Validation

The repository carries a reproducible validation contract in `VALIDATION.md`. The worked example is expected to have no conformance errors and to emit only `CHAL003` while the reviewed public process does not identify a factual/procedural correction route.

## Primary review question

**What would you delete, what is missing, and what would make this impractical in a real ENS funding workflow?**

A simpler mechanism is preferable wherever it preserves the same guarantees.

## Review lenses

### Committee workflow

- Does the distinction between evaluator participation and final decision authority match actual committee practice?
- Are quorum, decision-rule, recusal, and substitution records sufficient without duplicating internal administration?
- Is the five-surface governing-policy map sufficient to reconstruct which public rules governed a review?
- Which required fields create process cost without enough audit value?

### Grant administration and accountability

- Is evidence linkage for failed hard-screen rules operationally realistic?
- Does the challenge model correctly distinguish factual/procedural correction from relitigation of substantive judgment?
- Does the existing process already provide a correction route that the reviewed public Marketplace artifacts do not identify?
- Do delivery-condition fields support accountability without giving the verifier authority to re-evaluate grant merit?
- Which information should remain internal or selectively disclosed?

### AI-assisted evaluation

- Is `materiallyInformedRecommendation` the right threshold for triggering evaluator-manifest provenance?
- Which evaluator-manifest elements must be fixed before applications close, and which should remain undisclosed until later?
- Does the declared pre-deadline commitment requirement address configuration drift without implying stronger assurance than the record provides?
- What independently verifiable timestamp or publication anchor would be appropriate in a later commit–reveal protocol?
- Could the manifest or conformance rules themselves create a gaming surface?

## Suggested response format

For each issue, a short response is sufficient:

1. **Surface** — Charter section, schema field, or conformance rule.
2. **Failure mode or cost** — what goes wrong in a real workflow.
3. **Evidence or scenario** — concrete example if available.
4. **Smallest change** — delete, add, weaken, strengthen, or leave unchanged.

## Useful outcome

The strongest feedback identifies a concrete deletion, addition, constraint, simplification, or confirmed non-change grounded in an actual review or accountability workflow.
