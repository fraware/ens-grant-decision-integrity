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

## Hash-locked dependencies and build toolchain

| File | Role |
|---|---|
| `requirements-dev.txt` | Direct development/validation pins |
| `phase2/requirements.txt` | Phase II direct pins |
| `requirements.lock.txt` | Hash-locked release/validation environment for the documented CI platform |
| `requirements-build.lock.txt` | Hash-locked release build frontend/backend toolchain |

```bash
python -m pip install --require-hashes -r requirements.lock.txt
python -m pip install --require-hashes -r requirements-build.lock.txt
```

First-order version pins are **not** a complete transitive lock. The `security` CI job therefore checks that every direct runtime dependency declared in `pyproject.toml` is represented in `requirements.lock.txt`; checks that every PEP 517 build-system requirement is exactly pinned and represented at the same version in `requirements-build.lock.txt`; creates clean virtual environments for both lockfiles; performs exact `--require-hashes` installs; runs `pip check`; and audits both dependency sets. A file-presence check or separately printed wheel hashes is not sufficient release evidence.

The PEP 517 backend requirements in `pyproject.toml` are exact pins. Release distribution assembly does **not** allow the build frontend to create a fresh isolated environment from open-ended backend constraints. `scripts/release_artifacts.py` creates a disposable build venv from `requirements-build.lock.txt` and invokes `python -m build --no-isolation`, so the wheel and sdist are built with the reviewed toolchain versions and hashes.

Regenerate either lockfile deliberately whenever its corresponding dependency set changes. Recorded binary hashes are platform-specific where wheels are platform-specific; the release validation contract is Ubuntu + CPython 3.12. A different platform must regenerate and independently validate applicable hashes rather than assuming these locks are portable.

## Exact-SHA CI identity

For pull requests, GitHub's default checkout is a synthetic merge ref, not necessarily the raw PR-head commit. The release-facing workflow therefore defines:

```text
VALIDATION_SHA = pull_request.head.sha  # pull_request
VALIDATION_SHA = github.sha             # push / workflow_dispatch
```

Every job checks out `VALIDATION_SHA` explicitly and immediately asserts `git rev-parse HEAD == VALIDATION_SHA`. Historical PR runs that used the default synthetic merge checkout are integration evidence only and must not be cited as raw-head execution evidence.

After merge, `main` receives a fresh push run for the exact resulting commit. A public release additionally uses `workflow_dispatch` on that exact `main` SHA so all six prerequisite release jobs and asset assembly belong to the same workflow run.

## CI jobs

The release-critical prerequisite job names are:

- `conformance`
- `phase2`
- `schema-02`
- `package`
- `lint-type`
- `security`

| Job | Purpose |
|---|---|
| `conformance` | v0.1 contract, source/policy checks, corpus protocol, claims, profiles, adapters, and release-verifier tests |
| `phase2` | Phase II graph, commitment, replay, disclosure, and anchor-profile tests |
| `schema-02` | Schema 0.2 and projection tests, including generative coverage |
| `package` | Exercise release-asset assembly in non-release mode; install the assembled wheel in a clean venv; exercise substantive CLI paths away from the source checkout |
| `lint-type` | `ruff` on release-facing modules and adapters; `mypy` on adapters |
| `security` | Audit development pins; prove validation/build lock coverage and installability; run `pip check`; audit both locked environments |

The manual release run adds the seventh `release-assets` job after all six prerequisites. The historical three semantic contexts remain important for continuity, but the documented `v1.0.0` protection target is all six prerequisite release-critical contexts. Do not describe a three-check configuration as satisfying the final six-check target. The effective GitHub settings remain an administrative fact that must be verified separately; see `docs/BRANCH-PROTECTION.md` and release-control issue #31.

## Release artifact assembler

`scripts/release_artifacts.py` is the release-payload assembly and verification path, with separate offline and online evidence layers.

A normal PR `package` job runs assembly with `releaseEligible=false` to exercise the complete build/SBOM/manifest/checksum machinery without creating release evidence. The generated smoke bundle is disposable and cannot satisfy release gates.

For an actual release candidate, manually dispatch `validate` on the exact `main` commit with the prospective repository tag. The `release-assets` job runs only after the six validation jobs and additionally requires:

- `GITHUB_REF == refs/heads/main`;
- checkout SHA equals `VALIDATION_SHA`;
- `scripts/study_status.py` returns `readyForFinalReview=true`;
- same-run conclusions for exactly `conformance`, `phase2`, `schema-02`, `package`, `lint-type`, and `security` are all `success`.

The workflow-generated `release-validation.json` binds the candidate to repository, workflow name, event type, run ID, run attempt, exact commit/ref, six prerequisite job conclusions, and study status. The assembler validates that report against the local release policy before accepting `releaseEligible=true`. This is an internal consistency/policy check; it does **not** independently authenticate GitHub's Actions database.

The assembled payload contains:

1. exact-commit source archive;
2. Python wheel;
3. Python sdist;
4. `sbom.cdx.json`;
5. `release-validation.json`;
6. `requirements-build.lock.txt`;
7. `requirements.lock.txt`;
8. `release-manifest.json`;
9. `SHA256SUMS`.

`release-manifest.json` records the repository tag and commit, package name/version, explicit non-isolated build-toolchain policy, and hashes/sizes of every payload asset except itself. `SHA256SUMS` is created last over those seven payload files plus `release-manifest.json`. It necessarily excludes itself. This avoids a circular self-hash while placing every other attached payload under the checksum manifest.

### Verification layers

After the manual workflow has **completed**, download the candidate and run:

```bash
python scripts/release_artifacts.py verify path/to/release-directory
python scripts/release_artifacts.py verify-github path/to/release-directory
```

`verify` is offline. It fails on unsafe/path-escaping names, symbolic links, nested or non-regular entries, missing required payload classes, extra unchecksummed files, duplicate checksum entries, size mismatches, SHA-256 mismatches, invalid toolchain policy, or validation-evidence/manifest commit mismatch. It establishes integrity and internal consistency of the bytes supplied to it; it does not prove GitHub executed the workflow described by `release-validation.json`.

`verify-github` first runs the same offline verification, then queries GitHub's Actions API for the report's run ID. It requires the API record to match the expected public repository, `validate` workflow and workflow path, `workflow_dispatch` event, run attempt, `main` branch, exact candidate commit, completed/successful workflow conclusion, and workflow URL. It also requires exactly seven jobs: the six release-critical prerequisites plus `release-assets`, all completed successfully. Each prerequisite must expose a successful `Assert exact validation SHA` step, and `release-assets` must expose a successful `Require exact main-branch release commit` step.

`GITHUB_TOKEN` may be supplied to `verify-github` for authentication/rate limits. For this public repository anonymous API access can be sufficient when GitHub permits it.

This online check authenticates current GitHub API state for the referenced run. It does not cryptographically sign the candidate payload or prove that GitHub itself cannot later alter API state. Candidate bytes remain independently bound by `release-manifest.json` and `SHA256SUMS`. No signed artifact-attestation claim is made unless such an attestation is actually generated and verified.

## SBOM generation

The release assembler installs the hash-locked validation environment in a clean temporary venv, installs the built `ens-gdi` wheel with `--no-deps`, and invokes the pinned `pip-audit` toolchain to emit CycloneDX JSON for that installed environment. The SBOM therefore describes the release-validation environment containing the built package and locked dependencies; it is not presented as a minimal-runtime-only dependency graph.

The SBOM toolchain is part of the validated release environment in `requirements.lock.txt`. A future change to a different SBOM generator or scope requires an explicit documentation and lock update.

## Static analysis notes

- **Ruff:** configured in `pyproject.toml`; CI fails on lint findings for the explicitly enumerated release-facing package, adapter, release-engineering, and test surfaces.
- **Mypy:** gradual typing is currently enforced on `adapters`. Do not describe this as whole-repository static type coverage, and do not treat a coverage percentage as a correctness metric.

## Branch protection (required target)

Documented target for `main` before `v1.0.0`. Do not silently bypass. Maintainers with admin access must verify the effective GitHub settings; this document does not force-change repository settings via API.

Required target:

1. Require a pull request before merging to `main`
2. Require all six prerequisite release-critical status contexts: `conformance`, `phase2`, `schema-02`, `package`, `lint-type`, `security`
3. Require branches to be up to date before merging where operationally appropriate
4. Prohibit force-push to `main`
5. Prohibit deletion of `main`
6. Require review for protocol/security changes where team size permits
7. Minimize administrator/repository-role bypass for release candidates and `main`
8. Signed commits/tags only if the team can operate that policy reliably

Record any setting that cannot be enforced in release notes rather than implying it is enforced.

See also `docs/BRANCH-PROTECTION.md`.

## Reproducible build claims

Pinned build frontend/backend versions, hash-locked build inputs, a documented CPython/Ubuntu platform, and a non-isolated build recipe substantially narrow build variability. They do **not** establish cross-machine byte reproducibility. A **byte-reproducible** wheel/sdist claim requires independent clean builds of the same commit to produce byte-identical target artifacts under a documented comparison protocol, with that evidence retained.
