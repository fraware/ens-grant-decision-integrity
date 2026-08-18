# Phase II test vectors

## T1 canonicalization

`t1_objects.json` holds I-JSON objects compared under two independent RFC 8785 implementations:

- Production adapter: `rfc8785==0.1.4`
- Second implementation, tests only: `jcs==0.2.1` (cyberphone JSON Canonicalization Scheme lineage)

`t1_rfc8785_section_322.jcs.txt` stores the JCS encoding of the RFC 8785 §3.2.2 / §3.2.3 sample once generated.

## Rekor

T6 and T7 use `rekor-v1-recorded-fixture` receipts issued by a test-log ECDSA P-256 key (`rekor-fixture-private.pem`). Those receipts do **not** establish inclusion in the public Sigstore Rekor log.

`rekor-live-hashedrekord.json` is written only when live `https://rekor.sigstore.dev` accepted a hashedrekord during fixture generation. T7 skips that case when the file is absent.

The production profile pins the Rekor v1 public key in `phase2/src/anchors/rekor.py`. Verification does not trust a live `/api/v1/log/publicKey` response as the root.
