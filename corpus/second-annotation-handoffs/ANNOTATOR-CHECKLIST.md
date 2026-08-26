# Human second-annotator checklist

This checklist is for the human who completes the three frozen handoffs under `corpus/second-annotation-handoffs/`. Engineering prepares and verifies packages; engineering must not fill classifications, copy the primary annotation, add the independence attestation, or set `independent=true` on your behalf.

## Deliverables (one completed file per case)

| Case | Frozen handoff (do not edit in place) | Return as |
| --- | --- | --- |
| Namespace award | `spp3-namespace-2026.handoff.json` | `spp3-namespace-2026.completed.json` |
| EthID withdrawal | `spp3-ethid-withdrawal-2026.handoff.json` | `spp3-ethid-withdrawal-2026.completed.json` |
| Agora budget rejection | `spp2-agora-budget-rejection-2025.handoff.json` | `spp2-agora-budget-rejection-2025.completed.json` |

Keep the frozen handoff bytes unchanged. Copy the file, fill the copy, and return the copy. The frozen source-only packages remain the byte-hashed artifacts recorded in `HANDOFF-STATUS.md`; the completed copy is a distinct human response artifact.

## What you receive

- Source inventory and authorized source material (links / redistributable bytes listed in the handoff).
- Fixed material field paths and `requiredForProfile` flags.
- Classification definitions and corpus merit / privacy / unknown-evidence boundaries.

## What you must not receive before freezing your annotation

- Primary annotation classifications or rationales.
- Reconstructed decision-record values from `record-*.json`.
- Validator findings, dispositions, review notes, or computed corpus metrics.

Public sources may reveal the historical outcome. Independence means reconstructing from sources without consulting the primary reconstruction package.

## How to fill `annotationSubmission`

1. Use a distinct `annotatorId` that is not the primary annotator ID.
2. Cover every material field in the handoff (same paths; do not add/remove fields).
3. Classify each field using exactly one class defined in the frozen handoff: `direct-source`, `derived`, `interpretive`, `unknown`, or `not-applicable`. Use `not-applicable` only when the field is outside the represented process/profile and provide a rationale, as required by the verifier.
4. Cite only source artifact IDs from the handoff inventory.
5. Record `elapsedMinutes` honestly as active time spent inspecting the supplied source set and producing the annotation submission. Exclude unrelated breaks, communication, engineering/package preparation, and post-submission reconciliation. This timing instruction standardizes second-annotation timing prospectively; it does not retroactively redefine the scope of previously recorded primary-annotation times.
6. Add the following key to the completed copy's `annotationSubmission` object and reproduce the value exactly:

   ```json
   "independenceAttestation": "I produced this annotation without consulting the withheld primary reconstruction materials before submission."
   ```

   The frozen blank handoff intentionally does **not** contain this key. Adding it to the completed copy is the deliberate human attestation step; engineering must not add it for you.
7. Set `independent=true` only if the attestation is true. If you consulted withheld primary materials before freezing your submission, stop and return the package unused; do not add the attestation and do not mark the annotation independent.

## Operator verify + integrate (after return)

Do not mark cases double-annotated until verify succeeds.

```bash
python scripts/second_annotation.py verify \
  corpus/cases/spp3-namespace-2026/case.json \
  corpus/second-annotation-handoffs/spp3-namespace-2026.completed.json \
  --out corpus/second-annotation-handoffs/spp3-namespace-2026.verified.json

python scripts/second_annotation.py verify \
  corpus/cases/spp3-ethid-withdrawal-2026/case.json \
  corpus/second-annotation-handoffs/spp3-ethid-withdrawal-2026.completed.json \
  --out corpus/second-annotation-handoffs/spp3-ethid-withdrawal-2026.verified.json

python scripts/second_annotation.py verify \
  corpus/cases/spp2-agora-budget-rejection-2025/case.json \
  corpus/second-annotation-handoffs/spp2-agora-budget-rejection-2025.completed.json \
  --out corpus/second-annotation-handoffs/spp2-agora-budget-rejection-2025.verified.json
```

The verifier requires a distinct annotator ID, `independent=true`, the exact attestation text above, complete fixed-field coverage, valid classifications, and valid source references. A successful verified output preserves the attestation separately from the case annotation object; the case schema itself remains unchanged.

Then, for each verified annotation (human review, not automatic merge):

1. Freeze both the completed response and the verified output before exposing the annotator to primary reconstruction materials.
2. Append only the verified `annotation` object to `case.json` `annotations` without editing the primary annotation.
3. Set `review.doubleAnnotation=true` only after the second annotation is frozen in the case.
4. Compute raw classification agreement and Cohen's kappa on the frozen pair **before** reconciliation.
5. Preserve disagreements; do not copy answers between annotators to improve kappa.
6. Re-run `python scripts/validate_corpus_cases.py` and `python scripts/study_status.py`.

Interpretation and reporting rules frozen before any second-annotation agreement result are in `../analysis-plan-addendum-2026-08-26.json`.

## Blockers / non-claims

- Integration remains **blocked** until all three human returns verify.
- An explicit attestation is stronger audit evidence than a pre-populated boolean, but tooling still cannot prove what the human saw or whether the human process was actually independent.
- Three completed cases satisfy the predeclared 25% minimum at the current corpus size, but that case count is too small to support a population-level reliability claim. Agreement statistics remain descriptive for these cases unless a larger independent-annotation sample is obtained.
- `elapsedMinutes` is an annotation-time observation, not a complete measure of source discovery, institutional administration, or total adoption cost.
- This checklist is not itself a second annotation and does not count toward the double-annotation fraction.
