#!/usr/bin/env python3
"""Assemble and verify release-candidate payloads from one exact Git commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHECKSUM_NAME = "SHA256SUMS"
MANIFEST_NAME = "release-manifest.json"
VALIDATION_NAME = "release-validation.json"
SBOM_NAME = "sbom.cdx.json"
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


def _project_metadata() -> tuple[str, str]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    return str(project["name"]), str(project["version"])


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


def _validate_manifest_identity(manifest: dict[str, Any]) -> tuple[str, str]:
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
    return tag, commit


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


def _build_python_distributions(out_dir: Path) -> tuple[Path, Path]:
    _run(sys.executable, "-m", "build", "--outdir", str(out_dir))
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
        python = venv / "bin" / "python"
        if sys.platform == "win32":
            python = venv / "Scripts" / "python.exe"
        _run(
            str(python),
            "-m",
            "pip",
            "install",
            "--require-hashes",
            "-r",
            str(ROOT / "requirements.lock.txt"),
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
        "artifacts": [_descriptor(path) for path in sorted(payloads, key=lambda item: item.name)],
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
            "This manifest does not claim byte-reproducible builds across machines or toolchains.",
            "The Git commit SHA remains the reviewed source-tree identity anchor.",
        ],
    }


def write_checksum_manifest(out_dir: Path, *, payloads: list[Path]) -> Path:
    checksum = out_dir / CHECKSUM_NAME
    sorted_payloads = sorted(payloads, key=lambda item: item.name)
    lines = [f"{_sha256(path)}  {path.name}" for path in sorted_payloads]
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return checksum


def verify_directory(out_dir: Path) -> dict[str, Any]:
    _assert_flat_regular_directory(out_dir)
    manifest_path = out_dir / MANIFEST_NAME
    checksum_path = out_dir / CHECKSUM_NAME
    manifest = _load_json(manifest_path, label="release manifest")
    tag, commit = _validate_manifest_identity(manifest)
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

    if VALIDATION_NAME not in expected:
        raise ReleaseArtifactError("release manifest must include the validation report")

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
    source = _source_archive(out_dir, tag=tag, commit=commit)
    wheel, sdist = _build_python_distributions(out_dir)
    sbom = _generate_sbom(out_dir, wheel=wheel)
    package_name, package_version = _project_metadata()

    payloads = [source, wheel, sdist, sbom, validation]
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
        else:
            result = verify_directory(args.directory)
    except (ReleaseArtifactError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
