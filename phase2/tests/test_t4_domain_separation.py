"""T4: A different domain string cannot verify as an evaluator-manifest commitment."""

from __future__ import annotations

import pytest

from commitment import commitment_digest, generate_salt, open_commitment
from factories import sample_manifest
from support import Phase2Error


def test_wrong_domain_cannot_open() -> None:
    manifest = sample_manifest()
    salt = generate_salt()
    digest = commitment_digest(manifest, salt)
    with pytest.raises(Phase2Error, match="do not reopen"):
        open_commitment(
            digest_hex=digest,
            manifest=manifest,
            salt=salt,
            domain="ens-gdi/some-other-object/v1",
        )
    open_commitment(digest_hex=digest, manifest=manifest, salt=salt)
