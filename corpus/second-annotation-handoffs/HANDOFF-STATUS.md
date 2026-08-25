# Second-annotation handoff status

Status: **BLOCKED pending human return of completed annotations.**

Engineering prepared source-only handoffs for the three cases fixed by `corpus/double-annotation-plan-2026-08-25.json`. No second annotation was fabricated. `review.doubleAnnotation` remains `false` on every selected case. Integration into `case.json` is blocked until a distinct human annotator returns completed handoffs that pass `scripts/second_annotation.py verify`.

## Frozen handoffs (exact UTF-8 LF bytes)

| Case directory | Handoff path | SHA-256 (exact UTF-8 LF bytes) | Bytes |
| --- | --- | --- | --- |
| `corpus/cases/spp3-namespace-2026/` | `spp3-namespace-2026.handoff.json` | `sha256:48047269447cf331ed76403773d8431bcb44fe39dd3ee3853fff5e555a4d4674` | 13655 |
| `corpus/cases/spp3-ethid-withdrawal-2026/` | `spp3-ethid-withdrawal-2026.handoff.json` | `sha256:8cce81fc95b9066aa1959cce0f89abb62170230841ebf2b4249b4a68c42e6f01` | 13334 |
| `corpus/cases/spp2-agora-budget-rejection-2025/` | `spp2-agora-budget-rejection-2025.handoff.json` | `sha256:74bd65b6f29e55836f6932b9a3b562d1efa7480086c1fcec4d6f1c6a9489d83a` | 13730 |

Hashes are over the exact committed/handoff file bytes as prepared by `scripts/second_annotation.py` (LF newlines). Do not reformat JSON before hashing or verifying.

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

Windows note: `corpus/**/*.json` is forced to LF via `.gitattributes` (`text eol=lf`) so `core.autocrlf=true` checkouts do not break CORP020 snapshot hashes. After pulling this policy, run `git add --renormalize corpus` (or re-clone/checkout) if local working-tree records still show CRLF. Do not rewrite declared record hashes to match CRLF bytes.

## Human steps (from `corpus/DOUBLE-ANNOTATION.md`)

1. Deliver only the frozen handoff plus authorized source material (source inventory already listed in the handoff). Do not expose primary classifications/rationales, reconstructed record values, validator findings, review notes, or computed metrics before the second annotation is frozen.
2. Second annotator uses a distinct `annotatorId`, covers the exact material field set, records elapsed time, and sets `independent=true` only if the independence boundary was respected.
3. On return, verify without modifying the case:

```bash
python scripts/second_annotation.py verify \
  corpus/cases/<case>/case.json \
  corpus/second-annotation-handoffs/<case>.completed.json \
  --out corpus/second-annotation-handoffs/<case>.verified.json
```

4. Freeze the verified annotation, then integrate into `case.json` without editing the primary annotation. Only then set `review.doubleAnnotation=true`.
5. Compute raw classification agreement and Cohen’s kappa on the frozen pair before reconciliation. Preserve disagreements.

## Explicit non-claims

- Handoff preparation does not prove human independence.
- Integration is **BLOCKED** until all three human returns are verified.
- This status file is not a second annotation and does not count toward the double-annotation fraction.
