# Public record projection

Deterministic confidential-to-public projection for grant decision records. Given a canonical confidential record and a versioned projection spec, the module produces a public record with field allowlists, redaction categories, and SHA-256 commitments for withheld subtrees.

Projection does **not** claim Merkle or zero-knowledge selective disclosure. Withheld fields become `withheldCommitments` digests only.

## Layout

```
projection/
  schema/projection-spec.schema.json   Versioned projection spec
  src/project.py                       Core projection logic
  src/cli.py                           Command-line interface
  examples/tier-a-projection-spec.json Worked example spec
  tests/                               Determinism and validation tests
```

## Install and test

```bash
python -m pip install -r requirements-dev.txt
python -m pytest projection/tests
```

## CLI

```bash
python projection/src/cli.py \
  --confidential examples/tier-a-simplified-grant.example.json \
  --spec projection/examples/tier-a-projection-spec.json \
  --out /tmp/tier-a-public.json
```

Arguments:

| Flag | Meaning |
|---|---|
| `--confidential` | Canonical confidential record JSON |
| `--spec` | Projection spec JSON |
| `--out` | Output path for the public record JSON |

On success the CLI writes the public record and prints JSON including `ok`, `publicRecord`, `projectionDigestSha256`, and `withheldCommitments`. On failure it prints `ok: false` with an error `code` and exits non-zero.

The output public record validates against `schema/grant-decision-public-projection-0.2.schema.json` when top-level fields are withheld.

## Library API

From `projection/src/project.py`:

- `project_record(confidential, spec) -> ProjectionResult` — deterministic mapping;
- `verify_withheld_commitment(confidential, path, expected_digest) -> bool` — reopen a withheld top-level digest;
- `ProjectionResult` fields: `public_record`, `projection_digest`, `withheld_commitments`;
- `ProjectionError` carries an optional machine-readable `code`.

## Spec domain and limits

Projection specs use domain string `ens-gdi/public-projection/v1` and `specVersion` `"1"`. The projection digest is SHA-256 over RFC 8785 JCS bytes of a projection envelope that binds domain, spec version, record id, public record, and withheld digests.

Reference limits for v1:

- `fieldAllowlist` must be non-empty;
- every top-level source field must be either explicitly allowlisted for publication or explicitly redacted/withheld; silent omission raises `PROJ011`;
- a top-level field cannot be both published and withheld; that ambiguity raises `PROJ012`;
- redaction paths must be **top-level** field names (nested paths raise `PROJ008`);
- redaction categories are `privacy`, `security`, `commercial`, `legal`, `contractual`, `other`;
- allowlisted fields must exist on the confidential record;
- projection does not mutate the confidential input;
- v1 uses the public record's `integrity` field for generated projection-integrity metadata. A non-null source `integrity` value therefore raises `PROJ013` rather than being silently overwritten. A future projection version should separate source-integrity disposition from generated projection integrity explicitly.

Error codes: `PROJ001` (path not found), `PROJ003` (unknown category), `PROJ004` (unsupported spec version), `PROJ005` (domain mismatch), `PROJ006` (empty allowlist), `PROJ007` (missing allowlisted field), `PROJ008` (nested redaction path), `PROJ009` (duplicate allowlist field), `PROJ010` (duplicate redaction path), `PROJ011` (silent top-level omission), `PROJ012` (publish/withhold overlap), `PROJ013` (non-null source integrity would be overwritten).

## Trust boundary

A projection pass establishes:

- deterministic mapping from the supplied confidential input to the public output under the declared spec;
- explicit top-level disposition: no supplied top-level field disappears silently;
- SHA-256 commitments over withheld top-level subtrees listed in `withheldCommitments`.

It does **not** establish that the confidential input is complete, that redaction policy was substantively correct or followed outside this object, Merkle or ZK selective disclosure, or that withheld material matches the commitments without separate reveal verification.

## Related documents

- `ADOPTION.md` — public-record workflow for ENS programs
- `CONFORMANCE.md` — schema 0.2 conformance extensions
- `phase2/DEFERRED.md` — why cryptographic selective disclosure is deferred
