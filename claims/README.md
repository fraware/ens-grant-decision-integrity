# ENS GDI Claim Registry

Machine-readable claims for verifier surfaces live in `claim-registry.v1.json`, validated by `claim-registry.schema.json`.

## Rules

- Every claim ID emitted by verifier code MUST exist in the active registry.
- Active claims MUST list at least one required check.
- Phase II C1–C6 text is imported from `phase2/src/claims.py` / `phase2/CLAIM-MATRIX.md` without changing meanings.
- Signer authorization is **C4A**, not a silent strengthening of C4.
- Agreement, study readiness, allocation, and hashes are not fairness, legitimacy, payment, or authority.

## Regeneration

```bash
python scripts/generate_claim_registry.py
```

## Lookup

```bash
gdi claims --id C2
gdi claims --id PHASE2.C4A.AUTHORIZED_SIGNER
```

## Non-claims

The registry enumerates bounded propositions for package `ens-gdi` `0.4.0` / current verifier surfaces. It does not establish that ENS or any program adopted this repository, that a decision was fair, that funding was paid, or that a future `v1.0.0` gate matrix is complete.