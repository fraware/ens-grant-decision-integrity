# Deferred work, non-goals, and closure boundary

This register summarizes deferred technical work and explicit non-goals for the `v1.0.0` assurance boundary. It is derived from the engineering completion scope (Workstream 10). Phase II-specific deferred cryptography remains detailed in `phase2/DEFERRED.md`.

## Explicit non-goals for v1.0.0

1. **No grant-merit or fairness scoring engine** — no universal scoring, automatic approve/reject as a repository feature, fairness/legitimacy/evaluator-quality scores, or model-based merits appeals.
2. **No transfer of institutional authority to automation** — automated evaluators may be advisory only; they never become final funding authority via Phase II, signatures, hashes, adapters, or profiles.
3. **No universal DAO governance abstraction** — ENS-oriented profiles/adapters are intentional; do not expand into a universal governance product in the final phase.
4. **No universal identity system** — no DID/credential issuance or global evaluator identity infrastructure.
5. **No dashboard as an assurance substitute** — canonical outputs are machine-readable records, bundles, projections, and assurance reports.
6. **No blockchain for optics** — no live Ethereum anchoring without a concrete adopter and documented trust/cost assumptions; fixture profiles preserve the design boundary.
7. **No ZK/Merkle selective disclosure without demonstrated need** — projection path disposition and subtree commitments are the v1 privacy model.
8. **No false hosted-model reproducibility** — keep `not-replayable` when execution cannot be independently reproduced.
9. **No full historical truth reconstruction** — the corpus is a public/authorized evidence reconstruction study; missing public evidence is not proof that internal process did not exist.
10. **No silent v0.1 redesign** — use versioned extensions after recurring empirical needs are demonstrated.

## Deferred technical extensions

| Item | Reopen when |
|---|---|
| Live Ethereum profile | Adopter needs chain-time/inclusion semantics and accepts RPC/finality/key/gas/archive assumptions |
| Cryptographic selective disclosure | Ordinary subtree commitments fail a concrete privacy/audit need |
| Controlled implementation re-execution (C7-class) | Program advertises historical execution/re-execution claims with a reproducible execution contract |
| External monitoring / log witnesses | Need consistency monitoring, cosignatures, gossip, or checkpoint archival beyond current trust assumptions |
| Automated policy-change detection as judgment | Keep human confirmation for material governance-change decisions at v1 |
| Rich web UI / hosted service | Must preserve offline verifiability; must not become a trust requirement for old bundles |

## Research questions (carry forward)

Preserve as findings rather than patching the stable schema solely to erase them:

- representation of publicly unknown/protected applicant identity;
- whether aggregate cohort decisions need a separate process-observation object;
- minimum authority-member identity for committee reconstructability;
- public observability of challenge/correction processes;
- which fields are systematically interpretive rather than direct-source;
- administrative burden by materiality tier;
- equality leakage risk of deterministic withheld commitments for specific fields.

## Maintenance after v1.0.0

Expected maintenance: security/correctness fixes; supported Python/dependency compatibility; external trust-policy updates for roots/log shards where possible; versioned new ENS profiles; explicit protocol versioning; deprecation windows for public CLI/API; historical wire-format parseability per compatibility policy; fixture evidence labeled test-only.

Do not promise indefinite support for every protocol version. Publish a support matrix with the release.

## Change-control for post-v1 features

A post-v1 feature enters scope only with a written issue/RFC stating adopter need, proposition/claim, why existing mechanisms fail, threat/failure mode, evidence object and trust boundary, privacy impact, administrative burden, compatibility plan, acceptance tests, and explicit non-claims.
