# Phase II deferred work

Items intentionally not shipped in Wave 4 because half-built cryptography would overclaim privacy or fairness guarantees.

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
