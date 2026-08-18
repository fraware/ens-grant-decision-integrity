"""Anchor adapter interface. RFC 3161 and Ethereum remain unimplemented."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class TemporalClaim:
    profile_id: str
    anchored_at: datetime
    envelope_digest_hex: str
    trust_boundary: str

    def precedes(self, deadline: datetime) -> bool:
        if self.anchored_at.tzinfo is None:
            anchored = self.anchored_at.replace(tzinfo=timezone.utc)
        else:
            anchored = self.anchored_at.astimezone(timezone.utc)
        if deadline.tzinfo is None:
            due = deadline.replace(tzinfo=timezone.utc)
        else:
            due = deadline.astimezone(timezone.utc)
        return anchored < due


class AnchorAdapter(ABC):
    profile_id: str

    @abstractmethod
    def anchor(self, envelope_bytes: bytes) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def verify(self, envelope_bytes: bytes, receipt: dict[str, Any]) -> TemporalClaim:
        raise NotImplementedError


class Rfc3161Adapter(AnchorAdapter):
    profile_id = "rfc3161"

    def anchor(self, envelope_bytes: bytes) -> dict[str, Any]:
        raise NotImplementedError(
            "RFC 3161 timestamping is not implemented. Select profile rekor-v1 "
            "or rekor-v1-recorded-fixture. This stub does not emit timestamps."
        )

    def verify(self, envelope_bytes: bytes, receipt: dict[str, Any]) -> TemporalClaim:
        raise NotImplementedError(
            "RFC 3161 verification is not implemented. Select profile rekor-v1 "
            "or rekor-v1-recorded-fixture. This stub does not emit timestamps."
        )


class EthereumAdapter(AnchorAdapter):
    profile_id = "ethereum"

    def anchor(self, envelope_bytes: bytes) -> dict[str, Any]:
        raise NotImplementedError(
            "Ethereum anchoring is not implemented. EIP-712 is not a time anchor. "
            "Select profile rekor-v1 or rekor-v1-recorded-fixture."
        )

    def verify(self, envelope_bytes: bytes, receipt: dict[str, Any]) -> TemporalClaim:
        raise NotImplementedError(
            "Ethereum verification is not implemented. EIP-712 is not a time anchor. "
            "Select profile rekor-v1 or rekor-v1-recorded-fixture."
        )


def select_adapter(profile_id: str, **kwargs: Any) -> AnchorAdapter:
    from anchors.rekor import RekorAdapter

    if profile_id in {"rekor-v1", "rekor-v1-recorded-fixture"}:
        return RekorAdapter(profile_id=profile_id, **kwargs)
    if profile_id == "rfc3161":
        return Rfc3161Adapter()
    if profile_id == "ethereum":
        return EthereumAdapter()
    raise NotImplementedError(f"unknown anchor profile {profile_id}")
