# Phase II release procedure

Phase II releases remain anchored to a Git commit SHA under the repository-wide procedure in `RELEASE-INTEGRITY.md`. The repository-wide acceptance decision in `docs/V1_0_0_GATE_CHECKLIST.md` controls whether a `v1.0.0` tag may be created.

Repository version lineage relevant to this tree:

- `0.2.0` — Phase II commitment, anchoring, run attestation, and replay;
- `0.3.0` — schema 0.2 extensions, projection, and alternate anchor fixtures;
- `0.3.1` / `0.3.2` — documentation and public-readiness corrections (no Phase II claim-matrix change);
- package `0.4.0` / post-`0.3.2` hardening on `main` — claim-narrowing corrections, replay report v2, evidence-bundle v2, RFC 3161 production fail-closed behavior, projection v1/v2 completeness checks, Rekor v2 module (live issuance fail-closed), unified `gdi` verifier. These changes require a new annotated repository tag before being described as tagged-release behavior. Package `0.4.0` is not `v1.0.0`.

Grant-decision `schemaVersion` stays `"0.1"` unless a versioned schema change is separately specified. Evaluator manifest, commitment envelope, anchor receipt, and run predicate identifiers remain unchanged. Historical replay-report v1 and evidence-bundle v1 remain frozen; current replay generation emits replay-report v2, and new bundles carrying it use evidence-bundle v2.

## Exact candidate identity

For pull requests, GitHub's default checkout target is a synthetic merge ref. The current repository workflow instead checks out `github.event.pull_request.head.sha` explicitly and asserts `git rev-parse HEAD == VALIDATION_SHA` before every release-facing job. Historical PR runs that used the default synthetic merge ref remain integration evidence but are not proof that the raw PR-head commit itself executed the suite.

After merge, the exact resulting `main` commit must receive its own successful six-job validation. A successful PR run—raw head or synthetic merge—does not substitute for the merged-commit gate.

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
11. All six repository release jobs (`conformance`, `phase2`, `schema-02`, `package`, `lint-type`, `security`) are green on the exact raw PR head before merge and on the exact resulting `main` commit after merge. A successful run on an earlier commit is not evidence for a later commit.
12. The empirical study gate is complete. In particular, genuine independent second annotation must not be fabricated by software, and `scripts/study_status.py` must report `readyForFinalReview=true` before release-eligible assets can be assembled.

## Release-candidate assets

The repository's manually dispatched `validate` workflow provides a `release-assets` job for the final `main` commit. That job runs only after the six release jobs and requires the same-run empirical study status to be ready for final review.

`scripts/release_artifacts.py` then assembles and verifies:

- exact-commit source archive;
- Python wheel;
- Python sdist;
- CycloneDX SBOM;
- `release-validation.json`;
- `release-manifest.json`;
- `SHA256SUMS`.

The checksum graph is acyclic: `release-manifest.json` records hashes and sizes for the source archive, wheel, sdist, SBOM, and validation report; `SHA256SUMS` is generated last over those payloads plus the release manifest and necessarily excludes itself. The verifier also cross-checks manifest commit identity against the validation report and rejects missing, extra, renamed, size-mismatched, or digest-mismatched payloads.

`releaseEligible=true` evidence fails closed unless it is bound to `refs/heads/main`, contains exactly the six required release jobs all marked `success`, and embeds `studyStatus.readyForFinalReview=true`. PR assembly smoke uses `releaseEligible=false` and is not release evidence.

## Tag and notes

Only after the repository-wide gates and the final release-candidate asset verification succeed:

1. independently verify the downloaded release-candidate directory with `python scripts/release_artifacts.py verify <directory>`;
2. create an annotated tag on the exact eligible `main` commit;
3. publish the tag, commit SHA, package version, asset filenames, and SHA-256 digests together;
4. attach the verified individual release assets, not only GitHub's automatic source archives;
5. state explicitly what Phase II graph verification establishes (`CLAIM-MATRIX.md`) and what it does not;
6. state the replay-report and evidence-bundle versions supported and which versions are emitted/required for new evidence;
7. state the production status of every anchor profile. Do not infer implementation from a reserved profile identifier;
8. re-check the published asset hashes against `SHA256SUMS` after upload.

A Rekor envelope over an evaluator-manifest commitment is not a signed release of this repository and must not be described as one.

No byte-reproducible-build claim is made without independent byte-identity evidence from separate clean builds.

## Rekor v1 fixture and live evidence

When the historical `rekor-v1` service path is reachable, a hashedrekord may be recorded per `ADMIN-BURDEN.md`. Until a live receipt is actually recorded and documented, T6/T7 and the public example correctly use `rekor-v1-recorded-fixture`.

Rekor v1 compatibility must not be silently upgraded to successor semantics under the same profile identifier. Any successor transparency/timestamp profile requires a new profile id, trust specification, vectors, and claim-matrix entry.

## Alternate anchor profiles

`rfc3161-recorded-fixture` and `ethereum-calldata-fixture` are test profiles with explicit non-production trust boundaries. Production RFC 3161 is currently disabled in the reference client; live Ethereum anchoring is not implemented. See `DEFERRED.md` and `CLAIM-MATRIX.md`.
