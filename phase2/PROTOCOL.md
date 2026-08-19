# Phase II Protocol

Claim-bounded evaluator-manifest commitment, anchoring, run attestation, and replay. Implementers MUST treat `CLAIM-MATRIX.md` as the ceiling of what a verifier may say.

This protocol is version `1` of the Phase II objects. The v0.1 grant-decision `schemaVersion` remains `"0.1"`.

## 1. Design target

Close four gaps left open by v0.1 (`CHARTER.md` §5.3, `DESIGN-NOTES.md` §3):

1. Deterministic manifest canonicalization.
2. Hiding and binding commitment, round-bound.
3. Independent external existence-before-deadline evidence under an explicit profile.
4. Signed run and replay evidence that cannot become decision authority.

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

### 7.1 rekor-v1 (implemented)

Hashedrekord of SHA-256(JCS(envelope)). Receipt stores log index, UUID, signed entry timestamp, inclusion proof, signed checkpoint, and hashedrekord body. Verification uses the client-pinned Rekor v1 production public key, not a key carried solely in the receipt.

`TemporalClaim.anchored_at` is the SET `integratedTime` as UTC. C2 succeeds only when `anchored_at < applicationDeadline`.

See `CLAIM-MATRIX.md` for the trust boundary.

### 7.2 rekor-v1-recorded-fixture (test and retrospective illustration)

Same receipt shape and verification algorithm, with a test-log key. Does not establish public Rekor inclusion.

### 7.3 rfc3161

Profile `rfc3161` posts a timestamp query to a configured TSA endpoint and verifies the returned CMS `TimeStampToken` under a pinned trust root. Profile `rfc3161-recorded-fixture` issues and verifies signed `TSTInfo` fixtures under a test TSA key shipped with the repository. See `CLAIM-MATRIX.md` for trust boundaries.

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

## 9. Replay

Per-layer outcomes:

| Outcome | Meaning |
|---|---|
| `exact-match` | Recomputed digest equals the attested digest. |
| `bounded-match` | Distance is within a declared numeric bound. |
| `diverged` | Recomputed digest does not match. |
| `not-replayable` | The layer cannot be replayed; a reason is required. |

Deterministic layers in this implementation: `preprocessing`, `retrieval-snapshot`, `scoring`, `aggregation`. Digest is SHA-256 of JCS(layer input).

`hosted-generation` is `not-replayable` unless a program marks a model `replayable: true` and supplies replay material. Hosted-model non-replayability does not void independent deterministic-layer outcomes.

## 10. Evidence bundle and graph

Schema: `schema/evidence-bundle.schema.json`.

`verify-graph` schema-validates the bundle, verifies the selected anchor, applies reveal policy, verifies run DSSE if present, checks replay if present, links the v0.1 record, and enforces C6.

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

## 13. What this protocol will not do

It will not introduce a dashboard, scoring model, new cryptographic primitive, ZK disclosure, DAO identity system, or production KMS. It will not give AI funding authority.
