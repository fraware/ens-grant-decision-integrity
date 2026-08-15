# Release Integrity

Repository history is the development record. Release integrity should be anchored to an immutable release object, not to a checksum file that changes inside the same mutable tree.

## v0.1 release procedure

For a public v0.1 release:

1. merge the reviewed hardening changes;
2. require green validation on the exact release commit;
3. create an immutable `v0.1.0` tag at that commit;
4. create the release archive from the tagged tree;
5. compute SHA-256 over the release archive;
6. publish the tag, commit identifier, and archive digest together in the release notes;
7. preserve the Simocracy proposal and decision AT-URIs in `provenance/simocracy-funding.json`.

A later release may add an external signature or transparency-log entry for the tag or archive digest.

## Why no in-tree checksum manifest

An in-tree checksum list is useful for detecting accidental local corruption after distribution. It is not an independent authenticity guarantee when the checksums and the files they authenticate are committed and modified together.

The tagged Git tree provides version identity during development. The release archive digest provides a portable integrity check for distributed artifacts.

## Schema-level integrity field

The optional `integrity` object in a decision record remains descriptive in v0.1. This release does not define canonical JSON serialization, record-hash normalization, signature verification, or proof binding.

Those properties must be specified before `integrity.recordHash` can be treated as a cryptographic guarantee. Until then, implementations should avoid making stronger claims from that field.
