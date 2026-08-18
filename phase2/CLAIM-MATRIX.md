# Phase II Claim Matrix

This matrix is frozen before the reference implementation. A verifier may report a claim only when the corresponding check succeeded. Silence is not success. A green check is not a funding decision.

v0.1 records without a Phase II evidence bundle still do not prove that a commitment existed at a declared time.

## Claims

| Claim | Verifier establishes | Must not be claimed |
|---|---|---|
| C1 Manifest binding | Revealed manifest and salt reopen the anchored digest. | execution, operator honesty, or evaluator correctness |
| C2 Temporal precedence | Selected anchor profile places the envelope before the application deadline. | universal time; the named profile's trust root and monitoring assumptions apply |
| C3 Round binding | programId, roundId, applicationDeadline, and domain string bind the commitment. | prevention of cross-program reuse if programId, roundId, deadline, and domain are copied deliberately |
| C4 Run attribution | Signer asserts this run used the bound commitment, input snapshots, environment, and output digest. | that the signer actually used that configuration or that the output is sound |
| C5 Replay evidence | Replay report records per-layer exact-match, bounded-match, diverged, or not-replayable outcomes. | fairness, legitimacy, hosted-model identity over time, or substantive merit |
| C6 Human authority | No Phase II object populated decision.authorityKind. | institutional approval, committee adoption, or funding authority |

## Verifier commands

| Command | May establish | Never establishes |
|---|---|---|
| `commit` | Local digest construction only. No C1–C6 until later checks succeed. | Existence, time, execution, authority |
| `anchor` | Submission to the selected profile. C2 is not established until `verify-commitment` succeeds. | Universal time; other profiles |
| `verify-commitment` | C2 and the public envelope fields used by C3. C1 only after a successful `reveal`. | Execution; manifest contents when withheld |
| `reveal` | C1 and C3 when salt and manifest reopen the digest and match envelope round fields. | Execution; that disclosure policy was followed outside this object |
| `attest-run` | Local DSSE wrapping of an assertion. C4 is not established until `verify-run` succeeds. | Honesty; actual use of the committed configuration |
| `verify-run` | C4 as a signature over the in-toto statement and custom predicate. | Correctness of outputs; funding authority |
| `replay` | Local layer outcomes. C5 is not established until `verify-graph` accepts the report. | Fairness or hosted-model identity over time |
| `verify-graph` | Conjunction of present, successful checks: C1 if revealed, C2, C3, C4 if attestation present, C5 if replay present, always C6. | Any claim whose object is absent or failed |

`verify-commitment` on a withheld bundle reports C2 and C3 only. It MUST NOT report C1.

## Protocol controls (P1–P10)

These rows are Phase II controls. They do not rewrite v0.1 threat rows T1–T11 in `DESIGN-NOTES.md`.

| ID | Failure mode | Control |
|---|---|---|
| P1 | Two serializers produce different bytes for one manifest. | RFC 8785 JCS, I-JSON only; T1 dual implementation. |
| P2 | A material manifest change after commitment still opens. | Digest opening; T2. |
| P3 | Salt reuse or salt grinding is treated as one commitment. | 32-byte CSPRNG salt; two salts are two commitments; T3. |
| P4 | Another object type is verified as an evaluator-manifest commitment. | Versioned domain string; T4. |
| P5 | programId, roundId, or deadline drift after commitment. | Those fields are in the manifest and copied onto the envelope; T5. |
| P6 | A commitment at or after the deadline is treated as pre-deadline. | Profile-verified anchor time compared strictly before deadline; T6. |
| P7 | A corrupted inclusion proof or substituted digest still verifies. | Offline SET, inclusion, and digest match; T7. |
| P8 | Withheld state is reported as manifest-content verification. | Reveal-status gate; T8. |
| P9 | A run attestation with the wrong commitment or output is accepted. | Predicate binding; T9. |
| P10 | Replay of deterministic layers is taken as fairness, or Phase II objects become decision authority. | Layer outcomes including honest `not-replayable`; T10–T12. Authority stays on the v0.1 `decision` object. |

## Adversarial tests (T1–T12)

| ID | Assertion |
|---|---|
| T1 | RFC 8785 vectors and two independent JCS implementations produce identical bytes. |
| T2 | Any material manifest mutation fails opening. |
| T3 | Same manifest, two salts, two commitments; each opens only with its salt. |
| T4 | A different domain string cannot verify as an evaluator-manifest commitment. |
| T5 | Changing programId, roundId, or applicationDeadline invalidates opening against the envelope. |
| T6 | Anchor time at or after the deadline fails C2. |
| T7 | Corrupted inclusion proof or mismatched digest fails. |
| T8 | Withheld disclosure reports only anchor-supported claims; no C1. |
| T9 | Run attestation with wrong commitment or output digest fails graph validation. |
| T10 | Perturbing deterministic preprocessing, scoring, or aggregation is detected as `diverged`. |
| T11 | Hosted-model `not-replayable` does not void deterministic-layer claims. |
| T12 | No Phase II object can populate or imply v0.1 `decision.authorityKind`. |

## Hard non-claims

Every verifier prints:

- A valid commitment is not evidence of execution.
- A signed run is an assertion by the signer, not proof of operator honesty or that the committed configuration was used.
- Replay agreement is not correctness, fairness, or legitimacy.
- Hosted models may be not-replayable; that outcome does not void independent deterministic-layer results.
- Hashes and log inclusion are not institutional approval or funding authority.
- AI systems cannot approve, reject, suspend, or release funding.

## Rekor trust boundary

The first implemented profile is Sigstore Rekor v1 (`rekor-v1`).

A successful `rekor-v1` verify establishes that:

1. the hashedrekord body contains the SHA-256 digest of the JCS envelope bytes;
2. Rekor's signed entry timestamp verifies under the pinned Rekor v1 production key over the RFC 8785 encoding of `{body, integratedTime, logID, logIndex}`;
3. the RFC 6962 inclusion proof reconstructs the root hash in the proof;
4. the signed checkpoint verifies under the same pinned key and carries that root hash and tree size.

It does not establish that every observer saw the same log (monitoring against split-view is out of scope for this client). It does not establish RFC 3161 time. It does not establish an Ethereum block time. EIP-712 is not a time anchor.

`rekor-v1-recorded-fixture` receipts are verified under a test-log key shipped with the fixture. They do not establish inclusion in the public Sigstore Rekor log. Tests T6 and T7 use that fixture profile when live Rekor is unavailable or when a controllable timestamp is required.

RFC 3161 and Ethereum adapters exist only as interface stubs and raise `NotImplementedError`.

## v0.1 linkage non-claims

Filling `evaluatorManifest.commitment.algorithm` with `"other"` and `digest` with the Phase II digest does not make v0.1 validate the salt, JCS, or anchor. v0.1 still checks only declared `committedAt` versus `submissionDeadline`. Independently verifiable pre-deadline existence is a Phase II graph check.

Do not write algorithm `"sha256"` for a salted domain-separated digest. That identifier would describe a different function.

## Authority

Phase II objects MUST NOT contain `authorityKind`, `decisionAuthority`, `institutionalAuthority`, or `fundingAuthority`. Graph verification fails if they do. Graph verification never copies those fields into a v0.1 `decision` object. AI remains advisory.
