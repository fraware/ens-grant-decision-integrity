# Public record projection

Deterministic confidential-to-public projection for grant decision records. Given a canonical confidential record and a versioned projection spec, the module produces a public record with field allowlists, redaction categories, and SHA-256 commitments for withheld subtrees.

Projection does **not** claim Merkle or zero-knowledge selective disclosure. Withheld fields become `withheldCommitments` digests only.

## Layout

```
projection/
  schema/projection-spec.schema.json   Versioned projection spec
  src/project.py                     Core projection logic
  src/cli.py                         Command-line interface
  examples/tier-a-projection-spec.json Worked example spec
  tests/                             Determinism and validation tests
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

The output public record validates against `schema/grant-decision-public-projection-0.2.schema.json` when top-level fields are withheld.

## Spec domain

Projection specs use domain string `ens-gdi/public-projection/v1`. The projection digest is SHA-256 over RFC 8785 JCS bytes of the spec and redaction metadata.

## Trust boundary

A projection pass establishes:

- deterministic mapping from confidential input to public output under the declared spec;
- SHA-256 commitments over withheld subtrees listed in `withheldCommitments`.

It does **not** establish that the confidential input is complete, that redaction policy was followed outside this object, or that withheld material matches the commitments without separate reveal verification.

## Related documents

- `ADOPTION.md` — public-record workflow for ENS programs
- `CONFORMANCE.md` — schema 0.2 conformance extensions
- `phase2/DEFERRED.md` — why cryptographic selective disclosure is deferred
