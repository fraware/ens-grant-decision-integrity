# ENS Grant Decision Integrity — v0.1

A compact, vendor-neutral governance artifact for making material ENS grant decisions inspectable without delegating final authority to automated systems.

This package implements the first funded tranche of the Simocracy proposal **“No Black-Box Grants: Ratify the Rules Before SPP Is Absorbed.”** Five ENS Governance funding decisions allocated a cumulative **$219** to the proposal. The first proposed tranche was $200 for a draft Grants Charter and a machine-readable decision-record schema.

## Included

- `CHARTER.md` — draft institutional charter for grant decision integrity.
- `schema/grant-decision-record.schema.json` — JSON Schema (Draft 2020-12) for a versioned decision record.
- `CONFORMANCE.md` — machine-checkable cross-field invariants and severity model.
- `scripts/conformance.py` — semantic conformance validator.
- `scripts/test_conformance.py` — adversarial negative tests proving invalid institutional states are rejected.
- `examples/spp3-marketplace-rfp.example.json` — illustrative, non-evaluative mapping of the current SPP3 Marketplace RFP.
- `provenance/simocracy-funding.json` — the five recorded funding decisions and allocation totals.
- `DESIGN-NOTES.md` — design rationale, threat model, scope boundaries, and source mapping.
- `VALIDATION.md` — validation contract and expected checks.
- `LICENSE` — MIT license.

## Design objective

The charter does not try to automate grant judgment. It makes the decision procedure attributable and reviewable.

> A third party should be able to determine which rules governed a material funding decision, which evidence supported its material findings, who exercised authority, where conflicts or disagreement existed, and what conditions govern challenge and delivery.

## Two-layer validation

A structurally valid JSON document can still encode a broken governance state. v0.1 therefore uses two validation layers:

1. **JSON Schema** checks types, required fields, allowed states, and local conditional constraints.
2. **Semantic conformance** checks cross-references and institutional invariants across the record.

The semantic layer rejects, among other cases:

- a `supported-fact` without evidence;
- dangling evidence, evaluator, or finding references;
- criterion weights that are partial or do not sum to `1.0`;
- a pending record that claims a decision timestamp;
- an eligibility summary inconsistent with its underlying rules;
- approval or rejection without attributable material findings and rationale;
- an approved award without a positive amount or delivery conditions;
- a recused evaluator still marked as participating;
- a finalized decision with an unresolved material conflict;
- a final committee decision that omits participating human members, quorum, or decision rule;
- a final decision without a typed human-governed authority;
- inconsistent evaluator-manifest commitment/reveal states;
- a finalized decision with no defined factual or procedural correction path.

Run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
```

Use `--strict` when warnings should also fail validation.

## Current ENS fit

The design is intentionally compatible with current ENS practice:

- SPP3 uses published rubrics and structured evaluation.
- The Marketplace RFP requires output-defined, independently verifiable milestones.
- Committee conflict and quorum rules are explicit.
- The Marketplace RFP uses milestone-gated payment and on-chain traction evidence.
- ENS has separately experimented with automated grant screening and identified useful screening capabilities alongside evaluator-gaming and agreeableness risks.

The worked Marketplace RFP example also exposes one current public-process gap: the reviewed RFP artifacts do not specify a post-decision factual or procedural correction path. The example records `challenge.processDefined=false`, producing warning `CHAL003` while the decision remains pending. A finalized record would fail conformance until the gap is resolved.

## Status

**Draft v0.1 — implementation artifact, not an adopted ENS policy.**

This package does not claim ratification by ENS DAO, endorsement by the SPP3 committee, or adoption by the ENS Foundation.

## Suggested review questions

1. Which fields are genuinely necessary for a material decision record?
2. Which fields should be public, selectively disclosed, or retained only for audit?
3. What monetary or risk threshold should trigger the full record?
4. Which evaluator-manifest elements should be committed before review and disclosed after decisions?
5. Can the schema represent experimental grants without forcing false precision?
6. Can an accountability body verify milestones without acquiring substantive grant-selection authority?
7. Which semantic conformance rules would create unacceptable operational friction in a real ENS review?
8. Should ENS define an explicit factual/procedural correction mechanism before the Marketplace RFP decision is finalized?

## Sources

- ENS SPP3 Marketplace RFP: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP submission timeline and rubric: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 cohort recommendation and committee process: https://discuss.ens.domains/t/ep-6-49-spp3-cohort-recommendation/22237
- ENS automated grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
