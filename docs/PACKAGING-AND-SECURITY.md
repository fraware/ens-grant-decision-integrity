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

Package name: `ens-gdi`. Console entry point: `gdi`. Software version is independent of grant-decision `schemaVersion` `"0.1"`.

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

## Additive CI jobs

Existing required semantic job names are preserved:

- `conformance`
- `phase2`
- `schema-02`

Additive jobs (do not rename the three above):

| Job | Purpose |
|---|---|
| `package` | Build sdist/wheel; install wheel in a clean venv; exercise substantive CLI paths away from the source checkout |
| `lint-type` | `ruff` on release-facing modules and adapters; `mypy` on adapters |
| `security` | Audit development pins; prove runtime-lock coverage/installability; `pip check`; audit the locked environment |

Branch protection may continue to require only the three semantic gates for ordinary PRs. Before `v1.0.0`, all six jobs must be green on the exact release-candidate commit and again on the exact merged release commit before tagging.

## Static analysis notes

- **Ruff:** configured in `pyproject.toml`; CI fails on lint findings for the explicitly enumerated release-facing package, adapter, and test surfaces.
- **Mypy:** gradual typing is currently enforced on `adapters`. Do not describe this as whole-repository static type coverage, and do not treat a coverage percentage as a correctness metric.

## SBOM tooling

For a release candidate, generate an SBOM from the built package/environment and attach it as a release asset:

```bash
# CycloneDX (optional extra: pip install 'ens-gdi[sbom]' or cyclonedx-bom)
cyclonedx-py environment -o sbom.cdx.json
# or
cyclonedx-py pyproject -o sbom.cdx.json

# SPDX: use an SPDX-capable tool against the same locked environment
# (for example syft/trivy scan of the release venv or built wheel).
```

Publish the SBOM alongside wheel, sdist, SHA-256 manifest, and release validation report. The SBOM-generation toolchain is separate from the application runtime lock unless explicitly incorporated into that lock and validated. Record the tool/version used in the release manifest.

This repository does **not** claim byte-reproducible builds unless two independent clean builds of the same commit produce byte-identical artifacts under a documented process and that evidence is attached.

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
