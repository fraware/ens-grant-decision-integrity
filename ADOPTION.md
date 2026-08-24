# Adoption pathway

This note describes how ENS Foundation or DAO grant programs can adopt the draft Charter, v0.1 decision-record profile, Phase II commitment stack, and schema 0.2 extensions without treating the repository as adopted ENS policy.

## 1. Decide materiality tier

| Tier | Typical use | Minimum record |
|---|---|---|
| A-simplified | Low-value, routine, or internal grants | v0.1 core fields; optional schema 0.2 pinning and projection |
| B-standard | Material community grants | v0.1 + documented governing-policy sources |
| C-enhanced | High-value or contested rounds (e.g. Marketplace RFP class) | v0.1 + Phase II bundle when AI materially informs screening |

Proportionality matters. Phase II adds manifest design, anchor trust management, key ceremony, and reveal policy. A committee should not deploy the full stack for every low-stakes advisory screen.

## 2. Adopt the Charter as program policy

1. Publish which Charter version governs the round.
2. Map public artifacts to the five decision surfaces (`mandate`, `eligibility`, `evaluationCriteria`, `conflictRules`, `decisionProcedure`).
3. When schema 0.2 is used, pin governing-policy URIs with `policyPinning` content hashes at round open.
4. Document any deliberate deviation from Charter defaults in the program's public rules, not only in private notes.

The Charter remains a draft proposal until ENS governance adopts it. This repository proves declared consistency, not institutional adoption.

## 3. Phase II when AI materially informs recommendations

1. Author a versioned evaluator manifest before applications close.
2. Commit with RFC 8785 JCS and a domain-separated salted digest.
3. Anchor the public envelope only with a production-supported profile whose trust boundary the program has explicitly accepted. The reference client retains `rekor-v1` as a historical compatibility profile. Production `rfc3161` currently fails closed; `rekor-v1-recorded-fixture`, `rfc3161-recorded-fixture`, and `ethereum-calldata-fixture` are test profiles and do not establish production C2 evidence. Live Ethereum anchoring is not implemented.
4. Map outputs into the v0.1 `evaluatorManifest` block using verified anchor time for `committedAt`.
5. Attest and materialize replay evidence only when the program accepts the operational cost. Current replay is canonical artifact recomputation, not implementation re-execution and not a fairness proof.

A program may omit Phase II when it does not need the additional provenance claims. If it does claim independently verified pre-deadline existence (C2), a recorded fixture is not a substitute for a production-supported anchor under an explicit verifier trust policy.

See `phase2/README.md`, `phase2/ADMIN-BURDEN.md`, and `phase2/CLAIM-MATRIX.md`.

## 4. Public records and confidentiality

1. Maintain a confidential canonical record with full evidence linkage.
2. Apply a versioned projection spec (`projection/`) to publish a public record with `withheldCommitments` for redacted top-level fields.
3. Store public records at a durable URI referenced from `integrity.sourceUri` when appropriate.
4. Do not claim Merkle or ZK selective disclosure; see `phase2/DEFERRED.md`.

Projection v1 requires explicit top-level disposition: a supplied top-level source field must be published or withheld, and source integrity metadata must not be silently overwritten. These checks do not establish that the confidential source record is complete or that a redaction decision was substantively correct.

## 5. Structured authority

When schema 0.2 is used, optional `authorityIdentity` links committee or human members to evaluator IDs. This does not grant AI authority. `decision.authorityKind` remains the v0.1 authority surface; Phase II objects must never populate it.

## 6. Deviation documentation

Programs should record:

- which repository version, tag, and exact commit they implemented against;
- any anchor profile choice and verifier trust-root policy;
- any Charter or schema deviation and its public notice URI;
- where public decision records are published;
- whether a Phase II object is a production artifact or a recorded test fixture.

## 7. Validation contract

Programs can run the repository validators locally:

```bash
python -m pip install -r requirements-dev.txt
python scripts/conformance.py path/to/record.json
python -m pip install -r phase2/requirements.txt
python -m pytest phase2/tests
python phase2/src/cli.py verify-graph --bundle path/to/bundle.json
python -m pytest scripts/test_schema_02.py
python -m pytest projection/tests
python projection/src/cli.py --confidential confidential.json --spec projection/examples/tier-a-projection-spec.json --out public.json
```

For the full repository contract and expected outcomes, see `VALIDATION.md`.

A passing validator establishes internal consistency and only the claim-bounded results of the verifiers actually run. It does not establish evidence truth, operator honesty, institutional adoption, or funding authority.

## 8. What adoption does not require

- Phase II for every decision; its cost should be justified by materiality and the claims a program needs.
- A specific anchor backend. If C2 is claimed, however, the chosen profile must be production-supported and verified under an explicit trust policy; fixture evidence is insufficient.
- Ethereum mainnet anchoring.
- Cryptographic selective disclosure or ZK proofs.
- Payment or receipt of the Simocracy allocations recorded in this repository.

Simocracy funding decisions for this work **allocated** a cumulative **$219** across five decisions. The repository's current provenance snapshot records allocation amounts separately from payment or receipt and does not record evidence of either payment or receipt. v0.1 implements the first $200 Charter and schema item described in the originating proposal; Phase II implements evaluator-manifest commitment and anchoring; schema 0.2 extensions add policy pinning, structured authority, public projection, and alternate anchor fixture profiles.
