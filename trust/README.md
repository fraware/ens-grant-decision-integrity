# External trust policy

Trust is a **verifier input**, not an untrusted evidence property.

- Schema: `schema/trust-policy.schema.json`
- Fixture: `tests/fixtures/trust/test-trust-policy.json`

## Rules

- Supply trust policy with `--trust-policy` (or equivalent) for trust-dependent claims (production C2/C3 profiles, C4A).
- Bundles MAY reference a policy ID/digest; they MUST NOT embed a self-appointed trusted root that the verifier accepts without an external policy.
- Fixture keys and policies MUST NOT be used as production trust.
- Production `rfc3161` remains fail-closed unless a mature CMS stack and independent TSA vectors are integrated.
- Rekor v2 production verification requires an external Sigstore TUF `TrustedRoot` / signing configuration under the policy.

## C4 vs C4A

- **C4**: the supplied key signed the run assertion.
- **C4A**: that key is authorized by the external trust policy for the declared role and validity window.
