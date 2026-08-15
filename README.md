# ENS Grant Decision Integrity — v0.1

A compact, vendor-neutral governance artifact for making material ENS grant decisions inspectable without delegating final authority to automated systems.

This package implements the first funded tranche of the Simocracy proposal **“No Black-Box Grants: Ratify the Rules Before SPP Is Absorbed.”** Five ENS Governance funding decisions allocated a cumulative **$219** to the proposal. The first proposed tranche was $200 for a draft Grants Charter and a machine-readable decision-record schema.

## Included

- `CHARTER.md` — draft institutional charter for grant decision integrity.
- `schema/grant-decision-record.schema.json` — JSON Schema (Draft 2020-12) for a versioned grant decision record.
- `examples/spp3-marketplace-rfp.example.json` — illustrative, non-evaluative mapping of the current SPP3 Marketplace RFP into the schema.
- `provenance/simocracy-funding.json` — the five recorded funding decisions and allocation totals.
- `DESIGN-NOTES.md` — design rationale, threat model, scope boundaries, and source mapping.
- `VALIDATION.md` — structural validation results.
- `LICENSE` — MIT license.

## Design objective

The charter does not try to automate grant judgment. It makes the decision procedure attributable and reviewable.

> A third party should be able to determine which rules governed a material funding decision, which evidence supported its material findings, who exercised authority, where conflicts or disagreement existed, and what conditions govern challenge and delivery.

## Current ENS fit

The design is intentionally compatible with current ENS practice:

- SPP3 uses published rubrics and structured evaluation.
- The Marketplace RFP requires output-defined, dated, independently verifiable milestones.
- Committee recusals and quorum rules are explicit.
- The Marketplace RFP uses milestone-gated payment and on-chain traction evidence.
- ENS has separately experimented with AI-assisted grant screening and identified both useful screening capabilities and risks from evaluator gaming and overly agreeable models.

The schema encodes these practices rather than replacing them.

## Status

**Draft v0.1 — implementation artifact, not an adopted ENS policy.**

This package does not claim ratification by ENS DAO, endorsement by the SPP3 committee, or adoption by the ENS Foundation.

## Suggested review questions

1. Which fields are genuinely necessary for a material decision record?
2. Which fields should be public, selectively disclosed, or retained only for audit?
3. What monetary or risk threshold should trigger the full record?
4. Which parts of an AI evaluator manifest should be committed before review and disclosed after decisions?
5. Can the schema represent experimental grants without forcing false precision?
6. Can an accountability body verify milestones without becoming the substantive grant evaluator?

## Sources

- ENS SPP3 Marketplace RFP: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP submission timeline and rubric: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 cohort recommendation and committee process: https://discuss.ens.domains/t/ep-6-49-spp3-cohort-recommendation/22237
- ENS AI grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
