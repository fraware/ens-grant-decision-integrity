# Release Integrity

The reviewed Git commit SHA is the content-addressed anchor for a release. A Git tag is a human-readable release label and can be moved or deleted, so release notes should publish both the tag and the commit SHA.

## v0.1 release procedure

For a public v0.1 release:

1. merge the reviewed changes;
2. require green validation on the exact release commit;
3. record that commit SHA;
4. create an annotated `v0.1.0` tag pointing to that commit;
5. create an explicit release archive from the reviewed commit and attach that exact file to the release;
6. compute SHA-256 over the attached archive;
7. publish the tag, commit SHA, archive filename, and SHA-256 digest together in the release notes;
8. preserve the Simocracy proposal and decision AT-URIs in `provenance/simocracy-funding.json`.

The archive digest authenticates only the exact archive file whose digest is published. v0.1 does not claim reproducible archive generation across tools or platforms.

A later release can define deterministic packaging, signed tags or attestations, and an external transparency anchor.

Phase II, when released, remains anchored to a Git commit SHA under the same procedure. Repository version may move to `0.2.0` only at a Phase II release tag. Grant-decision `schemaVersion` stays `"0.1"` unless a versioned schema change is separately specified. A Rekor envelope over an evaluator-manifest commitment is not a signed release of this repository and must not be described as one.

Detailed Phase II exit gates, pre-tag checklist, and tag procedure: `phase2/RELEASE.md`.

## Why no in-tree checksum manifest

An in-tree checksum list can detect accidental corruption in a copied tree. It is not an independent authenticity anchor when the checksums and the files they describe can change in the same commit.

The reviewed commit SHA identifies the release tree. The published archive digest provides a portable integrity check for the distributed release artifact.

## Schema-level integrity field

The optional `integrity` object in a decision record remains descriptive in v0.1. This release does not define canonical JSON serialization, record-hash normalization, signature verification, or proof binding.

`integrity.recordHash` therefore must not be treated as a cryptographic guarantee under v0.1 alone.
