# ENS GDI Adopter Guide

Short guide for program operators. Engineering detail lives in `CHARTER.md`, `CONFORMANCE.md`, `VALIDATION.md`, and Phase II docs.

## What problem GDI solves

GDI makes material grant decisions **reconstructable**: a third party can see the procedural basis (rules, eligibility, findings, authority, conflicts, challenges, delivery conditions, and optional AI provenance) from a versioned record and evidence bundle.

## What GDI does not decide

GDI does **not**:

- score applicant merit or produce fairness/legitimacy scores;
- approve or reject applications as a repository feature;
- transfer institutional funding authority to automation;
- establish ENS endorsement merely because a profile was used;
- prove source truth from a content hash alone.

Adapters marshal evidence. Humans and program rules remain the decision-makers.

## Tier A / B / C decision guide

| Tier | When | Expect |
|---|---|---|
| A (`ens-foundation-tier-a-v1`) | Low-value / routine | Core decision record, policy URIs, human authority, correction route, delivery conditions |
| B (`ens-foundation-tier-b-v1`) | Material community grants | Five-surface mapping, policy pinning, authority identity, public projection, clearer challenge process |
| C (`ens-foundation-tier-c-v1`) | High-value / contested / committee-heavy | Stronger preservation, roster/quorum/recusal, protected bundle + projection, Phase II when AI is material |

Use `legacy-spp-mapping-v1` only for retrospective/historical mapping. It does not claim contemporaneous GDI compliance.

## Minimal setup

1. Select a profile from `profiles/`.
2. Fill templates under `templates/` (round setup, roster/conflicts, decision memo, delivery, challenge, projection, source capture; evaluator manifest only if AI is material).
3. Capture/pin policy sources when the profile requires it (`SOURCE-ARTIFACTS.md`).
4. Map workflow artifacts with adapters under operator confirmation (`adapters/`).
5. Validate with the repository validators (`VALIDATION.md`).
6. Publish only what your projection worksheet authorizes.

You do not need to understand cryptographic internals to use safe defaults. If you claim production temporal precedence (C2), you must accept an external trust policy; fixtures are not production C2.

## Privacy model

Keep a protected canonical record. Publish a projection with explicit field dispositions. Redaction basis is an operator/source input. Do not claim Merkle/ZK selective disclosure unless a separately reviewed mechanism exists.

## Automated evaluator boundary

Automated evaluators may be recorded as advisory participants. They never become final funding authority. Phase II commitments and run attestations are claim-bounded; see `phase2/CLAIM-MATRIX.md`.

## What a green assurance / validator report means

It means the checks that were actually run passed under the selected schema/profile/trust policy: structural consistency, declared cross-field rules, and claim-bounded verifier results.

## What it does not mean

It does not mean the decision was fair, correct, complete, adopted by ENS, or that missing evidence never existed. `ok` is not legitimacy.

## Workload expectations

Pilot burden metrics (operator time, confirmation counts, provenance mix, validator iterations, etc.) should be **predeclared and measured**. Until a pilot report exists for your program, treat workload numbers in external materials as estimates only.

## Upgrade / version policy

- Software package version (`ens-gdi` `0.4.0`) is independent of grant-decision `schemaVersion` (still `"0.1"` for the core record).
- Profiles and adapter mapping versions are versioned identifiers; changing mapping rules requires a new version.
- Prefer additive extensions over silent v0.1 redesign.
- Do not treat package `0.4.0` or docs gate trackers as a completed `v1.0.0` release.

## Related documents

- `ADOPTION.md` — engineering-oriented adoption pathway
- `profiles/` — machine-readable profiles
- `templates/` — operator worksheets
- `DEFERRED.md` — non-goals and deferred work
- `RELEASE-INTEGRITY.md` — release identity and artifacts
