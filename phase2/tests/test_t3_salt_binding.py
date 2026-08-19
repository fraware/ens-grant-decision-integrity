"""T3: Same manifest, two salts, two commitments; each opens only with its salt."""

from __future__ import annotations

import pytest

from commitment import generate_salt, open_commitment
from envelope import build_envelope
from factories import sample_manifest
from support import Phase2Error


def test_two_salts_are_two_commitments() -> None:
    manifest = sample_manifest()
    salt_a = generate_salt()
    salt_b = generate_salt()
    assert salt_a != salt_b
    env_a = build_envelope(manifest, salt_a)
    env_b = build_envelope(manifest, salt_b)
    assert env_a["commitmentDigest"] != env_b["commitmentDigest"]
    open_commitment(digest_hex=env_a["commitmentDigest"], manifest=manifest, salt=salt_a)
    open_commitment(digest_hex=env_b["commitmentDigest"], manifest=manifest, salt=salt_b)
    with pytest.raises(Phase2Error):
        open_commitment(digest_hex=env_a["commitmentDigest"], manifest=manifest, salt=salt_b)
    with pytest.raises(Phase2Error):
        open_commitment(digest_hex=env_b["commitmentDigest"], manifest=manifest, salt=salt_a)
