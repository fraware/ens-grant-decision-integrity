"""Frozen Phase II claim text.

Verifier output MUST use these strings. Expanding a claim beyond this module
is a protocol defect. These statements are what a successful check establishes,
not what a program may wish were true.
"""

from __future__ import annotations

C1_ID = "C1"
C2_ID = "C2"
C3_ID = "C3"
C4_ID = "C4"
C5_ID = "C5"
C6_ID = "C6"

C1_ESTABLISHED = (
    "Revealed manifest and salt reopen the anchored digest, and the revealed manifest's "
    "programId, roundId, and applicationDeadline match the anchored envelope."
)
C2_ESTABLISHED = (
    "Selected anchor profile places the envelope before the application deadline."
)
C3_ESTABLISHED = (
    "The verified anchor binds the public envelope's programId, roundId, applicationDeadline, "
    "commitment algorithm, and commitment digest as one anchored object."
)
C4_ESTABLISHED = (
    "Signer asserts this run used the bound commitment, input snapshots, "
    "environment, and output digest."
)
C5_ESTABLISHED = (
    "Accepted replay evidence records per-layer exact-match, diverged, or not-replayable outcomes "
    "from canonical artifact recomputation."
)
C6_ESTABLISHED = (
    "No Phase II object populated decision.authorityKind."
)

C1_DOES_NOT = "execution, operator honesty, or evaluator correctness"
C2_DOES_NOT = "universal time; the named profile's trust root and monitoring assumptions apply"
C3_DOES_NOT = (
    "that an unopened manifest contains matching round fields; successful reveal or authorized audit is required for that check"
)
C4_DOES_NOT = "that the signer actually used that configuration or that the output is sound"
C5_DOES_NOT = (
    "re-execution of the recorded implementation unless separately demonstrated; fairness, "
    "legitimacy, hosted-model identity over time, or substantive merit"
)
C6_DOES_NOT = "institutional approval, committee adoption, or funding authority"

NON_CLAIMS: tuple[str, ...] = (
    "A valid commitment is not evidence of execution.",
    "A signed run is an assertion by the signer, not proof of operator honesty or that the committed configuration was used.",
    "Artifact replay agreement is not proof that the recorded implementation was re-executed unless a separate re-execution protocol establishes that fact.",
    "Replay agreement is not correctness, fairness, or legitimacy.",
    "Hosted models may be not-replayable; that outcome does not void independent deterministic-layer results.",
    "Hashes and log inclusion are not institutional approval or funding authority.",
    "AI systems cannot approve, reject, suspend, or release funding.",
)

REKOR_TRUST_BOUNDARY = (
    "Rekor v1 temporal claims depend on Rekor's signed entry timestamp and signed "
    "tree state under the pinned Rekor v1 production key, plus independent log "
    "monitoring against split-view. This client does not operate a monitor."
)

FIXTURE_TRUST_BOUNDARY = (
    "rekor-v1-recorded-fixture receipts are verified under a test-log key shipped "
    "with the fixture. They do not establish inclusion in the public Sigstore Rekor log."
)

RFC3161_TRUST_BOUNDARY = (
    "Production RFC 3161 verification is disabled until complete CMS/RFC 3161 trust validation is integrated."
)

RFC3161_FIXTURE_TRUST_BOUNDARY = (
    "rfc3161-recorded-fixture tokens are verified under an independently supplied test TSA trust root. "
    "They do not establish a third-party TSA attestation."
)

ETHEREUM_FIXTURE_TRUST_BOUNDARY = (
    "ethereum-calldata-fixture receipts are verified against recorded block metadata "
    "shipped with the fixture. They do not establish mainnet inclusion."
)

COMMITMENT_ALGORITHM_ID = "sha256-salted-jcs-rfc8785-v1"
COMMITMENT_DOMAIN = "ens-gdi/evaluator-manifest/v1"
ENVELOPE_TYPE = "ens-gdi-evaluator-manifest-commitment"
V01_COMMITMENT_ALGORITHM = "other"
PREDICATE_TYPE = "urn:ens-gdi:phase2:evaluator-run:v1"
DSSE_PAYLOAD_TYPE = "application/vnd.in-toto+json"
IN_TOTO_STATEMENT_TYPE = "https://in-toto.io/Statement/v1"

FORBIDDEN_AUTHORITY_KEYS: tuple[str, ...] = (
    "authorityKind",
    "decisionAuthority",
    "institutionalAuthority",
    "fundingAuthority",
)

CLAIM_BY_ID: dict[str, str] = {
    C1_ID: C1_ESTABLISHED,
    C2_ID: C2_ESTABLISHED,
    C3_ID: C3_ESTABLISHED,
    C4_ID: C4_ESTABLISHED,
    C5_ID: C5_ESTABLISHED,
    C6_ID: C6_ESTABLISHED,
}
