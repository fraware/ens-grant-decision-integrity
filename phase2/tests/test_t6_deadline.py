"""T6: Anchor time at or after the deadline fails C2."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from factories import ANCHOR_TIME, build_bundle, generate_rekor_fixture_key
from graph import verify_graph
from support import Phase2Error


def test_anchor_before_deadline_establishes_c2() -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem, integrated_time=ANCHOR_TIME)
    result = verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
    assert result.ok
    assert "C2" in result.established


@pytest.mark.parametrize(
    "when",
    [
        datetime(2026, 8, 5, 23, 59, 0, tzinfo=timezone.utc),
        datetime(2026, 8, 6, 0, 0, 0, tzinfo=timezone.utc),
    ],
)
def test_anchor_at_or_after_deadline_fails_c2(when: datetime) -> None:
    private_pem, public_pem = generate_rekor_fixture_key()
    bundle = build_bundle(rekor_private_pem=private_pem, integrated_time=when)
    with pytest.raises(Phase2Error, match="not strictly before") as exc:
        verify_graph(bundle, fixture_private_key_pem=private_pem, trust_root_pem=public_pem)
    assert exc.value.claim == "C2"
