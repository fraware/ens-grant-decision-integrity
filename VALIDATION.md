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
- the historical allocation amounts in `provenance/simocracy-funding.json` reconcile to $219 without treating allocation as payment, transfer, receipt, or settlement evidence.

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

## Source-artifact and policy-pin contract (additive)

Schema 0.2 `policyPinning` metadata is not self-verifying. The source-artifact module adds an exact-byte verification path that remains separate from record conformance:

```bash
python -m pytest scripts/test_source_artifact.py scripts/test_policy_pins.py
python scripts/source_artifact.py verify --metadata path/to/source.artifact.json --file path/to/captured.bytes
python scripts/verify_policy_pins.py --record path/to/record.json --artifact path/to/source.artifact.json path/to/captured.bytes
```

Expected results:

- `schema/source-artifact.schema.json` validates under Draft 2020-12;
- the verifier re-hashes exact supplied bytes and rejects same-length byte tampering, forged hashes, and forged byte lengths;
- invalid source-artifact URI/hash/time encodings fail structurally;
- a policy pin succeeds only when an exact `sourceUri` or `resolvedUri` and the declared SHA-256 both match a byte-verified artifact;
- URI mismatch fails even when byte content is identical;
- duplicate source-artifact IDs and duplicate policy-pin URIs fail closed;
- source-artifact capture metadata does not become a second authority for the policy surface represented by the decision record;
- a record without `policyPinning` is explicitly reported as not applicable rather than as a successful pin check.

A successful source-artifact check establishes byte identity only for the supplied file and metadata. A successful policy-pin check additionally establishes exact URI/hash linkage to a byte-verified artifact. Neither establishes source truth, completeness, ownership, institutional adoption, or independent existence at `capturedAt` / `policyPinning.pinnedAt`.

## Phase II contract (additive)

The v0.1 commands and expected results above are unchanged. Phase II adds a second suite that must not be substituted for them:

```bash
python -m pip install -r phase2/requirements.txt
python -m pytest phase2/tests
python phase2/src/cli.py verify-graph --bundle phase2/examples/retrospective-public.bundle.json
```

Expected Phase II results:

- the canonicalization, commitment, round-envelope binding, anchor, disclosure, run-attestation, replay, authority-separation, CLI fail-closed, RFC 3161 fixture/fail-closed, and Ethereum-fixture adversarial tests pass;
- production JCS bytes match a second independent RFC 8785 implementation and RFC 8785 sample encoding;
- T6/T7 pass on `rekor-v1-recorded-fixture` receipts when live Rekor is unavailable;
- C1 is established only by opening manifest+salt and checking the manifest round fields against the supplied envelope; standalone reveal does not establish anchor validity or temporal precedence;
- `committed` and `withheld` remain unopened, carry no manifest/salt in current bundle-v2 verification, and do not establish C1; anchor verification may separately establish C2/C3;
- replay generation emits `reportVersion: "2"` with only `exact-match`, `diverged`, and `not-replayable` artifact-recomputation outcomes;
- replay-report v2 uses exactly the defined five layers and requires outcome, attested digest, recomputed digest, and reason fields to agree with verifier recomputation;
- the historical replay-report v1 schema remains unchanged and parseable, but v1 `bounded-match` / non-null bounds are rejected by the current verifier with `RPL008`;
- duplicate replay layer ids and missing/unexpected attested layer ids are rejected rather than being collapsed or surfacing raw mapping errors;
- historical evidence-bundle v1 remains the frozen parent for replay-report v1, while newly generated current test bundles use evidence-bundle v2 with replay-report v2;
- ambiguous CLI reveal inputs (`--manifest` without `--salt`, or vice versa) and incompatible profile-specific arguments fail closed before being silently ignored;
- T13 demonstrates that RFC 3161 fixture verification uses independently supplied verifier trust; receipt-selected trust substitution, malformed base64 fixture material, invalid configured trust material, and signature mismatch fail as structured protocol errors; production `rfc3161` fails closed rather than establishing unsupported C2 evidence;
- T14 exercises the Ethereum calldata fixture under its explicit fixture trust boundary;
- the public retrospective example has no confidential applicant data, hosted generation `not-replayable`, deterministic layers exact artifact matches, and preserves `CHAL003` on its embedded pending v0.1 record;
- `verify-graph` succeeds on `phase2/examples/retrospective-public.bundle.json` as historical bundle-v1/replay-v1 compatibility evidence under the fixture trust root;
- no Phase II object populates `decision.authorityKind`.

A Phase II pass does not establish actual implementation re-execution, correctness, fairness, legitimacy, or funding authority.

## Schema 0.2 and projection contract (additive)

```bash
python scripts/conformance.py examples/tier-a-simplified-grant.example.json
python -m pytest scripts/test_schema_02.py
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

## Funding-provenance status contract

`provenance/simocracy-status-2026-08-24.json` is a dated public-status snapshot, not a timeless assertion. It records five relevant rounds totaling $219, with three labeled `ratified` and two labeled `provisional` on the captured platform status surface. Its null financial-evidence fields mean only that the snapshot contains no payment-authorization, transfer, receipt, or settlement evidence.

Future status changes should be represented by a new dated snapshot. Historical snapshots should not be rewritten to imply continuity or settlement. See `provenance/ALLOCATION-CAPTURE.md`.

## Full local suite (pre-release)

Run all of the following on the exact candidate commit before tagging:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -r phase2/requirements.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_regressions.py
python -m pytest scripts/test_source_artifact.py scripts/test_policy_pins.py
python -m pytest phase2/tests
python -m pytest scripts/test_schema_02.py
python -m pytest projection/tests
```

CI mirrors this split across jobs `conformance`, `phase2`, and `schema-02` (see `.github/workflows/validate.yml`). The `conformance` job also runs the source-artifact and policy-pin tests. A release statement must identify the exact commit whose checks ran; success on an earlier head is not evidence for a later head.

## Limits

Validation establishes structural and declared cross-field consistency and the narrowly stated claims of successful additive verifiers. It does not establish:

- the truth, completeness, or ownership of cited evidence;
- institutional adoption merely because policy bytes match a recorded hash;
- the quality of substantive judgment;
- the legitimacy of the governing policy;
- independently verifiable source capture time from `capturedAt` metadata alone;
- independently verifiable existence of an AI manifest commitment at the declared time unless a supported anchor profile is actually verified;
- execution or re-execution of a committed evaluator implementation unless a separate execution protocol establishes that fact;
- production RFC 3161 C2 evidence while the production profile is fail-closed;
- institutional adoption of the Charter;
- payment, transfer, receipt, or settlement of recorded Simocracy allocations.

Release validation should be run against the exact release commit. `RELEASE-INTEGRITY.md` defines the release identity and archive-integrity procedure.
