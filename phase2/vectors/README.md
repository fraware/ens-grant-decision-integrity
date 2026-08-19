# Phase II test vectors

## T1 canonicalization

`t1_objects.json` holds I-JSON objects compared under two independent RFC 8785 implementations:

- Production adapter: `rfc8785==0.1.4`
- Second implementation, tests only: `jcs==0.2.1` (cyberphone JSON Canonicalization Scheme lineage)

`t1_rfc8785_section_322.jcs.txt` stores the JCS encoding of the RFC 8785 §3.2.2 / §3.2.3 sample once generated.

## Rekor

### Profiles

| Profile | Trust root | Establishes |
|---|---|---|
| `rekor-v1` | Pinned production PEM in `src/anchors/rekor.py` | Hashedrekord in public Sigstore Rekor under pinned key assumptions |
| `rekor-v1-recorded-fixture` | Test-log PEM (`rekor-fixture-trust-root.pem`) | Offline consistency under test-log key only; **not** public log inclusion |

T6 and T7 use `rekor-v1-recorded-fixture` receipts issued by a test-log ECDSA P-256 key (`rekor-fixture-private.pem`). Those receipts do **not** establish inclusion in the public Sigstore Rekor log.

### Live recording

`rekor-live-hashedrekord.json` is written only when live `https://rekor.sigstore.dev` accepted a hashedrekord. Format:

```json
{
  "envelopeBytesUtf8": "<UTF-8 JCS envelope bytes>",
  "receipt": { "...": "rekor-v1 receipt" },
  "note": "optional provenance string"
}
```

T7's `test_recorded_from_live_rekor_if_present` verifies under the pinned production key when the file exists; otherwise it skips.

As of 2026-08-19, live POST failed with `ConnectionResetError` from the fixture-generation environment. See `ADMIN-BURDEN.md`.

### Inclusion verification semantics

For both profiles, offline verification checks:

1. `envelopeDigestSha256` equals SHA-256 of the JCS envelope bytes.
2. The hashedrekord body's `spec.data.hash.value` equals that digest.
3. The signed entry timestamp (SET) verifies over RFC 8785 `{body, integratedTime, logID, logIndex}` under the pinned key.
4. The RFC 6962 Merkle inclusion proof reconstructs `rootHash` at `treeSize`.
5. The signed checkpoint verifies and matches `rootHash` and `treeSize`.

Monitoring against Rekor split-view is out of scope for this client. A fixture receipt must never be described as production Rekor inclusion.

The production profile pins the Rekor v1 public key in `phase2/src/anchors/rekor.py`. Verification does not trust a live `/api/v1/log/publicKey` response as the root.

## Run attestation keys

`run-attestation-ed25519-private.pem` and `run-attestation-ed25519-public.pem` are test keys for the harness and public example. Do not reuse them in a live program.
