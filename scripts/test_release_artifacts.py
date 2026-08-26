from __future__ import annotations

import json
from pathlib import Path

import pytest

from release_artifacts import (
    CHECKSUM_NAME,
    MANIFEST_NAME,
    REQUIRED_RELEASE_JOBS,
    ReleaseArtifactError,
    _validate_evidence,
    _write_json,
    build_manifest,
    verify_directory,
    write_checksum_manifest,
)

COMMIT = "a" * 40


def _nonrelease_evidence(*, commit: str = COMMIT) -> dict:
    return {
        "commit": commit,
        "releaseEligible": False,
        "workflowRunUrl": (
            "https://github.com/fraware/ens-grant-decision-integrity/actions/runs/1"
        ),
        "jobs": {"conformance": "skipped"},
    }


def _release_dir(tmp_path: Path) -> Path:
    out = tmp_path / "release"
    out.mkdir()
    validation = out / "release-validation.json"
    _write_json(validation, _nonrelease_evidence())

    payloads = [validation]
    for name, content in {
        "ens-gdi-0.4.0-py3-none-any.whl": b"wheel",
        "ens_gdi-0.4.0.tar.gz": b"sdist",
        "ens-grant-decision-integrity-v1.0.0.tar.gz": b"source",
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


def _eligible_evidence() -> dict:
    return {
        "commit": COMMIT,
        "ref": "refs/heads/main",
        "releaseEligible": True,
        "workflowRunUrl": (
            "https://github.com/fraware/ens-grant-decision-integrity/actions/runs/1"
        ),
        "jobs": {name: "success" for name in sorted(REQUIRED_RELEASE_JOBS)},
        "studyStatus": {"readyForFinalReview": True},
    }


def test_release_directory_verifies_complete_acyclic_checksum_scope(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    result = verify_directory(out)

    assert result["ok"] is True
    assert result["releaseEligible"] is False
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


def test_release_directory_rejects_nested_directory(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    (out / "nested").mkdir()

    with pytest.raises(ReleaseArtifactError, match="flat regular files"):
        verify_directory(out)


def test_release_directory_rejects_symlinked_payload(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    sbom = out / "sbom.cdx.json"
    outside = tmp_path / "outside-sbom.json"
    outside.write_bytes(sbom.read_bytes())
    sbom.unlink()
    try:
        sbom.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    with pytest.raises(ReleaseArtifactError, match="symbolic links"):
        verify_directory(out)


def test_release_manifest_rejects_path_escape_filename(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    manifest = out / MANIFEST_NAME
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_data["artifacts"][0]["name"] = "../outside.json"
    _write_json(manifest, manifest_data)

    with pytest.raises(ReleaseArtifactError, match="unsafe asset filename"):
        verify_directory(out)


def test_release_directory_rejects_checksum_scope_omission(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    lines = (out / CHECKSUM_NAME).read_text(encoding="utf-8").splitlines()
    (out / CHECKSUM_NAME).write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

    with pytest.raises(ReleaseArtifactError, match="checksum scope mismatch"):
        verify_directory(out)


def test_release_directory_rejects_cross_file_commit_mismatch(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    validation = out / "release-validation.json"
    _write_json(validation, _nonrelease_evidence(commit="b" * 40))

    manifest = out / MANIFEST_NAME
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    for artifact in manifest_data["artifacts"]:
        if artifact["name"] == validation.name:
            import hashlib

            data = validation.read_bytes()
            artifact["sha256"] = hashlib.sha256(data).hexdigest()
            artifact["size"] = len(data)
    _write_json(manifest, manifest_data)

    payloads = [out / item["name"] for item in manifest_data["artifacts"]]
    write_checksum_manifest(out, payloads=[*payloads, manifest])

    with pytest.raises(ReleaseArtifactError, match="does not match"):
        verify_directory(out)


def test_validation_evidence_must_bind_exact_commit_and_job_results() -> None:
    evidence = _nonrelease_evidence()
    _validate_evidence(evidence, commit=COMMIT)

    wrong = json.loads(json.dumps(evidence))
    wrong["commit"] = "b" * 40
    with pytest.raises(ReleaseArtifactError, match="does not match"):
        _validate_evidence(wrong, commit=COMMIT)


def test_validation_evidence_rejects_unrecognized_job_conclusion() -> None:
    evidence = _nonrelease_evidence()
    evidence["jobs"] = {"conformance": "green-ish"}
    with pytest.raises(ReleaseArtifactError, match="invalid validation conclusion"):
        _validate_evidence(evidence, commit=COMMIT)


def test_release_eligible_evidence_requires_main_six_green_and_ready_study() -> None:
    evidence = _eligible_evidence()
    _validate_evidence(evidence, commit=COMMIT)

    wrong_ref = json.loads(json.dumps(evidence))
    wrong_ref["ref"] = "refs/heads/release/final-hardening"
    with pytest.raises(ReleaseArtifactError, match="refs/heads/main"):
        _validate_evidence(wrong_ref, commit=COMMIT)

    missing_job = json.loads(json.dumps(evidence))
    missing_job["jobs"].pop("security")
    with pytest.raises(ReleaseArtifactError, match="exactly the six"):
        _validate_evidence(missing_job, commit=COMMIT)

    failed_job = json.loads(json.dumps(evidence))
    failed_job["jobs"]["package"] = "failure"
    with pytest.raises(ReleaseArtifactError, match="all release jobs"):
        _validate_evidence(failed_job, commit=COMMIT)

    incomplete_study = json.loads(json.dumps(evidence))
    incomplete_study["studyStatus"]["readyForFinalReview"] = False
    with pytest.raises(ReleaseArtifactError, match="readyForFinalReview=true"):
        _validate_evidence(incomplete_study, commit=COMMIT)
