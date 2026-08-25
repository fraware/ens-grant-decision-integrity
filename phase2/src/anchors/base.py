"""Anchor adapter interface."""

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


def select_adapter(profile_id: str, **kwargs: Any) -> AnchorAdapter:
    from anchors.ethereum import EthereumAdapter
    from anchors.rekor import RekorAdapter
    from anchors.rekor_v2 import RekorV2Adapter
    from anchors.rfc3161 import Rfc3161Adapter

    if profile_id in {"rekor-v1", "rekor-v1-recorded-fixture"}:
        return RekorAdapter(profile_id=profile_id, **kwargs)
    if profile_id in {"rekor-v2", "rekor-v2-recorded-fixture"}:
        return RekorV2Adapter(profile_id=profile_id, **kwargs)
    if profile_id in {"rfc3161", "rfc3161-recorded-fixture"}:
        return Rfc3161Adapter(profile_id=profile_id, **kwargs)
    if profile_id in {"ethereum", "ethereum-calldata-fixture"}:
        return EthereumAdapter(profile_id=profile_id, **kwargs)
    raise NotImplementedError(f"unknown anchor profile {profile_id}")
