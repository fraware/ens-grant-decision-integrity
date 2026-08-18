"""T5: Changing programId, roundId, or applicationDeadline invalidates opening against the envelope."""

from __future__ import annotations

import pytest

from commitment import generate_salt, open_commitment
from envelope import assert_round_binding, build_envelope
from factories import sample_manifest
from support import Phase2Error


@pytest.mark.parametrize("field,value", [
    ("programId", "some-other-program"),
    ("roundId", "some-other-round"),
    ("applicationDeadline", "2026-12-31T00:00:00Z"),
])
def test_round_field_change_fails_binding(field: str, value: str) -> None:
    original = sample_manifest()
    salt = generate_salt()
    envelope = build_envelope(original, salt)
    mutated = sample_manifest(**{field: value})
    with pytest.raises(Phase2Error):
        open_commitment(digest_hex=envelope["commitmentDigest"], manifest=mutated, salt=salt)
    # Even if a caller rebuilt a digest for the mutated manifest with the same
    # salt, envelope round fields still would not match.
    from envelope import build_envelope as rebuild
    other = rebuild(mutated, salt)
    with pytest.raises(Phase2Error, match=field):
        assert_round_binding(envelope, mutated)
    assert other["commitmentDigest"] != envelope["commitmentDigest"]
