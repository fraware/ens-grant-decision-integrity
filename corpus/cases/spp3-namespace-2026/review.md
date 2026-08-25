# SPP3 Namespace retrospective case review

## Scope

This case reconstructs the Namespace service-provider award within ENS SPP3 using public sources only. It was selected before examining validator outcome because it exercises multiple predeclared stress-test strata: approved award, merit evaluation, committee quorum, conflict/recusal, policy/timeline ambiguity, delivery accountability, public/private separation, and incomplete public evidence. It does not rescore Namespace or any other applicant.

## Source basis

1. **Program authorization and committee model** — `https://discuss.ens.domains/t/6-42-social-spp3-program-authorization-and-committee-model/22086`. Used for program mandate, committee composition, quorum and voting rules, conflict rules, authority separation, evaluation floor, and provider obligations.
2. **Submission timeline and rubric** — `https://discuss.ens.domains/t/spp3-submission-timeline-and-artifacts/22124`. Used for the hard eligibility screen and weighted criteria.
3. **Cohort recommendation** — `https://discuss.ens.domains/t/ep-6-49-spp3-cohort-recommendation/22237`. Used for the Namespace award, published aggregate scores, committee rationale, recusal disclosure, Chair scoring substitution, private/internal scoring boundary, delivery prerequisites, and later process narrative.
4. **Executed-proposal mirror** — `https://dao.ens.gregskril.com/proposal/30153206728472299340257495645753485226870528642942223493225654414745632348879`. Used for the displayed executed status, vote totals, quorum, and vote-end time. It is not treated as an independent cryptographic execution proof.
5. **Namespace application URI** — `https://bronze-accused-porpoise-217.mypinata.cloud/ipfs/bafybeiee73y2jwinefaszeng3frn47wmqini562qtcibzgnh42cnqiu2la`. The cohort recommendation links this URI, but retrieval was unsuccessful during reconstruction. No application-content claim is inferred from inaccessible content.

All five source entries are `reference-only`. The repository therefore makes no exact-byte preservation claim for these remote sources in this case. This is deliberately weaker than a redistributable Source Artifact and is reported as such by corpus metrics.

## Directly supported decision facts

The public cohort record reports a four-provider cohort totaling $1.69M and a $500,000 Namespace award. It reports Namespace aggregate criterion means of 4.1 (Prior Delivery), 3.4 (Scope Clarity), 3.3 (Milestones), and 3.5 (Adoption/Revenue/Utility), with a 3.43 weighted subtotal after excluding the 5% discretionary component. It also states that sovereignsignal.eth was recused from Namespace evaluation and vote, and that the Chair's independent scores replaced the recused scoring input for the Namespace row.

The authorization gives the committee four Member seats plus a Chair, requires 3 of 4 Members active for cohort voting/ranking, simple majority of participating Members, and Chair voting only as a tiebreaker. The final institutional decision is modeled separately as a DAO vote because the authorization makes the committee recommendation take-it-or-leave-it for final executable ratification.

## Deliberately unresolved fields

Two schema-v0.1 required timestamps are not reconstructed to exact instants: `governingPolicy.effectiveAt` and `eligibility.checkedAt`. Both are stored as `null`. The resulting `SCHEMA` findings are part of the empirical result and are not repaired with estimated dates.

The public artifacts also do not establish the underlying facts causing the Namespace conflict, internal individual scoring records or possible disagreements, a dedicated post-decision factual/procedural correction path, final provider-specific Award Notice contents, or the application body at the linked IPFS gateway. These remain explicit unknowns.

## Timeline ambiguity

The May 14 public timeline lists provider submissions closing June 9. The later cohort process narrative says submissions closed June 4. This case does not silently choose one as authoritative. The discrepancy is preserved as a policy/timeline ambiguity for later adjudication.

## Validator interpretation

The exact initial record hash is `sha256:04dd888a9d0c136d607a8903138ca2e402fcc2950f9cf33a8edb6a501aa87dd5`. The corpus verifier must re-hash those bytes and bind `verification.initialFindings` to the actual decision-record validator output. Because structural schema findings short-circuit semantic conformance in the current validator, semantic requirements that would otherwise be evaluated are not represented as having passed. In particular, the absence of a `CHAL002` finding in this structurally invalid record is not evidence that the public challenge/correction representation is adequate.

No reconciliation has been performed. The initial record remains the final record for this case, preserving the two unresolved structural findings.
