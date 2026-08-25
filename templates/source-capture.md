# Source-capture checklist

- Round / policy artifact label: __________________
- Profile ID: __________________
- Capture required by profile? yes | no

## Capture record

| Field | Value |
|---|---|
| Source URI | |
| Resolved URI (if different) | |
| Capture method | |
| Captured at (metadata only) | |
| Byte length | |
| SHA-256 | |
| Access class (public/reference-only/protected) | |
| Media type | |

## Verification

- [ ] Exact preserved bytes re-hash to the recorded digest
- [ ] Policy pin URI permitted and digest matched (when schema 0.2 pinning used)
- [ ] No implicit network fetch during verification
- [ ] Byte identity is not treated as source truth, ownership, adoption, or time

## Operator confirmation

- [ ] `confirm-unavailable-vs-protected` where fields are missing or redacted
