# Validation

The repository validates both representation and institutional conformance.

## Required checks

- PASS — schema is valid JSON Schema Draft 2020-12.
- PASS — worked example is structurally valid.
- PASS — worked example has no semantic conformance errors.
- EXPECTED WARNING — `CHAL003`: the public Marketplace RFP artifacts reviewed on 2026-08-15 do not define a post-decision factual/procedural correction process.
- PASS — adversarial suite rejects a pending record with a decision timestamp.
- PASS — adversarial suite rejects approval without delivery conditions.
- PASS — adversarial suite rejects a `supported-fact` without evidence.
- PASS — adversarial suite rejects broken evidence references.
- PASS — adversarial suite rejects an eligible summary with failed eligibility rules.
- PASS — adversarial suite rejects a recused evaluator still marked as participating.
- PASS — adversarial suite rejects a finalized decision with an unresolved conflict.
- PASS — adversarial suite rejects a final committee decision without participating human members.
- PASS — adversarial suite rejects finalization without a defined factual/procedural correction path (`CHAL002`).
- PASS — materially used automated evaluation without an evaluator manifest is surfaced.
- PASS — Simocracy allocation arithmetic: `65 + 59 + 20 + 51 + 24 = 219`.
- PASS — unilateral automated funding authority is prohibited by `CHARTER.md` and excluded from typed decision-authority values.
- PASS — commit–reveal boundary is explicitly scoped as integrity evidence, not proof of substantive correctness.
- PASS — worked example is explicitly non-evaluative.

## CI contract

```bash
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
```

`python scripts/conformance.py --strict ...` intentionally fails the current worked example until the public correction-path gap represented by `CHAL003` is resolved.
