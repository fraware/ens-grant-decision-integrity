# Release Integrity

The reviewed Git commit SHA is the content-addressed anchor for a release. A Git tag is a human-readable release label and can be moved or deleted, so release notes should publish both the tag and the commit SHA.

## Current release lineage

| Tag | Commit role | Notes |
|---|---|---|
| `v0.1.0` | Charter, schema 0.1, conformance, Marketplace example | Grant-decision `schemaVersion` `"0.1"` |
| `v0.2.0` | Phase II commitment, anchoring, run attestation, replay | Additive; `schemaVersion` remains `"0.1"` |
| `v0.3.0` | Schema 0.2 extensions, projection, alternate anchor fixtures | Additive |
| `v0.3.1` | Public-readiness documentation and fixture URI corrections | No validator or schema behavior changes |
| `v0.3.2` | Documentation accuracy: version labels, unpaid allocation caveat, stale scope/procedure text | No validator or schema behavior changes |

Grant-decision `schemaVersion` stays `"0.1"` unless a versioned schema change is separately specified. Schema `"0.2"` is an optional additive profile. Phase II protocol objects use their own version `"1"`.

Release URLs:

- Latest: https://github.com/fraware/ens-grant-decision-integrity/releases/latest
- Tags: https://github.com/fraware/ens-grant-decision-integrity/releases

## Release procedure

For a public release:

1. merge the reviewed changes to `main`;
2. require green validation on the exact release commit (local contract in `VALIDATION.md`; CI jobs `conformance`, `phase2`, `schema-02`);
3. record that commit SHA;
4. create an annotated tag (for example `v0.3.2`) pointing to that commit;
5. create an explicit release archive from the reviewed commit and attach that exact file to the release;
6. compute SHA-256 over the attached archive;
7. publish the tag, commit SHA, archive filename, and SHA-256 digest together in the release notes;
8. preserve the Simocracy proposal and decision AT-URIs in `provenance/simocracy-funding.json`, including the unpaid-allocation caveat.

The archive digest authenticates only the exact archive file whose digest is published. This repository does not claim reproducible archive generation across tools or platforms.

A later release can define deterministic packaging, signed tags or attestations, and an external transparency anchor.

A Rekor envelope over an evaluator-manifest commitment is not a signed release of this repository and must not be described as one.

Detailed Phase II exit gates, pre-tag checklist, and tag procedure: `phase2/RELEASE.md`.

## Why no in-tree checksum manifest

An in-tree checksum list can detect accidental corruption in a copied tree. It is not an independent authenticity anchor when the checksums and the files they describe can change in the same commit.

The reviewed commit SHA identifies the release tree. The published archive digest provides a portable integrity check for the distributed release artifact.

## Schema-level integrity field

The optional `integrity` object in a decision record remains descriptive under schema 0.1 alone. Schema 0.1 does not define canonical JSON serialization, record-hash normalization, signature verification, or proof binding for that field.

Projection outputs may set `integrity.recordHash` under algorithm `sha256-jcs-projection-v1`. That hash authenticates the projection envelope described in `projection/README.md`; it is not a general-purpose signature over an arbitrary decision record.

`integrity.recordHash` therefore must not be treated as a cryptographic guarantee under schema 0.1 alone.
