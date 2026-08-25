# Branch protection requirements

These settings are required for `main` ahead of `v1.0.0`. They are documentation for maintainers and release managers. This repository automation does **not** attempt to change GitHub branch protection via API from ordinary CI.

## Required protections

| Setting | Requirement |
|---|---|
| Pull requests | Required before merge to `main` |
| Required status checks | Exact head must pass `conformance`, `phase2`, and `schema-02` |
| Up-to-date branch | Prefer requiring branch up-to-date before merge |
| Force push | Disabled for `main` |
| Delete branch | Disabled for `main` |
| Reviews | Required for protocol/security changes where team size permits |
| Admin bypass | Minimized for release candidates and `main` |
| Signed commits/tags | Optional; enable only if operable |

## Additive checks

Jobs `package`, `lint-type`, and `security` are additive. Keep the three semantic job **names** unchanged until branch protection is deliberately migrated in the same reviewed administrative change.

Before tagging a release, the release-candidate commit must also have green `package`, `lint-type`, and `security` evidence even if those jobs are not yet mandatory on every PR.

## Verification

Maintainers should confirm settings in GitHub: **Settings → Branches → Branch protection rules** (or Rulesets). If a desired control cannot be enforced, state that limitation in release notes.
