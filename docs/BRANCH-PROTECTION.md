# Branch protection requirements

These settings are the required target state for `main` ahead of `v1.0.0`. They are documentation for maintainers and release managers. Repository CI does **not** change GitHub branch protection or Rulesets from ordinary workflow runs, and the current integration cannot independently read the active protection configuration (the branch-protection API request returns 403). Therefore this file defines the desired control state; it is not evidence that the settings are currently enabled.

## Required protections before v1.0.0

| Setting | Requirement |
|---|---|
| Pull requests | Required before merge to `main` |
| Required status checks | Exact candidate SHA must pass `conformance`, `phase2`, `schema-02`, `package`, `lint-type`, and `security` |
| Up-to-date branch | Require the PR branch to be current with `main` before merge when GitHub configuration permits this without weakening exact-SHA evidence |
| Force push | Disabled for `main` |
| Delete branch | Disabled for `main` |
| Reviews | Required for protocol/security/release-control changes where team size permits |
| Admin bypass | Disabled or minimized for release candidates and `main`; any unavoidable bypass must be disclosed in release evidence |
| Signed commits/tags | Optional; enable only if the team can operate and verify the policy reliably |

The workflow preserves the historical semantic job names `conformance`, `phase2`, and `schema-02`. The additive `package`, `lint-type`, and `security` jobs are now also release-critical because they cover distribution assembly, static checks, lock installability, and dependency audit. A final-release branch-protection configuration that requires only the historical three jobs is weaker than the documented v1.0.0 target.

## Exact-SHA semantics

For pull requests, the workflow explicitly checks out `github.event.pull_request.head.sha` and asserts that `git rev-parse HEAD` equals `VALIDATION_SHA` before every release-facing job. Do not substitute a GitHub synthetic PR merge-ref run for this raw-head evidence.

After merge, the exact resulting `main` SHA receives a fresh push validation. The manual release-candidate workflow runs all six jobs again on the selected `main` SHA before `release-assets` can execute.

Branch protection complements these in-tree controls; it does not replace them. Conversely, a green workflow does not prove that force-push, review, bypass, or deletion protections are configured.

## Administrative verification record

Before making PR #29 ready for final release review and again before tagging `v1.0.0`, an authorized maintainer should inspect **Settings → Branches / Rulesets** and record at minimum:

- whether PR-before-merge is enforced;
- the exact required status-check names;
- whether force-push and deletion are disabled;
- review requirements and dismissal behavior;
- administrator/repository-role bypass allowances;
- whether branch-up-to-date is required;
- any Ruleset that overlaps or overrides classic branch protection.

If the target cannot be enforced, record the actual configuration and limitation in the final validation report and release notes. Do not write “six-check branch protection” unless the six contexts are actually required by GitHub settings.

## Release decision

The repository may not treat this documentation as proof of active protection. The final release acceptance record should keep the branch-protection gate `partial / unverified-setting` until an authorized settings inspection provides evidence of the active configuration. If the active configuration is weaker than the target, either strengthen it before release or disclose the deviation and explicitly decide whether it is acceptable; do not silently waive it.
