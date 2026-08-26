"""Assurance report construction and text rendering."""

from __future__ import annotations

from typing import Any

from gdi import __version__

HARD_NON_CLAIMS = [
    (
        "ok=true means every required selected check reached pass or warning without failure; "
        "it does not mean all possible claims are true."
    ),
    "Hashes, anchors, and signatures are not institutional funding authority.",
    "Allocation is not payment, receipt, or settlement.",
    "Annotation agreement is not correctness, fairness, or legitimacy.",
    "Bundles cannot appoint their own trust roots.",
]


def empty_report(
    *,
    bundle_id: str,
    manifest_digest: str,
    bundle_class: str | None = None,
) -> dict[str, Any]:
    subject: dict[str, Any] = {
        "bundleId": bundle_id,
        "manifestDigestSha256": manifest_digest,
    }
    if bundle_class is not None:
        subject["bundleClass"] = bundle_class
    return {
        "reportVersion": "1",
        "verifier": {"name": "gdi", "version": __version__, "repositoryCommit": None},
        "subject": subject,
        "profileSet": [],
        "trustPolicy": None,
        "checks": [],
        "establishedClaims": [],
        "warnings": [],
        "failures": [],
        "unverified": [],
        "trustAssumptions": [],
        "nonClaims": list(HARD_NON_CLAIMS),
        "ok": True,
    }


def add_check(
    report: dict[str, Any],
    *,
    check_id: str,
    status: str,
    claim_ids: list[str],
    evidence: list[str],
    details: dict[str, Any] | None = None,
    required: bool = True,
) -> None:
    report["checks"].append(
        {
            "checkId": check_id,
            "status": status,
            "claimIds": claim_ids,
            "evidence": evidence,
            "details": details or {},
        }
    )
    if status == "pass":
        for claim_id in claim_ids:
            if claim_id not in report["establishedClaims"]:
                report["establishedClaims"].append(claim_id)
    elif status == "fail":
        report["failures"].append(f"{check_id}: {details or {}}")
        if required:
            report["ok"] = False
    elif status == "warning":
        report["warnings"].append(f"{check_id}: {details or {}}")
    elif status in {"not-run", "unsupported", "not-applicable"}:
        report["unverified"].append(f"{check_id}:{status}")
        if required:
            report["ok"] = False
            report["failures"].append(
                f"{check_id}: required check did not complete ({status}); {details or {}}"
            )
    else:
        report["ok"] = False
        report["failures"].append(f"{check_id}: unknown check status {status!r}")


def finalize(report: dict[str, Any]) -> dict[str, Any]:
    report["checks"] = sorted(report["checks"], key=lambda item: item["checkId"])
    report["establishedClaims"] = sorted(set(report["establishedClaims"]))
    report["warnings"] = sorted(report["warnings"])
    report["failures"] = sorted(report["failures"])
    report["unverified"] = sorted(report["unverified"])
    report["trustAssumptions"] = sorted(set(report["trustAssumptions"]))
    return report


def render_text(report: dict[str, Any]) -> str:
    lines = [
        f"subject: {report['subject']['bundleId']} ({report['subject']['manifestDigestSha256']})",
        f"required-checks: {'PASS' if report['ok'] else 'FAIL'}",
        "established-claims:",
    ]
    lines.extend(f"  - {item}" for item in report["establishedClaims"] or ["(none)"])
    lines.append("failures:")
    lines.extend(f"  - {item}" for item in report["failures"] or ["(none)"])
    lines.append("warnings:")
    lines.extend(f"  - {item}" for item in report["warnings"] or ["(none)"])
    lines.append("not-run/not-applicable/unsupported:")
    lines.extend(f"  - {item}" for item in report["unverified"] or ["(none)"])
    lines.append("trust-assumptions:")
    lines.extend(f"  - {item}" for item in report["trustAssumptions"] or ["(none)"])
    lines.append("non-claims:")
    lines.extend(f"  - {item}" for item in report["nonClaims"])
    return "\n".join(lines) + "\n"
