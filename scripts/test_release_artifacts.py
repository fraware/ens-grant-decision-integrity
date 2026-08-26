from __future__ import annotations

import json
from pathlib import Path

import pytest

from release_artifacts import (
    CHECKSUM_NAME,
    MANIFEST_NAME,
    ReleaseArtifactError,
    _validate_evidence,
    _write_json,
    build_manifest,
    verify_directory,
    write_checksum_manifest,
)

COMMIT = "a" * 40


def _release_dir(tmp_path: Path) -> Path:
    out = tmp_path / "release"
    out.mkdir()
    payloads = []
    for name, content in {
        "ens-gdi-0.4.0-py3-none-any.whl": b"wheel",
        "ens_gdi-0.4.0.tar.gz": b"sdist",
        "ens-grant-decision-integrity-v1.0.0.tar.gz": b"source",
        "release-validation.json": b'{"ok":true}\n',
        "sbom.cdx.json": b'{"bomFormat":"CycloneDX"}\n',
    }.items():
        path = out / name
        path.write_bytes(content)
        payloads.append(path)

    manifest = out / MANIFEST_NAME
    _write_json(
        manifest,
        build_manifest(
            tag="v1.0.0",
            commit=COMMIT,
            package_name="ens-gdi",
            package_version="0.4.0",
            payloads=payloads,
        ),
    )
    write_checksum_manifest(out, payloads=[*payloads, manifest])
    return out


def test_release_directory_verifies_complete_acyclic_checksum_scope(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    result = verify_directory(out)

    assert result["ok"] is True
    assert result["verifiedPayloadCount"] == 6
    checksums = (out / CHECKSUM_NAME).read_text(encoding="utf-8")
    assert MANIFEST_NAME in checksums
    assert CHECKSUM_NAME not in checksums


def test_release_directory_rejects_payload_tampering(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    (out / "sbom.cdx.json").write_text("tampered\n", encoding="utf-8")

    with pytest.raises(ReleaseArtifactError, match="mismatch"):
        verify_directory(out)


def test_release_directory_rejects_extra_unchecksummed_asset(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    (out / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")

    with pytest.raises(ReleaseArtifactError, match="missing or extra files"):
        verify_directory(out)


def test_release_directory_rejects_checksum_scope_omission(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    lines = (out / CHECKSUM_NAME).read_text(encoding="utf-8").splitlines()
    (out / CHECKSUM_NAME).write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

    with pytest.raises(ReleaseArtifactError, match="checksum scope mismatch"):
        verify_directory(out)


def test_validation_evidence_must_bind_exact_commit_and_job_results() -> None:
    evidence = {
        "commit": COMMIT,
        "releaseEligible": False,
        "workflowRunUrl": "https://github.com/fraware/ens-grant-decision-integrity/actions/runs/1",
        "jobs": {"conformance": "success"},
    }
    _validate_evidence(evidence, commit=COMMIT)

    wrong = json.loads(json.dumps(evidence))
    wrong["commit"] = "b" * 40
    with pytest.raises(ReleaseArtifactError, match="does not match"):
        _validate_evidence(wrong, commit=COMMIT)


def test_validation_evidence_rejects_unrecognized_job_conclusion() -> None:
    evidence = {
        "commit": COMMIT,
        "releaseEligible": False,
        "workflowRunUrl": "https://github.com/fraware/ens-grant-decision-integrity/actions/runs/1",
        "jobs": {"conformance": "green-ish"},
    }
    with pytest.raises(ReleaseArtifactError, match="invalid validation conclusion"):
        _validate_evidence(evidence, commit=COMMIT)
