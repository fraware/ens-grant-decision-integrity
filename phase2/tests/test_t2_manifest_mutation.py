"""T2: Any material manifest mutation fails opening."""

from __future__ import annotations

import pytest

from commitment import generate_salt, open_commitment
from envelope import build_envelope
from factories import sample_manifest
from support import Phase2Error


def test_material_mutation_fails_opening() -> None:
    manifest = sample_manifest()
    salt = generate_salt()
    envelope = build_envelope(manifest, salt)
    mutated = sample_manifest()
    mutated["instructions"] = {"text": manifest["instructions"]["text"] + " extra hidden rule"}
    with pytest.raises(Phase2Error, match="do not reopen"):
        open_commitment(
            digest_hex=envelope["commitmentDigest"],
            manifest=mutated,
            salt=salt,
        )
