# Phase II release procedure

Phase II releases remain anchored to a Git commit SHA under the repository-wide procedure in `RELEASE-INTEGRITY.md`.

Repository version lineage relevant to this tree:

- `0.2.0` — Phase II commitment, anchoring, run attestation, and replay;
- `0.3.0` — schema 0.2 extensions, projection, and alternate anchor fixtures;
- `0.3.1` / `0.3.2` — documentation and public-readiness corrections (no Phase II claim-matrix change);
- package `0.4.0` / post-`0.3.2` hardening on `main` — claim-narrowing corrections, replay report v2, evidence-bundle v2, RFC 3161 production fail-closed behavior, projection v1/v2 completeness checks, Rekor v2 module (live issuance fail-closed), unified `gdi` verifier. These changes require a new annotated repository tag before being described as tagged-release behavior. Package `0.4.0` is not `v1.0.0`.

Grant-decision `schemaVersion` stays `"0.1"` unless a versioned schema change is separately specified. Evaluator manifest, commitment envelope, anchor receipt, and run predicate identifiers remain unchanged. Historical replay-report v1 and evidence-bundle v1 remain frozen; current replay generation emits replay-report v2, and new bundles carrying it use evidence-bundle v2.

## Pre-tag checklist

1. v0.1 validation contract passes unchanged on the candidate commit.
2. `python -m pytest phase2/tests` passes, including canonicalization, commitment, anchor, authority-separation, disclosure-state, CLI fail-closed, replay-version/layer-set/evidence consistency, bundle-version compatibility, RFC 3161 fail-closed/trust-root/malformed-input, and Ethereum-fixture tests. Any optional network-dependent case must be reported as skipped, not passed.
3. If schema 0.2 is in scope: `python -m pytest scripts/test_schema_02.py` and `python -m pytest projection/tests` pass.
4. `phase2/examples/retrospective-public.bundle.json` verifies as the historical bundle-v1/replay-v1 compatibility example and preserves `CHAL003` on its embedded pending v0.1 record; current test builders generate bundle-v2/replay-v2 evidence.
5. No Phase II object populates `decision.authorityKind`.
6. Replay-report v1 and evidence-bundle v1 schema bytes/semantics remain unchanged from their released historical formats. v1 `bounded-match` is parseable but rejected as evidence by the current verifier. New replay generation emits v2; new bundles carrying replay v2 use bundle v2. Duplicate, incomplete, or inconsistent replay evidence fails closed.
7. Evidence-bundle v2 enforces current disclosure semantics: `committed` and `withheld` are unopened and do not carry manifest/salt; `revealed` and `selective-audit` provide material sufficient for opening. No unopened state establishes C1 or hidden-manifest round equality.
8. Production `rfc3161` issuance and verification remain fail-closed unless a separately reviewed standards-conformant implementation and adversarial/interoperability tests have landed. Fixture results must not be described as third-party TSA evidence. Invalid receipt encodings, signature mismatch, and invalid configured trust material must fail as structured verifier errors rather than uncaught parser/cryptography exceptions.
9. Release notes state Rekor trust boundaries: fixture receipts do not claim public Sigstore inclusion unless a live receipt is recorded and documented.
10. Projection tests demonstrate that top-level source fields cannot disappear silently, publish/withhold overlap fails, and non-null source integrity is not silently overwritten.
11. Required hosted checks are green on the exact candidate commit. A successful run on an earlier head is not evidence for a later head.

## Tag and notes

1. Create an annotated tag on the reviewed commit.
2. Publish tag, commit SHA, archive filename, and SHA-256 digest together.
3. State explicitly what Phase II graph verification establishes (`CLAIM-MATRIX.md`) and what it does not.
4. State the replay-report and evidence-bundle versions supported and which versions are emitted/required for new evidence.
5. State the production status of every anchor profile. Do not infer implementation from a reserved profile identifier.
6. A Rekor envelope over an evaluator-manifest commitment is not a signed release of this repository and must not be described as one.

## Rekor v1 fixture and live evidence

When the historical `rekor-v1` service path is reachable, a hashedrekord may be recorded per `ADMIN-BURDEN.md`. Until a live receipt is actually recorded and documented, T6/T7 and the public example correctly use `rekor-v1-recorded-fixture`.

Rekor v1 compatibility must not be silently upgraded to successor semantics under the same profile identifier. Any successor transparency/timestamp profile requires a new profile id, trust specification, vectors, and claim-matrix entry.

## Alternate anchor profiles

`rfc3161-recorded-fixture` and `ethereum-calldata-fixture` are test profiles with explicit non-production trust boundaries. Production RFC 3161 is currently disabled in the reference client; live Ethereum anchoring is not implemented. See `DEFERRED.md` and `CLAIM-MATRIX.md`.
