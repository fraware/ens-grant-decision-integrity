# Public projection / redaction worksheet

- Canonical record ID / digest: __________________
- Projection spec version: __________________
- Profile ID: __________________

| JSON Pointer path | Disposition (publish/withhold/drop) | Redaction basis | Unavailable vs protected | Operator |
|---|---|---|---|---|
| | | | | |

## Rules

- Every present source subtree needs an explicit disposition under the active projection rules.
- Redaction basis requires explicit operator/source input.
- Public outputs must not contain protected source content.
- Equality / low-entropy leakage of deterministic commitments is a residual risk; document sensitive fields.
- No Merkle/ZK claim unless separately implemented and reviewed.
