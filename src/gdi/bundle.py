"""Offline verification-bundle loader and verifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from gdi.claims import require_known_claim_ids
from gdi.core.conformance import validate_record
from gdi.exit_codes import (
    EVIDENCE_FAILURE,
    OK,
    TRUST_POLICY_INSUFFICIENT,
    UNSUPPORTED,
    USAGE_ERROR,
)
from gdi.report import add_check, empty_report, finalize
from gdi.source.artifact import SourceArtifactError, verify_artifact
from gdi.trust.policy import TrustPolicyError, load_trust_policy

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCHEMA = ROOT / "schema" / "verification-bundle-manifest.schema.json"
MAX_JSON_BYTES = 8_000_000
MAX_JSON_DEPTH = 64


class BundleError(Exception):
    def __init__(self, message: str, *, code: str = "BUNDLE001", exit_code: int = EVIDENCE_FAILURE) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _safe_resolve(root: Path, relative: str, *, label: str) -> Path:
    if not relative or relative.startswith("/") or relative.startswith("\\") or ":" in relative[:4]:
        raise BundleError(f"{label} path must be relative: {relative!r}", code="BUNDLE002", exit_code=USAGE_ERROR)
    parts = Path(relative).parts
    if any(part in {"", ".."} for part in parts):
        raise BundleError(f"{label} path escapes bundle root: {relative!r}", code="BUNDLE002", exit_code=USAGE_ERROR)
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise BundleError(f"{label} path escapes bundle root: {relative!r}", code="BUNDLE002", exit_code=USAGE_ERROR) from exc
    if resolved.is_symlink():
        raise BundleError(f"{label} path must not be a symlink: {relative!r}", code="BUNDLE003", exit_code=USAGE_ERROR)
    if not resolved.is_file():
        raise BundleError(f"{label} file not found: {relative!r}", code="BUNDLE004")
    return resolved


def _json_depth(value: Any, depth: int = 0) -> int:
    if depth > MAX_JSON_DEPTH:
        return depth
    if isinstance(value, dict):
        return max([depth] + [_json_depth(item, depth + 1) for item in value.values()] or [depth])
    if isinstance(value, list):
        return max([depth] + [_json_depth(item, depth + 1) for item in value] or [depth])
    return depth


def _load_json_file(path: Path, *, label: str) -> Any:
    raw = path.read_bytes()
    if len(raw) > MAX_JSON_BYTES:
        raise BundleError(f"{label} exceeds size limit", code="BUNDLE005", exit_code=USAGE_ERROR)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError(f"{label} is not valid JSON: {exc}", code="BUNDLE006") from exc
    if _json_depth(value) > MAX_JSON_DEPTH:
        raise BundleError(f"{label} exceeds JSON depth limit", code="BUNDLE005", exit_code=USAGE_ERROR)
    return value


def verify_bundle(
    bundle_dir: Path,
    *,
    trust_policy_path: Path | None = None,
    online: bool = False,
) -> tuple[dict[str, Any], int]:
    if online:
        raise BundleError(
            "online verification is not enabled; capture and verify offline artifacts instead",
            code="BUNDLE010",
            exit_code=UNSUPPORTED,
        )
    if not bundle_dir.is_dir():
        raise BundleError(f"bundle directory not found: {bundle_dir}", code="BUNDLE007", exit_code=USAGE_ERROR)

    manifest_path = _safe_resolve(bundle_dir, "manifest.json", label="manifest")
    manifest_digest = _sha256_file(manifest_path)
    manifest = _load_json_file(manifest_path, label="manifest")

    import jsonschema

    schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(manifest), key=lambda err: list(err.path))
    if errors:
        raise BundleError(f"manifest schema failure: {errors[0].message}", code="BUNDLE008", exit_code=USAGE_ERROR)

    report = empty_report(
        bundle_id=manifest["bundleId"],
        manifest_digest=manifest_digest,
        bundle_class=manifest.get("bundleClass"),
    )
    report["profileSet"] = [manifest["record"]["schemaProfile"]]

    trust_policy = None
    trust_digest = None
    if trust_policy_path is not None:
        try:
            trust_policy, trust_digest = load_trust_policy(trust_policy_path)
            report["trustPolicy"] = {
                "policyId": trust_policy["policyId"],
                "policyDigestSha256": trust_digest,
            }
            report["trustAssumptions"].append(f"external-trust-policy:{trust_policy['policyId']}")
            add_check(
                report,
                check_id="trust.policy",
                status="pass",
                claim_ids=["TRUST.POLICY.EXTERNAL"],
                evidence=[str(trust_policy_path)],
                details={"policyDigestSha256": trust_digest},
            )
        except TrustPolicyError as exc:
            add_check(
                report,
                check_id="trust.policy",
                status="fail",
                claim_ids=["TRUST.POLICY.EXTERNAL"],
                evidence=[str(trust_policy_path)],
                details={"error": str(exc), "code": exc.code},
            )
            finalize(report)
            return report, TRUST_POLICY_INSUFFICIENT
    else:
        add_check(
            report,
            check_id="trust.policy",
            status="not-run",
            claim_ids=["TRUST.POLICY.EXTERNAL"],
            evidence=[],
            details={"reason": "no --trust-policy supplied"},
            required=False,
        )

    record_path = _safe_resolve(bundle_dir, manifest["record"]["path"], label="record")
    record_digest = _sha256_file(record_path)
    if record_digest != manifest["record"]["sha256"]:
        add_check(
            report,
            check_id="bundle.record-digest",
            status="fail",
            claim_ids=["CORE.SCHEMA.STRUCTURE"],
            evidence=[manifest["record"]["path"]],
            details={"declared": manifest["record"]["sha256"], "observed": record_digest},
        )
        finalize(report)
        return report, EVIDENCE_FAILURE
    add_check(
        report,
        check_id="bundle.record-digest",
        status="pass",
        claim_ids=["CORE.SCHEMA.STRUCTURE"],
        evidence=[manifest["record"]["path"]],
        details={"sha256": record_digest},
    )

    record = _load_json_file(record_path, label="record")
    findings = validate_record(record)
    errors = [item.render() for item in findings if item.severity == "error"]
    warnings = [item.render() for item in findings if item.severity == "warning"]
    if errors:
        add_check(
            report,
            check_id="core.schema",
            status="fail",
            claim_ids=["CORE.SCHEMA.STRUCTURE", "CORE.CONFORMANCE.CROSS_FIELD"],
            evidence=[manifest["record"]["path"]],
            details={"errors": errors, "warnings": warnings},
        )
    else:
        add_check(
            report,
            check_id="core.schema",
            status="pass",
            claim_ids=["CORE.SCHEMA.STRUCTURE"],
            evidence=[manifest["record"]["path"]],
            details={"warnings": warnings},
        )
        add_check(
            report,
            check_id="core.conformance",
            status="pass" if not warnings else "warning",
            claim_ids=[
                "CORE.CONFORMANCE.CROSS_FIELD",
                "CORE.AUTHORITY.HUMAN_SURFACE",
                "CORE.EVIDENCE.REFERENCE_RESOLUTION",
                "CORE.CONFLICT.RECUSAL_CONSISTENCY",
                "CORE.CHALLENGE.LIFECYCLE",
                "CORE.DELIVERY.CONDITION_CONSISTENCY",
            ],
            evidence=[manifest["record"]["path"]],
            details={"warnings": warnings},
            required=True,
        )

    for index, source in enumerate(manifest.get("sourceArtifacts", [])):
        meta_path = _safe_resolve(bundle_dir, source["metadataPath"], label=f"source[{index}].metadata")
        bytes_path = _safe_resolve(bundle_dir, source["bytesPath"], label=f"source[{index}].bytes")
        try:
            metadata = _load_json_file(meta_path, label=f"source[{index}].metadata")
            verified = verify_artifact(metadata, bytes_path)
            add_check(
                report,
                check_id=f"source.bytes[{index}]",
                status="pass",
                claim_ids=["SOURCE.BYTES.MATCH_METADATA"],
                evidence=[source["metadataPath"], source["bytesPath"]],
                details={"artifactId": verified.artifact_id},
                required=bool(source.get("required", True)),
            )
        except (SourceArtifactError, BundleError, OSError, ValueError) as exc:
            add_check(
                report,
                check_id=f"source.bytes[{index}]",
                status="fail",
                claim_ids=["SOURCE.BYTES.MATCH_METADATA"],
                evidence=[source["metadataPath"], source["bytesPath"]],
                details={"error": str(exc)},
                required=bool(source.get("required", True)),
            )

    if "phase2" in manifest:
        if manifest["phase2"].get("required"):
            add_check(
                report,
                check_id="phase2.bundle",
                status="not-run",
                claim_ids=["PHASE2.C1.MANIFEST_BINDING"],
                evidence=[manifest["phase2"]["path"]],
                details={"reason": "use gdi verify-phase2 / phase2 CLI for full Phase II graph verification in this wrap"},
            )
        else:
            add_check(
                report,
                check_id="phase2.bundle",
                status="not-applicable",
                claim_ids=["PHASE2.C1.MANIFEST_BINDING"],
                evidence=[],
                details={"reason": "optional Phase II section not required"},
                required=False,
            )
    else:
        add_check(
            report,
            check_id="phase2.bundle",
            status="not-applicable",
            claim_ids=["PHASE2.C1.MANIFEST_BINDING"],
            evidence=[],
            required=False,
        )

    # C4A remains not-run unless trust policy + key authorization are evaluated by Phase II verify.
    if trust_policy is None:
        add_check(
            report,
            check_id="phase2.c4a",
            status="not-run",
            claim_ids=["PHASE2.C4A.AUTHORIZED_SIGNER"],
            evidence=[],
            details={"reason": "C4A requires external trust policy and a verified run signature key"},
            required=False,
        )
    else:
        add_check(
            report,
            check_id="phase2.c4a",
            status="not-run",
            claim_ids=["PHASE2.C4A.AUTHORIZED_SIGNER"],
            evidence=[],
            details={"reason": "trust policy loaded; run-signature authorization is evaluated in Phase II verify-run/graph"},
            required=False,
        )

    emitted = []
    for check in report["checks"]:
        emitted.extend(check["claimIds"])
    require_known_claim_ids(emitted)
    finalize(report)
    return report, OK if report["ok"] else EVIDENCE_FAILURE
