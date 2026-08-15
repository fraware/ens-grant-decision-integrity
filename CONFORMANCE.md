# Machine-Checkable Conformance

`grant-decision-record.schema.json` validates record structure. `scripts/conformance.py` validates cross-field decision-integrity invariants that JSON Schema cannot express cleanly.

A record is **core-conformant** only when both layers pass without errors.

## Core invariants

The conformance validator enforces the following properties.

### Reference integrity

Identifiers for evaluators, evidence, findings, criteria, disagreements, conflicts, delivery conditions, and eligibility rules must be unique. Every cross-reference must resolve to an identifier present in the same record.

### Evidence integrity

A finding classified as `supported-fact` must reference at least one evidence object. Public evidence must expose a retrievable URI. Non-public evidence without a content hash receives a warning because later integrity verification would be impossible.

### Evaluation integrity

Criterion weights must either be omitted consistently or be specified for every criterion and sum to `1.0`.

### Decision-state integrity

A `pending` record cannot claim a decision timestamp. Finalized dispositions require one. Approval or rejection requires an eligible application. Approved awards require a positive amount and at least one observable delivery condition. Rejected decisions cannot retain a positive award.

### Conflict integrity

A finalized decision cannot leave a material conflict in `disclosed` or `unresolved` state. A conflict must reach a resolved or recused state under the governing policy.

### Authority integrity

A finalized committee decision must identify participating human members, record quorum, and record the applicable voting or consensus rule. A generic committee label alone is insufficient for final attribution.

### Automated-evaluator provenance

If an automated evaluator materially informed the decision, absence of an evaluator manifest is reported as a warning. Manifest commitment and reveal states must be internally consistent.

### Challenge integrity

Every record must describe the scope of its factual or procedural challenge path, including cases where that path is not currently open.

### Temporal integrity

`updatedAt` cannot precede `createdAt`. A finalized decision cannot predate record creation. A governing policy cannot take effect after the decision it supposedly governed.

### Enhanced-profile checks

Tier `C-enhanced` finalized records receive warnings when integrity metadata, delivery-condition verifiers, or delivery target dates are absent.

## Severity model

- **ERROR** — the record cannot claim core conformance.
- **WARNING** — the record remains core-conformant, with a material auditability weakness that should be resolved for high-value or high-risk decisions.

Use `--strict` to treat warnings as failures.

## Commands

```bash
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/conformance.py --strict examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
```

## Design principle

Syntactic validity is insufficient for institutional conformance. A record that parses correctly can still encode an unsupported factual claim, a hidden broken reference, an unresolved conflict, or an unattributed decision. The semantic layer exists to reject those states explicitly.

## Scope boundary

The validator checks internal consistency and declared process invariants. It does not determine whether an evaluator's substantive judgment is correct, whether cited evidence is truthful, or whether the governing policy itself is legitimate.
