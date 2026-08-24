# Phase II deferred work

Items intentionally not shipped as production guarantees because half-built cryptography or verification logic would overclaim privacy, provenance, temporal, or fairness guarantees.

## Production RFC 3161 verification

**Status:** reserved profile, fail-closed (`rfc3161`); offline test fixture only (`rfc3161-recorded-fixture`).

**Why:** the earlier prototype parsed enough timestamp material to exercise a fixture but did not implement the complete CMS/RFC 3161 verification obligations required for a production C2 temporal-precedence claim. In particular, receipt-carried certificate material must never choose its own trust root, and production verification must not collapse CMS signer/signed-attribute/certificate-path semantics into a direct signature check over extracted `TSTInfo` bytes.

**Build only when all of the following are true:**

1. The verifier has an independently configured trust policy; receipt-carried certificates are treated as untrusted chain material, not roots.
2. CMS verification covers signer identification and the required signed-attribute/content-digest relationship for the timestamp token.
3. RFC 3161 / RFC 5816 certificate-identification semantics, TSA timestamping authorization/EKU and applicable policy constraints are enforced.
4. Message imprint and request/response bindings are verified, including nonce semantics when the request uses a nonce.
5. Certificate-path validation is performed against the independent trust policy with explicit handling of validity and revocation policy.
6. Malformed CMS/ASN.1/base64 input, signature failure, invalid trust configuration, and certificate-path failure become structured verifier failures, not uncaught parser/cryptography exceptions.
7. Interoperability/golden vectors from real standards-conformant TSA responses and adversarial negative vectors pass.
8. `CLAIM-MATRIX.md` states exactly what the profile establishes and what remains trusted before the profile is enabled.

Until then, the production profile MUST fail closed. The recorded fixture is test evidence only and MUST NOT be described as third-party timestamp evidence.

## Merkleized / cryptographic selective disclosure

**Status:** deferred

**Why:** v0.1 and Phase II already support `withheld`, `revealed`, and `selective-audit` states without Merkle proofs. A partial Merkle or ZK layer would imply verification claims the current claim matrix does not support.

**Build when all of the following are true:**

1. A live ENS program documents a concrete privacy requirement that hash commitments on redacted fields are insufficient.
2. The program selects a disclosure boundary (field set, auditor class, and publication rules) in writing.
3. An independent test corpus can prove both positive openings and negative forgeries under that boundary.
4. `CLAIM-MATRIX.md` is versioned to state exactly what a proof establishes and does not establish before any code merges.

**Do not ship:** stub Merkle trees, incomplete ZK circuits, or proof formats without adversarial tests and claim-bounded documentation.

## Live Ethereum anchoring

**Status:** fixture profile only (`ethereum-calldata-fixture`)

**Build when:** a program accepts chain timestamp trust, funds calldata or event emission, and documents RPC/archive verification policy. See `phase2/src/anchors/ethereum.py` for the minimal calldata commitment pattern and trust boundary.

## Actual implementation re-execution

**Status:** not implemented; current replay v2 is canonical artifact recomputation only.

**Why:** proving or even reconstructing that a recorded implementation was re-executed requires more than hashing supplied layer objects. A credible protocol must identify the executable implementation, bind the execution environment and inputs, invoke it under controlled semantics, capture outputs, and compare those outputs under versioned type-aware rules.

**Build when:** a target evaluator has a reproducible execution contract and the project can define execution-environment identity, implementation invocation, input materialization, output capture, comparator semantics, nondeterminism policy, and claim text before implementation. Approximate matching MUST operate on typed outputs; it MUST NOT use distance between cryptographic digest strings.
