# ENS Grant Decision Integrity — v0.1

A compact governance artifact for making material ENS grant decisions inspectable with human decision authority preserved.

This package implements the first $200 work item in the Simocracy proposal **“No Black-Box Grants: Ratify the Rules Before SPP Is Absorbed”**: a draft Grants Charter and a machine-readable decision-record schema. Five ENS Governance funding decisions allocated a cumulative **$219** to the proposal.

## Included

- `CHARTER.md` — draft institutional charter for grant decision integrity.
- `schema/grant-decision-record.schema.json` — JSON Schema (Draft 2020-12) for a versioned decision record.
- `CONFORMANCE.md` — cross-field conformance rules and severity model.
- `scripts/conformance.py` — semantic conformance validator.
- `scripts/test_conformance.py` — adversarial tests for specified invalid states and valid edge cases.
- `examples/spp3-marketplace-rfp.example.json` — illustrative, non-evaluative mapping of the current SPP3 Marketplace RFP.
- `provenance/simocracy-funding.json` — the five recorded funding decisions and allocation totals.
- `DESIGN-NOTES.md` — design rationale, threat model, scope boundaries, and source mapping.
- `RELEASE-INTEGRITY.md` — release-identity and archive-integrity procedure.
- `VALIDATION.md` — validation contract and expected checks.
- `LICENSE` — MIT license.

## Design objective

The Charter does not automate grant judgment. It makes the decision procedure attributable and reviewable.

> A third party should be able to determine which rules governed a material funding decision, which evidence supported its material findings, who exercised authority, where conflicts or disagreement existed, and which conditions govern challenge and delivery.

## Two-layer validation

A structurally valid record can still contain cross-field inconsistencies that defeat the Charter's guarantees. v0.1 therefore uses two validation layers:

1. **JSON Schema** checks types, required fields, allowed states, and local conditional constraints.
2. **Semantic conformance** checks cross-references and decision-integrity relations across the record.

The semantic layer detects, among other cases:

- a `supported-fact` without evidence;
- dangling evidence, evaluator, or finding references;
- partially specified criterion weights or weights that do not sum to `1.0`;
- a pending record that claims a decision timestamp;
- an eligibility summary inconsistent with its underlying rules;
- an approval, rejection, or suspension without attributable material findings and rationale;
- an approved or suspended award without a positive amount or delivery conditions;
- a recused evaluator still marked as participating;
- an adjudicated decision with an unresolved material conflict;
- a non-pending committee decision that omits participating human members, quorum, or decision rule;
- an adjudicated decision without a defined factual or procedural correction path;
- material AI use without the minimum evaluator-manifest provenance envelope;
- a missing submission deadline when AI materially informs a recommendation;
- an evaluator manifest committed at or after the application deadline;
- an AI-recommendation departure recorded without materially influential AI evaluation.

The profile also represents an eligibility hard-screen separately from a merit rejection. This matches the Marketplace RFP's published rule that an ineligible application is returned without scoring.

Run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
```

Use `--strict` when warnings should also fail validation.

## AI provenance boundary

When AI materially informs a grant recommendation, v0.1 requires a versioned evaluator manifest and a cryptographic commitment recorded strictly before the submission deadline. The record captures the minimum provenance envelope: manifest version, model identity, human-review policy, commitment metadata, and reveal state.

v0.1 does **not** define manifest serialization, commitment generation, proof verification, selective-disclosure proofs, or evaluator replay. A conforming record therefore establishes declared timing and cross-field consistency; it does not prove that a committed evaluator configuration actually ran or that its judgment was correct.

## Current ENS fit

The design maps directly onto current ENS practices:

- SPP3 uses published eligibility rules, rubrics, and a named committee process.
- The Marketplace RFP requires output-defined, independently verifiable milestones.
- The SPP3 committee model defines quorum and voting rules.
- The Marketplace RFP uses milestone-gated payment and independently verifiable traction evidence.
- ENS has separately tested AI-assisted grant screening and identified both useful screening capabilities and risks from prompt gaming and model agreeableness.

The worked Marketplace RFP example records one unresolved documentation question without inferring an answer: the reviewed public artifacts do not identify a post-decision process for correcting factual errors or procedural deviations. The example sets `challenge.processDefined=false`, which produces warning `CHAL003` for the pending record. It does not assert that no internal or unpublished process exists, and it does not propose changing the rules of the active review.

## Status

**Draft v0.1 — implementation artifact, not adopted ENS policy.**

This package does not claim ratification by ENS DAO, endorsement by the SPP3 committee, or adoption by the ENS Foundation.

## Suggested review questions

1. Which fields are necessary for a material decision record?
2. Which fields should be public, selectively disclosed, or retained only for audit?
3. Should v0.1 define a formal public projection of a confidential canonical record, or leave projection semantics to the adopting program?
4. What value or risk threshold should trigger the full record?
5. Is the minimum AI provenance envelope sufficient to make the pre-deadline commitment rule auditable without importing the later full evaluator-manifest protocol?
6. Can the schema represent experimental grants without forcing false precision?
7. Can an accountability body verify milestones without acquiring substantive grant-selection authority?
8. Which conformance rules would create disproportionate operational cost in an actual ENS review?
9. Does the existing SPP3 process already provide a factual/procedural correction route that the reviewed Marketplace RFP artifacts do not identify? If so, how should the record represent it?

## Sources

- ENS SPP3 Marketplace RFP: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP submission timeline and rubric: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 program authorization and committee model: https://discuss.ens.domains/t/social-spp3-program-authorization-and-committee-model/22086
- ENS AI grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
