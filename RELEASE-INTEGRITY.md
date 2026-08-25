# Release Integrity

The reviewed Git commit SHA is the content-addressed anchor for a release. A Git tag is a human-readable release label and can be moved or deleted, so release notes should publish both the tag and the commit SHA.

## Current release lineage

| Tag | Commit role | Notes |
|---|---|---|
| `v0.1.0` | Charter, schema 0.1, conformance, Marketplace example | Grant-decision `schemaVersion` `"0.1"` |
| `v0.2.0` | Phase II commitment, anchoring, run attestation, replay | Additive; `schemaVersion` remains `"0.1"` |
| `v0.3.0` | Schema 0.2 extensions, projection, alternate anchor fixtures | Additive |
| `v0.3.1` | Public-readiness documentation and fixture URI corrections | No validator or schema behavior changes |
| `v0.3.2` | Documentation accuracy: version labels, allocation/payment caveat, stale scope/procedure text | No validator or schema behavior changes |

**Package line `0.4.0` (current `pyproject.toml` / `gdi`):** engineering checkpoint on `main` after `v0.3.2`. Includes unified verifier packaging, claim registry, profiles/adapters, corpus expansion, projection v2, and Rekor v2 module surfaces among other hardening. **Not** an annotated Git tag unless/until one is created. **Not** `v1.0.0`. Do not describe `0.4.0` tree behavior as part of tag `v0.3.2`.

Grant-decision `schemaVersion` stays `"0.1"` unless a versioned schema change is separately specified. Schema `"0.2"` is an optional additive profile. Phase II evaluator manifest, commitment envelope, anchor receipt, and run predicate retain version `"1"`; replay reports and evidence bundles are independently versioned (historical v1; current v2). Projection has v1 and v2 engines.

Release URLs:

- Latest: https://github.com/fraware/ens-grant-decision-integrity/releases/latest
- Tags: https://github.com/fraware/ens-grant-decision-integrity/releases

## Release procedure

For a public release:

1. merge the reviewed changes to `main`;
2. require green validation on the exact release commit (local contract in `VALIDATION.md`; CI jobs `conformance`, `phase2`, `schema-02`, plus additive `package`, `lint-type`, and `security` for the release candidate);
3. record that commit SHA;
4. build release assets from that exact SHA in a clean Python 3.12 environment with the hash-locked dependency set (`requirements.lock.txt`);
5. create an annotated tag pointing to that commit;
6. attach explicit release assets (not only auto-generated source archives):
   - source archive from the exact release commit;
   - Python wheel;
   - source distribution (sdist);
   - SHA-256 checksum manifest covering **all attached release assets**;
   - SBOM (CycloneDX or SPDX);
   - machine-readable release manifest (tag, commit, artifact names/hashes/sizes, validation report reference);
   - release validation report;
   - optional signed build provenance/attestation when infrastructure supports it;
7. verify every artifact hash before and after publication;
8. publish the tag, commit SHA, asset filenames, and SHA-256 digests together in the release notes;
9. preserve the Simocracy proposal and decision source identifiers in provenance records, keeping allocation-decision status separate from payment authorization, transfer, receipt, and settlement evidence.

The archive/wheel/sdist digest authenticates only the exact file whose digest is published. This repository does **not** claim byte-reproducible builds across tools or platforms unless two independent clean builds of the same commit produce byte-identical target artifacts under a documented process and that evidence is attached. Deterministic inputs (Python 3.12, locked deps, `python -m build`) are documented without equating them to byte reproducibility.

Do not repeat the v0.3.2 pattern of a tag with no attached assets while advertising an attached-archive integrity procedure.

A Rekor envelope over an evaluator-manifest commitment is not a signed release of this repository and must not be described as one.

Packaging, SBOM tooling, and branch-protection requirements: `docs/PACKAGING-AND-SECURITY.md`, `docs/BRANCH-PROTECTION.md`.

Detailed Phase II exit gates, pre-tag checklist, and tag procedure: `phase2/RELEASE.md`.

## Evidence-version discipline

Released wire formats are immutable historical contracts. A corrected semantic mechanism must receive a new child format when required, and a parent container must also be versioned when accepting the new child would otherwise change the released parent contract.

For the current hardening line:

- replay-report v1 remains the historical schema; its `bounded-match` field remains parseable but is rejected as evidence by the current verifier;
- replay-report v2 is the current artifact-recomputation report;
- evidence-bundle v1 remains the historical parent for replay-report v1;
- evidence-bundle v2 carries current replay-report v2 and current disclosure-state constraints.

A release note must identify which versions are read-compatible and which are emitted for new evidence. It must not describe unreleased behavior as part of an earlier tag.

## Funding-provenance discipline

An allocation amount, a ratification state, payment authorization, a transfer, receipt, and settlement are distinct propositions. Release notes and provenance files should preserve the exact status represented by the authoritative source and should not infer a later financial state from an earlier one.

The current repository provenance snapshot records $219 in Simocracy allocation decisions and does not record payment or receipt evidence. If that state changes, update provenance only after the relevant authoritative artifact exists; preserve the earlier snapshot rather than rewriting history.

## Why no in-tree checksum manifest for the source tree

An in-tree checksum list can detect accidental corruption in a copied tree. It is not an independent authenticity anchor when the checksums and the files they describe can change in the same commit.

The reviewed commit SHA identifies the release tree. The **published** SHA-256 manifest for release assets (wheel, sdist, source archive, SBOM, validation report) provides a portable integrity check for distributed artifacts. That release-asset manifest belongs on the GitHub Release (or equivalent), not as a substitute for the commit SHA.

## Schema-level integrity field

The optional `integrity` object in a decision record remains descriptive under schema 0.1 alone. Schema 0.1 does not define canonical JSON serialization, record-hash normalization, signature verification, or proof binding for that field.

Projection outputs may set `integrity.recordHash` under algorithm `sha256-jcs-projection-v1`. That hash authenticates the projection envelope described in `projection/README.md`; it is not a general-purpose signature over an arbitrary decision record.

`integrity.recordHash` therefore must not be treated as a cryptographic guarantee under schema 0.1 alone.
