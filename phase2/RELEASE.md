# Phase II release procedure

Phase II releases remain anchored to a Git commit SHA under the repository-wide procedure in `RELEASE-INTEGRITY.md`.

Repository version lineage relevant to this tree:

- `0.2.0` — Phase II commitment, anchoring, run attestation, and replay;
- `0.3.0` — schema 0.2 extensions, projection, and alternate anchor fixtures;
- `0.3.1` / `0.3.2` — documentation and public-readiness corrections (no Phase II claim-matrix change);
- post-`0.3.2` hardening — claim-narrowing corrections, replay report v2, RFC 3161 production fail-closed behavior, and projection completeness checks. These changes require a new repository release before being described as released behavior.

Grant-decision `schemaVersion` stays `"0.1"` unless a versioned schema change is separately specified. Evaluator manifest, commitment envelope, anchor receipt, run predicate, and evidence-bundle version identifiers remain unchanged. Historical replay report v1 remains frozen; current replay generation emits replay report v2.

## Pre-tag checklist

1. v0.1 validation contract passes unchanged on the candidate commit.
2. `python -m pytest phase2/tests` passes, including canonicalization, commitment, anchor, authority-separation, replay-version/layer-set, RFC 3161 fail-closed/trust-root/malformed-input, and Ethereum-fixture tests. Any optional network-dependent case must be reported as skipped, not passed.
3. If schema 0.2 is in scope: `python scripts/test_schema_02.py` and `python -m pytest projection/tests` pass.
4. `phase2/examples/retrospective-public.bundle.json` verifies with `verify-graph` and preserves `CHAL003` on its embedded pending v0.1 record.
5. No Phase II object populates `decision.authorityKind`.
6. Replay-report v1 schema bytes/semantics remain unchanged from the released historical format; v1 `bounded-match` is parseable but rejected as evidence by the current verifier, while new replay generation emits v2. Duplicate or incomplete attested layer sets fail as structured C5 protocol errors.
7. Production `rfc3161` issuance and verification remain fail-closed unless a separately reviewed standards-conformant implementation and adversarial/interoperability tests have landed. Fixture results must not be described as third-party TSA evidence. Invalid receipt encodings, signature mismatch, and invalid configured trust material must fail as structured verifier errors rather than uncaught parser/cryptography exceptions.
8. Release notes state Rekor trust boundaries: fixture receipts do not claim public Sigstore inclusion unless a live receipt is recorded and documented.
9. Projection tests demonstrate that top-level source fields cannot disappear silently, publish/withhold overlap fails, and non-null source integrity is not silently overwritten.

## Tag and notes

1. Create an annotated tag on the reviewed commit.
2. Publish tag, commit SHA, archive filename, and SHA-256 digest together.
3. State explicitly what Phase II graph verification establishes (`CLAIM-MATRIX.md`) and what it does not.
4. State the replay report versions supported and which one is emitted.
5. State the production status of every anchor profile. Do not infer implementation from a reserved profile identifier.
6. A Rekor envelope over an evaluator-manifest commitment is not a signed release of this repository and must not be described as one.

## Rekor v1 fixture and live evidence

When the historical `rekor-v1` service path is reachable, a hashedrekord may be recorded per `ADMIN-BURDEN.md`. Until a live receipt is actually recorded and documented, T6/T7 and the public example correctly use `rekor-v1-recorded-fixture`.

Rekor v1 compatibility must not be silently upgraded to successor semantics under the same profile identifier. Any successor transparency/timestamp profile requires a new profile id, trust specification, vectors, and claim-matrix entry.

## Alternate anchor profiles

`rfc3161-recorded-fixture` and `ethereum-calldata-fixture` are test profiles with explicit non-production trust boundaries. Production RFC 3161 is currently disabled in the reference client; live Ethereum anchoring is not implemented. See `DEFERRED.md` and `CLAIM-MATRIX.md`.
