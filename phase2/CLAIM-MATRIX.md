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
| C5 Replay evidence | Accepted replay evidence records per-layer `exact-match`, `diverged`, or `not-replayable` outcomes from canonical artifact recomputation. | re-execution of the recorded implementation unless separately demonstrated; fairness, legitimacy, hosted-model identity over time, or substantive merit |
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
| `replay` | Local artifact-recomputation outcomes. C5 is not established until `verify-graph` accepts the report. | Re-execution of the recorded implementation; fairness or hosted-model identity over time |
| `verify-graph` | Conjunction of present, successful checks: C1 if revealed, C2, C3, C4 if attestation present, C5 if accepted replay evidence is present, always C6. | Any claim whose object is absent or failed |

`verify-commitment` on a withheld bundle reports C2 and C3 only. It MUST NOT report C1.

## Replay report versions

Replay reports are independently versioned within the Phase II evidence-bundle surface.

- `reportVersion: "1"` is the historical wire format and remains schema-valid for compatibility. It included `bounded-match`. The current verifier does **not** accept `bounded-match` or a non-null `bound` as C5 evidence because distance between cryptographic digest strings is not a meaningful measure of distance between underlying computations.
- `reportVersion: "2"` is the current emitted format. It records only `exact-match`, `diverged`, and `not-replayable` outcomes from canonical artifact recomputation.

A safe historical v1 report that contains only exact/diverged/not-replayable outcomes may still be verified. The v1 schema is not silently repurposed.

The defined replay layer set must be complete and exact. Duplicate report layers and missing or unexpected attested layer identifiers fail closed as structured C5 errors.

Neither replay-report version proves that the implementation identified in a run attestation was actually re-executed. A future re-execution protocol would require its own versioned execution environment, implementation invocation, output capture, comparator semantics, and claim boundary.

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
| P10 | Artifact recomputation is taken as implementation re-execution, fairness, or Phase II objects become decision authority. | Versioned replay outcomes including honest `not-replayable`; invalid digest-distance bounds and malformed layer sets fail closed; T10–T12 plus replay regressions. Authority stays on the v0.1 `decision` object. |

## Adversarial tests

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
| T13 | RFC 3161 fixture verification is bound to independently supplied verifier trust; receipt-selected trust substitution, malformed fixture material, and production-profile overclaim fail closed with structured verifier errors. |
| T14 | Ethereum calldata fixture verification binds the recorded calldata digest under the fixture trust boundary; it does not claim mainnet inclusion. |

Additional regression tests cover replay-version compatibility, rejection of v1 `bounded-match`, duplicate/missing/unexpected replay layers, and projection disclosure completeness.

## Hard non-claims

Every verifier prints:

- A valid commitment is not evidence of execution.
- A signed run is an assertion by the signer, not proof of operator honesty or that the committed configuration was used.
- Artifact replay agreement is not proof that the recorded implementation was re-executed unless a separate re-execution protocol establishes that fact.
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

## RFC 3161 trust boundary

The production profile identifier `rfc3161` is reserved, but production issuance and verification currently fail closed with `TS3178`. This implementation does **not** establish C2 from a production RFC 3161 token.

Production support may be enabled only after the verifier validates the relevant CMS/RFC 3161 semantics, including signer selection, signed attributes, message imprint, TSA certificate identification, timestamping authorization/EKU and policy as applicable, certificate-path validation against independently configured verifier trust, and the protocol's request/response bindings. Receipt-carried certificate material must never become an independent trust root merely because it appears in the receipt.

`rfc3161-recorded-fixture` verifies the repository's simplified signed-`TSTInfo` test fixture under an independently supplied test TSA trust root. Malformed base64/token material and signature failures are normalized to structured protocol failures. The fixture is useful for adversarial trust-binding and deadline tests only. It does not establish a third-party TSA attestation or production RFC 3161 conformance.

## Ethereum calldata trust boundary

Profile `ethereum-calldata-fixture` verifies recorded transaction calldata of the form `gdi:<sha256(envelope)>` against fixture block metadata. Live Ethereum anchoring is not implemented. Block timestamp trust is explicit. EIP-712 is not a time anchor.

## Deferred profiles

Production RFC 3161 remains disabled until the verification obligations above are implemented and tested against interoperable vectors. Ethereum live anchoring requires RPC policy and cost accounting; see `phase2/DEFERRED.md` and `phase2/src/anchors/ethereum.py`.

## v0.1 linkage non-claims

Filling `evaluatorManifest.commitment.algorithm` with `"other"` and `digest` with the Phase II digest does not make v0.1 validate the salt, JCS, or anchor. v0.1 still checks only declared `committedAt` versus `submissionDeadline`. Independently verifiable pre-deadline existence is a Phase II graph check.

Do not write algorithm `"sha256"` for a salted domain-separated digest. That identifier would describe a different function.

## Authority

Phase II objects MUST NOT contain `authorityKind`, `decisionAuthority`, `institutionalAuthority`, or `fundingAuthority`. Graph verification fails if they do. Graph verification never copies those fields into a v0.1 `decision` object. AI remains advisory.
