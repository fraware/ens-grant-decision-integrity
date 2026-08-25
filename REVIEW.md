# Review Guide

## Objective

Test whether the Charter and decision-record schema improve an actual ENS funding workflow without creating disproportionate process cost.

A useful review is adversarial: identify concrete failure modes, unnecessary requirements, missing invariants, and implementation cost. Review does not imply endorsement, funding, or a decision on any applicant.

## Scope

This repository currently ships:

- a draft Grants Charter (not adopted ENS policy);
- grant-decision schema `0.1` and optional schema `0.2` extensions;
- a conformance validator and adversarial suites;
- a fictional mapping of the public SPP3 Marketplace process;
- Phase II evaluator-manifest commitment, anchor verification (Rekor v1/v2 modules; production RFC 3161 fail-closed), run attestation, and canonical artifact-recomputation evidence (additive);
- deterministic confidential-to-public projection v1 and v2 (additive);
- packaged `gdi` verifier, claim registry, profiles, and adapters;
- a retrospective empirical corpus (in progress; double annotation not complete).

Production RFC 3161 verification, actual evaluator implementation re-execution, cryptographic selective-disclosure proofs, and live Ethereum mainnet anchoring are not shipped as production guarantees; see `phase2/DEFERRED.md`. Package `0.4.0` is not a `v1.0.0` claim.
The worked Marketplace record is a dated, fictional process snapshot. It does not identify, score, recommend, or reject a real applicant, and it does not prescribe changes to the mapped process.

## Validation

The repository carries a reproducible validation contract in `VALIDATION.md`. The worked example is expected to have no conformance errors and to emit only `CHAL003` while the reviewed public process does not identify a factual/procedural correction route.

Validation results are evidence only for the exact commit and configuration that ran. A successful historical or fixture test must not be generalized into a production guarantee outside its stated trust boundary.

## Primary review question

**What would you delete, what is missing, and what would make this impractical in a real ENS funding workflow?**

A simpler mechanism is preferable wherever it preserves the same guarantees.

## Review lenses

### Committee workflow

- Does the distinction between evaluator participation and final decision authority match actual committee practice?
- Are quorum, decision-rule, recusal, and substitution records sufficient without duplicating internal administration?
- Is the five-surface governing-policy map sufficient to reconstruct which public rules governed a review?
- When schema 0.2 `authorityIdentity` is used, does member linkage reduce ambiguity without adding unused process cost?
- Which required fields create process cost without enough audit value?

### Grant administration and accountability

- Is evidence linkage for failed hard-screen rules operationally realistic?
- Does the challenge model correctly distinguish factual/procedural correction from relitigation of substantive judgment?
- Does the existing process already provide a correction route that the reviewed public Marketplace artifacts do not identify?
- Do delivery-condition fields support accountability without giving the verifier authority to re-evaluate grant merit?
- Is the projection allowlist/redaction model usable for publishing without overclaiming selective disclosure or source completeness?
- Which information should remain confidential or selectively disclosed?

### AI-assisted evaluation

- Is `materiallyInformedRecommendation` the right threshold for triggering evaluator-manifest provenance?
- Which evaluator-manifest elements must be fixed before applications close, and which should remain undisclosed until later?
- Does the declared pre-deadline commitment requirement address configuration drift without implying stronger assurance than the record provides?
- If a production temporal-precedence claim is required, which currently supported anchor profile and trust policy are acceptable? `rekor-v1` is retained as a historical compatibility profile; production `rfc3161` is currently fail-closed, and recorded fixture profiles are test evidence only.
- Does canonical artifact recomputation provide enough audit value without being mistaken for implementation re-execution?
- Could the manifest, conformance rules, or claim matrix themselves create a gaming surface?

## Suggested response format

For each issue, a short response is sufficient:

1. **Surface** — Charter section, schema field, conformance rule, Phase II claim, or projection path.
2. **Failure mode or cost** — what goes wrong in a real workflow.
3. **Evidence or scenario** — concrete example if available.
4. **Smallest change** — delete, add, weaken, strengthen, or leave unchanged.

## Useful outcome

The strongest feedback identifies a concrete deletion, addition, constraint, simplification, or confirmed non-change grounded in an actual review or accountability workflow.
