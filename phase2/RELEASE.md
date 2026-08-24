# Phase II release procedure

Phase II releases remain anchored to a Git commit SHA under the repository-wide procedure in `RELEASE-INTEGRITY.md`.

Repository version lineage relevant to this tree:

- `0.2.0` — Phase II commitment, anchoring, run attestation, and replay;
- `0.3.0` — schema 0.2 extensions, projection, and alternate anchor fixtures;
- `0.3.1` / `0.3.2` — documentation and public-readiness corrections (no Phase II claim-matrix change).

Grant-decision `schemaVersion` stays `"0.1"` unless a versioned schema change is separately specified. Phase II protocol objects remain version `"1"`.

## Pre-tag checklist

1. v0.1 validation contract passes unchanged on the candidate commit.
2. `python -m pytest phase2/tests` passes (T1–T12; optional live Rekor vector may skip).
3. If schema 0.2 is in scope: `python scripts/test_schema_02.py` and `python -m pytest projection/tests` pass.
4. `phase2/examples/retrospective-public.bundle.json` verifies with `verify-graph` and preserves `CHAL003` on its embedded pending v0.1 record.
5. No Phase II object populates `decision.authorityKind`.
6. Release notes state Rekor trust boundaries: fixture receipts do not claim public Sigstore inclusion unless a live receipt is recorded and documented.

## Tag and notes

1. Create an annotated tag (for example `v0.3.2`) on the reviewed commit.
2. Publish tag, commit SHA, archive filename, and SHA-256 digest together.
3. State explicitly what Phase II graph verification establishes (`CLAIM-MATRIX.md`) and what it does not.
4. A Rekor envelope over an evaluator-manifest commitment is not a signed release of this repository and must not be described as one.

## Fixture and live Rekor

When live `https://rekor.sigstore.dev` is reachable, record a hashedrekord and add `vectors/rekor-live-hashedrekord.json` per `ADMIN-BURDEN.md`. Until then, T6/T7 and the public example correctly use `rekor-v1-recorded-fixture`.

## Alternate anchor profiles

RFC 3161 and Ethereum calldata adapters ship with fixture profiles for offline verification. Live TSA and live mainnet anchoring are program responsibilities documented in `DEFERRED.md` and `CLAIM-MATRIX.md`.
