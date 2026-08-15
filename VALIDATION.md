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
- PASS — non-public evidence with neither a URI nor a content hash is surfaced as `EVID003` without forcing disclosure.
- PASS — non-public evidence with a retrievable URI remains usable without `EVID003`.
- PASS — adversarial suite rejects broken evidence references.
- PASS — adversarial suite rejects an eligible summary with failed eligibility rules.
- PASS — adversarial suite rejects a recused evaluator still marked as participating.
- PASS — adversarial suite rejects an adjudicated decision with an unresolved conflict.
- PASS — adversarial suite rejects a non-pending committee decision without participating human members.
- PASS — adversarial suite rejects adjudication without a defined factual/procedural correction path (`CHAL002`).
- PASS — material AI use without an evaluator manifest fails as `AI001`.
- PASS — an empty evaluator manifest cannot satisfy schema provenance requirements.
- PASS — material AI use without a recorded submission deadline fails as `AI004`.
- PASS — an evaluator-manifest commitment at or after the submission deadline fails as `AI005`.
- PASS — an AI-recommendation departure cannot be recorded without materially influential AI evaluation (`AI006`).
- PASS — a valid pre-deadline AI provenance envelope is accepted.
- PASS — a valid human departure from a materially influential AI recommendation is accepted.
- PASS — hard-screen ineligibility is represented separately from merit rejection.
- PASS — suspension requires substantive rationale and attributable findings.
- PASS — deferral requires a rationale without being treated as a merit judgment.
- PASS — retrospective finalized records are permitted.
- PASS — Marketplace example records the published August 5, 2026 23:59 UTC submission deadline.
- PASS — Simocracy allocation arithmetic: `65 + 59 + 20 + 51 + 24 = 219`.
- PASS — AI cannot occupy a decision-authority type, consistent with `CHARTER.md`.
- PASS — AI materiality is represented against the grant recommendation, not the institutional decision.
- PASS — the generic `humanOverride` field is absent; AI-recommendation departures are explicit.
- PASS — commitment semantics are scoped as configuration-integrity evidence, not proof that a configuration was executed or that a judgment was correct.
- PASS — worked example is explicitly non-evaluative.

## CI contract

```bash
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
```

`python scripts/conformance.py --strict ...` intentionally fails the current worked example on `CHAL003` until a factual/procedural correction process is represented.
