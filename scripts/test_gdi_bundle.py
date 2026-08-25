"""Verification-bundle path safety and offline verify-bundle tests."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gdi.bundle import BundleError, verify_bundle  # noqa: E402
from gdi.exit_codes import EVIDENCE_FAILURE, OK, USAGE_ERROR  # noqa: E402


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _minimal_bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / "bundle"
    (bundle / "record").mkdir(parents=True)
    record_src = ROOT / "examples" / "spp3-marketplace-rfp.example.json"
    record_dst = bundle / "record" / "decision.json"
    shutil.copyfile(record_src, record_dst)
    manifest = {
        "bundleManifestVersion": "1",
        "bundleId": "minimal-public-v01",
        "bundleClass": "public",
        "record": {
            "path": "record/decision.json",
            "sha256": _sha256(record_dst),
            "schemaProfile": "grant-decision-record/0.1",
        },
        "nonClaims": [
            "This example bundle is for offline verifier tests only.",
        ],
    }
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return bundle


def test_verify_bundle_minimal_public_offline(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    report, code = verify_bundle(bundle, trust_policy_path=ROOT / "tests" / "fixtures" / "trust" / "test-trust-policy.json")
    assert code == OK
    assert report["ok"] is True
    assert "CORE.SCHEMA.STRUCTURE" in report["establishedClaims"]
    assert report["trustPolicy"]["policyId"] == "gdi-test-fixture-policy"


def test_reject_absolute_path(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    manifest["record"]["path"] = str((bundle / "record" / "decision.json").resolve())
    (bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BundleError) as exc:
        verify_bundle(bundle)
    assert exc.value.code == "BUNDLE002"
    assert exc.value.exit_code == USAGE_ERROR


def test_reject_parent_escape(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    manifest["record"]["path"] = "../outside.json"
    (bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BundleError) as exc:
        verify_bundle(bundle)
    assert exc.value.code == "BUNDLE002"


def test_digest_mismatch_fails(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    manifest["record"]["sha256"] = "sha256:" + ("0" * 64)
    (bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    report, code = verify_bundle(bundle)
    assert code == EVIDENCE_FAILURE
    assert report["ok"] is False
