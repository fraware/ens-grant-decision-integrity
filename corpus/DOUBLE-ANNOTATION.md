# Independent second annotation

The retrospective study plan requires at least 25% of counted empirical cases to be double annotated independently before reconciliation. This file defines the execution procedure used to satisfy that requirement without converting a second reading of the primary reconstruction into "independent" evidence.

The dated selection addendum is `double-annotation-plan-2026-08-25.json`. It was created after primary annotations existed and therefore is **not** part of the original pre-study declaration. It fixes the second-annotation sample by selecting every empirical case present at exact repository commit `00fb82311d3be427f45d50697f4d74aa111886f2`, before any second annotation was recorded. All three baseline empirical cases are selected. If all three are completed, the study retains at least the predeclared 0.25 double-annotation fraction even at the study-plan maximum of twelve total cases.

Interpretation and reporting rules frozen before any second-annotation agreement result are recorded in `analysis-plan-addendum-2026-08-26.json`. That file is explicitly a post-start addendum and does not rewrite the original study plan.

## Independence boundary

The second annotator should receive only:

- the source inventory and the source material they are authorized to access;
- the fixed material field paths and `requiredForProfile` flags;
- the annotation-class definitions;
- the corpus merit, privacy, and unknown-evidence boundaries.

Before the second annotation is frozen, do not provide the primary annotation classifications or rationales, the primary reconstructed record values, validator findings or dispositions, review/reconciliation notes, or previously computed corpus metrics. Public source material may reveal the historical outcome; the goal is independent reconstruction from sources, not blindness to facts contained in those sources.

The second annotator must use a distinct `annotatorId`, record elapsed time, cover the exact same material field set, and affirm the independence boundary. The completed copy must include both `independent=true` and the exact verifier-required attestation:

> I produced this annotation without consulting the withheld primary reconstruction materials before submission.

The frozen blank handoff files do not contain the `independenceAttestation` key. The human adds it to the **completed copy**. This preserves the hashes of the frozen source-only packages while preventing an untouched pre-populated boolean from being sufficient evidence of an affirmative human attestation.

Tooling can enforce identifier separation, field-set equality, source-reference validity, the explicit boolean, and the exact attestation value. It cannot prove what the annotator actually saw or whether the human process was independent.

## Operator package (frozen handoffs)

The three baseline handoffs are prepared under `corpus/second-annotation-handoffs/` with hashes recorded in `HANDOFF-STATUS.md`. Human annotator steps and verify/integrate commands are in `second-annotation-handoffs/ANNOTATOR-CHECKLIST.md`. Do not fabricate second annotations, copy primary classifications, add the attestation on the annotator's behalf, or mark an annotation independent unless the independence boundary was actually respected.

## Handoff tooling

Prepare a handoff from a checked-in single-annotation case:

```bash
python scripts/second_annotation.py prepare \
  corpus/cases/spp3-namespace-2026/case.json \
  --out /tmp/namespace-second-annotation.json
```

The generated source-only file intentionally excludes the primary annotation, reconstructed decision-record values, validator findings, case selection rationale/strata, review notes, and computed metrics. Its `annotationSubmission` section is a response form over the fixed material field set. For the three already frozen packages, the human completed copy must add the explicit attestation key required by the current verifier.

After the second annotator returns a completed handoff, verify it against the unchanged case:

```bash
python scripts/second_annotation.py verify \
  corpus/cases/spp3-namespace-2026/case.json \
  /tmp/namespace-second-annotation.completed.json \
  --out /tmp/namespace-second-annotation.verified.json
```

Verification fails if the static handoff differs from the handoff regenerated from the current case, if the annotator ID matches the primary annotator, if `independent=true` is not asserted, if the exact independence attestation is absent or altered, if material field coverage changes, if `requiredForProfile` changes, or if source references/classification requirements are invalid.

A successful verification returns an annotation object suitable for human-reviewed integration into `case.json` and separately preserves the independence attestation in the verified output. It does **not** modify the case automatically. Freeze both the completed response and verified output before exposing the second annotator to the primary reconstruction. Only then set `review.doubleAnnotation=true`, preserve both original annotation sets, compute agreement, and begin reconciliation.

## Reconciliation discipline

Agreement metrics are computed on the two independently frozen annotations before reconciliation. Reconciliation may change the decision record or finding dispositions, but the original annotation sets remain preserved. If the reconstructed record changes, the corpus contract requires the original and reconciled record hashes, exact validator outputs, a change rationale, and reconciliation notes.

Do not resolve disagreements by deleting `unknown`, copying the primary answer into the second annotation, or editing one annotation so kappa improves. Agreement is an empirical outcome.

Three completed selected cases satisfy the predeclared 25% minimum at the current corpus size. That minimum is a study-completion rule, not evidence that three cases can support a population-level reliability estimate. Report agreement descriptively under `analysis-plan-addendum-2026-08-26.json`.

## Non-claims

Double annotation measures reproducibility of the field classification exercise under the supplied evidence set. It does not establish that either annotation is correct, that the source material is true or complete, that the historical decision was fair, that applicant merit was assessed correctly, or that the represented institution followed every private/internal procedure. The explicit independence attestation is auditable human-reported evidence, not cryptographic proof of the annotator's information exposure.
