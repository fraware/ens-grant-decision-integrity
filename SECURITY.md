# Security and sensitive disclosures

This repository contains governance specifications, validation code, and fictional examples. It should not contain applicant-confidential material, production credentials, or undisclosed evaluator configuration.

Phase II test vectors may include test-log and test-attestation private keys. Those keys exist only for the harness and the public retrospective example. They are not production keys and MUST NOT be reused for a live program.

The packaged `gdi` verifier and claim registry do not appoint institutional trust roots. Bundles cannot self-appoint production trust policy; operators must supply external trust policy when production C2/C4A claims are asserted.

## Sensitive reports

Do not place sensitive material in a public issue. If GitHub private vulnerability reporting is enabled for this repository, use that channel. Otherwise contact the maintainer through their GitHub profile and establish a private channel before sending confidential details.

Examples that should be reported privately include:

- a validator bypass that can incorrectly establish conformance;
- disclosure, redaction, or projection behavior that could expose protected applicant material;
- release-integrity ambiguity that could cause a reviewer to verify the wrong artifact;
- leaked credentials, keys, or security-sensitive evaluator configuration.

Provide only the minimum information needed to reproduce and assess the concern.

## Public issues

Public issues are appropriate for non-sensitive threat-model gaps, protocol-design concerns, schema interoperability problems, disclosure-classification questions, and implementation feedback. The Charter is a draft proposal, not adopted ENS policy; design challenges belong in public issues when they do not expose protected material.
