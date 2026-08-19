# Phase II administrative burden

This note records the operational cost of constructing one fictional public retrospective bundle (`examples/retrospective-public.bundle.json`). It is evidence for proportionality decisions, not a reason to auto-tighten v0.1 checks.

## What constructing the example required

1. **Manifest authoring** — Write a versioned evaluator manifest with `programId`, `roundId`, and `applicationDeadline` bound to the illustrative round. Keep sensitive operational detail out of the public envelope until reveal policy allows it.

2. **Commitment** — Generate a 32-byte CSPRNG salt, compute the domain-separated SHA-256 digest over RFC 8785 JCS bytes, and publish only the envelope (no salt, no hidden prompt text).

3. **Anchor profile selection** — Choose `rekor-v1` for production Sigstore Rekor or `rekor-v1-recorded-fixture` for tests and the public example. Retain offline-verifiable receipt material (hashedrekord body, signed entry timestamp, Merkle inclusion proof, signed checkpoint). Pin the trust root; do not treat a live `/api/v1/log/publicKey` response as the root.

4. **Run attestation** — Generate an Ed25519 test key, sign an in-toto Statement v1 + DSSE envelope over the custom run predicate, and retain the public key for verification.

5. **Replay** — Compute deterministic layer snapshots, record an honest `not-replayable` outcome for the hosted-generation layer, and keep deterministic layers at `exact-match` where inputs are available.

6. **v0.1 linkage** — Fill `evaluatorManifest.commitment.algorithm` with `"other"`, copy the Phase II digest, set `committedAt` to the **verified anchor time** (never a self-declared wall clock), map reveal status, and point `integrity.sourceUri` at the evidence bundle. Confirm the pending record still emits only `CHAL003`.

## What a live committee would additionally do

- **Before applications close:** decide reveal policy (`revealed`, `withheld`, or `selective-audit`); keep salt and hidden manifest contents off the public envelope; assign who may sign run attestations.
- **During the round:** monitor the chosen anchor trust root; treat run signatures as operator assertions, not proof of honest use; refuse to let AI output or replay results set `decision.authorityKind`.
- **After the round:** reveal or audit per policy; publish only claim-bounded verification results; retain keys and receipts under the program's secrets policy.

## Keys and secrets handling

| Asset | Example bundle | Live program |
|---|---|---|
| Manifest salt | Test vector; disclosed on reveal | CSPRNG; withheld until reveal or selective audit |
| Rekor artifact signing key | Ephemeral test key inside hashedrekord | Program-controlled key; not reused across rounds without policy |
| Rekor log trust root | Pinned production PEM (`rekor-v1`) or test-log PEM (fixture) | Pin and monitor; rotate only with documented ceremony |
| Run attestation key | Test Ed25519 in `vectors/` | Program-controlled; not the test harness key |

Test private keys in `phase2/vectors/` exist only for the harness and the public example. They must not be reused for a live program.

## Anchor steps (Rekor v1)

1. JCS-canonicalize the envelope bytes.
2. POST a hashedrekord to `https://rekor.sigstore.dev` (`rekor-v1`) or issue a fixture receipt (`rekor-v1-recorded-fixture`).
3. Store the receipt with offline verifier material, not merely a URL.
4. Verify under the pinned trust root: hashedrekord digest match, SET signature, Merkle inclusion, checkpoint signature.
5. Compare verified `integratedTime` strictly before `applicationDeadline`.

## Live Rekor status (2026-08-19, Wave 4 re-check)

POST to `https://rekor.sigstore.dev/api/v1/log/entries` failed again with `ConnectionResetError` from this environment during Wave 4 completion. T6, T7, and the public example therefore continue to use `rekor-v1-recorded-fixture` receipts verified under the shipped test-log key (`vectors/rekor-fixture-trust-root.pem`). That profile does **not** establish inclusion in the public Sigstore Rekor log.

When live Rekor is reachable, record a hashedrekord with:

```bash
python phase2/src/cli.py commit --manifest MANIFEST.json --out-envelope /tmp/envelope.json --out-salt /tmp/salt.json
python phase2/src/cli.py anchor --envelope /tmp/envelope.json --profile rekor-v1 --out /tmp/receipt.json
```

Then write `vectors/rekor-live-hashedrekord.json` with `envelopeBytesUtf8` (UTF-8 JCS envelope bytes) and `receipt`. T7's `test_recorded_from_live_rekor_if_present` verifies it under the pinned production key.

## Fixture verification semantics (rigorous, not a public claim)

`rekor-v1-recorded-fixture` verification establishes:

1. The hashedrekord body SHA-256 matches the JCS envelope bytes.
2. The signed entry timestamp verifies under the pinned test-log ECDSA P-256 key.
3. The RFC 6962 inclusion proof reconstructs the claimed root hash.
4. The signed checkpoint verifies under the same key and matches tree size and root.

It does **not** establish that any entry appears in production Sigstore Rekor, universal time, or institutional approval.

## Proportionality notes

- Phase II adds people-time for manifest design, key ceremony, anchor monitoring, reveal policy, and claim-bounded publication.
- A committee should weigh that cost against round materiality: a low-stakes advisory screen may not warrant full commitment + anchor + run attestation for every round.
- v0.1 remains valid without a Phase II bundle; absence of a bundle is not a v0.1 defect.
- Do not describe fixture receipts as production Rekor inclusion. Do not describe a valid commitment as execution or a signed run as funding authority.
