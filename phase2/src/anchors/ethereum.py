"""Ethereum calldata anchor profile (fixture-first).

Live anchoring requires an RPC endpoint, funded key, and chain-specific policy.
This reference ships ``ethereum-calldata-fixture`` for offline verification of a
minimal pattern: a transaction whose input data commits ``keccak256(envelope)``.

EIP-712 typed data alone is not a time anchor. Block timestamp trust is explicit.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Any

from anchors.base import AnchorAdapter, TemporalClaim
from support import Phase2Error, sha256_hex, validate_schema

ETHEREUM_TRUST_BOUNDARY = (
    "Ethereum calldata anchoring depends on block timestamp and inclusion under "
    "the selected chain's consensus assumptions, plus an RPC or archive that serves "
    "the referenced transaction. This client does not operate an Ethereum monitor."
)
ETHEREUM_FIXTURE_TRUST_BOUNDARY = (
    "ethereum-calldata-fixture receipts are verified against recorded block metadata "
    "shipped with the fixture. They do not establish mainnet inclusion."
)

CALldata_PREFIX = "0x6764693a"  # "gdi:" UTF-8 hex prefix for human inspection


class EthereumAdapter(AnchorAdapter):
    def __init__(self, *, profile_id: str = "ethereum-calldata-fixture") -> None:
        if profile_id not in {"ethereum", "ethereum-calldata-fixture"}:
            raise Phase2Error(f"unsupported Ethereum profile {profile_id}", code="ETH001")
        self.profile_id = profile_id

    def anchor(self, envelope_bytes: bytes) -> dict[str, Any]:
        raise NotImplementedError(
            "Live Ethereum anchoring is not implemented in this reference client. "
            "Use profile ethereum-calldata-fixture for offline verification, or supply "
            "a program-controlled RPC workflow. EIP-712 is not a time anchor."
        )

    def anchor_fixture(
        self,
        envelope_bytes: bytes,
        *,
        chain_id: int = 1,
        block_number: int = 19_000_000,
        block_timestamp: datetime,
        tx_hash: str,
    ) -> dict[str, Any]:
        if self.profile_id != "ethereum-calldata-fixture":
            raise Phase2Error("anchor_fixture requires ethereum-calldata-fixture profile", code="ETH002")
        digest = sha256_hex(envelope_bytes)
        calldata = f"{CALldata_PREFIX}{digest}"
        if block_timestamp.tzinfo is None:
            block_timestamp = block_timestamp.replace(tzinfo=timezone.utc)
        else:
            block_timestamp = block_timestamp.astimezone(timezone.utc)
        receipt = {
            "profileId": self.profile_id,
            "envelopeDigestSha256": digest,
            "anchorId": tx_hash,
            "anchoredAt": block_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "logIndex": block_number,
            "verifierMaterial": {
                "kind": "ethereum-calldata-offline",
                "chainId": chain_id,
                "txHash": tx_hash,
                "blockNumber": block_number,
                "blockTimestamp": int(block_timestamp.timestamp()),
                "calldataHex": calldata,
                "envelopeDigestSha256": digest,
            },
        }
        validate_schema(receipt, "anchor-receipt.schema.json")
        self.verify(envelope_bytes, receipt)
        return receipt

    def verify(self, envelope_bytes: bytes, receipt: dict[str, Any]) -> TemporalClaim:
        validate_schema(receipt, "anchor-receipt.schema.json")
        if receipt["profileId"] != self.profile_id:
            raise Phase2Error(
                f"receipt profile {receipt['profileId']} does not match adapter {self.profile_id}",
                code="ETH003",
                claim="C2",
            )
        digest = sha256_hex(envelope_bytes)
        if receipt["envelopeDigestSha256"] != digest:
            raise Phase2Error("receipt envelope digest does not match envelope bytes", code="ETH004", claim="C2")
        material = receipt["verifierMaterial"]
        if material.get("kind") != "ethereum-calldata-offline":
            raise Phase2Error("expected ethereum-calldata-offline verifier material", code="ETH005", claim="C2")
        expected_calldata = f"{CALldata_PREFIX}{digest}"
        if str(material.get("calldataHex", "")).lower() != expected_calldata.lower():
            raise Phase2Error("calldata does not commit the envelope digest", code="ETH006", claim="C2")
        if str(material.get("envelopeDigestSha256", "")).lower() != digest:
            raise Phase2Error("verifier material digest mismatch", code="ETH007", claim="C2")
        unix_time = int(material["blockTimestamp"])
        anchored_at = datetime.fromtimestamp(unix_time, tz=timezone.utc)
        claimed = datetime.fromisoformat(receipt["anchoredAt"].replace("Z", "+00:00"))
        if int(claimed.timestamp()) != unix_time:
            raise Phase2Error("receipt anchoredAt does not match block timestamp", code="ETH008", claim="C2")
        boundary = (
            ETHEREUM_FIXTURE_TRUST_BOUNDARY
            if self.profile_id == "ethereum-calldata-fixture"
            else ETHEREUM_TRUST_BOUNDARY
        )
        return TemporalClaim(
            profile_id=self.profile_id,
            anchored_at=anchored_at,
            envelope_digest_hex=digest,
            trust_boundary=boundary,
        )
