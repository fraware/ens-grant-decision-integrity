# Preserved source artifacts

This module closes one narrow provenance gap: a schema 0.2 `policyPinning` entry can be checked against exact preserved bytes instead of treating a hash copied into metadata as self-verifying evidence.

## Assurance chain

For each pinned governing-policy source, verification is deliberately split into distinct checks:

1. the decision record passes its selected schema and semantic conformance rules;
2. `policyPinning` declares an exact URI and `sha256:<hex>` content hash;
3. source-artifact metadata identifies a captured source URI (and, when applicable, an exact resolved URI), capture metadata, byte length, and the same content-hash format;
4. the verifier re-hashes the preserved bytes and checks both byte length and SHA-256;
5. the policy-pin verifier requires an exact URI match against `sourceUri` or `resolvedUri` and exact hash equality.

The source-artifact verifier does not decide which governance surface a source controls. That relation remains on the decision record and is checked by schema 0.2 conformance (`POL007`–`POL010`). This avoids making capture metadata a second authority for policy semantics.

## Source-artifact v1

Schema: `schema/source-artifact.schema.json`.

Required fields are `artifactVersion`, `artifactId`, `sourceUri`, `capturedAt`, `mediaType`, `byteLength`, `contentHash`, and `capture`. Optional fields include `resolvedUri`, `httpStatus`, `storedPath`, `archiveUri`, `contentEncoding`, and observations.

`contentHash` is SHA-256 over the exact bytes supplied to the capture tool, encoded as `sha256:<64 lowercase hex>`. No text normalization, HTML rendering, PDF extraction, canonical JSON conversion, or other content transformation occurs before hashing.

For dynamic web material, preserve the exact response/export bytes actually relied on when redistribution and policy permit. If a browser export, API response, repository blob, or manually saved document is the reviewed artifact, identify that capture method explicitly; do not imply byte identity with another representation.

## Capture storage model

Captured content bytes are deduplicated by SHA-256 under `sha256/<prefix>/<digest>/source.bytes`. Capture provenance is stored separately under an artifact-ID-derived path in `captures/`. Therefore two distinct source/capture events may safely refer to the same immutable content bytes without overwriting each other's metadata or capture log.

`artifactId` is unique within a capture store. Reusing an existing artifact ID fails closed (`CAP020`) rather than silently replacing provenance.

The artifact ID itself is hashed before it participates in a filesystem path, so an untrusted ID does not become a path traversal surface.

## Network capture boundary

The built-in HTTP acquisition path is **SSRF-hardened**, not claimed to be universally SSRF-safe. It rejects unsupported schemes, localhost, private/link-local/reserved destinations, validates each redirect target, defaults to HTTPS, imposes response-size and redirect limits, and records redirect/cross-origin observations.

The standard-library HTTP transport may resolve a hostname again when opening the connection. The current client therefore does **not** establish immunity to DNS rebinding between preflight validation and transport connection. That limitation is emitted in network-capture evidence. Operators requiring a stronger network boundary should capture through infrastructure that pins the vetted destination IP while preserving TLS hostname/SNI verification, then feed the resulting bytes to the offline source verifier.

Network capture is acquisition evidence only. It does not authenticate institutional source ownership, prove publication time, or turn a redirect target into a semantically equivalent governing-policy URI.

## CLI

Build metadata from already captured bytes:

```bash
gdi source -- build \
  --artifact-id policy-001 \
  --source-uri https://example.org/policy \
  --file policy.html \
  --media-type text/html \
  --method http \
  --tool curl \
  --tool-version 8.x \
  --out policy-001.artifact.json
```

Capture a local file into the provenance store:

```bash
gdi source -- capture \
  --artifact-id policy-001 \
  --source-uri https://example.org/policy \
  --method manual-file \
  --file policy.html \
  --media-type text/html \
  --out-dir evidence
```

Verify metadata against preserved bytes:

```bash
gdi verify-source \
  --metadata policy-001.artifact.json \
  --file policy.html
```

Verify schema 0.2 policy pins against one or more byte-verified artifacts:

```bash
python scripts/verify_policy_pins.py \
  --record record.json \
  --artifact policy-001.artifact.json policy.html
```

Run record conformance separately or use a verification bundle that contains the relevant source artifacts. A policy-pin byte match is not a substitute for record semantic conformance.

## Claim boundary

A successful source-artifact check establishes exact byte identity under SHA-256 for the supplied file and metadata. A successful policy-pin check additionally establishes that at least one byte-verified artifact matches the pin's exact URI and content hash.

It does **not** establish:

- that the source is true, complete, authoritative, or institutionally adopted;
- that the declared URI is owned by the expected institution;
- that the bytes existed at `capturedAt` or `policyPinning.pinnedAt` under an independent timestamp;
- that the source governs the decision surface named by the record without the separate conformance check;
- that a later live page still contains the captured bytes;
- that an archive URI is immutable or independently trustworthy;
- that network capture is protected against every DNS-rebinding or transport-layer attack.

These limits are part of the interface, not optional caveats.
