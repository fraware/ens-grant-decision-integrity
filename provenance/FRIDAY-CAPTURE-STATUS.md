# Friday 2026-08-28 capture status

**As of engineering refresh:** 2026-08-25 (local notes; post-event capture still blocked)  
**Current `main` SHA (local = `origin/main`):** `8728f9848673b19e349870b7e89fff1d97d8eef0`  
**Historical pre-event checkpoint file:** `provenance/pre-friday-checkpoint-2026-08-25.json` (frozen at `757d35e2de7e113787d66166d736b9c740adaa3c` — leave that file's recorded baseline as historical; do not rewrite it to imply a later freeze was the original pre-event SHA)  
**Capture template (not evidence):** `provenance/simocracy-status-2026-08-28.template.json`  
**Operator checklist:** `provenance/FRIDAY-2026-08-28-CAPTURE-CHECKLIST.md`

## Completed now

- Pre-event repository SHA and validation run recorded in the dated checkpoint (`757d35e…`).
- Local staging note updated to current `main` `8728f98…` so operators know main moved after the original freeze without inventing Friday outcomes.
- `provenance/simocracy-status-2026-08-24.json` left unchanged (byte hash matches `HEAD`).
- `provenance/simocracy-funding.json` left unchanged.
- Two-axis capture rule restated in `ALLOCATION-CAPTURE.md` and the Friday checklist (Axis A decision vocabulary vs Axis B financial evidence).
- Empty/null financial fields in the template only; no authoritative `simocracy-status-2026-08-28.json` invented.

## Blocked (external)

Post-event capture of `provenance/simocracy-status-2026-08-28.json` (or the actual authoritative publication date) is **blocked** until an authoritative public Friday artifact exists after 2026-08-28.

Do not invent:

- Friday decision/status vocabulary;
- payment authorization, transfer, receipt, or settlement fields;
- continuity edits to the August 24 snapshot.

When the artifact exists, follow `ALLOCATION-CAPTURE.md` and `FRIDAY-2026-08-28-CAPTURE-CHECKLIST.md`: preserve exact bytes when lawful, write a new dated snapshot from the template, keep Axis A and Axis B separate.
