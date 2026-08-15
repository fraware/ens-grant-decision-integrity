# ENS Grant Decision Integrity — v0.1

A compact governance artifact for making material ENS grant decisions inspectable with human decision authority preserved.

This package implements the first $200 work item in the Simocracy proposal **“No Black-Box Grants: Ratify the Rules Before SPP Is Absorbed”**: a draft Grants Charter and a machine-readable decision-record schema. Five ENS Governance funding decisions allocated a cumulative **$219** to the proposal.

## Included

- `CHARTER.md` — draft institutional charter for grant decision integrity.
- `schema/grant-decision-record.schema.json` — JSON Schema (Draft 2020-12) for a versioned decision record.
- `CONFORMANCE.md` — cross-field conformance rules and severity model.
- `scripts/conformance.py` — semantic conformance validator.
- `scripts/test_conformance.py` — adversarial tests for specified invalid states and valid edge cases.
- `scripts/test_final_consistency.py` — focused source-fidelity and cross-field regression checks from the final hardening pass.
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
- a failed eligibility gate without supporting evidence;
- use of `risk` as an epistemic classification instead of `supported-fact`, `judgment`, `uncertainty`, or `unverified-claim`;
- dangling evidence, evaluator, or finding references;
- an unattributed disagreement or one attributed to a non-participating or recused evaluator;
- non-public evidence with neither a URI nor a content hash;
- partially specified criterion weights or weights that do not sum to `1.0`;
- a public governing-policy URI outside the declared governing source set;
- a missing or undeclared source for mandate, eligibility, evaluation criteria, conflict rules, or decision procedure;
- an in-round policy change with incomplete prior-version, change-notice, or rerun traceability;
- a pending record that claims a decision timestamp;
- an eligibility summary inconsistent with its underlying rules;
- an adjudicated decision recorded before its supporting eligibility check;
- a non-pending decision recorded after the record's own last-update timestamp;
- a pending or deferred record that claims a positive award;
- an approval, rejection, or suspension without attributable material findings and rationale;
- an approved or suspended award without a positive amount or delivery conditions;
- a recused evaluator still marked as participating;
- a conflict record that claims a known evaluator was recused when the evaluator state contradicts that claim;
- a recusal that omits the affected decision surface or substitution state;
- a substitute evaluator reference that does not resolve to an active, non-recused evaluator;
- an adjudicated decision with an unresolved material conflict;
- a committee decision that omits participating human members, quorum, or decision rule, without conflating an advisory committee evaluator with the final decision authority;
- an adjudicated decision without a defined factual or procedural correction path;
- an active challenge without a defined process, a pending decision claiming a post-decision challenge, or a resolved challenge without a resolution;
- material AI use without the minimum evaluator-manifest provenance envelope;
- a missing submission deadline when AI materially informs a recommendation;
- a declared evaluator-manifest commitment time at or after the application deadline;
- an AI evaluator claiming material influence without participation;
- an AI-recommendation departure recorded without materially influential AI evaluation;
- stale AI-departure rationale when no departure is recorded;
- an institutional AI-recommendation departure recorded while the decision is still pending.

The profile also represents an eligibility hard-screen separately from a merit rejection. This matches the Marketplace RFP's published rule that an ineligible application is returned without scoring.

Run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_final_consistency.py
```

Use `--strict` when warnings should also fail validation.

## Fixed-policy traceability

For an active review, the record identifies a public governing-policy URI and maps five normative decision surfaces—mandate, eligibility, evaluation criteria, conflict rules, and decision procedure—to URIs in the declared governing source set.

If policy changes during review, the record additionally identifies the prior version, the disclosed change record, and whether evaluations already completed under the prior version were rerun. v0.1 checks this declared lineage; it does not determine whether the policy itself is legitimate or whether an evaluator interpreted it correctly.

## AI provenance boundary

When AI materially informs a grant recommendation, v0.1 requires a versioned evaluator manifest and records commitment metadata whose declared `committedAt` value must precede the submission deadline. The record captures the minimum provenance envelope: manifest version, model identity, human-review policy, commitment metadata, and reveal state.

v0.1 does **not** define manifest serialization, commitment generation, an external timestamp/publication anchor, proof verification, selective-disclosure proofs, or evaluator replay. The current validator therefore establishes only the internal ordering of declared timestamps and cross-field consistency. It does not prove that the commitment existed before the deadline, that a committed evaluator configuration actually ran, or that its judgment was correct. Independently verifiable anchoring belongs to the later evaluator-manifest/commit–reveal protocol.

## Current ENS fit

The design maps directly onto current ENS practices:

- SPP3 uses published eligibility rules, rubrics, and a named committee process.
- The Marketplace RFP requires output-defined, independently verifiable milestones.
- The SPP3 committee model defines quorum and voting rules.
- The Marketplace RFP uses milestone-gated payment and independently verifiable traction evidence.
- ENS has separately tested AI-assisted grant screening and identified both useful screening capabilities and risks from prompt gaming and model agreeableness.

The worked Marketplace RFP example maps all seven published hard eligibility gates, preserves the published M1–M5 weights, and maps the public governing-policy URI and each of the five normative decision surfaces to the reviewed public sources. It also records one unresolved documentation question without inferring an answer: the reviewed public artifacts do not identify a post-decision process for correcting factual errors or procedural deviations. The example sets `challenge.processDefined=false`, which produces warning `CHAL003` for the pending record. It does not assert that no internal or unpublished process exists, and it does not propose changing the rules of the active review.

## Status

**Draft v0.1 — implementation artifact, not adopted ENS policy.**

This package does not claim ratification by ENS DAO, endorsement by the SPP3 committee, or adoption by the ENS Foundation.

## Suggested review questions

1. Which fields are necessary for a material decision record?
2. Which fields should be public, selectively disclosed, or retained only for audit?
3. Should v0.1 define a formal public projection of a confidential canonical record, or leave projection semantics to the adopting program?
4. Is the five-surface governing-policy map sufficient to reconstruct the rules of a review without duplicating the policy text?
5. What value or risk threshold should trigger the full record?
6. Does v0.1 stop at the correct boundary for AI commitment metadata, and what independently verifiable anchor should the later commit–reveal protocol require to establish pre-deadline existence?
7. Can the schema represent experimental grants without forcing false precision?
8. Can an accountability body verify milestones without acquiring substantive grant-selection authority?
9. Which conformance rules would create disproportionate operational cost in an actual ENS review?
10. Does the existing SPP3 process already provide a factual/procedural correction route that the reviewed Marketplace RFP artifacts do not identify? If so, how should the record represent it?

## Sources

- ENS SPP3 Marketplace RFP: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP submission timeline and rubric: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 program authorization and committee model: https://discuss.ens.domains/t/social-spp3-program-authorization-and-committee-model/22086
- ENS AI grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
