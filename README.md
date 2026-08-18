# ENS Grant Decision Integrity

A draft Charter and machine-readable decision-record profile for making material ENS grant and service-provider decisions reconstructable.

The project originated in the Simocracy proposal **“No Black-Box Grants: Ratify the Rules Before SPP Is Absorbed.”** Five ENS Governance funding decisions allocated a cumulative **$219** to that proposal. v0.1 implements its first $200 work item: a Grants Charter and a machine-readable decision-record schema.

## What v0.1 provides

The profile records enough information for a third party to reconstruct the procedural basis of a material funding decision:

- the versioned public rules governing the review;
- eligibility results and evidence for failed gates;
- evaluation criteria, material findings, and evidence references;
- evaluator participation, disagreement, conflicts, recusals, and substitutions;
- the human-governed decision authority and decision state;
- a factual/procedural correction path;
- delivery conditions for funded awards;
- minimum provenance when AI materially informs a recommendation.

JSON Schema validates record structure. A separate conformance validator checks cross-field relations that JSON Schema alone cannot express.

## Repository

- `CHARTER.md` — normative decision-integrity requirements.
- `schema/grant-decision-record.schema.json` — JSON Schema Draft 2020-12 record format.
- `CONFORMANCE.md` — cross-field conformance rules and severity model.
- `scripts/conformance.py` — semantic conformance validator.
- `scripts/test_conformance.py` — adversarial and valid-edge tests.
- `scripts/test_final_consistency.py` — source-fidelity and cross-field regression tests.
- `examples/spp3-marketplace-rfp.example.json` — fictional, non-evaluative mapping of the ENS SPP3 Marketplace RFP.
- `provenance/simocracy-funding.json` — recorded Simocracy funding decisions.
- `DESIGN-NOTES.md` — design rationale, threat model, and scope boundaries.
- `VALIDATION.md` — validation contract and expected outcomes.
- `REVIEW-REQUEST.md` — focused review protocol.
- `RELEASE-INTEGRITY.md` — release-integrity procedure.

## Validation

Install the pinned development dependency and run the complete contract:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_final_consistency.py
```

The Marketplace example is intentionally pending. It should produce no conformance errors and one warning, `CHAL003`, which records that the reviewed public process artifacts do not identify a post-decision route for correcting factual or procedural errors. See `VALIDATION.md` for the full contract.

## ENS process mapping

The worked example maps the public SPP3 Marketplace process without evaluating any applicant. It records:

- all seven published hard eligibility conditions;
- the published M1–M5 weights: 25%, 20%, 35%, 10%, and 10%;
- the public rules and sources governing mandate, eligibility, evaluation criteria, conflict rules, and decision procedure;
- the published committee quorum and decision rule;
- milestone and traction-verification requirements.

The example is a dated snapshot of the published process. It is fictional, does not identify, score, recommend, or reject a real applicant, and does not need to be rewritten when the underlying RFP later reaches an award state. A later process change warrants a new example or version only if it changes the decision-integrity model.

## AI provenance boundary

When AI materially informs a grant recommendation, v0.1 requires a versioned evaluator manifest and records a minimum provenance envelope: model identity, human-review policy, commitment metadata, reveal state, and the application deadline used for the timing check.

The validator checks only that the declared commitment time precedes the declared submission deadline. v0.1 does not define canonical manifest serialization, commitment generation, an independently verifiable timestamp or publication anchor, proof verification, selective-disclosure proofs, or evaluator replay. It therefore does not prove that a commitment existed at the declared time or that the committed configuration was actually used.

## Scope

This project governs the integrity of the decision record. It does not determine which projects ENS should fund, replace substantive committee judgment, establish the truth of cited evidence, or create authority for AI systems to approve, reject, suspend, or release funding.

**Draft v0.1.** This artifact is not adopted ENS policy and does not claim endorsement by ENS DAO, the ENS Foundation, or the SPP3 committee.

## Sources

- ENS SPP3 Marketplace RFP: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP submission timeline and rubric: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 program authorization and committee model: https://discuss.ens.domains/t/social-spp3-program-authorization-and-committee-model/22086
- ENS AI grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
