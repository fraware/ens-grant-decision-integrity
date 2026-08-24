# Allocation provenance capture

This procedure records funding-allocation evidence without conflating a decision to allocate with payment, settlement, receipt, institutional adoption, or completion of the funded work.

## Friday 2026-08-28 checkpoint

The repository state immediately before the allocation event SHOULD be preserved by exact Git commit SHA and release tag. The allocation record MUST be added only after an authoritative public decision artifact exists.

For each allocation event record:

- canonical decision identifier and source URI;
- publication/decision timestamp represented by the source;
- proposal or work-item identity;
- amount and denomination represented by the source;
- recipient identity exactly as represented by the source;
- decision text or rationale when publicly available;
- allocation status;
- payment/settlement status as a separate field;
- independent receipt evidence only if separately available;
- repository baseline tag and commit SHA that preceded the event;
- capture timestamp and source-artifact SHA-256 where the source bytes are preserved.

## Status vocabulary

Use narrow status terms:

- `allocated` — an authoritative decision artifact allocates an amount;
- `payment-authorized` — a separate authoritative artifact authorizes payment;
- `transferred` — transaction evidence shows a transfer occurred;
- `received` — recipient-side or equivalent evidence establishes receipt;
- `settled` — the applicable settlement condition is evidenced.

Do not infer a later state from an earlier state. In particular, `allocated` MUST NOT be rewritten as `paid`, `received`, `funded`, or `settled` without separate evidence.

## Claim boundary

An allocation record establishes only what the cited source supports. It does not establish the correctness of the decision, completion of work, ENS endorsement of this repository, or payment settlement unless those propositions have their own evidence.
