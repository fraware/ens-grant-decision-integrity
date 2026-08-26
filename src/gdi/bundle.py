"""Offline verification-bundle loader and verifier.

The bundle verifier is deliberately fail closed: every manifest component marked
``required`` must reach a completed acceptable state. A required component that
is unavailable, unsupported, or missing verification inputs cannot coexist with
``ok=true``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from gdi.claims import lookup, require_known_claim_ids
from gdi.core.runtime import validate_record
from gdi.exit_codes import (
    EVIDENCE_FAILURE,
    OK,
    TRUST_POLICY_INSUFFICIENT,
    UNSUPPORTED,
    USAGE_ERROR,
)
from gdi.phase2 import phase2_error_type, verify_graph_bundle
from gdi.projection import project_record, verify_projection_v2
from gdi.report import add_check, empty_report, finalize
from gdi.resources import resource_path
from gdi.source.artifact import SourceArtifactError, VerifiedSourceArtifact, verify_artifact
from gdi.source.policy_pins import PolicyPinError, verify_policy_pins
from gdi.trust.policy import TrustPolicyError, load_trust_policy

MANIFEST_SCHEMA = resource_path("schema", "verification-bundle-manifest.schema.json")
MAX_JSON_BYTES = 8_000_000
MAX_JSON_DEPTH = 64


class BundleError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "BUNDLE001",
        exit_code: int = EVIDENCE_FAILURE,
    ) -> None:
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
        raise BundleError(
            f"{label} path must be relative: {relative!r}",
            code="BUNDLE002",
            exit_code=USAGE_ERROR,
        )
    parts = Path(relative).parts
    if any(part in {"", ".."} for part in parts):
        raise BundleError(
            f"{label} path escapes bundle root: {relative!r}",
            code="BUNDLE002",
            exit_code=USAGE_ERROR,
        )

    root_resolved = root.resolve()
    candidate = root.joinpath(*parts)
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise BundleError(
                f"{label} path must not traverse a symlink: {relative!r}",
                code="BUNDLE003",
                exit_code=USAGE_ERROR,
            )

    resolved = candidate.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise BundleError(
            f"{label} path escapes bundle root: {relative!r}",
            code="BUNDLE002",
            exit_code=USAGE_ERROR,
        ) from exc
    if not resolved.is_file():
        raise BundleError(f"{label} file not found: {relative!r}", code="BUNDLE004")
    return resolved


def _json_depth(value: Any, depth: int = 0) -> int:
    if depth > MAX_JSON_DEPTH:
        return depth
    if isinstance(value, dict):
        return max([depth] + [_json_depth(item, depth + 1) for item in value.values()])
    if isinstance(value, list):
        return max([depth] + [_json_depth(item, depth + 1) for item in value])
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
        raise BundleError(
            f"{label} exceeds JSON depth limit",
            code="BUNDLE005",
            exit_code=USAGE_ERROR,
        )
    return value


def _canonical_phase2_claim_ids(ids: list[str]) -> list[str]:
    canonical: list[str] = []
    for claim_id in ids:
        resolved = lookup(claim_id)["claimId"]
        if resolved not in canonical:
            canonical.append(resolved)
    return canonical


def _declared_digest_check(
    report: dict[str, Any],
    *,
    check_id: str,
    path: Path,
    declared: str | None,
    evidence: str,
    required: bool,
    claim_ids: list[str],
) -> bool:
    if declared is None:
        return True
    observed = _sha256_file(path)
    if observed != declared:
        add_check(
            report,
            check_id=check_id,
            status="fail",
            claim_ids=claim_ids,
            evidence=[evidence],
            details={"declared": declared, "observed": observed},
            required=required,
        )
        return False
    add_check(
        report,
        check_id=check_id,
        status="pass",
        claim_ids=[],
        evidence=[evidence],
        details={"sha256": observed},
        required=required,
    )
    return True


def verify_bundle(
    bundle_dir: Path,
    *,
    trust_policy_path: Path | None = None,
    trust_root_path: Path | None = None,
    online: bool = False,
) -> tuple[dict[str, Any], int]:
    if online:
        raise BundleError(
            "online verification is not enabled; capture and verify offline artifacts instead",
            code="BUNDLE010",
            exit_code=UNSUPPORTED,
        )
    if not bundle_dir.is_dir():
        raise BundleError(
            f"bundle directory not found: {bundle_dir}",
            code="BUNDLE007",
            exit_code=USAGE_ERROR,
        )

    manifest_path = _safe_resolve(bundle_dir, "manifest.json", label="manifest")
    manifest_digest = _sha256_file(manifest_path)
    manifest = _load_json_file(manifest_path, label="manifest")

    import jsonschema

    schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(manifest),
        key=lambda err: list(err.path),
    )
    if errors:
        raise BundleError(
            f"manifest schema failure: {errors[0].message}",
            code="BUNDLE008",
            exit_code=USAGE_ERROR,
        )

    report = empty_report(
        bundle_id=manifest["bundleId"],
        manifest_digest=manifest_digest,
        bundle_class=manifest.get("bundleClass"),
    )
    report["profileSet"] = [manifest["record"]["schemaProfile"]]

    trust_policy: dict[str, Any] | None = None
    trust_digest: str | None = None
    if trust_policy_path is not None:
        try:
            trust_policy, trust_digest = load_trust_policy(trust_policy_path)
            reference = manifest.get("trustPolicyReference") or {}
            expected_id = reference.get("policyId")
            expected_digest = reference.get("expectedDigestSha256")
            if expected_id is not None and expected_id != trust_policy["policyId"]:
                raise TrustPolicyError(
                    "external trust policy id does not match bundle reference",
                    code="TRUST005",
                )
            if expected_digest is not None and expected_digest != trust_digest:
                raise TrustPolicyError(
                    "external trust policy digest does not match bundle reference",
                    code="TRUST006",
                )
            report["trustPolicy"] = {
                "policyId": trust_policy["policyId"],
                "policyDigestSha256": trust_digest,
            }
            report["trustAssumptions"].append(
                f"external-trust-policy:{trust_policy['policyId']}"
            )
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

    trust_root_pem: str | None = None
    if trust_root_path is not None:
        try:
            trust_root_pem = trust_root_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise BundleError(
                f"cannot read external trust root: {exc}",
                code="BUNDLE011",
                exit_code=TRUST_POLICY_INSUFFICIENT,
            ) from exc

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
        claim_ids=[],
        evidence=[manifest["record"]["path"]],
        details={"sha256": record_digest},
    )

    record = _load_json_file(record_path, label="record")
    if not isinstance(record, dict):
        raise BundleError("record must be a JSON object", code="BUNDLE012")
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

    verified_sources: list[VerifiedSourceArtifact] = []
    for index, source in enumerate(manifest.get("sourceArtifacts", [])):
        required = bool(source.get("required", True))
        metadata_path = _safe_resolve(
            bundle_dir,
            source["metadataPath"],
            label=f"source[{index}].metadata",
        )
        bytes_path = _safe_resolve(
            bundle_dir,
            source["bytesPath"],
            label=f"source[{index}].bytes",
        )
        metadata_digest_ok = _declared_digest_check(
            report,
            check_id=f"bundle.source-metadata-digest[{index}]",
            path=metadata_path,
            declared=source.get("metadataSha256"),
            evidence=source["metadataPath"],
            required=required,
            claim_ids=["SOURCE.BYTES.MATCH_METADATA"],
        )
        bytes_digest_ok = _declared_digest_check(
            report,
            check_id=f"bundle.source-bytes-digest[{index}]",
            path=bytes_path,
            declared=source.get("bytesSha256"),
            evidence=source["bytesPath"],
            required=required,
            claim_ids=["SOURCE.BYTES.MATCH_METADATA"],
        )
        if not (metadata_digest_ok and bytes_digest_ok):
            continue
        try:
            metadata = _load_json_file(metadata_path, label=f"source[{index}].metadata")
            if not isinstance(metadata, dict):
                raise BundleError("source metadata must be a JSON object", code="BUNDLE013")
            verified = verify_artifact(metadata, bytes_path)
            verified_sources.append(verified)
            add_check(
                report,
                check_id=f"source.bytes[{index}]",
                status="pass",
                claim_ids=["SOURCE.BYTES.MATCH_METADATA"],
                evidence=[source["metadataPath"], source["bytesPath"]],
                details={"artifactId": verified.artifact_id},
                required=required,
            )
        except (SourceArtifactError, BundleError, OSError, ValueError) as exc:
            add_check(
                report,
                check_id=f"source.bytes[{index}]",
                status="fail",
                claim_ids=["SOURCE.BYTES.MATCH_METADATA"],
                evidence=[source["metadataPath"], source["bytesPath"]],
                details={"error": str(exc)},
                required=required,
            )

    try:
        pins = verify_policy_pins(record, verified_sources)
        if pins["applicable"]:
            add_check(
                report,
                check_id="source.policy-pins",
                status="pass" if pins["ok"] else "fail",
                claim_ids=["SOURCE.POLICY_PIN.MATCH"],
                evidence=[manifest["record"]["path"]],
                details={"checks": pins["checks"]},
                required=True,
            )
        else:
            add_check(
                report,
                check_id="source.policy-pins",
                status="not-applicable",
                claim_ids=["SOURCE.POLICY_PIN.MATCH"],
                evidence=[],
                details={"reason": "record has no policyPinning object"},
                required=False,
            )
    except PolicyPinError as exc:
        add_check(
            report,
            check_id="source.policy-pins",
            status="fail",
            claim_ids=["SOURCE.POLICY_PIN.MATCH"],
            evidence=[manifest["record"]["path"]],
            details={"error": str(exc), "code": exc.code},
            required=record.get("policyPinning") is not None,
        )

    if "phase2" in manifest:
        phase2 = manifest["phase2"]
        required = bool(phase2.get("required"))
        phase2_path = _safe_resolve(bundle_dir, phase2["path"], label="phase2")
        digest_ok = _declared_digest_check(
            report,
            check_id="bundle.phase2-digest",
            path=phase2_path,
            declared=phase2.get("sha256"),
            evidence=phase2["path"],
            required=required,
            claim_ids=["PHASE2.C1.MANIFEST_BINDING"],
        )
        if digest_ok:
            try:
                phase2_bundle = _load_json_file(phase2_path, label="phase2")
                if not isinstance(phase2_bundle, dict):
                    raise BundleError("Phase II evidence must be a JSON object", code="BUNDLE014")
                result = verify_graph_bundle(
                    phase2_bundle,
                    trust_root_pem=trust_root_pem,
                    trust_policy=trust_policy,
                )
                if not bool(result.ok):
                    add_check(
                        report,
                        check_id="phase2.bundle",
                        status="fail",
                        claim_ids=_canonical_phase2_claim_ids(list(result.established)),
                        evidence=[phase2["path"]],
                        details=result.as_dict(),
                        required=required,
                    )
                else:
                    established = _canonical_phase2_claim_ids(list(result.established))
                    add_check(
                        report,
                        check_id="phase2.bundle",
                        status="pass",
                        claim_ids=established,
                        evidence=[phase2["path"]],
                        details=result.as_dict(),
                        required=required,
                    )
                    trust_boundary = result.details.get("trustBoundary")
                    if isinstance(trust_boundary, str) and trust_boundary:
                        report["trustAssumptions"].append(trust_boundary)
            except (BundleError, Exception) as exc:  # noqa: BLE001
                phase_error = phase2_error_type()
                code = getattr(exc, "code", None)
                unsupported_error = isinstance(exc, NotImplementedError | phase_error)
                status = (
                    "unsupported"
                    if unsupported_error and code in {"RKR263", "TS3178"}
                    else "fail"
                )
                add_check(
                    report,
                    check_id="phase2.bundle",
                    status=status,
                    claim_ids=["PHASE2.C1.MANIFEST_BINDING"],
                    evidence=[phase2["path"]],
                    details={"error": str(exc), "code": code},
                    required=required,
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

    if "projection" in manifest:
        projection = manifest["projection"]
        required = bool(projection.get("required"))
        spec_path = _safe_resolve(bundle_dir, projection["specPath"], label="projection.spec")
        public_path = _safe_resolve(
            bundle_dir,
            projection["publicRecordPath"],
            label="projection.public",
        )
        confidential_rel = projection.get("confidentialRecordPath")
        if confidential_rel is None:
            add_check(
                report,
                check_id="projection.execute",
                status="not-run",
                claim_ids=["PROJ.EXEC.DETERMINISTIC"],
                evidence=[projection["specPath"], projection["publicRecordPath"]],
                details={
                    "reason": (
                        "confidentialRecordPath is required for deterministic recomputation"
                    )
                },
                required=required,
            )
        else:
            confidential_path = _safe_resolve(
                bundle_dir,
                confidential_rel,
                label="projection.confidential",
            )
            try:
                spec = _load_json_file(spec_path, label="projection.spec")
                public = _load_json_file(public_path, label="projection.public")
                confidential = _load_json_file(
                    confidential_path,
                    label="projection.confidential",
                )
                if not all(isinstance(item, dict) for item in (spec, public, confidential)):
                    raise BundleError("projection inputs must be JSON objects", code="BUNDLE015")
                spec_version = str(spec.get("specVersion"))
                if spec_version == "2":
                    details = verify_projection_v2(confidential, spec, public)
                    claims = [
                        "PROJ.SPEC.STRUCTURE",
                        "PROJ.EXEC.DETERMINISTIC",
                        "PROJ.COVERAGE.COMPLETE",
                        "PROJ.WITHHELD.COMMITMENT",
                        "PROJ.INTEGRITY.BIND",
                    ]
                elif spec_version == "1":
                    expected = project_record(confidential, spec)
                    if expected.public_record != public:
                        raise BundleError(
                            "public projection does not match deterministic v1 recomputation",
                            code="BUNDLE016",
                        )
                    details = {
                        "ok": True,
                        "projectionDigestSha256": expected.projection_digest,
                        "specVersion": "1",
                    }
                    claims = [
                        "PROJ.SPEC.STRUCTURE",
                        "PROJ.EXEC.DETERMINISTIC",
                        "PROJ.COVERAGE.COMPLETE",
                    ]
                else:
                    add_check(
                        report,
                        check_id="projection.execute",
                        status="unsupported",
                        claim_ids=["PROJ.SPEC.STRUCTURE"],
                        evidence=[projection["specPath"]],
                        details={"specVersion": spec_version},
                        required=required,
                    )
                    claims = []
                    details = {}
                if claims:
                    add_check(
                        report,
                        check_id="projection.execute",
                        status="pass",
                        claim_ids=claims,
                        evidence=[
                            confidential_rel,
                            projection["specPath"],
                            projection["publicRecordPath"],
                        ],
                        details=details,
                        required=required,
                    )
            except Exception as exc:  # noqa: BLE001
                add_check(
                    report,
                    check_id="projection.execute",
                    status="fail",
                    claim_ids=["PROJ.EXEC.DETERMINISTIC"],
                    evidence=[
                        confidential_rel,
                        projection["specPath"],
                        projection["publicRecordPath"],
                    ],
                    details={"error": str(exc), "code": getattr(exc, "code", None)},
                    required=required,
                )
    else:
        add_check(
            report,
            check_id="projection.execute",
            status="not-applicable",
            claim_ids=["PROJ.EXEC.DETERMINISTIC"],
            evidence=[],
            required=False,
        )

    if "funding" in manifest and manifest["funding"].get("statusSnapshotPath"):
        funding = manifest["funding"]
        required = bool(funding.get("required"))
        snapshot_path = _safe_resolve(
            bundle_dir,
            funding["statusSnapshotPath"],
            label="funding.statusSnapshot",
        )
        try:
            snapshot = _load_json_file(snapshot_path, label="funding.statusSnapshot")
            if not isinstance(snapshot, dict):
                raise BundleError("funding status snapshot must be a JSON object", code="BUNDLE017")
            add_check(
                report,
                check_id="funding.status-snapshot",
                status="not-run",
                claim_ids=["FUNDING.STATUS.SNAPSHOT"],
                evidence=[funding["statusSnapshotPath"]],
                details={
                    "reason": (
                        "snapshot bytes parsed, but no versioned funding-status verifier "
                        "is registered"
                    )
                },
                required=required,
            )
        except BundleError as exc:
            add_check(
                report,
                check_id="funding.status-snapshot",
                status="fail",
                claim_ids=["FUNDING.STATUS.SNAPSHOT"],
                evidence=[funding["statusSnapshotPath"]],
                details={"error": str(exc), "code": exc.code},
                required=required,
            )
    else:
        add_check(
            report,
            check_id="funding.status-snapshot",
            status="not-applicable",
            claim_ids=["FUNDING.STATUS.SNAPSHOT"],
            evidence=[],
            required=False,
        )

    add_check(
        report,
        check_id="phase2.c4a",
        status="not-run",
        claim_ids=["PHASE2.C4A.AUTHORIZED_SIGNER"],
        evidence=[],
        details={
            "reason": (
                "C4A requires a separately executed run-signer authorization check "
                "against the external policy"
            )
        },
        required=False,
    )

    emitted: list[str] = []
    for check in report["checks"]:
        emitted.extend(check["claimIds"])
    require_known_claim_ids(emitted)
    finalize(report)
    return report, OK if report["ok"] else EVIDENCE_FAILURE
