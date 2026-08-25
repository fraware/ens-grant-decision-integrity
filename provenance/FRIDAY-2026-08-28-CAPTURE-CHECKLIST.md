# Friday 2026-08-28 capture checklist

Use after an authoritative public artifact exists. Do **not** invent status or financial fields beforehand.

## Pre-event freeze (engineering)

| Item | State |
| --- | --- |
| Aug 24 snapshot `provenance/simocracy-status-2026-08-24.json` | Must remain byte-unchanged |
| Funding index `provenance/simocracy-funding.json` | Must remain unchanged for continuity edits |
| Pre-event SHA record | Update local staging notes if `main` moved after `757d35e…`; do not rewrite Aug 24 |
| Template | `provenance/simocracy-status-2026-08-28.template.json` (not authoritative) |

Current `main` at local engineering refresh: record in `FRIDAY-CAPTURE-STATUS.md`.

## Axis A vs Axis B (required split)

| Axis | What to record | What not to infer |
| --- | --- | --- |
| **A — Decision status** | Exact platform vocabulary from the artifact (e.g. `provisional`, `ratified`) | Do not upgrade allocation → ratification → payment |
| **B — Financial evidence** | `paymentAuthorization` / `transfer` / `receipt` / `settlement` only with separate sources | Do not fill from Axis A alone; leave `null` until evidenced |

## Capture steps

1. Confirm the authoritative public URI/artifact and lawful retention of exact bytes.
2. Hash preserved bytes; record hash in the new dated snapshot (not in the Aug 24 file).
3. Copy the template to `provenance/simocracy-status-2026-08-28.json` (or the actual publication date) only when filling from evidence.
4. Populate Axis A from the platform vocabulary; leave Axis B null unless separately evidenced.
5. Record repository baseline SHA preceding the capture.
6. Do not edit `simocracy-status-2026-08-24.json` or invent continuity.

## Explicit blocked until evidence

- Authoritative Friday allocation/payment status vocabulary.
- Any non-null Axis B financial field without a cited separate source.
- Tagging or claiming “paid/funded/settled” from allocation text alone.
