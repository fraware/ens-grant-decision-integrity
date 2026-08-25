# Corpus study status

`scripts/study_status.py` reports machine-checkable progress against `corpus/study-plan.json` without treating an unfinished study as a CI failure.

Run:

```bash
python scripts/study_status.py
```

The command first re-validates every checked-in empirical case through the corpus contract, including exact record-snapshot bytes and validator-output binding. It then reports case-count progress, declared stratum coverage, conditional stratum coverage, double-annotation progress, completion gates, blockers, and explicit non-claims.

`ok: true` means the status computation succeeded and every counted case satisfied the machine corpus contract. It does not mean the empirical study is complete. `readyForFinalReview: true` means only that the predeclared machine-checkable case-count, declared required-stratum coverage, and double-annotation gates are satisfied. It does not certify source truth, historical completeness, merit, fairness, or institutional legitimacy.

The study plan qualifies required strata with “where evidence exists.” The status tool can establish that a stratum is represented by a checked-in case. It cannot establish that evidence for an uncovered stratum does not exist. An uncovered required stratum is therefore reported as unresolved and requires either an evidence-backed case or an explicit research disposition outside the machine report.

Conditional strata are reported separately and do not become completion gates unless the study plan is changed explicitly. Additional observed strata are reported but do not silently alter the predeclared design.

If the empirical case count exceeds the predeclared maximum, the report uses `protocol-deviation`. If all machine-checkable gates are satisfied, it uses `ready-for-final-review`, not `complete`, because final study completion requires research judgment beyond these mechanical checks.
