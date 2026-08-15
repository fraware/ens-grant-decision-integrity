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
- PASS — a failed eligibility rule cannot omit supporting evidence (`EVID004`).
- PASS — `risk` is rejected as an epistemic material-finding classification; the allowed classifications are `supported-fact`, `judgment`, `uncertainty`, and `unverified-claim`.
- PASS — material findings cannot be attributed to non-participating or recused evaluators (`EVAL003`).
- PASS — material disagreements cannot be attributed to non-participating or recused evaluators (`EVAL004`); a valid participating-evaluator disagreement is accepted.
- PASS — non-public evidence with neither a URI nor a content hash is surfaced as `EVID003` without forcing disclosure.
- PASS — non-public evidence with a retrievable URI remains usable without `EVID003`.
- PASS — adversarial suite rejects broken evidence references.
- PASS — adversarial suite rejects an eligible summary with failed eligibility rules.
- PASS — a public governing-policy URI must occur in the declared governing source set (`POL002`).
- PASS — the schema requires source mappings for mandate, eligibility, evaluation criteria, conflict rules, and decision procedure.
- PASS — each decision-surface source must occur in the declared governing source set (`POL003`).
- PASS — an in-round policy change must identify a prior version and that version cannot equal the active version (`POL004`).
- PASS — an in-round policy-change notice must occur in the declared source set (`POL005`).
- PASS — an in-round policy change must state whether prior evaluations were rerun.
- PASS — a record declaring `changeDuringReview=false` cannot retain stale change metadata (`POL006`); the canonical no-change record is accepted.
- PASS — a complete in-round policy-change record is accepted.
- PASS — adversarial suite rejects a recused evaluator still marked as participating.
- PASS — a conflict record cannot mark a known evaluator as recused when that evaluator's own state contradicts recusal (`COI009`).
- PASS — a recusal must identify the affected decision surface (`COI004`).
- PASS — a recusal must explicitly state whether substitution occurred (`COI005`).
- PASS — a substitute evaluator identifier must resolve (`REF107`).
- PASS — a valid recusal without substitution is accepted.
- PASS — a valid recusal with an active, non-recused substitute is accepted.
- PASS — adversarial suite rejects an adjudicated decision with an unresolved conflict.
- PASS — adversarial suite rejects a non-pending committee decision without participating human members.
- PASS — adversarial suite rejects adjudication without a defined factual/procedural correction path (`CHAL002`).
- PASS — an AI evaluator cannot materially inform the recommendation without participating (`AI008`).
- PASS — material AI use without an evaluator manifest fails as `AI001`.
- PASS — an empty evaluator manifest cannot satisfy schema provenance requirements.
- PASS — material AI use without a recorded submission deadline fails as `AI004`.
- PASS — a declared evaluator-manifest commitment time at or after the submission deadline fails as `AI005`.
- PASS — an AI-recommendation departure cannot be recorded without materially influential AI evaluation (`AI006`).
- PASS — `aiOverrideRationale` cannot remain populated when `aiRecommendationOverridden=false` (`AI009`).
- PASS — a pending decision cannot record an institutional departure from an AI recommendation (`AI010`).
- PASS — a valid pre-deadline AI provenance envelope is accepted.
- PASS — a valid finalized human departure from a materially influential AI recommendation is accepted.
- PASS — hard-screen ineligibility is represented separately from merit rejection.
- PASS — pending and deferred records cannot carry a positive award (`DEC013`).
- PASS — suspension requires substantive rationale and attributable findings.
- PASS — deferral requires a rationale without being treated as a merit judgment.
- PASS — retrospective finalized records are permitted.
- PASS — Marketplace example records the published August 5, 2026 23:59 UTC submission deadline.
- PASS — Marketplace example maps all seven published hard eligibility gates, including acknowledgment of the SPP3 Program Terms and Award Notice.
- PASS — Marketplace example preserves the published M1–M5 weights: `25% / 20% / 35% / 10% / 10%`.
- PASS — Marketplace example maps the public rules URI and all five normative decision surfaces to declared governing sources.
- PASS — Simocracy allocation arithmetic: `65 + 59 + 20 + 51 + 24 = 219`.
- PASS — AI cannot occupy a decision-authority type, consistent with `CHARTER.md`.
- PASS — AI materiality is represented against the grant recommendation, not the institutional decision.
- PASS — the generic `humanOverride` field is absent; AI-recommendation departures are explicit.
- PASS — commitment timing validation is scoped to the ordering of declared timestamps; v0.1 does not prove pre-deadline existence without an external timestamp or publication anchor.
- PASS — worked example is explicitly non-evaluative.

## CI contract

```bash
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_final_consistency.py
```

`python scripts/conformance.py --strict ...` intentionally fails the current worked example on `CHAL003` until a factual/procedural correction process is represented.
