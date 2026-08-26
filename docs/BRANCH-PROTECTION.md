# Branch protection requirements

These settings are the required target state for `main` ahead of `v1.0.0`. They are documentation for maintainers and release managers; repository CI does **not** change GitHub branch protection or Rulesets from ordinary workflow runs.

## Last independently observed GitHub state

As of 2026-08-26, the GitHub branch summary for `main` reports classic branch protection enabled, but its required status-check contexts are exactly:

- `conformance`
- `phase2`
- `schema-02`

The repository Rulesets API returns no repository Rulesets. Therefore the independently observable configuration is **weaker than the v1.0.0 target** because `package`, `lint-type`, and `security` are not currently required status contexts.

The full classic branch-protection endpoint remains inaccessible to the available integration (HTTP 403). Consequently, PR-before-merge enforcement, strict/up-to-date behavior, review/dismissal rules, force-push/deletion controls, and bypass allowances are not independently verified here. The known three-check state and the unreadable remaining settings are separate facts; neither should be generalized into a claim that protection is wholly unknown or fully compliant.

This observation is a point-in-time release-control record, not a mechanism that freezes GitHub settings. An authorized maintainer must re-check the effective configuration immediately before final review/merge and before `v1.0.0` publication.

## Required protections before v1.0.0

| Setting | Requirement |
|---|---|
| Pull requests | Required before merge to `main` |
| Required status checks | Exact candidate SHA must pass and GitHub must require `conformance`, `phase2`, `schema-02`, `package`, `lint-type`, and `security` |
| Up-to-date branch | Require the PR branch to be current with `main` before merge when GitHub configuration permits this without weakening exact-SHA evidence |
| Force push | Disabled for `main` |
| Delete branch | Disabled for `main` |
| Reviews | Required for protocol/security/release-control changes where team size permits |
| Admin bypass | Disabled or minimized for release candidates and `main`; any unavoidable bypass must be disclosed in release evidence |
| Signed commits/tags | Optional; enable only if the team can operate and verify the policy reliably |

The workflow preserves the historical semantic job names `conformance`, `phase2`, and `schema-02`. The additive `package`, `lint-type`, and `security` jobs are also release-critical because they cover distribution assembly, static checks, lock installability, and dependency audit. The currently observed three-check requirement does not satisfy the documented v1.0.0 target.

## Exact-SHA semantics

For pull requests, the workflow explicitly checks out `github.event.pull_request.head.sha` and asserts that `git rev-parse HEAD` equals `VALIDATION_SHA` before every release-facing job. Do not substitute a GitHub synthetic PR merge-ref run for this raw-head evidence.

After merge, the exact resulting `main` SHA receives a fresh push validation. The manual release-candidate workflow runs all six jobs again on the selected `main` SHA before `release-assets` can execute.

Branch protection complements these in-tree controls; it does not replace them. Conversely, a green workflow does not prove that force-push, review, bypass, deletion, or required-check settings are correctly configured.

## Administrative verification record

Before making PR #29 ready for final release review and again before tagging `v1.0.0`, an authorized maintainer should inspect **Settings → Branches / Rulesets** and record at minimum:

- that `package`, `lint-type`, and `security` have been added to the currently observed `conformance`, `phase2`, and `schema-02` required contexts;
- whether PR-before-merge is enforced;
- whether the branch must be up to date before merge;
- whether force-push and deletion are disabled;
- review requirements and dismissal behavior;
- administrator/repository-role bypass allowances;
- any Ruleset added after the 2026-08-26 observation and its interaction with classic protection.

If the target cannot be enforced, record the actual configuration and limitation in the final validation report and release notes. Do not write “six-check branch protection” unless the six contexts are actually required by GitHub settings.

## Release decision

The branch-protection gate currently **fails the six-check requirement** and remains partially unverified for controls hidden behind the inaccessible full protection endpoint. Before final release, either strengthen the active configuration to the target and verify the remaining controls, or explicitly disclose and deliberately accept any deviation. Documentation alone is never evidence that the settings are active.
