"""Verification-bundle path safety and fail-closed orchestration tests."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gdi.bundle import BundleError, verify_bundle  # noqa: E402
from gdi.core.runtime import validate_record  # noqa: E402
from gdi.exit_codes import EVIDENCE_FAILURE, OK, USAGE_ERROR  # noqa: E402
from gdi.report import add_check, empty_report  # noqa: E402
from gdi.trust.policy import (  # noqa: E402
    TrustPolicyError,
    load_trust_policy,
    signer_authorized,
)


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
    (bundle / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return bundle


def _trust_policy() -> dict:
    return json.loads(
        (ROOT / "tests" / "fixtures" / "trust" / "test-trust-policy.json").read_text(
            encoding="utf-8"
        )
    )


def _write_policy(tmp_path: Path, policy: dict) -> Path:
    path = tmp_path / "trust-policy.json"
    path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    return path


def test_verify_bundle_minimal_public_offline(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    policy = ROOT / "tests" / "fixtures" / "trust" / "test-trust-policy.json"
    report, code = verify_bundle(bundle, trust_policy_path=policy)
    assert code == OK
    assert report["ok"] is True
    assert "CORE.SCHEMA.STRUCTURE" in report["establishedClaims"]
    assert report["trustPolicy"]["policyId"] == "gdi-test-fixture-policy"


def test_bundle_manifest_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    manifest_path = bundle / "manifest.json"
    raw = manifest_path.read_text(encoding="utf-8")
    raw = raw.replace(
        '"bundleId": "minimal-public-v01",',
        '"bundleId": "minimal-public-v01",\n  "bundleId": "ambiguous",',
        1,
    )
    manifest_path.write_text(raw, encoding="utf-8")

    with pytest.raises(BundleError) as exc:
        verify_bundle(bundle)
    assert exc.value.code == "BUNDLE006"
    assert "duplicate JSON object key" in str(exc.value)


def test_bundle_record_rejects_nonstandard_nan(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    record_path = bundle / "record" / "decision.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["application"]["requestedAmount"] = float("nan")
    record_path.write_text(json.dumps(record), encoding="utf-8")

    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["record"]["sha256"] = _sha256(record_path)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(BundleError) as exc:
        verify_bundle(bundle)
    assert exc.value.code == "BUNDLE006"
    assert "non-standard JSON numeric constant" in str(exc.value)


def test_core_record_rejects_nonfinite_numeric_values() -> None:
    record = json.loads(
        (ROOT / "examples" / "spp3-marketplace-rfp.example.json").read_text(encoding="utf-8")
    )
    record["application"]["requestedAmount"] = float("nan")

    findings = validate_record(record)
    assert any(
        item.code == "SCHEMA"
        and item.path == "application.requestedAmount"
        and "finite JSON numbers" in item.message
        for item in findings
    )


def test_trust_policy_rejects_invalid_datetime_format(tmp_path: Path) -> None:
    policy = _trust_policy()
    policy["validFor"]["start"] = "not-a-date"
    with pytest.raises(TrustPolicyError) as exc:
        load_trust_policy(_write_policy(tmp_path, policy))
    assert exc.value.code == "TRUST004"


def test_trust_policy_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    source = ROOT / "tests" / "fixtures" / "trust" / "test-trust-policy.json"
    raw = source.read_text(encoding="utf-8")
    raw = raw.replace(
        '"policyId": "gdi-test-fixture-policy",',
        '"policyId": "gdi-test-fixture-policy",\n  "policyId": "ambiguous",',
        1,
    )
    path = tmp_path / "duplicate-policy.json"
    path.write_text(raw, encoding="utf-8")

    with pytest.raises(TrustPolicyError) as exc:
        load_trust_policy(path)
    assert exc.value.code == "TRUST003"
    assert "duplicate JSON object key" in str(exc.value)


def test_trust_policy_rejects_nonpositive_validity_interval(tmp_path: Path) -> None:
    policy = _trust_policy()
    policy["validFor"] = {
        "start": "2026-01-02T00:00:00Z",
        "end": "2026-01-01T00:00:00Z",
    }
    with pytest.raises(TrustPolicyError) as exc:
        load_trust_policy(_write_policy(tmp_path, policy))
    assert exc.value.code == "TRUST008"


def test_signer_authorization_respects_global_policy_validity(tmp_path: Path) -> None:
    policy = _trust_policy()
    policy["validFor"]["end"] = "2026-06-01T00:00:00Z"
    loaded, _digest = load_trust_policy(_write_policy(tmp_path, policy))
    key_id = loaded["runSigners"][0]["keyId"]

    assert signer_authorized(
        loaded,
        key_id=key_id,
        role="evaluator-run-attestor",
        at=datetime(2026, 5, 1, tzinfo=UTC),
    )
    assert not signer_authorized(
        loaded,
        key_id=key_id,
        role="evaluator-run-attestor",
        at=datetime(2026, 7, 1, tzinfo=UTC),
    )


def test_required_not_run_can_never_leave_report_ok() -> None:
    report = empty_report(bundle_id="x", manifest_digest="sha256:" + "0" * 64)
    add_check(
        report,
        check_id="required.component",
        status="not-run",
        claim_ids=[],
        evidence=[],
        required=True,
    )
    assert report["ok"] is False
    assert "required.component:not-run" in report["unverified"]


def test_optional_not_applicable_is_nonblocking() -> None:
    report = empty_report(bundle_id="x", manifest_digest="sha256:" + "0" * 64)
    add_check(
        report,
        check_id="optional.component",
        status="not-applicable",
        claim_ids=[],
        evidence=[],
        required=False,
    )
    assert report["ok"] is True


def test_required_projection_without_confidential_source_fails_closed(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    (bundle / "projection").mkdir()
    (bundle / "projection" / "spec.json").write_text("{}\n", encoding="utf-8")
    (bundle / "projection" / "public.json").write_text("{}\n", encoding="utf-8")
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["projection"] = {
        "specPath": "projection/spec.json",
        "publicRecordPath": "projection/public.json",
        "required": True,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report, code = verify_bundle(bundle)
    assert code == EVIDENCE_FAILURE
    assert report["ok"] is False
    assert "projection.execute:not-run" in report["unverified"]


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


def test_reject_symlinked_path_component(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    target = outside / "decision.json"
    target.write_text("{}\n", encoding="utf-8")
    link = bundle / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable")
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    manifest["record"]["path"] = "linked/decision.json"
    manifest["record"]["sha256"] = _sha256(target)
    (bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BundleError) as exc:
        verify_bundle(bundle)
    assert exc.value.code == "BUNDLE003"


def test_digest_mismatch_fails(tmp_path: Path) -> None:
    bundle = _minimal_bundle(tmp_path)
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    manifest["record"]["sha256"] = "sha256:" + ("0" * 64)
    (bundle / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    report, code = verify_bundle(bundle)
    assert code == EVIDENCE_FAILURE
    assert report["ok"] is False
