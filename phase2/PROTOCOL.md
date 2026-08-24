# Phase II Protocol

Claim-bounded evaluator-manifest commitment, anchoring, run attestation, and replay evidence. Implementers MUST treat `CLAIM-MATRIX.md` as the ceiling of what a verifier may say.

The evaluator manifest, commitment envelope, anchor receipt, and run predicate retain their existing version-1 identifiers. Replay reports and evidence bundles are independently versioned: historical replay report v1 and evidence-bundle v1 remain schema-frozen, while corrected artifact-recomputation semantics are emitted as replay report v2 and carried by evidence-bundle v2. The v0.1 grant-decision `schemaVersion` remains `"0.1"`.

## 1. Design target

Close four gaps left open by v0.1 (`CHARTER.md` §5.3, `DESIGN-NOTES.md` §3):

1. Deterministic manifest canonicalization.
2. Hiding and binding commitment, round-bound.
3. Independent external existence-before-deadline evidence under an explicit profile.
4. Signed run assertions and replay evidence that cannot become decision authority.

## 2. Canonicalization

- Internet JSON (RFC 7493) only.
- Canonical bytes: RFC 8785 JCS of the manifest, UTF-8.
- No alternate whitespace, key order, or Unicode form.
- Integers that cannot be represented exactly in IEEE 754 binary64 MUST be encoded as strings.
- `NaN`, `Infinity`, and lone surrogates are rejected.
- The production adapter is the pinned `rfc8785` library. Tests compare it to an independent second implementation.

## 3. Evaluator manifest

Schema: `schema/evaluator-manifest.schema.json`. `manifestVersion` is `"1"`. Required fields:

`manifestVersion`, `programId`, `roundId`, `applicationDeadline`, `models`, `instructions`, `retrieval`, `tools`, `parameters`, `aggregation`, `humanReviewPolicy`, `canonicalization`.

`canonicalization` MUST be `"RFC8785"`.

Public normative rules (mandate, eligibility, evaluation dimensions, evidence standards, conflict rules, challenge rights, human authority) remain on v0.1 governing-policy surfaces. They MUST NOT exist only inside a hidden manifest.

Sensitive operational detail MAY remain undisclosed until reveal or selective audit. Absence of disclosure is not a cryptographic selective-disclosure proof.

## 4. Commitment

Let `JCS(manifest)` be the canonical UTF-8 bytes.

Let `salt` be 32 bytes from a CSPRNG (`secrets.token_bytes(32)`).

Let `domain` be the UTF-8 bytes of `ens-gdi/evaluator-manifest/v1` followed by a single `0x00` byte.

```
commitmentDigest = SHA-256(domain || salt || JCS(manifest))
```

The digest is encoded as lowercase hex. The domain string is versioned and MUST NOT be reused for another object type.

Salt is withheld from the public envelope. It is stored only in reveal material, a selective-audit channel, or an operator secret.

## 5. Envelope

Public object, no salt, no hidden prompt or config:

```json
{
  "type": "ens-gdi-evaluator-manifest-commitment",
  "version": "1",
  "programId": "...",
  "roundId": "...",
  "applicationDeadline": "...",
  "commitmentAlgorithm": "sha256-salted-jcs-rfc8785-v1",
  "commitmentDigest": "...",
  "manifestSchemaVersion": "1"
}
```

The envelope is itself JCS-canonicalized before hashing for the hashedrekord and before anchoring. `programId`, `roundId`, and `applicationDeadline` MUST equal the corresponding manifest fields.

## 6. Reveal states

| Phase II state | v0.1 `revealStatus` |
|---|---|
| (envelope only, pre-reveal) | `committed` |
| `revealed` | `revealed` |
| `selective-audit` | `partially-revealed` |
| `withheld` | `withheld` |

There is no Merkleized selective disclosure in this version. Selective-audit means a private full manifest and salt to an authorized auditor, who publishes a signed result naming verified claims and the disclosure boundary.

Withheld verification reports C2 and C3 only.

## 7. Anchor profiles

```
AnchorAdapter.anchor(envelope_bytes) -> receipt
AnchorAdapter.verify(envelope_bytes, receipt) -> TemporalClaim
```

### 7.1 rekor-v1 (implemented historical profile)

Hashedrekord of SHA-256(JCS(envelope)). Receipt stores log index, UUID, signed entry timestamp, inclusion proof, signed checkpoint, and hashedrekord body. Verification uses the client-pinned Rekor v1 production public key, not a key carried solely in the receipt.

`TemporalClaim.anchored_at` is the SET `integratedTime` as UTC. C2 succeeds only when `anchored_at < applicationDeadline`.

See `CLAIM-MATRIX.md` for the trust boundary. Rekor v1 remains supported for existing evidence; a successor profile should be introduced under a new profile identifier instead of silently changing v1 semantics.

### 7.2 rekor-v1-recorded-fixture (test and retrospective illustration)

Same receipt shape and verification algorithm, with a test-log key. Does not establish public Rekor inclusion.

### 7.3 rfc3161 (reserved; production fail-closed)

The profile identifier `rfc3161` is reserved for standards-conformant production RFC 3161 timestamp verification. The current implementation intentionally refuses production issuance and verification with `TS3178`.

It MUST NOT establish C2 until verification covers the CMS/RFC 3161 obligations named in `CLAIM-MATRIX.md`, including signer selection, signed attributes, message imprint, TSA certificate identification, timestamping authorization/EKU and applicable policy, certificate-path validation against independently configured verifier trust, and request/response binding. Receipt-carried certificate material MUST NOT act as its own trust root.

`rfc3161-recorded-fixture` is an offline test profile. It verifies the repository's simplified signed-`TSTInfo` fixture under an independently supplied test TSA trust root. Fixture issuance requires explicit private-key and certificate material; verification requires explicit trust-root material. Malformed base64/token material, invalid trust material, and signature mismatch fail as structured protocol errors. The fixture is not evidence of third-party TSA service or production RFC 3161 conformance.

### 7.4 ethereum

Profile `ethereum-calldata-fixture` verifies recorded transaction calldata of the form `gdi:<sha256(envelope)>` against fixture block metadata. Live Ethereum anchoring (`ethereum`) is not implemented. See `DEFERRED.md` and `src/anchors/ethereum.py`.

## 8. Run attestation

in-toto Statement v1 wrapped in DSSE.

- `_type`: `https://in-toto.io/Statement/v1`
- `predicateType`: `urn:ens-gdi:phase2:evaluator-run:v1`
- Payload type: `application/vnd.in-toto+json`
- Signature: Ed25519 over DSSE PAE (`DSSEv1`).

This is not a software-build predicate. Meaning: the signer asserts that this run used these inputs and this bound commitment and produced this output digest.

Subject is the run output digest. The predicate binds `manifestCommitmentDigest`, input snapshots, implementation digest, environment notes, operator, human-review state, and per-layer digests.

Signing keys in this repository are test keys generated in the harness. A real program MUST supply its own signing identity. This protocol does not provide a production key-management service.

## 9. Replay evidence

The reference implementation performs **canonical artifact recomputation**: it canonicalizes supplied layer objects and compares their SHA-256 digests with attested layer digests. It does not invoke or re-execute the implementation named in the run attestation. Therefore an artifact match MUST NOT be reported as proof of implementation re-execution.

The defined layer set is exactly `preprocessing`, `retrieval-snapshot`, `scoring`, `aggregation`, and `hosted-generation`. Missing or unexpected attested layer identifiers fail with `RPL010`; duplicate or non-exact report layer sets fail closed. The verifier also recomputes and checks each reported `recomputedDigest`; an outcome label alone is insufficient evidence.

### Replay report v1 — historical wire format

Historical `schema/replay-report.schema.json` has `reportVersion: "1"` and includes `bounded-match`. The schema is retained unchanged for compatibility. The current verifier refuses any v1 `bounded-match` or non-null `bound` with `RPL008`. Cryptographic hash distance is not a meaningful approximation metric for the underlying computation.

A historical v1 report containing only `exact-match`, `diverged`, and `not-replayable` outcomes may still be verified when its evidence fields are consistent with recomputation.

### Replay report v2 — current emitted format

Current `schema/replay-report-v2.schema.json` has `reportVersion: "2"`, exactly five layer records, complete attested/recomputed evidence fields, and outcomes:

| Outcome | Meaning |
|---|---|
| `exact-match` | Canonical digest of the supplied layer artifact equals the attested digest. |
| `diverged` | Canonical digest of the supplied layer artifact does not equal the attested digest. |
| `not-replayable` | The layer is not available for this artifact-recomputation check; `recomputedDigest` is null and a reason is required. |

Digest is SHA-256 of JCS(layer input).

`hosted-generation` is `not-replayable` unless a program marks the layer replayable and supplies the corresponding artifact material. Hosted-model non-replayability does not void independent deterministic-layer artifact outcomes.

If approximate reproducibility is introduced later, it MUST use a separately versioned, type-aware comparator over underlying outputs with explicit algorithm, parameters, units/semantics, and claim boundary. It MUST NOT use distance between cryptographic digest strings.

Actual implementation re-execution is a distinct future protocol surface and would require a versioned execution environment, implementation invocation, input/output capture, comparator semantics, and evidence of what was actually executed.

## 10. Evidence bundle and graph

Historical `schema/evidence-bundle.schema.json` has `bundleVersion: "1"` and remains byte-for-byte compatible with the released v1 wire format; its optional replay report is replay-report v1. New evidence carrying replay-report v2 uses `schema/evidence-bundle-v2.schema.json` with `bundleVersion: "2"`.

`verify-graph` selects the bundle schema from `bundleVersion`, verifies the selected anchor, applies reveal policy, verifies run DSSE if present, checks the version-compatible replay report if present, links the v0.1 record, and enforces C6. Unsupported bundle versions fail closed.

This parent-container versioning prevents corrected replay semantics from being silently inserted into the historical bundle-v1 contract.

## 11. v0.1 linkage

Fill existing `evaluatorManifest` without mutating the v0.1 schema:

- `commitment.algorithm`: `"other"`
- `commitment.digest`: Phase II commitment digest (lowercase hex)
- `commitment.committedAt`: verified anchor time, never a self-declared wall clock
- `revealStatus`: mapped as in §6
- `integrity.sourceUri` (optional): URI of the evidence bundle

Do not silently use algorithm `"sha256"` for this salted JCS commitment.

Phase II objects MUST NOT populate `decision.authorityKind`. Graph verification fails any attempt.

## 12. CLI

```
python phase2/src/cli.py commit|anchor|verify-commitment|reveal|attest-run|verify-run|replay|verify-graph
```

Every command prints the hard non-claims from `CLAIM-MATRIX.md`.

The `replay` command emits replay report v2. New bundles containing that report use `bundleVersion: "2"`. The verifier retains safe read compatibility for historical bundle-v1/replay-v1 evidence but rejects v1 bounded-match evidence.

## 13. What this protocol will not do

It will not introduce a dashboard, scoring model, new cryptographic primitive, ZK disclosure, DAO identity system, production KMS, or live Ethereum mainnet anchoring in this reference client. It will not give AI funding authority. It will not represent artifact recomputation as actual implementation re-execution or production RFC 3161 support while those capabilities are absent.
