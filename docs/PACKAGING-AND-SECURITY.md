# Packaging, CI, security, and release engineering

## Python support

- **Supported / CI-tested runtime:** CPython **3.12**
- `requires-python = ">=3.12"` in `pyproject.toml`
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
| `requirements.lock.txt` | Hash-locked direct + transitive set for release/validation reinstall |

```bash
python -m pip install --require-hashes -r requirements.lock.txt
```

First-order version pins are **not** a complete transitive lock. Regenerate `requirements.lock.txt` when release dependencies change. Platform-specific wheels can differ; release validation should use the documented CI platform (ubuntu + CPython 3.12) or regenerate hashes there.

## Additive CI jobs

Existing required semantic job names are preserved:

- `conformance`
- `phase2`
- `schema-02`

Additive jobs (do not rename the three above):

| Job | Purpose |
|---|---|
| `package` | Build sdist/wheel; install wheel; CLI smoke |
| `lint-type` | `ruff` on adapters/package; `mypy` on public modules |
| `security` | `pip-audit` on direct pins; lock/SBOM notes |

Branch protection may continue to require only the three semantic gates for ordinary PRs. Before `v1.0.0`, package/lint/security should be green on the exact release-candidate commit (release workflow or required checks).

## Static analysis notes

- **Ruff:** configured in `pyproject.toml`; CI fails on lint findings for `src/gdi`, `adapters`, and new profile/adapter tests.
- **Mypy:** gradual typing on `gdi` and `adapters`. Tighten public APIs over time; do not treat global coverage percentage as a correctness metric.

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

Publish the SBOM alongside wheel, sdist, SHA-256 manifest, and release validation report. This repository does **not** claim byte-reproducible builds unless two independent clean builds of the same commit produce byte-identical artifacts under a documented process and that evidence is attached.

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

Deterministic inputs and a documented build recipe (Python 3.12, locked deps, `python -m build`) are expected. **Byte-reproducible** wheel/sdist identity across machines is **not** claimed unless demonstrated with evidence.
