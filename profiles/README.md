# Operational adoption profiles

Machine-readable, versioned profiles that state **evidence and reconstruction requirements** for ENS-oriented grant workflows. Profiles do not encode substantive grant criteria, merit scores, or institutional authority.

## Profiles

| Profile ID | Tier | Intent |
|---|---|---|
| `ens-foundation-tier-a-v1` | A | Low-value / routine; minimal burden |
| `ens-foundation-tier-b-v1` | B | Material community grants |
| `ens-foundation-tier-c-v1` | C | High-value / contested / committee-heavy |
| `legacy-spp-mapping-v1` | legacy | Historical SPP mapping conventions only |

Schema: `profile.schema.json` (`profileVersion` `"1"`).

## Invariants

- Adapters using these profiles marshal evidence; they do not score merit, infer eligibility without confirmation, resolve conflicts, invent quorum, or assign authority.
- Material mappings require operator confirmation and field-level provenance (`direct` | `derived` | `interpretive` | `unknown`).
- Profile use is not ENS adoption or endorsement.

## Validation

```bash
python -m pytest scripts/test_profiles.py scripts/test_adapters.py
```
