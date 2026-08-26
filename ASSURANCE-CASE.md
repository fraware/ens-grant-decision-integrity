# Assurance Case — ENS Grant Decision Integrity

This document maps the project objective to bounded machine claims in `claims/claim-registry.v1.json`. It is an assurance map for package `0.4.0` / current development `main`, not a claim that every gate is satisfied for a `v1.0.0` tag, and not ENS endorsement.

## Goal G0

A material grant/service-provider decision package can be reconstructed later with explicit rules, evidence linkage, participation, authority, conflict handling, disagreement, correction state, delivery obligations, and bounded evaluator provenance.

**Does not establish:** substantive merit, fairness, institutional legitimacy, payment, or adoption of this repository.

## Subgoals

### G1 — Governing policy identity and optional pins

- Claims: `SOURCE.BYTES.MATCH_METADATA`, `SOURCE.POLICY_PIN.MATCH`, `CORE.SCHEMA.STRUCTURE`
- Checks: `source.bytes`, `source.policy-pins`, `core.schema`
- Evidence: decision record; source-artifact metadata/bytes when redistributable
- Trust: none for byte match; operator trust in capture process is out of band
- Non-claims: truth/ownership/adoption of the policy; independent capture-time authenticity beyond metadata

### G2 — Decision-record structure and declared semantics

- Claims: `CORE.SCHEMA.STRUCTURE`, `CORE.CONFORMANCE.CROSS_FIELD`, `CORE.EVIDENCE.REFERENCE_RESOLUTION`, `CORE.CONFLICT.RECUSAL_CONSISTENCY`, `CORE.CHALLENGE.LIFECYCLE`, `CORE.DELIVERY.CONDITION_CONSISTENCY`
- Checks: `core.schema`, `core.conformance`
- Evidence: decision record
- Non-claims: evidence truth; judgment quality; legitimacy

### G3 — Human / collective authority surfaces

- Claims: `CORE.AUTHORITY.HUMAN_SURFACE`, `PHASE2.C6.HUMAN_AUTHORITY_SEPARATION`
- Checks: `core.conformance`, `phase2.c6`
- Evidence: decision record; Phase II bundle when present
- Non-claims: AI/automation as funding authority; institutional endorsement of GDI

### G4 — Automated evaluator provenance (when used)

- Claims: `PHASE2.C1.MANIFEST_BINDING` … `PHASE2.C5.REPLAY_EVIDENCE`, plus `PHASE2.C4A.AUTHORIZED_SIGNER` only when an external trust policy separately authorizes the run key
- Checks: Phase II graph verification plus a separate signer-authorization check for C4A
- Evidence: Phase II evidence bundle; external verifier trust inputs as required by the selected profile
- Trust assumptions: selected anchor profile trust root; external trust-policy digest when used
- Non-claims: operator honesty; implementation re-execution unless separately claimed; fairness; C4 ≠ C4A

Production `rekor-v2` C2 verification is reserved and fails closed until native Rekor v2 inclusion semantics and independent signed timestamp evidence are implemented. The recorded Rekor-v2 fixture is non-production. Production RFC 3161 also remains fail closed until its complete CMS/TSA trust boundary is implemented.

### G5 — Public disclosure via projection

- Claims: `PROJ.SPEC.STRUCTURE`, `PROJ.EXEC.DETERMINISTIC`, `PROJ.COVERAGE.COMPLETE`, `PROJ.WITHHELD.COMMITMENT`, `PROJ.INTEGRITY.BIND`
- Checks: deterministic projection recomputation under the selected v1/v2 profile
- Evidence: confidential record (authorized), projection spec, public projection
- Non-claims: adequacy of disclosure policy; dictionary-attack resistance for low-entropy withheld fields

### G6 — Empirical reconstruction study

- Claims: `CORPUS.*`
- Checks: `corpus.case`, `corpus.snapshot-bytes`, `corpus.findings`, `corpus.sources`, `corpus.metrics`, `corpus.study-status`
- Evidence: corpus cases and study plan
- Non-claims: agreement ≠ correctness; ready-for-final-review ≠ complete/representative research; uncovered stratum ≠ universal absence

The preregistered independent second-annotation requirement is a human research gate. Software must not manufacture, copy, or relabel a primary annotation as independent evidence.

### G7 — Release / package identity

- Claims: `RELEASE.COMMIT.IDENTITY`, `RELEASE.CHECKS.CORRESPOND`, `RELEASE.ARCHIVE.DIGEST`, `RELEASE.SBOM.PIPELINE`
- Checks: `release.*`
- Evidence: release manifest, exact-commit CI run record, archives, SBOM
- Non-claims: byte-reproducible builds unless two independent clean builds match; vulnerability absence

### Funding provenance (orthogonal axis)

- Claims: `FUNDING.STATUS.SNAPSHOT`, `FUNDING.FINANCIAL.SEPARATE_EVIDENCE`
- Checks: versioned funding provenance checks when registered
- Non-claims: allocation → payment/receipt/settlement

The package-level bundle orchestrator does not currently register a funding-status semantic verifier. If a bundle marks a funding snapshot required, `gdi verify-bundle` therefore fails closed rather than converting parsed JSON into a funding claim.

### Trust binding

- Claim: `TRUST.POLICY.EXTERNAL`
- Check: `trust.policy`
- Non-claims: correctness of operator trust choices; bundles cannot self-appoint trust

## Verification orchestration

`gdi verify-bundle` executes the registered offline checks in fail-closed order: manifest/path safety → declared digests → record schema/conformance → source bytes → policy pins → Phase II graph when present → deterministic projection when present → funding registration state → claim aggregation.

Check states are `pass | fail | warning | not-applicable | not-run | unsupported`. Every check marked required must complete in `pass` or `warning` for the report to retain `ok=true`. A required `fail`, `not-run`, `unsupported`, or `not-applicable` state makes the report fail closed. Optional unavailable or inapplicable checks remain explicit in `unverified` and do not create claims.

C4A signer authorization remains a separately executed trust-policy check; loading a trust policy does not by itself authorize a run signer.

## Explicit non-goals

Merit/fairness scoring, authority transfer to automation, dashboard-as-assurance, live Ethereum, ZK selective disclosure, and silent v0.1 redesign remain deferred. See `DEFERRED.md`.
