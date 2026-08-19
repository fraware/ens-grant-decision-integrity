# Phase II release procedure

Repository version moves to `0.2.0` only when Phase II exit gates pass and an annotated tag is created on the reviewed merge commit. Grant-decision `schemaVersion` remains `"0.1"`. v0.1 files on `main` stay behavior-identical until merge.

## Exit gates (all required)

1. T1–T12 pass (`python -m pytest phase2/tests`).
2. Full v0.1 validation contract passes unchanged (`python scripts/validate.py` and related scripts); Marketplace example warning set is exactly `CHAL003`.
3. Public claim matrix matches verifier CLI output (`phase2/CLAIM-MATRIX.md` ↔ `phase2/src/claims.py`).
4. Authority separation holds (T12; no Phase II object populates `decision.authorityKind`).
5. Public example has no confidential applicant data; uses public forum URIs only.
6. Administrative burden documented (`phase2/ADMIN-BURDEN.md`).
7. At least one Rekor profile verifies from a clean environment: production `rekor-v1` with a recorded live receipt when network allows, or rigorous `rekor-v1-recorded-fixture` verification with pinned test-log key and documented fixture semantics when live Rekor is unavailable.

## Pre-tag checklist

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/conformance.py examples/spp3-marketplace-rfp.example.json
python scripts/test_conformance.py
python scripts/test_regressions.py

python -m pip install -r phase2/requirements.txt
python -m pytest phase2/tests
python phase2/src/cli.py verify-graph --bundle phase2/examples/retrospective-public.bundle.json
```

Record: commit SHA, tree SHA, test counts, live Rekor status, and whether the public example uses fixture or production receipts.

## Tag and release (after merge to main)

1. Merge the Phase II PR via pull request; do not push semantic drift directly to `main`.
2. Require green validation on the exact release commit (local Python 3.12 contract pass if hosted CI billing is blocked).
3. Confirm `CITATION.cff` version is `0.2.0` on the release commit.
4. Create an annotated tag:

```text
git tag -a v0.2.0 <release-commit-sha>
```

Tag message must include: commit SHA, tree SHA, Phase II scope summary, test counts, live Rekor status, and a note that grant-decision `schemaVersion` remains `"0.1"`.

5. Build an explicit archive from the release commit (same procedure as v0.1 in `RELEASE-INTEGRITY.md`).
6. Create a GitHub Release attaching the archive and SHA-256 sidecar only.
7. Release notes must state claim boundaries and non-claims from `phase2/CLAIM-MATRIX.md`.

## What a Phase II release does not prove

- Execution, operator honesty, or evaluator correctness.
- Fairness, legitimacy, or funding authority.
- That every observer saw the same Rekor log (monitoring against split-view is out of scope).
- That a Rekor envelope over an evaluator-manifest commitment is a signed release of this repository.

A Rekor hashedrekord anchors an envelope digest under a selected profile's trust assumptions. It is not a substitute for the Git commit SHA that identifies this codebase release.
