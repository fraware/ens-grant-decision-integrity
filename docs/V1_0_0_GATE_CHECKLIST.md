# v1.0.0 Gate Checklist (Gates A-L)

Date: 2026-08-25
Tag decision: **DO NOT TAG v1.0.0** — blocking items remain.

| Gate | Status | Notes |
|---|---|---|
| A Corpus / PR19 | pass / partial | PR #19 merged; case count still 4/8 |
| B Double annotation | blocked | Human second annotations pending |
| C Claim registry | pass | Merged via PR #21 |
| D Unified verifier | pass / partial | gdi wrap merged; orchestration incomplete |
| E Trust / C4A | pass / partial | Schema + C4A text merged; runtime wiring partial |
| F Projection v2 | pending | Stashed / PR in progress |
| G Rekor v2 | pending | Stashed / PR in progress |
| H RFC3161 | pass (fail-closed) | Production remains fail-closed by design |
| I Source capture | blocked / pending | SSRF-safe capture not fully shipped |
| J ENS adapters | pending | Profiles/templates in this PR |
| K Packaging / CI / security | pending | Docs and additive CI notes in this PR |
| L Friday provenance | blocked | Pre-event freeze done; post-event after 2026-08-28 |

## Red-team / non-overclaim

- Do not claim payment from allocation.
- Do not claim the empirical study is complete.
- Do not claim RFC 3161 production C2.
- Do not tag v1.0.0 until every blocking gate is yes.
