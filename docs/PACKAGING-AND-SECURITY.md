# Packaging, CI, security, and release engineering

## Python support

- **Supported / CI-tested runtime:** CPython **3.12**
- `requires-python = ">=3.12"` in `pyproject.toml`
- Release hash validation is executed on the documented Ubuntu + CPython 3.12 CI platform
- Do not claim a broader support matrix than CI exercises

## Installable package

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e .
gdi --version
gdi profiles
python -m build
```

Package name: `ens-gdi`. Console entry point: `gdi`. Software package versioning is independent of grant-decision `schemaVersion` `"0.1"` and is recorded separately from the repository release tag in `release-manifest.json`.

## Hash-locked dependencies

| File | Role |
|---|---|
| `requirements-dev.txt` | Direct development/validation pins |
| `phase2/requirements.txt` | Phase II direct pins |
| `requirements.lock.txt` | Hash-locked runtime + validation dependency set for the documented CI platform |

```bash
python -m pip install --require-hashes -r requirements.lock.txt
```

First-order version pins are **not** a complete transitive lock. The `security` CI job therefore checks that every direct runtime dependency declared in `pyproject.toml` is represented in `requirements.lock.txt`, creates a clean virtual environment, performs the exact `--require-hashes` install, runs `pip check`, and audits the resulting locked environment. A file-presence check or separately printed wheel hashes is not sufficient release evidence.

Regenerate `requirements.lock.txt` whenever release dependencies change. The recorded binary hashes are platform-specific where wheels are platform-specific; the release validation contract is Ubuntu + CPython 3.12. A different platform must regenerate and independently validate the applicable hashes rather than assuming this lock is portable.

## Exact-SHA CI identity

For pull requests, GitHub's default checkout is a synthetic merge ref, not necessarily the raw PR-head commit. The release-facing workflow therefore defines:

```text
VALIDATION_SHA = pull_request.head.sha  # pull_request
VALIDATION_SHA = github.sha             # push / workflow_dispatch
```

Every job checks out `VALIDATION_SHA` explicitly and immediately asserts `git rev-parse HEAD == VALIDATION_SHA`. Historical PR runs that used the default synthetic merge checkout are integration evidence only and must not be cited as raw-head execution evidence.

After merge, `main` receives a fresh push run for the exact resulting commit. A public release additionally uses `workflow_dispatch` on that exact `main` SHA so all six release jobs and asset assembly belong to the same workflow run.

## CI jobs

Existing required semantic job names are preserved:

- `conformance`
- `phase2`
- `schema-02`

Additive jobs (do not rename the three above):

| Job | Purpose |
|---|---|
| `package` | Exercise release-asset assembly in non-release mode; install the assembled wheel in a clean venv; exercise substantive CLI paths away from the source checkout |
| `lint-type` | `ruff` on release-facing modules and adapters; `mypy` on adapters |
| `security` | Audit development pins; prove lock coverage/installability; `pip check`; audit the locked environment |

Branch protection may continue to require only the three semantic gates for ordinary PRs. Before `v1.0.0`, all six jobs must be green on the exact release-candidate commit and again on the exact merged release commit before tagging.

## Release artifact assembler

`scripts/release_artifacts.py` is the single release-payload assembly and verification path.

A normal PR `package` job runs it with `releaseEligible=false` to exercise the complete build/SBOM/manifest/checksum machinery without creating release evidence. The generated smoke bundle is disposable and cannot satisfy release gates.

For an actual release candidate, manually dispatch `validate` on the exact `main` commit with the prospective repository tag. The `release-assets` job runs only after the six validation jobs and additionally requires:

- `GITHUB_REF == refs/heads/main`;
- checkout SHA equals `VALIDATION_SHA`;
- `scripts/study_status.py` returns `readyForFinalReview=true`;
- same-run conclusions for exactly `conformance`, `phase2`, `schema-02`, `package`, `lint-type`, and `security` are all `success`.

The assembler independently validates those conditions when `releaseEligible=true`; they are not trusted merely because the workflow wrapper says so.

The assembled payload contains:

1. exact-commit source archive;
2. Python wheel;
3. Python sdist;
4. `sbom.cdx.json`;
5. `release-validation.json`;
6. `release-manifest.json`;
7. `SHA256SUMS`.

`release-manifest.json` records the repository tag and commit, package name/version, and hashes/sizes of the source archive, wheel, sdist, SBOM, and validation report. `SHA256SUMS` is created last over those five files plus `release-manifest.json`. It necessarily excludes itself. This avoids a circular self-hash while still placing every other attached payload under the checksum manifest.

Verify a downloaded/unpacked candidate with:

```bash
python scripts/release_artifacts.py verify path/to/release-directory
```

Verification fails on missing payloads, extra unchecksummed files, duplicate checksum entries, size mismatches, or SHA-256 mismatches.

## SBOM generation

The release assembler installs the hash-locked validation environment in a clean temporary venv, installs the built `ens-gdi` wheel with `--no-deps`, and invokes the pinned `pip-audit` toolchain to emit CycloneDX JSON for that installed environment. The SBOM therefore describes the release-validation environment containing the built package and locked dependencies; it is not presented as a minimal-runtime-only dependency graph.

The SBOM toolchain is part of the validated release environment in `requirements.lock.txt`. A future change to a different SBOM generator or scope requires an explicit documentation and lock update.

## Static analysis notes

- **Ruff:** configured in `pyproject.toml`; CI fails on lint findings for the explicitly enumerated release-facing package, adapter, release-engineering, and test surfaces.
- **Mypy:** gradual typing is currently enforced on `adapters`. Do not describe this as whole-repository static type coverage, and do not treat a coverage percentage as a correctness metric.

## Branch protection (required settings)

Documented requirements for `main` before `v1.0.0`. Do not silently bypass. Maintainers with admin access should verify these in GitHub settings; this document does not force-change repository settings via API.

Required:

1. Require a pull request before merging to `main`
2. Require status checks to pass on the exact head: at minimum `conformance`, `phase2`, `schema-02`
3. Require branches to be up to date before merging (if operationally appropriate)
4. Prohibit force-push to `main`
5. Prohibit deletion of `main`
6. Require review for protocol/security changes where team size permits
7. Minimize administrator bypass for release candidates / `main`
8. Signed commits/tags only if the team can operate that policy reliably

Record any setting that cannot be enforced in release notes rather than implying it is enforced.

See also `docs/BRANCH-PROTECTION.md`.

## Reproducible build claims

Deterministic inputs and a documented build recipe (Python 3.12, validated hash-locked dependencies, `python -m build`) are expected. **Byte-reproducible** wheel/sdist identity across machines is **not** claimed unless demonstrated with evidence.
