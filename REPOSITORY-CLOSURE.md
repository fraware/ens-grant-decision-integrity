# Repository closure record

**Closure date:** 2026-08-26  
**Scope:** repository/integration closure for the current development campaign.  
**Authority boundary:** this record closes active engineering/repository work; it does **not** convert incomplete empirical evidence or weaker-than-target branch protection into satisfied `v1.0.0` release gates.

## Closure decision

The repository is being reduced to a single authoritative development line: `main`.

At closure:

- there are no open pull requests;
- all accepted engineering work is represented on `main`;
- historical branches that are ancestors of `main` are redundant;
- two old August 24 work branches diverged before later release hardening and are explicitly **superseded**, not candidates for wholesale merge;
- the remaining genuine human second-annotation requirement is not fabricated or waived as completed;
- the documented six-check branch-protection target is not claimed to be enforced when the live machine-readable state shows only three required contexts;
- no `v1.0.0` tag is authorized by repository closure alone.

This file intentionally does not self-reference its own containing commit SHA. The authoritative closure commit is the merge commit that introduces this record, followed by a successful exact-SHA `validate` push run on `main`.

## Pre-closure authoritative baseline

Immediately before this closure record was created, authoritative `main` was:

`dce0eec8e60409202e74fa939c5494da3bdbb83f`

Push workflow run `32998524511` completed successfully on that exact SHA with all six release-critical jobs successful:

- `conformance`
- `phase2`
- `schema-02`
- `package`
- `lint-type`
- `security`

`release-assets` was correctly skipped because that run was an ordinary push, not the guarded manual release workflow.

The closure merge itself must be revalidated independently; the pre-closure baseline is not evidence for a later tree.

## Pull-request disposition

At closure there are **zero open pull requests**.

The final repository-hardening line was integrated through reviewed/validated pull requests, including PR #29 (final release hardening) and PR #34 (binding all three frozen second-annotation handoffs to exact byte length, SHA-256 identity, strict JSON loading, and regeneration from current cases).

No closed/superseded PR is reopened merely to make its historical commit graph appear linear. A closed PR that was explicitly superseded remains historical evidence, not an integration obligation.

### Historical stacked PR #9

PR #9, `Add preserved source artifacts and retrospective corpus infrastructure`, is explicitly recorded in its own body as **Superseded**. It states that the stacked branch was prepared before PR #8 was accepted, is no longer the integration path, and **should not be rebased or merged wholesale** because that would make review provenance and version boundaries harder to reconstruct. Its intended source-artifact, policy-pin, retrospective-corpus, and allocation-capture work was subsequently re-audited and reintroduced from accepted `main` in narrower changes.

That disposition is preserved. Closure does not reverse it.

## Branch provenance and disposition

Original non-`main` branch tips immediately before closure:

| Branch | Original tip | Relationship / disposition |
|---|---|---|
| `evidence/corpus-spp3-namespace` | `c79dada801fe828ba915e52e48138345f30c7a46` | Ancestor of pre-closure `main`; redundant. |
| `research/double-annotation-freeze-2` | `00fb82311d3be427f45d50697f4d74aa111886f2` | Ancestor of pre-closure `main`; redundant. |
| `research/double-annotation-freeze-v1` | `00fb82311d3be427f45d50697f4d74aa111886f2` | Ancestor of pre-closure `main`; redundant duplicate ref. |
| `research/double-annotation-freeze-v2` | `00fb82311d3be427f45d50697f4d74aa111886f2` | Ancestor of pre-closure `main`; redundant duplicate ref. |
| `work/source-corpus` | `c213c30bbcbfb6a2a5a294a1b8e108c1e18f30c4` | Diverged historical stacked line; associated PR #9 is explicitly superseded and not to be merged wholesale. |
| `work/source-artifact-binding-v2` | `8f79b074fd34dc0337c54106bb770e56279eb140` | Diverged pre-hardening August 24 development line; do not merge wholesale into the later hardened protocol tree. |

### Why the two divergent work branches are not merged

A branch containing commits absent from `main` is not automatically valid pending work. These two branches diverged from the August 24 pre-hardening graph and contain older versions of protocol, replay, projection, source-artifact, and documentation surfaces.

Their intended capabilities were subsequently integrated through narrower accepted changes and then hardened further on `main`. In particular:

- merged PR #10 introduced exact-byte source-artifact and policy-pin provenance controls from the accepted `main` baseline;
- later corpus PRs introduced the predeclared corpus, exact record/finding binding, empirical cases, and machine study status;
- later Phase II/replay hardening retained a dedicated fail-closed replay regression suite on `main`;
- PR #29 integrated the final engineering/release-integrity hardening line;
- PR #34 strengthened the frozen human-annotation handoff regression evidence.

Merging either stale work branch wholesale at closure would reintroduce an obsolete graph and would require resolving old protocol/wire-format changes against substantially newer implementations. That would increase semantic risk while weakening provenance clarity. The correct disposition is **superseded historical line, not merged**.

After this closure record is merged and its exact `main` SHA passes the full six-job validation contract, every non-`main` branch ref is to be moved to that exact final `main` SHA. This deliberately removes all branch-level divergent work while preserving the original tips above in this immutable closure record and in Git history. If the connected repository interface does not expose physical Git-ref deletion, the names may remain as redundant aliases to `main`; they are not active development lines and contain no unique tip after the collapse.

## Empirical-study closure boundary

The corpus contains nine counted empirical cases. The machine study-status contract requires at least 25% genuine independent double annotation; at the current corpus size this means three cases. The selected cases remain:

- `ens-spp3-2026-namespace-award`
- `ens-spp3-2026-ethid-withdrawal`
- `ens-spp2-2025-agora-budget-rejection`

At repository closure, genuine independent second annotations remain **0/9**. The frozen source-only handoffs exist and are machine-bound, but no human-return `.completed.json` artifacts are fabricated by engineering.

Issue #30 is therefore closed administratively as **not planned in this closed repository campaign**, not as completed. If a future release effort resumes, the requirement must be reopened or re-established from the frozen protocol and satisfied with genuine human work before any empirical-completion or population-reliability claim is made.

The following remain non-claims:

- repository closure does not establish independent human annotation;
- three eventual second annotations would satisfy the declared fraction but would not establish population-level reliability;
- current retrospective `elapsedMinutes` values do not establish total administrative burden or proportionality;
- the current design does not identify a causal/comparative reconstructability improvement effect.

## Branch-protection closure boundary

Live machine-readable GitHub state before closure shows `main` protected, but required status contexts are only:

- `conformance`
- `phase2`
- `schema-02`

The documented target additionally requires:

- `package`
- `lint-type`
- `security`

The repository Rulesets collection is empty, and the connected integration cannot read or modify the full effective protection configuration. Therefore repository closure does **not** claim six-check branch protection.

Issue #31 is closed administratively as **not planned / accepted unresolved release-control deviation for this closed campaign**, not as completed. This deviation remains disqualifying for the documented `v1.0.0` target unless an authorized maintainer later changes and verifies the effective protection configuration.

## Release disposition

Repository closure is **not** `v1.0.0` release authorization.

The latest published release remains `v0.3.2`. The package-line `0.4.0` work on `main` remains unreleased development state unless a future release campaign independently satisfies the remaining empirical, protection, final-candidate, artifact-verification, and publication gates.

Do not infer any of the following from this closure record:

- that the empirical study is complete;
- that branch protection meets the six-check target;
- that `release-assets` has produced an eligible final candidate;
- that an SBOM/checksum bundle from a non-release run is a published release asset;
- that `v1.0.0` exists;
- that historical source truth, institutional adoption, fairness, merit, legitimacy, payment, transfer, receipt, or settlement has been established beyond the repository's explicitly bounded evidence.

## Reopening rule

If this project is resumed, start from then-current `main`, not from any historical branch alias. Before a future `v1.0.0` attempt:

1. verify all three genuine human second annotations and integrate them without rewriting primaries;
2. compute and report pre-reconciliation agreement honestly;
3. regenerate corpus metrics, study status, and the final empirical report from the exact resulting commit;
4. enforce and verify the intended `main` protection policy, or explicitly define a new documented target;
5. run all six jobs on the exact final `main` SHA;
6. execute the guarded manual release workflow so `release-assets` runs on that same eligible SHA;
7. verify candidate bytes, manifests, checksums, SBOM, workflow identity, and published artifacts before tagging.

Historical branches must not be revived as an alternative integration path.

## Closure acceptance criteria

The repository campaign is operationally closed when all of the following are true:

- this closure record is merged into `main`;
- the exact closure merge SHA passes `conformance`, `phase2`, `schema-02`, `package`, `lint-type`, and `security`;
- there are zero open PRs;
- issues #30 and #31 are closed with `not_planned` semantics and explicit unresolved-boundary comments;
- every non-`main` branch ref points to the exact final `main` SHA, leaving no branch with unique active work;
- a final read-back confirms authoritative `main`, CI, PR, issue, and branch state.

Physical deletion of redundant branch names is desirable but is not represented as complete unless the repository interface actually exposes and executes Git-ref deletion. Collapsing all non-`main` refs onto the final `main` SHA is the fail-safe fallback because it removes divergent active state without inventing a deletion operation.