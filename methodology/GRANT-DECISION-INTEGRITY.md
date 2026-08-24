# Grant Decision Integrity methodology (draft)

Status: **draft** — not a frozen ENS standard. This document describes a twelve-step review pattern in mechanism-first language for inspecting grant decision records. It does not certify outcomes, fairness, or funding authority.

## Purpose

Provide a repeatable review sequence for determining whether a material grant or service-provider decision is reconstructable from declared public rules, evidence references, evaluator participation, human authority, and—when present—Phase II commitment and anchor artifacts.

## Scope boundary

This methodology establishes what a reviewer can verify from the supplied and independently checked artifacts. It does not:

- prove cited evidence is true;
- prove a commitment existed without verifying a production-supported anchor profile under its stated trust assumptions;
- treat a recorded test fixture as production temporal evidence;
- treat AI output, run signatures, or replay results as institutional approval;
- treat canonical artifact recomputation as implementation re-execution;
- replace ENS governance adoption of the Charter.

## Twelve-step review

### Step 1 — Identify the governing round

Record `program.roundId`, submission deadline, materiality tier, and the public rules URI. Confirm the round being reviewed matches the artifact set.

### Step 2 — Trace governing-policy surfaces

Verify `governingPolicy.surfaceSources` maps mandate, eligibility, evaluation criteria, conflict rules, and decision procedure to URIs that also appear in `governingPolicy.sources`. When schema 0.2 `policyPinning` is present, independently compare each declared content hash with the exact source bytes used for review when those bytes are available. If byte-level verification cannot be performed, record that limitation instead of treating pin metadata as self-verifying evidence.

### Step 3 — Check policy change lineage

If `changeDuringReview=true`, require prior version, change notice URI, rerun statement, and change summary. If `false`, confirm no stale change metadata remains.

### Step 4 — Eligibility integrity

Distinguish hard-screen ineligibility from merit rejection. Failed eligibility rules must reference evidence. Eligibility timing must not postdate an adjudicated decision.

### Step 5 — Evaluator participation and recusal

Confirm findings and disagreements attach only to participating, non-recused evaluators. Recusals must identify affected decision surfaces and substitution state.

### Step 6 — Evidence and epistemic classification

Supported facts require evidence references. Non-public evidence without URI or content hash is an auditability warning, not automatic disclosure.

### Step 7 — AI provenance boundary

When AI materially informs a recommendation, require a versioned evaluator manifest block. Verify Phase II graph claims separately if a bundle is present. AI must not appear in `decision.authorityKind` or structured authority identity.

### Step 8 — Phase II commitment and anchor (when present)

Verify the selected evidence-bundle version, envelope, selected anchor-profile receipt, and strict pre-deadline anchor time under the profile's stated trust boundary. `committed` and `withheld` are unopened states and must not be reported as manifest-content verification. `revealed` and the current `selective-audit` path establish manifest-to-envelope opening only when manifest and salt are actually supplied and verified. Production `rfc3161` is currently fail-closed; fixture profiles are test evidence only.

### Step 9 — Run attestation and replay (when present)

Treat signed runs as operator assertions. Current replay performs canonical artifact recomputation and records `exact-match`, `diverged`, or `not-replayable` outcomes. It does not invoke the implementation identified by the run attestation and must not be described as implementation re-execution. Preserve honest `not-replayable` outcomes for hosted layers when applicable.

### Step 10 — Decision state and authority

Confirm decision status, rationale, award rules, challenge lifecycle, and human authority type. Committee decisions require quorum and decision rule when `authorityKind=committee`.

### Step 11 — Public projection (when present)

Verify projection spec domain, explicit top-level publish/withhold disposition, withheld commitments, and projection digest. Confirm the public record uses the relaxed public-projection schema when top-level fields are withheld. A projection pass does not establish completeness of the confidential input or the substantive correctness of a redaction decision.

### Step 12 — Residual gaps and non-claims

Document unresolved warnings (for example undocumented correction paths), explicit trust boundaries for anchors, unavailable source bytes, and any deviation from Charter or schema profile. Stop before claiming implementation execution, correctness, fairness, legitimacy, institutional adoption, payment, receipt, or settlement unless those propositions have separate evidence.

## Outputs

A review should produce:

1. validator and graph command results pinned to the exact repository commit used;
2. a list of established claims bounded by `phase2/CLAIM-MATRIX.md` when Phase II applies;
3. residual warnings, unverified assumptions, and undocumented process gaps;
4. a clear statement of what was not verified.

## Relationship to repository releases

Pin reviews to an exact repository tag and commit SHA. The latest tagged release is `v0.3.2`; later development commits may contain unreleased hardening and must not be attributed to that tag. v0.1 records remain valid without Phase II bundles. Schema 0.2 extensions are additive; v0.1 records must continue to validate unchanged. The Charter and this methodology remain drafts until ENS governance adopts them.
