# External Review Protocol — Draft v0.1

## Objective

Test whether the Charter and decision-record schema improve an actual ENS funding workflow without creating disproportionate process cost.

The request is for adversarial critique. It is not a request for endorsement, funding, or a decision on any live applicant.

## Review boundary

The package implements the proposal's first $200 work item: a draft Grants Charter and machine-readable decision-record schema. It does not implement the later full evaluator-manifest protocol, commitment anchoring, selective-disclosure proofs, evaluator replay, or a deterministic confidential-to-public record projection.

The Marketplace worked example is fictional and non-evaluative. It maps the published process only. It does not identify, score, recommend, or reject any live applicant, and it does not propose changing the rules of the active Marketplace review.

## Validation state

The executable surface at commit `dc3a86a8ec7c555b89865a4e6b37dc45ef443879` was independently reconstructed from GitHub-backed file contents, byte-matched to the corresponding Git blob identities, and passed the full validation contract:

```bash
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_final_consistency.py
```

The current branch differs from that executable commit only in review/validation documentation. GitHub-hosted Actions is separately blocked by the repository owner's account billing/spending-limit condition; GitHub reports that the job never started.

## Primary review question

**What would you delete, what is missing, and what would make this impractical in a real ENS funding round?**

A simpler mechanism is preferable wherever it preserves the same guarantees.

## Review lenses

### Committee workflow

- Does the distinction between evaluator participation and final decision authority match the actual SPP3 workflow?
- Are quorum, decision-rule, recusal, and substitution records sufficient without duplicating internal committee administration?
- Is the five-surface governing-policy map sufficient to reconstruct which public rules governed a review?
- Which required fields would create process cost without enough audit value?

### Grants and accountability

- Is evidence linkage for failed hard-screen rules operationally realistic?
- Does the challenge model correctly distinguish factual/procedural correction from relitigation of substantive judgment?
- Does the existing SPP3 process already provide a correction route that the reviewed public Marketplace artifacts do not identify?
- Do delivery-condition fields support accountability without giving the verifier authority to re-evaluate grant merit?
- Which information should remain internal or selectively disclosed?

### AI-assisted evaluation

- Is `materiallyInformedRecommendation` the right threshold for triggering evaluator-manifest provenance?
- Which evaluator-manifest elements must be fixed before applications close, and which should remain undisclosed until later?
- Does requiring a declared pre-deadline commitment address configuration drift without implying stronger assurance than the record provides?
- What independently verifiable timestamp or publication anchor would be acceptable in a later commit–reveal protocol?
- Could the manifest or conformance rules create a new gaming surface?

## Requested response format

A useful review can be very short. For each issue:

1. **Surface** — Charter section, schema field, or conformance rule.
2. **Failure mode or cost** — what goes wrong in a real workflow.
3. **Evidence or scenario** — concrete example if available.
4. **Smallest change** — delete, add, weaken, strengthen, or leave unchanged.

## Success condition

The review succeeds if it produces at least one concrete deletion, addition, constraint, or confirmed non-change grounded in an actual ENS review or accountability workflow.

## Suggested first reviewers

The first review round should remain small and cover distinct failure surfaces:

- **SPP3 committee/process:** test committee authority, quorum, recusals, decision procedure, and operational burden.
- **Grant administration/accountability:** test eligibility, correction paths, evidence handling, and delivery verification.
- **AI screening:** test evaluator-manifest boundaries, prompt-gaming assumptions, and commitment semantics.

Broader public review should follow only after these distinct lenses have produced concrete feedback.
