"""Evidence-marshaling adapters for GDI operational profiles.

Adapters collect ordinary workflow artifacts into draft records. They MUST NOT
score merit, infer eligibility without confirmation, resolve conflicts, invent
quorum, or assign institutional authority.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

PROVENANCE_KINDS = frozenset({"direct", "derived", "interpretive", "unknown"})

MATERIAL_CONFIRMATION_IDS = frozenset(
    {
        "confirm-governing-surfaces",
        "confirm-eligibility-vs-merit",
        "confirm-roster-vs-participation",
        "confirm-decision-authority",
        "confirm-conflict-status",
        "confirm-finding-epistemics",
        "confirm-unavailable-vs-protected",
        "confirm-material-ai-influence",
        "confirm-production-anchor-claim",
        "confirm-no-contemporaneous-gdi-claim",
    }
)

FORBIDDEN_OPERATIONS = frozenset(
    {
        "merit_score",
        "recommend_approval",
        "recommend_rejection",
        "infer_eligibility",
        "resolve_conflicts",
        "invent_quorum",
        "assign_authority",
        "ai_as_authority",
        "unknown_to_pass",
    }
)


class AdapterError(ValueError):
    """Raised when an adapter refuses an unsafe or incomplete mapping."""


class ProvenanceKind(str, Enum):
    DIRECT = "direct"
    DERIVED = "derived"
    INTERPRETIVE = "interpretive"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FieldProvenance:
    kind: str
    source_path: str | None = None
    derivation_rule_id: str | None = None
    mapping_rule_id: str | None = None
    operator_confirmed: bool = False
    confirmation_id: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in PROVENANCE_KINDS:
            raise AdapterError(f"invalid provenance kind: {self.kind}")


@dataclass
class MappedField:
    path: str
    value: Any
    provenance: FieldProvenance
    material: bool = False


@dataclass
class OperatorConfirmation:
    confirmation_id: str
    confirmed: bool
    operator: str | None = None
    notes: str | None = None


@dataclass
class DraftRecord:
    profile_id: str
    mapping_version: str
    fields: list[MappedField] = field(default_factory=list)
    confirmations: list[OperatorConfirmation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profileId": self.profile_id,
            "mappingVersion": self.mapping_version,
            "fields": [
                {
                    "path": f.path,
                    "value": f.value,
                    "material": f.material,
                    "provenance": asdict(f.provenance),
                }
                for f in self.fields
            ],
            "confirmations": [asdict(c) for c in self.confirmations],
            "warnings": list(self.warnings),
        }


def load_profile(profile_id: str, profiles_dir: Path | None = None) -> dict[str, Any]:
    root = profiles_dir or Path(__file__).resolve().parents[1] / "profiles"
    path = root / f"{profile_id}.json"
    if not path.is_file():
        raise AdapterError(f"unknown profile: {profile_id}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def refuse_forbidden_operation(operation: str) -> None:
    """Hard refuse substantive judgment operations."""
    if operation in FORBIDDEN_OPERATIONS:
        raise AdapterError(
            f"adapter refuses operation '{operation}': adapters marshal evidence only"
        )


def require_confirmation(
    confirmations: list[OperatorConfirmation],
    confirmation_id: str,
    *,
    material: bool,
) -> None:
    if not material:
        return
    matched = [c for c in confirmations if c.confirmation_id == confirmation_id]
    if not matched or not matched[0].confirmed:
        raise AdapterError(
            f"material mapping requires operator confirmation: {confirmation_id}"
        )


def map_field(
    *,
    path: str,
    value: Any,
    provenance: FieldProvenance,
    material: bool,
    confirmations: list[OperatorConfirmation],
) -> MappedField:
    if provenance.kind == "unknown" and value not in (None, "unknown", ""):
        # Unknown provenance may accompany an explicit unknown marker, not a
        # fabricated pass/fail disposition.
        if value in ("pass", "fail", "approved", "rejected"):
            raise AdapterError(
                "refusing to convert unknown provenance into pass/fail disposition"
            )
    if material:
        if provenance.kind in {"interpretive", "derived", "unknown"}:
            conf_id = provenance.confirmation_id
            if not conf_id:
                raise AdapterError(
                    f"material field '{path}' with provenance '{provenance.kind}' "
                    "requires confirmation_id"
                )
            require_confirmation(confirmations, conf_id, material=True)
            if not provenance.operator_confirmed:
                raise AdapterError(
                    f"material field '{path}' requires operator_confirmed=true"
                )
        elif provenance.kind == "direct" and not provenance.source_path:
            raise AdapterError(
                f"direct provenance for '{path}' requires source_path"
            )
    return MappedField(path=path, value=value, provenance=provenance, material=material)


def build_draft(
    *,
    profile_id: str,
    mapping_version: str,
    fields: list[MappedField],
    confirmations: list[OperatorConfirmation],
    profiles_dir: Path | None = None,
) -> DraftRecord:
    profile = load_profile(profile_id, profiles_dir=profiles_dir)
    required_ids = {
        item["id"]
        for item in profile.get("operatorConfirmations", [])
        if item.get("material")
    }
    confirmed = {
        c.confirmation_id for c in confirmations if c.confirmed
    }
    missing = sorted(required_ids - confirmed)
    warnings: list[str] = []
    if missing:
        # Draft may be incomplete; do not invent confirmations.
        warnings.append(
            "incomplete operator confirmations: " + ", ".join(missing)
        )
    for mapped in fields:
        if mapped.path.endswith("authorityKind") and mapped.value == "ai":
            raise AdapterError("adapter cannot assign AI as decision.authorityKind")
        if mapped.path.endswith(".participant") and mapped.value is True:
            if mapped.provenance.kind == "unknown" or not (
                mapped.provenance.operator_confirmed
                or mapped.provenance.kind == "direct"
            ):
                raise AdapterError(
                    "roster member cannot be marked participant without "
                    "direct source or operator confirmation"
                )
    return DraftRecord(
        profile_id=profile_id,
        mapping_version=mapping_version,
        fields=fields,
        confirmations=confirmations,
        warnings=warnings,
    )


def explain(draft: DraftRecord) -> list[dict[str, Any]]:
    """Return per-field explain rows for operator/auditor review."""
    rows: list[dict[str, Any]] = []
    for mapped in draft.fields:
        prov = mapped.provenance
        rows.append(
            {
                "path": mapped.path,
                "value": mapped.value,
                "material": mapped.material,
                "provenanceKind": prov.kind,
                "source": prov.source_path,
                "derivationRuleId": prov.derivation_rule_id,
                "mappingRuleId": prov.mapping_rule_id,
                "operatorConfirmed": prov.operator_confirmed,
                "confirmationId": prov.confirmation_id,
                "notes": prov.notes,
            }
        )
    return rows


def import_normalized_event(source: dict[str, Any]) -> dict[str, Any]:
    """Normalize a narrow workflow artifact into an intermediate event model.

    This does not map into a grant-decision record; mapping is a separate step
    that requires profile selection and operator confirmations.
    """
    if not isinstance(source, dict):
        raise AdapterError("source must be an object")
    event_type = source.get("eventType")
    if not event_type:
        raise AdapterError("normalized event requires eventType")
    return {
        "eventType": event_type,
        "sourceId": source.get("sourceId"),
        "capturedAt": source.get("capturedAt"),
        "payload": source.get("payload", {}),
        "accessClass": source.get("accessClass", "unknown"),
    }
