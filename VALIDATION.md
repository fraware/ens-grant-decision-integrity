# Validation

The repository checks structural validity and the v0.1 cross-field conformance profile.

## Required checks

- PASS — schema is valid JSON Schema Draft 2020-12.
- PASS — worked example is structurally valid.
- PASS — worked example has no conformance errors.
- EXPECTED WARNING — `CHAL003`: no factual/procedural correction process is recorded in the worked example; the reviewed public governing artifacts do not identify one.
- PASS — adversarial suite rejects a pending record with a decision timestamp.
- PASS — adversarial suite rejects approval without delivery conditions.
- PASS — adversarial suite rejects a `supported-fact` without evidence.
- PASS — adversarial suite rejects broken evidence references.
- PASS — adversarial suite rejects an eligible summary with failed eligibility rules.
- PASS — adversarial suite rejects a recused evaluator still marked as participating.
- PASS — adversarial suite rejects an adjudicated decision with an unresolved conflict.
- PASS — adversarial suite rejects a non-pending committee decision without participating human members.
- PASS — adversarial suite rejects adjudication without a defined factual/procedural correction path (`CHAL002`).
- PASS — materially used AI evaluation without an evaluator manifest is surfaced as `AI001`.
- PASS — hard-screen ineligibility is represented separately from merit rejection.
- PASS — retrospective finalized records are permitted.
- PASS — Simocracy allocation arithmetic: `65 + 59 + 20 + 51 + 24 = 219`.
- PASS — AI cannot occupy a decision-authority type, consistent with `CHARTER.md`.
- PASS — commit–reveal is scoped as configuration-integrity evidence, not proof that a configuration was used or that a judgment was correct.
- PASS — worked example is explicitly non-evaluative.

## CI contract

```bash
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
```

`python scripts/conformance.py --strict ...` intentionally fails the current worked example on `CHAL003` until a factual/procedural correction process is represented.
