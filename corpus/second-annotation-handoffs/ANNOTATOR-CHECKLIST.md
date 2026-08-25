# Human second-annotator checklist

This checklist is for the human who completes the three frozen handoffs under `corpus/second-annotation-handoffs/`. Engineering prepares and verifies packages; engineering must not fill classifications, copy the primary annotation, or set `independent=true` on your behalf.

## Deliverables (one completed file per case)

| Case | Frozen handoff (do not edit in place) | Return as |
| --- | --- | --- |
| Namespace award | `spp3-namespace-2026.handoff.json` | `spp3-namespace-2026.completed.json` |
| EthID withdrawal | `spp3-ethid-withdrawal-2026.handoff.json` | `spp3-ethid-withdrawal-2026.completed.json` |
| Agora budget rejection | `spp2-agora-budget-rejection-2025.handoff.json` | `spp2-agora-budget-rejection-2025.completed.json` |

Keep the frozen handoff bytes unchanged. Copy the file, fill the copy, and return the copy.

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
3. Classify each field using only the allowed classes (`direct-source`, `derived`, `interpretive`, `unknown`).
4. Cite only source artifact IDs from the handoff inventory.
5. Record elapsed minutes honestly.
6. Set `independent=true` only if you did not consult withheld primary materials before submission. If you did consult them, stop and return the package unused; do not mark independent.

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

Then, for each verified annotation (human review, not automatic merge):

1. Append the verified annotation object to `case.json` `annotations` without editing the primary annotation.
2. Set `review.doubleAnnotation=true` only after the second annotation is frozen in the case.
3. Compute raw classification agreement and Cohen's kappa on the frozen pair **before** reconciliation.
4. Preserve disagreements; do not copy answers between annotators to improve kappa.
5. Re-run `python scripts/validate_corpus_cases.py` and `python scripts/study_status.py`.

## Blockers / non-claims

- Integration remains **blocked** until all three human returns verify.
- Tooling cannot prove the human process was independent.
- This checklist is not itself a second annotation and does not count toward the double-annotation fraction.
