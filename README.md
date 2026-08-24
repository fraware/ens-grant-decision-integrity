# ENS Grant Decision Integrity

A versioned draft Charter and machine-readable decision-record profile for making material ENS grant and service-provider decisions reconstructable.

The project originated in the Simocracy proposal **“No Black-Box Grants: Ratify the Rules Before SPP Is Absorbed.”** Five ENS Governance funding decisions **allocated** a cumulative **$219** to that proposal. Those allocations were **never received or paid**. v0.1 implements the first $200 work item described in that proposal: a Grants Charter and a machine-readable decision-record schema. v0.2 added Phase II evaluator-manifest commitment and anchoring. v0.3 added optional schema 0.2 extensions, deterministic public projection, and alternate anchor fixture profiles.

**Releases:** [v0.3.2](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.3.2) (latest) · [v0.3.1](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.3.1) · [v0.3.0](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.3.0) · [v0.2.0](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.2.0) · [v0.1.0](https://github.com/fraware/ens-grant-decision-integrity/releases/tag/v0.1.0)

The latest tagged release remains v0.3.2. Development after that tag is treated as unreleased until a new reviewed tag is created; do not attribute unreleased hardening behavior to v0.3.2.

## What this repository provides

The profile records enough information for a third party to reconstruct the procedural basis of a material funding decision:

- the versioned public rules governing the review;
- eligibility results and evidence for failed gates;
- evaluation criteria, material findings, and evidence references;
- evaluator participation, disagreement, conflicts, recusals, and substitutions;
- the human-governed decision authority and decision state;
- a factual/procedural correction path;
- delivery conditions for funded awards;
- minimum provenance when AI materially informs a recommendation.

JSON Schema validates record structure. A separate conformance validator checks cross-field relations that JSON Schema alone cannot express. Additive modules cover evaluator-manifest commitment (Phase II), optional schema 0.2 pinning and authority identity, and deterministic confidential-to-public projection.

## Repository layout

| Path | Purpose |
|---|---|
| `CHARTER.md` | Normative decision-integrity requirements (draft governance proposal — not adopted ENS policy) |
| `schema/grant-decision-record.schema.json` | JSON Schema Draft 2020-12 record format (default `schemaVersion` `"0.1"`) |
| `schema/grant-decision-record-0.2.schema.json` | Optional schema 0.2 extensions (`policyPinning`, `authorityIdentity`) |
| `schema/grant-decision-public-projection-0.2.schema.json` | Relaxed schema for projected public records with `withheldCommitments` |
| `CONFORMANCE.md` | Cross-field conformance rules, severity model, and rule-ID index |
| `scripts/conformance.py` | Semantic conformance validator |
| `phase2/` | Evaluator-manifest commitment, anchoring, run attestation, and replay evidence |
| `projection/` | Deterministic confidential-to-public record projection |
| `examples/` | Fictional worked examples (non-evaluative) |
| `methodology/GRANT-DECISION-INTEGRITY.md` | Draft twelve-step review methodology |
| `ADOPTION.md` | Adoption pathway for ENS grant programs |
| `VALIDATION.md` | Validation contract and expected outcomes |
| `DESIGN-NOTES.md` | Design rationale, threat model, and scope boundaries |
| `RELEASE-INTEGRITY.md` | Release-identity and archive-integrity procedure |
| `REVIEW.md` | Adversarial review guide |
| `CONTRIBUTING.md` | Contribution preferences and pre-change validation |
| `SECURITY.md` | Sensitive-disclosure reporting |
| `CITATION.cff` | Citation metadata for the latest tagged release |
| `provenance/simocracy-funding.json` | Recorded Simocracy allocation provenance ($219 allocated; not paid) |

## Quickstart

Install pinned dependencies and run the complete v0.1 validation contract:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_regressions.py
```

The Marketplace example is intentionally pending. It should produce no conformance errors and one warning, `CHAL003`, which records that the reviewed public process artifacts do not identify a post-decision route for correcting factual or procedural errors. See `VALIDATION.md` for the full contract, including Phase II, schema 0.2, and projection suites.

## Phase II (evaluator provenance)

`phase2/` is an additive protocol for evaluator-manifest commitment, anchor-profile verification, run attestation, and replay evidence. Grant-decision `schemaVersion` remains `"0.1"`. Phase II does not change v0.1 Charter, schema, or conformance behavior.

A Phase II graph pass establishes only the claims in `phase2/CLAIM-MATRIX.md`. A valid commitment is not execution. A signed run is an assertion. Artifact replay agreement is not proof that the recorded implementation was re-executed and is not correctness, fairness, or legitimacy. Hosted models may be `not-replayable`. Hashes are not institutional authority. AI systems cannot approve, reject, suspend, or release funding.

```bash
python -m pip install -r phase2/requirements.txt
python -m pytest phase2/tests
python phase2/src/cli.py verify-graph --bundle phase2/examples/retrospective-public.bundle.json
```

Rekor tests and the public example use `rekor-v1-recorded-fixture` receipts verified under a shipped test-log key. That profile does **not** establish inclusion in the public Sigstore Rekor log. Rekor v1 remains a historical compatibility profile. See `phase2/ADMIN-BURDEN.md` and `phase2/CLAIM-MATRIX.md`.

Current replay generation emits replay-report v2 (`exact-match`, `diverged`, `not-replayable`) from canonical artifact recomputation. Historical replay-report v1 remains schema-frozen for compatibility, but its `bounded-match` digest-distance mechanism is rejected by the current verifier because cryptographic hash distance is not a meaningful approximation measure for the underlying computation.

## Schema 0.2 extensions and projection

Optional schema `0.2` extensions do not mutate v0.1 behavior:

- `schema/grant-decision-record-0.2.schema.json` — optional `policyPinning` and `authorityIdentity`
- `schema/grant-decision-public-projection-0.2.schema.json` — relaxed requirements for projected public records
- `projection/` — deterministic confidential-to-public record projection with withheld commitments; projection v1 uses top-level redaction paths, fails closed on silent top-level omission or ambiguous publish/withhold disposition, and refuses to overwrite non-null source integrity metadata
- `phase2/src/anchors/rfc3161.py` — reserved production RFC 3161 profile plus recorded test fixture; production `rfc3161` currently fails closed until standards-conformant CMS/RFC 3161 verification is implemented
- `phase2/src/anchors/ethereum.py` — Ethereum calldata fixture profile (`ethereum-calldata-fixture`); live mainnet anchoring is not implemented
- `examples/tier-a-simplified-grant.example.json` — fictional Tier A approved grant with pinning and structured authority
- `ADOPTION.md` — adoption pathway for ENS programs
- `methodology/GRANT-DECISION-INTEGRITY.md` — draft twelve-step review methodology

```bash
python scripts/conformance.py examples/tier-a-simplified-grant.example.json
python -m pytest scripts/test_schema_02.py
python -m pytest projection/tests
python projection/src/cli.py --confidential examples/tier-a-simplified-grant.example.json --spec projection/examples/tier-a-projection-spec.json --out /tmp/tier-a-public.json
```

Cryptographic selective disclosure remains deferred; see `phase2/DEFERRED.md`.

## What validators prove and do not prove

**Prove:** record structure and declared cross-field consistency under the selected profile; Phase II graph claims bounded by `phase2/CLAIM-MATRIX.md` when a bundle is present; deterministic projection from the supplied confidential input under a declared projection spec.

**Do not prove:** truth of cited evidence; quality of substantive judgment; institutional adoption of the Charter; independently verifiable existence of an AI manifest commitment without verifying a supported anchor profile; execution or re-execution of a committed evaluator implementation unless a separate execution protocol establishes that fact; funding authority; payment or receipt of Simocracy allocations.

## AI provenance boundary

When AI materially informs a grant recommendation, v0.1 requires a versioned evaluator manifest and records a minimum provenance envelope: model identity, human-review policy, commitment metadata, reveal state, and the application deadline used for the timing check.

The v0.1 validator checks only that the declared commitment time precedes the declared submission deadline. v0.1 does not define canonical manifest serialization, commitment generation, an independently verifiable timestamp or publication anchor, proof verification, selective-disclosure proofs, or evaluator replay. A schema 0.1 record without a Phase II evidence bundle therefore does not prove that a commitment existed at the declared time or that the committed configuration was actually used.

## ENS process mapping

The worked example maps the public SPP3 Marketplace process without evaluating any applicant. It records all seven published hard eligibility conditions, the published M1–M5 weights, the public rules and sources governing mandate, eligibility, evaluation criteria, conflict rules, and decision procedure, the published committee quorum and decision rule, and milestone and traction-verification requirements.

The example is a dated snapshot of the published process. It is fictional, does not identify, score, recommend, or reject a real applicant, and does not need to be rewritten when the underlying RFP later reaches an award state.

## Scope and status

This project governs the integrity of the decision record. It does not determine which projects ENS should fund, replace substantive committee judgment, establish the truth of cited evidence, or create authority for AI systems to approve, reject, suspend, or release funding.

| Item | Value |
|---|---|
| Latest tagged repository release | `0.3.2` |
| Development state | unreleased changes may exist after the latest tag; exact commit SHA is authoritative |
| Default grant-decision `schemaVersion` | `"0.1"` |
| Optional extensions | schema `"0.2"` (additive) |
| Phase II object versions | core version-1 objects; replay report v1 historical, v2 current emission |
| Charter status | Draft governance proposal — not adopted ENS policy |
| Methodology status | Draft — not a frozen ENS standard |
| Funding provenance | $219 allocated across five Simocracy decisions; never received or paid |
| Endorsement | Does not claim endorsement by ENS DAO, the ENS Foundation, or the SPP3 committee |

For adoption guidance, see `ADOPTION.md`. For security-sensitive reports, see `SECURITY.md`.

## Sources

- ENS SPP3 Marketplace RFP: https://discuss.ens.domains/t/7-1-social-spp3-marketplace-rfp/22263
- Marketplace RFP submission timeline and rubric: https://discuss.ens.domains/t/marketplace-rfp-submission-timeline-and-artifacts/22309
- SPP3 program authorization and committee model: https://discuss.ens.domains/t/social-spp3-program-authorization-and-committee-model/22086
- ENS AI grant/SPP screening experiment: https://discuss.ens.domains/t/ai-for-grant-spp-evaluation-screening/21939
