# Allocation and funding-state provenance capture

This procedure records platform decision status and financial evidence without conflating allocation, ratification, payment authorization, transfer, receipt, settlement, institutional adoption, or completion of funded work.

## Friday 2026-08-28 checkpoint

Do not presuppose what the Friday event will establish. Capture the authoritative public state after it exists and preserve the exact status vocabulary used by the platform or decision artifact.

Before the checkpoint:

1. preserve the current repository baseline by exact Git commit SHA;
2. retain the dated `provenance/simocracy-status-2026-08-24.json` snapshot unchanged;
3. identify the canonical proposal and decision identifiers already recorded in `simocracy-funding.json`;
4. prepare source-artifact capture for any public status/decision page whose exact bytes can lawfully be retained.

After an authoritative artifact appears, add a **new dated snapshot**. Do not rewrite the August 24 snapshot to make history look continuous.

For each decision record:

- canonical decision identifier and source URI;
- publication/decision timestamp represented by the source;
- proposal or work-item identity;
- amount and denomination represented by the source;
- platform decision status exactly as represented by the source (for example `provisional` or `ratified` when those are the platform terms);
- payment-authorization evidence only if a separate source supports it;
- transfer evidence only if a transaction source supports it;
- receipt evidence only if recipient-side or equivalent evidence supports it;
- settlement evidence only if the applicable settlement condition is independently evidenced;
- repository baseline tag/commit preceding the event;
- capture timestamp and source-artifact content hash when exact bytes are preserved.

## Two-axis status model

Decision/procedural status and financial state are independent axes.

`decisionStatus` should preserve the authoritative platform term instead of translating it into a stronger project-defined state. `financialEvidence` should contain only separately evidenced propositions such as payment authorization, transfer, receipt, or settlement.

Examples of invalid inference:

- `allocated` → `ratified` without an authoritative ratification artifact;
- `ratified` → `payment-authorized` without a payment authorization;
- `payment-authorized` → `transferred` without transaction evidence;
- `transferred` → `received` without receipt evidence;
- `received` → `settled` without the applicable settlement evidence.

The repository may report that a proposition is **not evidenced in the captured artifact set**. It should not turn absence of repository evidence into a universal claim that the event did not occur.

## Current pre-Friday snapshot

`simocracy-status-2026-08-24.json` records the public funding page as observed on August 24: five proposal rounds totaling $219, with the first three rounds labeled `ratified` and the August 3 and August 4 rounds labeled `provisional`. That snapshot is decision-status evidence only. It contains no payment, transfer, receipt, or settlement evidence.

`provenance/pre-friday-checkpoint-2026-08-25.json` freezes the actual pre-event repository SHA (`757d35e2de7e113787d66166d736b9c740adaa3c` as of this checkpoint file), leaves `simocracy-status-2026-08-24.json` and `simocracy-funding.json` unchanged, and marks post-event Friday capture as **blocked until an authoritative artifact exists after 2026-08-28**. Do not invent a `simocracy-status-2026-08-28.json` (or any stronger financial state) before that artifact exists.

## Claim boundary

A funding-state record establishes only what the cited source supports. It does not establish the correctness of the funding decision, completion of work, endorsement of this repository, payment, receipt, or settlement unless those propositions have their own evidence.
