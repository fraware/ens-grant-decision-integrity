# Contributing

The project is optimized for narrow, evidence-backed improvements to grant decision integrity.

## Preferred contributions

- identify a real failure mode in the Charter;
- remove a requirement that adds process cost without improving accountability;
- add a missing invariant with a concrete motivating case;
- improve schema interoperability without weakening semantics;
- contribute a non-evaluative mapping from a public grant process into the schema;
- report implementation friction from an actual review workflow.

## Review standard

A proposed change should state:

1. the decision surface affected;
2. the failure mode or operational cost;
3. the evidence or concrete scenario;
4. the smallest change that resolves it;
5. any new privacy, security, or governance trade-off introduced.

Please avoid broad governance manifestos or unsupported claims of objectivity. The artifact governs decision integrity; it does not determine which projects should receive funding. The Charter is a draft proposal, not adopted ENS policy.

## Validation before proposing a change

Run the validation contract that covers the surfaces you touch. For changes that could affect any of the shipped profiles, run the full local suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -r phase2/requirements.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_regressions.py
python -m pytest phase2/tests
python scripts/test_schema_02.py
python -m pytest projection/tests
```

Expected Marketplace outcome: no conformance errors; warning set exactly `{CHAL003}`.

A contribution that intentionally changes a conformance rule should update the corresponding adversarial or regression test and explain the new guarantee or trade-off. See `VALIDATION.md` and `CONFORMANCE.md`.

## Sensitive reports

Do not open a public issue for validator bypasses, redaction leaks, credential exposure, or release-integrity ambiguity. Use `SECURITY.md`.
