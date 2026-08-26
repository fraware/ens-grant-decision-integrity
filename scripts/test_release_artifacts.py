from __future__ import annotations

import json
from pathlib import Path

import pytest

from release_artifacts import (
    BUILD_LOCK_NAME,
    CHECKSUM_NAME,
    MANIFEST_NAME,
    REQUIRED_RELEASE_JOBS,
    VALIDATION_LOCK_NAME,
    ReleaseArtifactError,
    _validate_evidence,
    _validate_github_artifacts,
    _validate_github_records,
    _write_json,
    build_manifest,
    verify_directory,
    write_checksum_manifest,
)

COMMIT = "a" * 40
RUN_ID = 123456
RUN_ATTEMPT = 2
MANIFEST_SHA = "c" * 64


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
        BUILD_LOCK_NAME: b"build==1.3.0 --hash=sha256:" + b"a" * 64 + b"\n",
        VALIDATION_LOCK_NAME: b"jsonschema==4.26.0 --hash=sha256:" + b"b" * 64 + b"\n",
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
        "evidenceKind": "same-run-main-release-validation",
        "repository": "fraware/ens-grant-decision-integrity",
        "eventName": "workflow_dispatch",
        "workflowName": "validate",
        "runId": RUN_ID,
        "runAttempt": RUN_ATTEMPT,
        "workflowRunUrl": (
            f"https://github.com/fraware/ens-grant-decision-integrity/actions/runs/{RUN_ID}"
        ),
        "jobs": {name: "success" for name in sorted(REQUIRED_RELEASE_JOBS)},
        "studyStatus": {"readyForFinalReview": True},
    }


def _github_run() -> dict:
    evidence = _eligible_evidence()
    return {
        "id": RUN_ID,
        "run_attempt": RUN_ATTEMPT,
        "name": "validate",
        "path": ".github/workflows/validate.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": COMMIT,
        "status": "completed",
        "conclusion": "success",
        "html_url": evidence["workflowRunUrl"],
        "repository": {"full_name": "fraware/ens-grant-decision-integrity"},
    }


def _github_jobs() -> dict:
    rows = []
    for name in sorted(REQUIRED_RELEASE_JOBS):
        rows.append(
            {
                "name": name,
                "status": "completed",
                "conclusion": "success",
                "steps": [
                    {
                        "name": "Assert exact validation SHA",
                        "status": "completed",
                        "conclusion": "success",
                    }
                ],
            }
        )
    rows.append(
        {
            "name": "release-assets",
            "status": "completed",
            "conclusion": "success",
            "steps": [
                {
                    "name": "Require exact main-branch release commit",
                    "status": "completed",
                    "conclusion": "success",
                }
            ],
        }
    )
    return {"total_count": len(rows), "jobs": rows}


def _github_artifacts(*, manifest_sha: str = MANIFEST_SHA) -> dict:
    name = f"release-candidate-v1.0.0-{COMMIT}-{manifest_sha}"
    return {
        "total_count": 1,
        "artifacts": [
            {
                "id": 987654,
                "name": name,
                "expired": False,
                "archive_download_url": (
                    "https://api.github.com/repos/fraware/ens-grant-decision-integrity/"
                    "actions/artifacts/987654/zip"
                ),
            }
        ],
    }


def test_release_directory_verifies_complete_acyclic_checksum_scope(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    result = verify_directory(out)

    assert result["ok"] is True
    assert result["releaseEligible"] is False
    assert result["verifiedPayloadCount"] == 8
    checksums = (out / CHECKSUM_NAME).read_text(encoding="utf-8")
    assert MANIFEST_NAME in checksums
    assert BUILD_LOCK_NAME in checksums
    assert VALIDATION_LOCK_NAME in checksums
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


def test_release_manifest_rejects_extra_even_when_checksummed(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    unexpected = out / "unexpected.txt"
    unexpected.write_text("unexpected\n", encoding="utf-8")

    manifest = out / MANIFEST_NAME
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    import hashlib

    data = unexpected.read_bytes()
    manifest_data["artifacts"].append(
        {
            "name": unexpected.name,
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
        }
    )
    _write_json(manifest, manifest_data)
    payloads = [out / item["name"] for item in manifest_data["artifacts"]]
    write_checksum_manifest(out, payloads=[*payloads, manifest])

    with pytest.raises(ReleaseArtifactError, match="unexpected payloads"):
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


def test_release_manifest_rejects_missing_required_wheel(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    manifest = out / MANIFEST_NAME
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_data["artifacts"] = [
        item for item in manifest_data["artifacts"] if not item["name"].endswith(".whl")
    ]
    _write_json(manifest, manifest_data)

    with pytest.raises(ReleaseArtifactError, match="exactly one package wheel"):
        verify_directory(out)


def test_release_manifest_rejects_toolchain_policy_tampering(tmp_path: Path) -> None:
    out = _release_dir(tmp_path)
    manifest = out / MANIFEST_NAME
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_data["toolchain"]["pep517Isolation"] = True
    _write_json(manifest, manifest_data)

    with pytest.raises(ReleaseArtifactError, match="toolchain policy"):
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

    wrong_run_url = json.loads(json.dumps(evidence))
    wrong_run_url["workflowRunUrl"] = (
        "https://github.com/fraware/ens-grant-decision-integrity/actions/runs/999"
    )
    with pytest.raises(ReleaseArtifactError, match="runId"):
        _validate_evidence(wrong_run_url, commit=COMMIT)


def test_github_records_bind_completed_release_run_and_all_seven_jobs() -> None:
    _validate_github_records(
        _eligible_evidence(),
        _github_run(),
        _github_jobs(),
        commit=COMMIT,
    )


def test_github_records_reject_failed_release_assets_job() -> None:
    jobs = _github_jobs()
    for job in jobs["jobs"]:
        if job["name"] == "release-assets":
            job["conclusion"] = "failure"
            break

    with pytest.raises(ReleaseArtifactError, match="unsuccessful jobs"):
        _validate_github_records(
            _eligible_evidence(),
            _github_run(),
            jobs,
            commit=COMMIT,
        )


def test_github_records_reject_wrong_head_sha() -> None:
    run = _github_run()
    run["head_sha"] = "b" * 40

    with pytest.raises(ReleaseArtifactError, match="identity mismatch"):
        _validate_github_records(
            _eligible_evidence(),
            run,
            _github_jobs(),
            commit=COMMIT,
        )


def test_github_artifact_binds_manifest_digest_to_run() -> None:
    artifact_id, name = _validate_github_artifacts(
        _github_artifacts(),
        tag="v1.0.0",
        commit=COMMIT,
        manifest_sha256=MANIFEST_SHA,
    )
    assert artifact_id == 987654
    assert name.endswith(MANIFEST_SHA)


def test_github_artifact_rejects_different_manifest_digest() -> None:
    with pytest.raises(ReleaseArtifactError, match="artifact name mismatch"):
        _validate_github_artifacts(
            _github_artifacts(),
            tag="v1.0.0",
            commit=COMMIT,
            manifest_sha256="d" * 64,
        )


def test_github_artifact_requires_exactly_one_candidate() -> None:
    artifacts = _github_artifacts()
    duplicate = json.loads(json.dumps(artifacts["artifacts"][0]))
    duplicate["id"] = 987655
    artifacts["artifacts"].append(duplicate)
    artifacts["total_count"] = 2

    with pytest.raises(ReleaseArtifactError, match="exactly one artifact"):
        _validate_github_artifacts(
            artifacts,
            tag="v1.0.0",
            commit=COMMIT,
            manifest_sha256=MANIFEST_SHA,
        )
