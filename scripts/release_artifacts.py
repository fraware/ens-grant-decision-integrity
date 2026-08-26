#!/usr/bin/env python3
"""Assemble and verify release-candidate payloads from one exact Git commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "fraware/ens-grant-decision-integrity"
WORKFLOW_NAME = "validate"
WORKFLOW_PATH = ".github/workflows/validate.yml"
CHECKSUM_NAME = "SHA256SUMS"
MANIFEST_NAME = "release-manifest.json"
VALIDATION_NAME = "release-validation.json"
SBOM_NAME = "sbom.cdx.json"
BUILD_LOCK_NAME = "requirements-build.lock.txt"
VALIDATION_LOCK_NAME = "requirements.lock.txt"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SAFE_TAG_RE = re.compile(r"^[A-Za-z0-9._-]+$")
ASSET_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")
REQUIRED_RELEASE_JOBS = {
    "conformance",
    "phase2",
    "schema-02",
    "package",
    "lint-type",
    "security",
}


class ReleaseArtifactError(Exception):
    pass


def _run(*args: str, cwd: Path = ROOT, capture: bool = False) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    return result.stdout.strip() if capture else ""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _descriptor(path: Path) -> dict[str, Any]:
    return {"name": path.name, "sha256": _sha256(path), "size": path.stat().st_size}


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseArtifactError(f"cannot load {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseArtifactError(f"{label} must be a JSON object: {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _pyproject() -> dict[str, Any]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _project_metadata() -> tuple[str, str]:
    project = _pyproject()["project"]
    return str(project["name"]), str(project["version"])


def _venv_python(venv: Path) -> Path:
    if sys.platform == "win32":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def _assert_commit(commit: str, *, require_clean: bool) -> None:
    if not SHA_RE.fullmatch(commit):
        raise ReleaseArtifactError("commit must be a lowercase 40-hex Git SHA")
    actual = _run("git", "rev-parse", "HEAD", capture=True)
    if actual != commit:
        raise ReleaseArtifactError(
            f"checked-out HEAD {actual} does not match requested commit {commit}"
        )
    if require_clean:
        status = _run("git", "status", "--porcelain", "--untracked-files=all", capture=True)
        if status:
            raise ReleaseArtifactError(
                "release assembly requires a clean checkout before output creation"
            )


def _validate_evidence(evidence: dict[str, Any], *, commit: str) -> None:
    if evidence.get("commit") != commit:
        raise ReleaseArtifactError("validation evidence commit does not match release commit")
    release_eligible = evidence.get("releaseEligible")
    if not isinstance(release_eligible, bool):
        raise ReleaseArtifactError("validation evidence must define boolean releaseEligible")
    run_url = evidence.get("workflowRunUrl")
    if not isinstance(run_url, str) or not run_url.startswith("https://github.com/"):
        raise ReleaseArtifactError("validation evidence must contain a GitHub workflowRunUrl")
    jobs = evidence.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        raise ReleaseArtifactError("validation evidence must contain a non-empty jobs object")
    for name, conclusion in jobs.items():
        if not isinstance(name, str) or not name:
            raise ReleaseArtifactError("validation job names must be non-empty strings")
        if conclusion not in {"success", "failure", "cancelled", "skipped"}:
            raise ReleaseArtifactError(f"invalid validation conclusion for {name}: {conclusion!r}")

    if release_eligible:
        if evidence.get("evidenceKind") != "same-run-main-release-validation":
            raise ReleaseArtifactError("release-eligible evidence has the wrong evidenceKind")
        if evidence.get("repository") != REPOSITORY:
            raise ReleaseArtifactError("release-eligible evidence has the wrong repository")
        if evidence.get("eventName") != "workflow_dispatch":
            raise ReleaseArtifactError("release-eligible evidence must come from workflow_dispatch")
        if evidence.get("workflowName") != WORKFLOW_NAME:
            raise ReleaseArtifactError("release-eligible evidence has the wrong workflow name")
        run_id = evidence.get("runId")
        run_attempt = evidence.get("runAttempt")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ReleaseArtifactError("release-eligible evidence must contain a positive runId")
        if (
            not isinstance(run_attempt, int)
            or isinstance(run_attempt, bool)
            or run_attempt <= 0
        ):
            raise ReleaseArtifactError(
                "release-eligible evidence must contain a positive runAttempt"
            )
        expected_url = f"https://github.com/{REPOSITORY}/actions/runs/{run_id}"
        if run_url != expected_url:
            raise ReleaseArtifactError("workflowRunUrl does not match repository/runId")
        if evidence.get("ref") != "refs/heads/main":
            raise ReleaseArtifactError(
                "release-eligible evidence must be produced from refs/heads/main"
            )
        if set(jobs) != REQUIRED_RELEASE_JOBS:
            raise ReleaseArtifactError(
                "release-eligible evidence must contain exactly the six required release jobs"
            )
        failed = sorted(name for name, conclusion in jobs.items() if conclusion != "success")
        if failed:
            raise ReleaseArtifactError(
                f"release-eligible evidence requires all release jobs to succeed: {failed}"
            )
        study_status = evidence.get("studyStatus")
        if (
            not isinstance(study_status, dict)
            or study_status.get("readyForFinalReview") is not True
        ):
            raise ReleaseArtifactError(
                "release-eligible evidence requires studyStatus.readyForFinalReview=true"
            )


def _validate_asset_name(name: Any, *, label: str) -> str:
    if not isinstance(name, str) or ASSET_NAME_RE.fullmatch(name) is None:
        raise ReleaseArtifactError(f"{label} contains an unsafe asset filename: {name!r}")
    if name in {".", ".."} or Path(name).name != name:
        raise ReleaseArtifactError(f"{label} contains an unsafe asset filename: {name!r}")
    return name


def _assert_flat_regular_directory(out_dir: Path) -> None:
    if out_dir.is_symlink() or not out_dir.is_dir():
        raise ReleaseArtifactError("release directory must be a real directory, not a symlink")
    for entry in out_dir.iterdir():
        if entry.is_symlink():
            raise ReleaseArtifactError(
                f"release directory must not contain symbolic links: {entry.name}"
            )
        if not entry.is_file():
            raise ReleaseArtifactError(
                f"release directory must contain only flat regular files: {entry.name}"
            )


def _validate_manifest_identity(
    manifest: dict[str, Any],
) -> tuple[str, str, str, str]:
    if manifest.get("manifestVersion") != "1":
        raise ReleaseArtifactError("release manifest must use manifestVersion 1")
    tag = manifest.get("tag")
    if not isinstance(tag, str) or SAFE_TAG_RE.fullmatch(tag) is None:
        raise ReleaseArtifactError("release manifest contains an invalid tag")
    commit = manifest.get("commit")
    if not isinstance(commit, str) or SHA_RE.fullmatch(commit) is None:
        raise ReleaseArtifactError("release manifest contains an invalid commit SHA")
    package = manifest.get("package")
    if not isinstance(package, dict) or set(package) != {"name", "version"}:
        raise ReleaseArtifactError("release manifest package must contain name and version")
    if any(not isinstance(package[key], str) or not package[key] for key in package):
        raise ReleaseArtifactError(
            "release manifest package name/version must be non-empty strings"
        )
    checksum = manifest.get("checksumManifest")
    if not isinstance(checksum, dict):
        raise ReleaseArtifactError("release manifest checksumManifest must be an object")
    if checksum.get("name") != CHECKSUM_NAME or checksum.get("selfHashExcluded") is not True:
        raise ReleaseArtifactError("release manifest checksum policy is invalid")
    toolchain = manifest.get("toolchain")
    expected_toolchain = {
        "buildLock": BUILD_LOCK_NAME,
        "validationLock": VALIDATION_LOCK_NAME,
        "pep517Isolation": False,
    }
    if toolchain != expected_toolchain:
        raise ReleaseArtifactError("release manifest toolchain policy is invalid")
    return tag, commit, package["name"], package["version"]


def _source_archive(out_dir: Path, *, tag: str, commit: str) -> Path:
    if SAFE_TAG_RE.fullmatch(tag) is None:
        raise ReleaseArtifactError(
            "tag must contain only letters, digits, dot, underscore, or hyphen"
        )
    path = out_dir / f"ens-grant-decision-integrity-{tag}.tar.gz"
    _run(
        "git",
        "archive",
        "--format=tar.gz",
        f"--prefix=ens-grant-decision-integrity-{tag}/",
        f"--output={path}",
        commit,
    )
    return path


def _copy_release_lockfiles(out_dir: Path) -> tuple[Path, Path]:
    build_lock = out_dir / BUILD_LOCK_NAME
    validation_lock = out_dir / VALIDATION_LOCK_NAME
    shutil.copyfile(ROOT / BUILD_LOCK_NAME, build_lock)
    shutil.copyfile(ROOT / VALIDATION_LOCK_NAME, validation_lock)
    return build_lock, validation_lock


def _build_python_distributions(out_dir: Path) -> tuple[Path, Path]:
    venv = out_dir.parent / f".{out_dir.name}-build-venv"
    if venv.exists():
        shutil.rmtree(venv)
    try:
        _run(sys.executable, "-m", "venv", str(venv))
        python = _venv_python(venv)
        _run(
            str(python),
            "-m",
            "pip",
            "install",
            "--require-hashes",
            "-r",
            str(ROOT / BUILD_LOCK_NAME),
        )
        _run(
            str(python),
            "-m",
            "build",
            "--no-isolation",
            "--outdir",
            str(out_dir),
        )
    finally:
        if venv.exists():
            shutil.rmtree(venv)

    wheels = sorted(out_dir.glob("*.whl"))
    sdists = sorted(out_dir.glob("*.tar.gz"))
    source_archives = [
        path
        for path in sdists
        if path.name.startswith("ens-grant-decision-integrity-")
    ]
    sdists = [path for path in sdists if path not in source_archives]
    if len(wheels) != 1 or len(sdists) != 1:
        raise ReleaseArtifactError(
            f"expected exactly one wheel and one sdist; wheels={len(wheels)} sdists={len(sdists)}"
        )
    return wheels[0], sdists[0]


def _generate_sbom(out_dir: Path, *, wheel: Path) -> Path:
    venv = out_dir.parent / f".{out_dir.name}-sbom-venv"
    if venv.exists():
        shutil.rmtree(venv)
    try:
        _run(sys.executable, "-m", "venv", str(venv))
        python = _venv_python(venv)
        _run(
            str(python),
            "-m",
            "pip",
            "install",
            "--require-hashes",
            "-r",
            str(ROOT / VALIDATION_LOCK_NAME),
        )
        _run(str(python), "-m", "pip", "install", "--no-deps", str(wheel))
        site_packages = _run(
            str(python),
            "-c",
            "import site; print(site.getsitepackages()[0])",
            capture=True,
        )
        sbom = out_dir / SBOM_NAME
        _run(
            sys.executable,
            "-m",
            "pip_audit",
            "--path",
            site_packages,
            "--format",
            "cyclonedx-json",
            "--output",
            str(sbom),
        )
        if not sbom.is_file() or sbom.stat().st_size == 0:
            raise ReleaseArtifactError("SBOM generation produced no output")
        return sbom
    finally:
        if venv.exists():
            shutil.rmtree(venv)


def build_manifest(
    *,
    tag: str,
    commit: str,
    package_name: str,
    package_version: str,
    payloads: list[Path],
) -> dict[str, Any]:
    names = [path.name for path in payloads]
    if len(names) != len(set(names)):
        raise ReleaseArtifactError("release payload filenames must be unique")
    return {
        "manifestVersion": "1",
        "tag": tag,
        "commit": commit,
        "package": {"name": package_name, "version": package_version},
        "toolchain": {
            "buildLock": BUILD_LOCK_NAME,
            "validationLock": VALIDATION_LOCK_NAME,
            "pep517Isolation": False,
        },
        "artifacts": [
            _descriptor(path) for path in sorted(payloads, key=lambda item: item.name)
        ],
        "checksumManifest": {
            "name": CHECKSUM_NAME,
            "scope": (
                "Every attached payload asset including this release manifest, "
                "excluding SHA256SUMS itself."
            ),
            "selfHashExcluded": True,
        },
        "nonClaims": [
            "Artifact hashes authenticate the exact distributed bytes only.",
            "Pinned build inputs do not establish cross-machine byte reproducibility.",
            "Offline verification does not authenticate GitHub Actions state; use verify-github.",
            "The Git commit SHA remains the reviewed source-tree identity anchor.",
        ],
    }


def write_checksum_manifest(out_dir: Path, *, payloads: list[Path]) -> Path:
    checksum = out_dir / CHECKSUM_NAME
    sorted_payloads = sorted(payloads, key=lambda item: item.name)
    lines = [f"{_sha256(path)}  {path.name}" for path in sorted_payloads]
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return checksum


def _require_release_payload_set(
    expected: set[str],
    *,
    tag: str,
    package_name: str,
    package_version: str,
) -> None:
    normalized = package_name.replace("-", "_")
    source_name = f"ens-grant-decision-integrity-{tag}.tar.gz"
    sdist_name = f"{normalized}-{package_version}.tar.gz"
    wheel_prefix = f"{normalized}-{package_version}-"
    wheels = sorted(
        name for name in expected if name.startswith(wheel_prefix) and name.endswith(".whl")
    )
    required = {
        source_name,
        sdist_name,
        SBOM_NAME,
        VALIDATION_NAME,
        BUILD_LOCK_NAME,
        VALIDATION_LOCK_NAME,
    }
    missing = sorted(required - expected)
    if missing:
        raise ReleaseArtifactError(f"release manifest is missing required payloads: {missing}")
    if len(wheels) != 1:
        raise ReleaseArtifactError(
            f"release manifest must contain exactly one package wheel; observed={wheels}"
        )


def verify_directory(out_dir: Path) -> dict[str, Any]:
    _assert_flat_regular_directory(out_dir)
    manifest_path = out_dir / MANIFEST_NAME
    checksum_path = out_dir / CHECKSUM_NAME
    manifest = _load_json(manifest_path, label="release manifest")
    tag, commit, package_name, package_version = _validate_manifest_identity(manifest)
    validation = _load_json(out_dir / VALIDATION_NAME, label="release validation report")
    _validate_evidence(validation, commit=commit)

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ReleaseArtifactError("release manifest artifacts must be a list")

    expected: dict[str, tuple[str, int]] = {}
    for item in artifacts:
        if not isinstance(item, dict):
            raise ReleaseArtifactError("release manifest artifact entries must be objects")
        name = _validate_asset_name(item.get("name"), label="release manifest")
        digest = item.get("sha256")
        size = item.get("size")
        if name in expected:
            raise ReleaseArtifactError(f"duplicate manifest artifact name: {name!r}")
        if name in {MANIFEST_NAME, CHECKSUM_NAME}:
            raise ReleaseArtifactError(
                f"manifest artifact cannot self-reference control file: {name}"
            )
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ReleaseArtifactError(f"invalid SHA-256 for manifest artifact {name}")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise ReleaseArtifactError(f"invalid size for manifest artifact {name}")
        expected[name] = (digest, size)

    _require_release_payload_set(
        set(expected),
        tag=tag,
        package_name=package_name,
        package_version=package_version,
    )

    for name, (digest, size) in expected.items():
        path = out_dir / name
        if not path.is_file():
            raise ReleaseArtifactError(f"manifest payload is missing: {name}")
        if path.stat().st_size != size:
            raise ReleaseArtifactError(f"size mismatch for manifest payload: {name}")
        if _sha256(path) != digest:
            raise ReleaseArtifactError(f"SHA-256 mismatch for manifest payload: {name}")

    checksum_lines = checksum_path.read_text(encoding="utf-8").splitlines()
    parsed: dict[str, str] = {}
    for line in checksum_lines:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            raise ReleaseArtifactError(f"invalid checksum-manifest line: {line!r}")
        digest, raw_name = match.groups()
        name = _validate_asset_name(raw_name, label="checksum manifest")
        if name in parsed:
            raise ReleaseArtifactError(f"duplicate checksum entry: {name}")
        parsed[name] = digest

    checksum_scope = set(expected) | {MANIFEST_NAME}
    if set(parsed) != checksum_scope:
        raise ReleaseArtifactError(
            f"checksum scope mismatch: expected={sorted(checksum_scope)} observed={sorted(parsed)}"
        )
    for name, digest in parsed.items():
        path = out_dir / name
        if not path.is_file() or _sha256(path) != digest:
            raise ReleaseArtifactError(f"checksum verification failed for {name}")

    permitted = checksum_scope | {CHECKSUM_NAME}
    observed = {path.name for path in out_dir.iterdir()}
    if observed != permitted:
        raise ReleaseArtifactError(
            f"release directory contains missing or extra files: expected={sorted(permitted)} "
            f"observed={sorted(observed)}"
        )
    return {
        "ok": True,
        "tag": tag,
        "commit": commit,
        "releaseEligible": validation["releaseEligible"],
        "verifiedPayloadCount": len(parsed),
        "checksumManifest": CHECKSUM_NAME,
    }


def _github_json(url: str, *, token: str | None) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ens-gdi-release-verifier",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        urllib.error.HTTPError,
        urllib.error.URLError,
    ) as exc:
        raise ReleaseArtifactError(f"cannot query GitHub Actions evidence: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReleaseArtifactError("GitHub Actions API returned a non-object payload")
    return payload


def _validate_github_records(
    evidence: dict[str, Any],
    run: dict[str, Any],
    jobs_document: dict[str, Any],
    *,
    commit: str,
) -> None:
    _validate_evidence(evidence, commit=commit)
    if evidence.get("releaseEligible") is not True:
        raise ReleaseArtifactError("GitHub verification requires releaseEligible=true evidence")

    run_id = evidence["runId"]
    run_attempt = evidence["runAttempt"]
    expected_run = {
        "id": run_id,
        "run_attempt": run_attempt,
        "name": WORKFLOW_NAME,
        "path": WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": commit,
        "status": "completed",
        "conclusion": "success",
        "html_url": evidence["workflowRunUrl"],
    }
    mismatches = {
        key: {"expected": expected, "observed": run.get(key)}
        for key, expected in expected_run.items()
        if run.get(key) != expected
    }
    repository = run.get("repository")
    if not isinstance(repository, dict) or repository.get("full_name") != REPOSITORY:
        mismatches["repository.full_name"] = {
            "expected": REPOSITORY,
            "observed": repository.get("full_name") if isinstance(repository, dict) else None,
        }
    if mismatches:
        raise ReleaseArtifactError(f"GitHub workflow-run identity mismatch: {mismatches}")

    rows = jobs_document.get("jobs")
    total_count = jobs_document.get("total_count")
    if not isinstance(rows, list) or not isinstance(total_count, int):
        raise ReleaseArtifactError("GitHub jobs response is malformed")
    if total_count != len(rows):
        raise ReleaseArtifactError(
            "GitHub jobs response is incomplete; expected all jobs in one verified response"
        )

    expected_names = REQUIRED_RELEASE_JOBS | {"release-assets"}
    observed: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ReleaseArtifactError("GitHub jobs response contains a non-object job")
        name = row.get("name")
        if not isinstance(name, str) or name in observed:
            raise ReleaseArtifactError(f"invalid or duplicate GitHub job name: {name!r}")
        observed[name] = row
    if set(observed) != expected_names:
        raise ReleaseArtifactError(
            f"GitHub release run job set mismatch: expected={sorted(expected_names)} "
            f"observed={sorted(observed)}"
        )

    failed = sorted(
        name
        for name, row in observed.items()
        if row.get("status") != "completed" or row.get("conclusion") != "success"
    )
    if failed:
        raise ReleaseArtifactError(f"GitHub release run has unsuccessful jobs: {failed}")

    for name in REQUIRED_RELEASE_JOBS:
        steps = observed[name].get("steps")
        if not isinstance(steps, list):
            raise ReleaseArtifactError(f"GitHub job lacks step evidence: {name}")
        exact_sha = [step for step in steps if step.get("name") == "Assert exact validation SHA"]
        if len(exact_sha) != 1 or exact_sha[0].get("conclusion") != "success":
            raise ReleaseArtifactError(f"GitHub job lacks successful exact-SHA assertion: {name}")

    release_steps = observed["release-assets"].get("steps")
    if not isinstance(release_steps, list):
        raise ReleaseArtifactError("release-assets job lacks step evidence")
    main_binding = [
        step for step in release_steps if step.get("name") == "Require exact main-branch release commit"
    ]
    if len(main_binding) != 1 or main_binding[0].get("conclusion") != "success":
        raise ReleaseArtifactError("release-assets lacks successful main-branch SHA binding")


def verify_github_evidence(out_dir: Path, *, token: str | None = None) -> dict[str, Any]:
    verification = verify_directory(out_dir)
    if verification["releaseEligible"] is not True:
        raise ReleaseArtifactError("GitHub verification is only valid for release-eligible candidates")
    evidence = _load_json(out_dir / VALIDATION_NAME, label="release validation report")
    run_id = evidence["runId"]
    run = _github_json(
        f"https://api.github.com/repos/{REPOSITORY}/actions/runs/{run_id}",
        token=token,
    )
    jobs_document = _github_json(
        f"https://api.github.com/repos/{REPOSITORY}/actions/runs/{run_id}/jobs?per_page=100",
        token=token,
    )
    _validate_github_records(evidence, run, jobs_document, commit=verification["commit"])
    return {
        **verification,
        "githubEvidenceVerified": True,
        "githubRunId": run_id,
        "githubRunAttempt": evidence["runAttempt"],
    }


def assemble(
    *,
    tag: str,
    commit: str,
    evidence_path: Path,
    out_dir: Path,
    require_clean: bool,
) -> dict[str, Any]:
    _assert_commit(commit, require_clean=require_clean)
    evidence = _load_json(evidence_path, label="validation evidence")
    _validate_evidence(evidence, commit=commit)

    if out_dir.exists():
        if out_dir.is_symlink() or not out_dir.is_dir():
            raise ReleaseArtifactError("output path must be a real directory")
        if any(out_dir.iterdir()):
            raise ReleaseArtifactError(f"output directory must be empty: {out_dir}")
    else:
        out_dir.mkdir(parents=True)

    validation = out_dir / VALIDATION_NAME
    _write_json(validation, evidence)
    build_lock, validation_lock = _copy_release_lockfiles(out_dir)
    source = _source_archive(out_dir, tag=tag, commit=commit)
    wheel, sdist = _build_python_distributions(out_dir)
    sbom = _generate_sbom(out_dir, wheel=wheel)
    package_name, package_version = _project_metadata()

    payloads = [
        source,
        wheel,
        sdist,
        sbom,
        validation,
        build_lock,
        validation_lock,
    ]
    manifest = out_dir / MANIFEST_NAME
    _write_json(
        manifest,
        build_manifest(
            tag=tag,
            commit=commit,
            package_name=package_name,
            package_version=package_version,
            payloads=payloads,
        ),
    )
    checksum = write_checksum_manifest(out_dir, payloads=[*payloads, manifest])
    verification = verify_directory(out_dir)
    return {
        **verification,
        "artifacts": sorted(path.name for path in [*payloads, manifest, checksum]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    assemble_parser = subparsers.add_parser("assemble")
    assemble_parser.add_argument("--tag", required=True)
    assemble_parser.add_argument("--commit", required=True)
    assemble_parser.add_argument("--validation-evidence", type=Path, required=True)
    assemble_parser.add_argument("--out", type=Path, required=True)
    assemble_parser.add_argument(
        "--allow-dirty-checkout",
        action="store_true",
        help="CI smoke only; final release assembly must use a clean checkout.",
    )

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("directory", type=Path)

    verify_github_parser = subparsers.add_parser("verify-github")
    verify_github_parser.add_argument("directory", type=Path)

    args = parser.parse_args()
    try:
        if args.command == "assemble":
            result = assemble(
                tag=args.tag,
                commit=args.commit,
                evidence_path=args.validation_evidence,
                out_dir=args.out,
                require_clean=not args.allow_dirty_checkout,
            )
        elif args.command == "verify-github":
            result = verify_github_evidence(
                args.directory,
                token=os.environ.get("GITHUB_TOKEN"),
            )
        else:
            result = verify_directory(args.directory)
    except (ReleaseArtifactError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
