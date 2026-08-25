# Public record projection

Deterministic confidential-to-public projection for grant decision records.

Projection does **not** claim Merkle proofs, zero-knowledge proofs, or selective-disclosure cryptography.

The unified `gdi` CLI exposes `project`, `verify-projection`, and `verify-withheld`. Implementation remains under `projection/src/`.

## CLI

```bash
python -m gdi project \
  --confidential examples/tier-a-simplified-grant.example.json \
  --spec projection/examples/tier-a-projection-spec-v2.json \
  --out /tmp/tier-a-public-v2.json --force
```

## Projection v2

Domain `ens-gdi/public-projection/v2`. RFC 6901 paths. Actions: `publish-subtree`, `withhold-subtree`, `drop-by-profile`, `descend`. Arrays are atomic (`/array/0` rejected).

Withheld digests: `SHA-256("ens-gdi/withheld-subtree/v2" || 0x00 || pointer || 0x00 || JCS(subtree))` as `sha256-jcs-path-v2:<hex>`.

Generated integrity is `projectionIntegrity` and never overwrites source `integrity`.

### Privacy limitation

Unsalted withheld commitments are dictionary-attackable for low-entropy values. Do not withhold tiny secrets unless the profile accepts equality leakage.

## v1

Historical v1 remains verifiable under `ens-gdi/public-projection/v1`.
