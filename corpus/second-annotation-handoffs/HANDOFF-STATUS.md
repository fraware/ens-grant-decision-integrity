# Second-annotation handoff status

Status: **BLOCKED pending human return of completed annotations.**

Engineering prepared source-only handoffs for the three cases fixed by `corpus/double-annotation-plan-2026-08-25.json`. No second annotation was fabricated. `review.doubleAnnotation` remains `false` on every selected case. Integration into `case.json` is blocked until a distinct human annotator returns completed handoffs that pass `scripts/second_annotation.py verify`.

Operator / annotator procedure: `ANNOTATOR-CHECKLIST.md` (this directory), `corpus/DOUBLE-ANNOTATION.md`, and the pre-outcome interpretation rules in `corpus/analysis-plan-addendum-2026-08-26.json`.

## Frozen handoffs (exact UTF-8 LF bytes)

Verified 2026-08-25 against the corresponding `case.json` via `scripts/second_annotation.py prepare` (regenerated frozen-package bytes must match these hashes). Working-tree CRLF corruption invalidates hashes; `corpus/**/*.json` is forced to LF via `.gitattributes`.

| Case directory | Handoff path | SHA-256 (exact UTF-8 LF bytes) | Bytes |
| --- | --- | --- | --- |
| `corpus/cases/spp3-namespace-2026/` | `spp3-namespace-2026.handoff.json` | `sha256:48047269447cf331ed76403773d8431bcb44fe39dd3ee3853fff5e555a4d4674` | 13655 |
| `corpus/cases/spp3-ethid-withdrawal-2026/` | `spp3-ethid-withdrawal-2026.handoff.json` | `sha256:8cce81fc95b9066aa1959cce0f89abb62170230841ebf2b4249b4a68c42e6f01` | 13334 |
| `corpus/cases/spp2-agora-budget-rejection-2025/` | `spp2-agora-budget-rejection-2025.handoff.json` | `sha256:74bd65b6f29e55836f6932b9a3b562d1efa7480086c1fcec4d6f1c6a9489d83a` | 13730 |

Hashes are over the exact frozen handoff file bytes (LF newlines). Do not reformat those source-only package files. The completed human response is a **copy** and is intentionally a different artifact; it must add the explicit `independenceAttestation` field described below before verification.

## Prepare commands used

```bash
python scripts/second_annotation.py prepare \
  corpus/cases/spp3-namespace-2026/case.json \
  --out corpus/second-annotation-handoffs/spp3-namespace-2026.handoff.json

python scripts/second_annotation.py prepare \
  corpus/cases/spp3-ethid-withdrawal-2026/case.json \
  --out corpus/second-annotation-handoffs/spp3-ethid-withdrawal-2026.handoff.json

python scripts/second_annotation.py prepare \
  corpus/cases/spp2-agora-budget-rejection-2025/case.json \
  --out corpus/second-annotation-handoffs/spp2-agora-budget-rejection-2025.handoff.json
```

Windows note: after pull, if local handoff or record JSON shows CRLF, re-run prepare (or `git add --renormalize corpus`) so LF bytes match declared hashes. Do not rewrite declared record hashes to match CRLF bytes.

## Human steps

See `ANNOTATOR-CHECKLIST.md`. Summary:

1. Deliver only the frozen handoff plus authorized source material. Do not expose primary classifications/rationales, reconstructed record values, validator findings, review notes, or computed metrics before the second annotation is frozen.
2. The second annotator copies the frozen handoff, uses a distinct `annotatorId`, covers the exact material field set, records elapsed time, and completes the classifications/source references.
3. In the completed copy, the human adds exactly:

   `"independenceAttestation": "I produced this annotation without consulting the withheld primary reconstruction materials before submission."`

   and leaves `independent=true` only if that statement is true. The frozen package does not contain this attestation key, so engineering cannot satisfy the new verifier merely by handing over an untouched template.
4. On return, verify without modifying the case (`second_annotation.py verify` — commands in the checklist). Verification requires the exact attestation text as well as the existing structural constraints.
5. Freeze the completed response and verified output, then integrate only the verified annotation object into `case.json` without editing the primary annotation. Only then set `review.doubleAnnotation=true`.
6. Compute raw classification agreement and Cohen's kappa on the frozen pair before reconciliation. Preserve disagreements.

## Explicit non-claims

- Handoff preparation does not prove human independence.
- The explicit attestation creates auditable evidence of what the annotator asserted; it still does not prove the annotator's actual information exposure.
- Integration is **BLOCKED** until all three human returns are verified.
- This status file is not a second annotation and does not count toward the double-annotation fraction.
