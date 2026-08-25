# Independent second annotation

The retrospective study plan requires at least 25% of counted empirical cases to be double annotated independently before reconciliation. This file defines the execution procedure used to satisfy that requirement without converting a second reading of the primary reconstruction into "independent" evidence.

The dated selection addendum is `double-annotation-plan-2026-08-25.json`. It was created after primary annotations existed and therefore is **not** part of the original pre-study declaration. It fixes the second-annotation sample by selecting every empirical case present at exact repository commit `00fb82311d3be427f45d50697f4d74aa111886f2`, before any second annotation was recorded. All three baseline empirical cases are selected. If all three are completed, the study retains at least the predeclared 0.25 double-annotation fraction even at the study-plan maximum of twelve total cases.

## Independence boundary

The second annotator should receive only:

- the source inventory and the source material they are authorized to access;
- the fixed material field paths and `requiredForProfile` flags;
- the annotation-class definitions;
- the corpus merit, privacy, and unknown-evidence boundaries.

Before the second annotation is frozen, do not provide the primary annotation classifications or rationales, the primary reconstructed record values, validator findings or dispositions, review/reconciliation notes, or previously computed corpus metrics. Public source material may reveal the historical outcome; the goal is independent reconstruction from sources, not blindness to facts contained in those sources.

The second annotator must use a distinct `annotatorId`, record elapsed time, cover the exact same material field set, and set `independent=true` only if the withheld primary reconstruction materials were not consulted before submission. Tooling can enforce identifier separation, field-set equality, source-reference validity, and the explicit independence attestation. It cannot prove the human process was actually independent.

## Operator package (frozen handoffs)

The three baseline handoffs are prepared under `corpus/second-annotation-handoffs/` with hashes recorded in `HANDOFF-STATUS.md`. Human annotator steps and verify/integrate commands are in `second-annotation-handoffs/ANNOTATOR-CHECKLIST.md`. Do not fabricate second annotations, copy primary classifications, or set `independent=true` unless the independence boundary was actually respected.

## Handoff tooling

Prepare a handoff from a checked-in single-annotation case:

```bash
python scripts/second_annotation.py prepare \
  corpus/cases/spp3-namespace-2026/case.json \
  --out /tmp/namespace-second-annotation.json
```

The generated file intentionally excludes the primary annotation, reconstructed decision-record values, validator findings, case selection rationale/strata, review notes, and computed metrics. Its `annotationSubmission` section is a blank response form over the fixed material field set.

After the second annotator returns a completed handoff, verify it against the unchanged case:

```bash
python scripts/second_annotation.py verify \
  corpus/cases/spp3-namespace-2026/case.json \
  /tmp/namespace-second-annotation.completed.json \
  --out /tmp/namespace-second-annotation.verified.json
```

Verification fails if the static handoff differs from the handoff regenerated from the current case, if the annotator ID matches the primary annotator, if `independent=true` is not asserted, if material field coverage changes, if `requiredForProfile` changes, or if source references/classification requirements are invalid.

A successful verification returns an annotation object suitable for human-reviewed integration into `case.json`. It does **not** modify the case automatically. Freeze the returned annotation before exposing the second annotator to the primary reconstruction. Only then set `review.doubleAnnotation=true`, preserve both original annotation sets, compute agreement, and begin reconciliation.

## Reconciliation discipline

Agreement metrics are computed on the two independently frozen annotations before reconciliation. Reconciliation may change the decision record or finding dispositions, but the original annotation sets remain preserved. If the reconstructed record changes, the corpus contract requires the original and reconciled record hashes, exact validator outputs, a change rationale, and reconciliation notes.

Do not resolve disagreements by deleting `unknown`, copying the primary answer into the second annotation, or editing one annotation so kappa improves. Agreement is an empirical outcome.

## Non-claims

Double annotation measures reproducibility of the field classification exercise under the supplied evidence set. It does not establish that either annotation is correct, that the source material is true or complete, that the historical decision was fair, that applicant merit was assessed correctly, or that the represented institution followed every private/internal procedure.
