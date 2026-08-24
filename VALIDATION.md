# Validation

v0.1 uses two validation layers:

1. JSON Schema Draft 2020-12 for record structure and local constraints.
2. Cross-field conformance checks for relations among policy, evidence, evaluators, conflicts, decisions, challenges, delivery conditions, and AI provenance.

## Validation contract

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_regressions.py
```

Expected results:

- the schema is valid Draft 2020-12;
- the worked Marketplace example has no conformance errors;
- the worked example emits only warning `CHAL003` while the reviewed public process lacks a documented factual/procedural correction route;
- the adversarial suites reject the specified inconsistent states;
- valid edge cases, including retrospective records and legitimate recusals, remain accepted;
- the recorded Simocracy allocations in `provenance/simocracy-funding.json` reconcile to $219 (allocation figures only; those funds were never received or paid).

`python scripts/conformance.py --strict examples/spp3-marketplace-rfp.example.json` intentionally fails while `CHAL003` is present, because strict mode promotes warnings to failures.

## Coverage

### Policy and source traceability

- public governing-policy URI belongs to the declared source set;
- mandate, eligibility, evaluation criteria, conflict rules, and decision procedure each map to a declared source;
- in-round changes identify prior version, change notice, and rerun treatment;
- no-change records cannot retain stale change metadata.

### Evidence and evaluation

- supported factual findings reference evidence;
- failed eligibility gates reference evidence;
- references resolve to declared evidence, evaluators, findings, and delivery conditions;
- findings and disagreements are attributable to participating, non-recused evaluators;
- criterion weights are complete when used and sum to 1.0;
- material-finding classifications remain epistemic.

### Decision authority and conflicts

- AI is excluded from decision-authority types;
- committee final authority records participating human members, quorum, and decision rule;
- advisory committee participation does not imply committee final authority;
- recusal state is consistent across evaluator and conflict records;
- recusals identify affected decision surfaces and substitution state;
- substitutes resolve to participating, non-recused evaluators;
- adjudicated decisions cannot retain unresolved material conflicts.

### Decision and challenge lifecycle

- pending records cannot claim a decision timestamp or positive award;
- ineligibility is distinct from merit rejection;
- approval, rejection, and suspension require eligible status, rationale, and attributable findings;
- approval and suspension require a positive award and delivery conditions;
- deferral requires rationale and cannot carry a positive award;
- challenge states require a defined process when active or complete;
- pending decisions cannot claim post-decision challenge activity;
- resolved challenges include a resolution.

### Temporal consistency

- `updatedAt` does not precede `createdAt`;
- the governing policy is effective by the decision time;
- an adjudicated decision does not precede its recorded eligibility check;
- a non-pending decision does not occur after the record's `updatedAt` time;
- retrospective documentation remains valid when a historical decision predates record creation.

### AI provenance

- materially influential AI evaluation requires participation and a versioned evaluator manifest;
- the minimum manifest provenance envelope is present;
- a submission deadline is recorded when commitment timing is checked;
- the declared commitment time precedes the submission deadline;
- departures from materially influential AI recommendations are recorded only on non-pending dispositions and include rationale.

## Phase II contract (additive)

The v0.1 commands and expected results above are unchanged. Phase II adds a second suite that must not be substituted for them:

```bash
python -m pip install -r phase2/requirements.txt
python -m pytest phase2/tests
python phase2/src/cli.py verify-graph --bundle phase2/examples/retrospective-public.bundle.json
```

Expected Phase II results:

- the canonicalization, commitment, round-binding, anchor, disclosure, run-attestation, replay, authority-separation, RFC 3161 fixture/fail-closed, and Ethereum-fixture adversarial tests pass;
- production JCS bytes match a second independent RFC 8785 implementation and RFC 8785 sample encoding;
- T6/T7 pass on `rekor-v1-recorded-fixture` receipts when live Rekor is unavailable;
- replay generation emits `reportVersion: "2"` with only `exact-match`, `diverged`, and `not-replayable` artifact-recomputation outcomes;
- the historical replay-report v1 schema remains unchanged and parseable, but v1 `bounded-match` / non-null bounds are rejected by the current verifier with `RPL008`;
- duplicate replay layer ids are rejected rather than being collapsed by map construction;
- T13 demonstrates that RFC 3161 fixture verification uses independently supplied verifier trust and that production `rfc3161` fails closed rather than establishing unsupported C2 evidence;
- T14 exercises the Ethereum calldata fixture under its explicit fixture trust boundary;
- the public retrospective example has no confidential applicant data, hosted generation `not-replayable`, deterministic layers exact artifact matches, and preserves `CHAL003` on its embedded pending v0.1 record;
- `verify-graph` succeeds on `phase2/examples/retrospective-public.bundle.json` under the fixture trust root;
- no Phase II object populates `decision.authorityKind`.

A Phase II pass does not establish actual implementation re-execution, correctness, fairness, legitimacy, or funding authority.

## Schema 0.2 and projection contract (additive)

```bash
python scripts/conformance.py examples/tier-a-simplified-grant.example.json
python scripts/test_schema_02.py
python -m pytest projection/tests
python projection/src/cli.py --confidential examples/tier-a-simplified-grant.example.json --spec projection/examples/tier-a-projection-spec.json --out /tmp/tier-a-public.json
```

Expected schema 0.2 / projection results:

- Tier A example passes schema 0.2 and conformance checks;
- adversarial schema 0.2 tests reject bad pins and AI authority identity;
- projection tests are deterministic and the public projection validates;
- every top-level confidential source field is explicitly published or withheld; silent omission fails with `PROJ011`;
- a field cannot be both published and withheld (`PROJ012`);
- non-null source `integrity` cannot be silently overwritten by generated projection integrity (`PROJ013`);
- the CLI produces a public record with `withheldCommitments` when the spec redacts top-level fields;
- v0.1 contract remains unchanged.

`rfc3161-recorded-fixture` and `ethereum-calldata-fixture` are test profiles. Production `rfc3161` currently fails closed pending complete CMS/RFC 3161 verification; live Ethereum anchoring is not implemented. The reference suite must not turn fixture success into a production temporal or chain-inclusion claim.

Live Rekor v1 observation: POST to `https://rekor.sigstore.dev` failed with `ConnectionResetError` from the development environment on 2026-08-19. T7 continues to use `rekor-v1-recorded-fixture`; the optional live-vector case may skip. A skipped network-dependent case must be reported as skipped, not passed.

## Full local suite (pre-release)

Run all of the following on the exact candidate commit before tagging:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -r phase2/requirements.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_regressions.py
python -m pytest phase2/tests
python scripts/test_schema_02.py
python -m pytest projection/tests
```

CI mirrors this split across jobs `conformance`, `phase2`, and `schema-02` (see `.github/workflows/validate.yml`). A release statement must identify the exact commit whose checks ran; success on an earlier head is not evidence for a later head.

## Limits

Validation establishes structural and declared cross-field consistency and the narrowly stated claims of successful additive verifiers. It does not establish:

- the truth of cited evidence;
- the quality of substantive judgment;
- the legitimacy of the governing policy;
- independently verifiable existence of an AI manifest commitment at the declared time unless a supported anchor profile is actually verified;
- execution or re-execution of a committed evaluator implementation unless a separate execution protocol establishes that fact;
- production RFC 3161 C2 evidence while the production profile is fail-closed;
- institutional adoption of the Charter;
- payment or receipt of recorded Simocracy allocations.

Release validation should be run against the exact release commit. `RELEASE-INTEGRITY.md` defines the release identity and archive-integrity procedure.
