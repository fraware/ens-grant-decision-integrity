"""Claim registry consistency tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "phase2" / "src"))

from gdi.claims import active_claim_ids, claims_by_id, load_registry, lookup  # noqa: E402
import claims as phase2_claims  # noqa: E402


def test_registry_matches_schema() -> None:
    registry = load_registry()
    assert registry["registryVersion"] == "1"
    assert len(registry["claims"]) >= 20


def test_every_active_claim_has_required_check() -> None:
    for claim in load_registry()["claims"]:
        if claim["status"] != "active":
            continue
        assert claim["requiredChecks"], claim["claimId"]


def test_phase2_c1_c6_text_matches_frozen_module() -> None:
    mapping = {
        "C1": phase2_claims.C1_ESTABLISHED,
        "C2": phase2_claims.C2_ESTABLISHED,
        "C3": phase2_claims.C3_ESTABLISHED,
        "C4": phase2_claims.C4_ESTABLISHED,
        "C5": phase2_claims.C5_ESTABLISHED,
        "C6": phase2_claims.C6_ESTABLISHED,
    }
    by_id = claims_by_id()
    for alias, text in mapping.items():
        assert by_id[alias]["proposition"] == text


def test_c4a_is_separate_from_c4() -> None:
    by_id = claims_by_id()
    assert by_id["C4"]["claimId"] != by_id["C4A"]["claimId"]
    assert "authorized" in by_id["C4A"]["proposition"].lower()
    assert "authorized by an external" in by_id["C4"]["doesNotEstablish"][1].lower() or any(
        "C4A" in item for item in by_id["C4"]["doesNotEstablish"]
    )


def test_lookup_rejects_unknown_claim() -> None:
    with pytest.raises(Exception):
        lookup("NOT.A.REAL.CLAIM")


def test_active_claim_ids_stable() -> None:
    ids = active_claim_ids()
    assert ids == sorted(ids)
    assert "PHASE2.C4A.AUTHORIZED_SIGNER" in ids
