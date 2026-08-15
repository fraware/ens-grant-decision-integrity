# Review Request — Draft v0.1

## Intended audience

SPP3 committee / accountability participants and Lighthouse Labs contributors working on grant evaluation.

## Objective

Obtain one concrete external judgment on whether the Charter and decision-record schema would improve an actual ENS funding process without adding disproportionate administrative overhead.

The request is deliberately for critique, not endorsement or funding.

## Public forum note

I used the recent ENS Simocracy experiment to test a narrow governance question: if grant evaluation becomes more structured and increasingly AI-assisted, what minimum record should exist so the DAO can still reconstruct how a material decision was made?

Five ENS Governance funding decisions allocated a cumulative $219 to the resulting proposal, with evaluators repeatedly identifying the Grants Charter and commit–reveal treatment of AI-assisted screening as the distinctive pieces. I have now implemented the first tranche as a small v0.1 package: a draft Grant Decision Integrity Charter, a machine-readable decision-record schema, and a non-evaluative mapping of the current Marketplace RFP into that schema.

I deliberately used the Marketplace RFP only as a process example. The example does not identify, score, or comment on any live applicant.

The question I would value feedback on is narrow: **which fields would actually improve the committee/accountability workflow, and which fields would create process cost without enough audit value?**

In particular, I would be interested in reactions to three boundaries:

1. public normative criteria versus operational evaluator details;
2. public decision records versus selectively disclosed audit material;
3. milestone verification versus substantive re-evaluation of the grantee.

If the schema is useful, I can revise it against the committee's actual workflow. If a simpler record provides the same guarantees, I would prefer the simpler design.

## Direct review request

I built a small v0.1 artifact from the ENS Simocracy proposal on grant decision integrity: a draft Charter plus a JSON decision-record schema. I mapped the public Marketplace RFP process into one fictional, pending record so the design could be tested against a real ENS workflow without touching live applicant evaluation.

Would you be willing to give it a quick adversarial read from the committee/accountability side? The useful question for me is not “do you like the idea?” It is: **what would you delete, what is missing, and what would make this impractical to use in an actual grant round?**

I am especially interested in whether the proposed boundary between public criteria and committed/revealed operational evaluator details addresses the prompt-gaming concern raised in the AI screening experiment without creating unnecessary process overhead.

## Review checklist

A reviewer can respond to any subset:

- Is policy versioning already captured elsewhere in a way that makes the schema field redundant?
- Is an evidence link for every material finding realistic?
- Should individual evaluator identity remain internal in some programs?
- Is preserved disagreement valuable, or would it create noise?
- Is the proposed factual-correction challenge path too broad or too narrow?
- Which milestone fields match the accountability body's actual needs?
- Where should confidential applicant evidence live?
- Is commit–reveal worth implementing, or is simple evaluator versioning sufficient?
- What is the minimum decision record you would actually use?

## Success condition

The review succeeds if it produces at least one concrete schema deletion, addition, or constraint grounded in an actual ENS review workflow.
