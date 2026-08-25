# Workflow adapters

Adapters marshal ordinary grant-workflow evidence into GDI draft records under a versioned profile. They do **not** score merit, recommend approval/rejection, infer eligibility without confirmation, resolve conflicts, invent quorum, or assign institutional authority.

## Provenance kinds

Every material mapped field MUST carry one of:

| Kind | Meaning |
|---|---|
| `direct` | Value taken from an identified source artifact/path |
| `derived` | Deterministic derivation with a recorded rule ID |
| `interpretive` | Operator-entered/confirmed interpretation |
| `unknown` | Not available / not established |

Interpretive and other material non-direct mappings require an operator confirmation record. Confirmations are provenance of interpretation, not proof that the interpretation is correct.

## Mapping version

Change the adapter `mappingVersion` whenever mapping rules change. Do not silently alter historical mapping semantics in place.

## CLI-shaped operations (library today)

```text
adapter discover <source>     # identify supported artifact class
adapter import <source>       # emit normalized.json
adapter map normalized.json --profile <id> --out record-draft.json
adapter explain record-draft.json
```

Python entry points live in `adapters/__init__.py`. Tests: `scripts/test_adapters.py`.

## Forbidden

- merit scoring
- converting `unknown` to `pass`/`fail`
- marking roster members as participants without source/confirmation
- setting `decision.authorityKind` to `ai`
- hidden network calls during verification
