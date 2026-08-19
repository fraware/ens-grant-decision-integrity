# Public record projection

Deterministic rules for projecting a confidential canonical grant decision record into a publishable public record without disclosing withheld subtrees.

## What projection establishes

- A public record containing only allowlisted top-level fields.
- Redacted paths replaced by category-tagged commitments: `SHA-256(JCS(withheld subtree))`.
- A projection envelope digest binding the public record and withheld commitments under domain `ens-gdi/public-projection/v1`.

## What projection does not establish

- That the confidential record is true or complete.
- That redaction policy was followed outside this algorithm.
- Merkle or zero-knowledge selective disclosure (see `phase2/DEFERRED.md`).

## Usage

```bash
python projection/src/cli.py \
  --confidential examples/tier-a-confidential.example.json \
  --spec projection/examples/tier-a-projection-spec.json \
  --out /tmp/tier-a-public.json
```

Run tests:

```bash
python -m pytest projection/tests
```

Schema: `projection/schema/projection-spec.schema.json`.
