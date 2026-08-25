"""Production Rekor v2 remains fail closed until native v2 timing semantics exist."""

from __future__ import annotations

import pytest

from anchors.base import select_adapter
from support import Phase2Error


def test_production_rekor_v2_selector_is_reserved() -> None:
    with pytest.raises(Phase2Error) as exc:
        select_adapter("rekor-v2", trust_policy={})
    assert exc.value.code == "RKR263"
    assert exc.value.claim == "C2"
