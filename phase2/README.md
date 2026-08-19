# Phase II — Evaluator provenance

Reference implementation of evaluator-manifest commitment, Rekor-profile anchoring, run attestation, and replay. Claims are capped by `CLAIM-MATRIX.md`. Protocol mechanics are in `PROTOCOL.md`.

v0.1 grant-decision `schemaVersion` remains `"0.1"`. This tree does not change v0.1 Charter, schema, or conformance behavior.

## What a pass establishes

Only the claims listed in `CLAIM-MATRIX.md`. In short: a revealed manifest can reopen an anchored digest; a selected anchor profile can place that digest before a deadline under that profile's trust root; a signer can attest a run; replay can record layer outcomes including honest `not-replayable`. None of that is execution, fairness, legitimacy, or funding authority.

AI systems cannot approve, reject, suspend, or release funding.

## Layout

```
phase2/
  CLAIM-MATRIX.md
  PROTOCOL.md
  schema/          JSON Schema Draft 2020-12
  src/             reference implementation and CLI
  vectors/         public T1–T4 vectors and recorded Rekor fixtures
  examples/        one fictional public retrospective bundle
  tests/           T1–T12
  requirements.txt pinned dependencies
```

## Install and test

```bash
python -m pip install -r phase2/requirements.txt
python -m pytest phase2/tests
```

T1 compares the production RFC 8785 adapter (`rfc8785`) with a second independent implementation (`jcs`, the cyberphone/RFC-author lineage) and with RFC 8785 vectors.

T6 and T7 use `rekor-v1-recorded-fixture` receipts so they do not depend on live Sigstore availability or on a controllable production timestamp. See [ADMIN-BURDEN.md](ADMIN-BURDEN.md) for operational cost, key handling, and proportionality notes.

### Live Rekor (2026-08-19)

POST to `https://rekor.sigstore.dev/api/v1/log/entries` failed from this environment with `ConnectionResetError` (remote host forcibly closed the connection). No `vectors/rekor-live-hashedrekord.json` was recorded. T7 skips the optional live-receipt case; T6/T7 and the public example rely on the recorded-fixture profile.

Fixture verification is rigorous but not a public Rekor claim:

- The hashedrekord body SHA-256 must match the JCS envelope bytes.
- The signed entry timestamp must verify under the pinned test-log ECDSA P-256 key (`vectors/rekor-fixture-trust-root.pem`).
- The RFC 6962 inclusion proof must reconstruct the claimed root hash.
- The signed checkpoint must verify under the same key.

Production `rekor-v1` pins the Sigstore Rekor v1 production public key in `src/anchors/rekor.py` and does not trust a live `/api/v1/log/publicKey` response as the root. When live Rekor is reachable, record a receipt per `ADMIN-BURDEN.md` and enable T7's live fixture test.

## CLI

```bash
python phase2/src/cli.py commit --manifest MANIFEST.json --out-envelope envelope.json --out-salt salt.json
python phase2/src/cli.py anchor --envelope envelope.json --profile rekor-v1-recorded-fixture --fixture-key test-rekor.pem --out receipt.json
python phase2/src/cli.py verify-commitment --envelope envelope.json --receipt receipt.json
python phase2/src/cli.py reveal --envelope envelope.json --manifest MANIFEST.json --salt salt.json
python phase2/src/cli.py attest-run --predicate predicate.json --key ed25519.pem --out attestation.json
python phase2/src/cli.py verify-run --attestation attestation.json --public-key ed25519.pub.pem
python phase2/src/cli.py replay --attestation attestation.json --layer-inputs layers.json --out report.json
python phase2/src/cli.py verify-graph --bundle bundle.json
```

`anchor --profile rekor-v1` submits to `https://rekor.sigstore.dev`. `rfc3161` requires a pinned TSA trust root at issuance and verification time. `rfc3161-recorded-fixture` and `ethereum-calldata-fixture` issue offline fixture receipts. Live Ethereum anchoring (`ethereum`) raises `NotImplementedError`.

Signing keys in tests and in the public example are test keys. A real program must supply its own signing identity.

## Public example

`examples/retrospective-public.bundle.json` is a fictional, non-evaluative mapping of a Marketplace-like process using only public ENS forum URIs. It does not identify, score, recommend, or reject a real applicant. The hosted-generation layer is `not-replayable`. Deterministic layers are `exact-match`. The embedded v0.1 record remains pending and preserves warning `CHAL003`.

The example's anchor is a `rekor-v1-recorded-fixture` receipt. It does not claim inclusion in production Rekor on a date before the published Marketplace deadline.

## Administrative burden

See [ADMIN-BURDEN.md](ADMIN-BURDEN.md) for keys, reveal policy, anchor steps, committee operational cost, and proportionality notes. The summary below remains for quick orientation.

Constructing one fictional bundle required: writing a versioned manifest with round identifiers; generating salt and a commitment; selecting an anchor profile and retaining offline-verifiable receipt material; generating a test Ed25519 key, signing a run statement, and storing the public key; computing deterministic layer snapshots; writing an honest `not-replayable` hosted-generation outcome; filling v0.1 `evaluatorManifest` with algorithm `other` and the verified fixture time; confirming the pending record still emits only `CHAL003`.

A live committee would also have to: decide a reveal policy before applications close; keep salt off the public envelope; pin and monitor a trust root rather than trusting a URL; treat run signatures as operator assertions; refuse to let replay or AI output set `decision.authorityKind`; and budget the people-time for those steps against the round's materiality. That cost is real. It is not a reason to auto-tighten v0.1 checks.

## Dependencies

Pinned in `requirements.txt`. Production canonicalization uses `rfc8785`. Tests also pin `jcs` as the second JCS implementation. Merkle inclusion follows RFC 6962 as used by Rekor; DSSE PAE follows the DSSE specification.

## Out of scope

No dashboard, grant-scoring model, new cryptographic primitive, ZK selective disclosure, universal DAO identity, production KMS, or live Ethereum mainnet anchoring in this reference client.
