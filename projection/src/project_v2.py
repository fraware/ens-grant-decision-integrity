"""Projection v2: nested disposition with path-bound withheld commitments.

Projection v1 remains in ``project.py`` for historical verification. This module
implements ``ens-gdi/public-projection/v2`` with RFC 6901 JSON Pointer paths,
recursive disposition actions, and separate ``projectionIntegrity`` metadata.

Privacy note (equality / dictionary-attack risk)
------------------------------------------------
Withheld commitments are unsalted and deterministic:
``SHA-256(domain || 0x00 || pointer || 0x00 || JCS(subtree))``.
Identical low-entropy subtrees (booleans, small enums) produce identical digests
and are dictionary-attackable. Do not withhold tiny secrets under this algorithm
unless the disclosure profile accepts equality leakage. Optional per-path salts
are deferred; when absent, this limitation is intentional and documented.
These commitments are not Merkle proofs, ZK proofs, or selective-disclosure proofs.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rfc8785 import dumps as jcs_dumps

PROJECTION_DOMAIN_V2 = "ens-gdi/public-projection/v2"
WITHHELD_DOMAIN_V2 = "ens-gdi/withheld-subtree/v2"
COMMITMENT_ALGORITHM_V2 = "sha256-jcs-path-v2"
PROJECTION_INTEGRITY_ALGORITHM = "sha256-jcs-projection-v2"
SOURCE_DIGEST_ALGORITHM = "sha256-jcs"
REDACTION_CATEGORIES = frozenset(
    {"privacy", "security", "commercial", "legal", "contractual", "other"}
)
TERMINAL_ACTIONS = frozenset({"publish-subtree", "withhold-subtree", "drop-by-profile"})
ALL_ACTIONS = TERMINAL_ACTIONS | {"descend"}

# Generated projection fields must never be accepted from the confidential source.
GENERATED_PUBLIC_KEYS = frozenset(
    {"withheldCommitments", "projectionIntegrity", "sourceIntegrityDisposition"}
)

_POINTER_TOKEN_RE = re.compile(r"^([^/~]|~0|~1)*$")


class ProjectionError(Exception):
    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ProjectionResult:
    public_record: dict[str, Any]
    projection_digest: str
    withheld_commitments: dict[str, dict[str, Any]]
    source_record_digest: str
    projection_spec_digest: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "publicRecord": self.public_record,
            "projectionDigestSha256": self.projection_digest,
            "withheldCommitments": self.withheld_commitments,
            "sourceRecordDigest": self.source_record_digest,
            "projectionSpecDigest": self.projection_spec_digest,
        }


def _canonical_bytes(value: Any) -> bytes:
    encoded = jcs_dumps(value)
    if isinstance(encoded, bytes):
        return encoded
    return encoded.encode("utf-8")


def digest_sha256_jcs(value: Any) -> str:
    return f"{SOURCE_DIGEST_ALGORITHM}:{hashlib.sha256(_canonical_bytes(value)).hexdigest()}"


def parse_json_pointer(pointer: str) -> list[str]:
    """Parse an RFC 6901 JSON Pointer into unescaped reference tokens."""
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise ProjectionError(f"malformed JSON Pointer (must start with /): {pointer!r}", code="PROJ201")
    tokens: list[str] = []
    # Split on '/' but keep empty tokens between consecutive slashes.
    parts = pointer.split("/")[1:]
    for part in parts:
        if not _POINTER_TOKEN_RE.fullmatch(part):
            raise ProjectionError(f"malformed JSON Pointer token in {pointer!r}", code="PROJ201")
        tokens.append(part.replace("~1", "/").replace("~0", "~"))
    return tokens


def format_json_pointer(tokens: list[str]) -> str:
    if not tokens:
        return ""
    return "/" + "/".join(token.replace("~", "~0").replace("/", "~1") for token in tokens)


def resolve_pointer(document: Any, pointer: str) -> Any:
    tokens = parse_json_pointer(pointer)
    current = document
    for index, token in enumerate(tokens):
        if isinstance(current, list):
            # Arrays are atomic in v2; only the array itself may be addressed.
            raise ProjectionError(
                f"per-index array addressing is unsupported in projection v2: {pointer}",
                code="PROJ214",
            )
        if not isinstance(current, dict):
            raise ProjectionError(f"path not found: {pointer}", code="PROJ202")
        if token not in current:
            raise ProjectionError(f"path not found: {pointer}", code="PROJ202")
        current = current[token]
        # Reject any pointer that continues into an array element.
        remaining = tokens[index + 1 :]
        if isinstance(current, list) and remaining:
            raise ProjectionError(
                f"per-index array addressing is unsupported in projection v2: {pointer}",
                code="PROJ214",
            )
    return current


def path_exists(document: Any, pointer: str) -> bool:
    try:
        resolve_pointer(document, pointer)
        return True
    except ProjectionError as exc:
        if exc.code in {"PROJ202"}:
            return False
        raise


def withheld_digest_v2(*, pointer: str, subtree: Any) -> str:
    """Path-bound withheld commitment digest (lowercase hex without algorithm prefix)."""
    material = (
        WITHHELD_DOMAIN_V2.encode("utf-8")
        + b"\x00"
        + pointer.encode("utf-8")
        + b"\x00"
        + _canonical_bytes(subtree)
    )
    return hashlib.sha256(material).hexdigest()


def format_withheld_commitment(digest_hex: str) -> str:
    return f"{COMMITMENT_ALGORITHM_V2}:{digest_hex.lower()}"


def parse_withheld_commitment(value: str) -> str:
    prefix = f"{COMMITMENT_ALGORITHM_V2}:"
    if not value.startswith(prefix):
        raise ProjectionError(
            f"withheld commitment algorithm mismatch; expected {COMMITMENT_ALGORITHM_V2}",
            code="PROJ215",
        )
    digest = value[len(prefix) :]
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ProjectionError("malformed withheld commitment digest", code="PROJ215")
    return digest


def _validate_rule(rule: dict[str, Any], *, index: int) -> None:
    if not isinstance(rule, dict):
        raise ProjectionError(f"rules[{index}] must be an object", code="PROJ203")
    path = rule.get("path")
    action = rule.get("action")
    if not isinstance(path, str):
        raise ProjectionError(f"rules[{index}].path must be a string", code="PROJ203")
    if path != "":
        parse_json_pointer(path)  # validates
    if action not in ALL_ACTIONS:
        raise ProjectionError(f"unknown projection action {action!r}", code="PROJ204")
    if action == "withhold-subtree":
        category = rule.get("category")
        if category not in REDACTION_CATEGORIES:
            raise ProjectionError(f"invalid withhold category {category!r}", code="PROJ205")
    if action == "drop-by-profile":
        if not rule.get("profileRuleId"):
            raise ProjectionError("drop-by-profile requires profileRuleId", code="PROJ206")
        if not rule.get("explanation"):
            raise ProjectionError("drop-by-profile requires explanation", code="PROJ206")
    when_absent = rule.get("whenAbsent")
    if when_absent is not None and when_absent != "ignore":
        raise ProjectionError(f"unsupported whenAbsent value {when_absent!r}", code="PROJ207")


def _index_rules(rules: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for index, rule in enumerate(rules):
        _validate_rule(rule, index=index)
        path = rule["path"]
        # Normalize empty vs absent: keep as provided after pointer validation.
        if path in indexed:
            raise ProjectionError(f"duplicate projection pointer: {path}", code="PROJ208")
        indexed[path] = rule
    return indexed


def _child_pointer(parent: str, key: str) -> str:
    escaped = key.replace("~", "~0").replace("/", "~1")
    if parent == "":
        return f"/{escaped}"
    return f"{parent}/{escaped}"


def _has_descendant_rule(path: str, rules: dict[str, dict[str, Any]]) -> bool:
    prefix = path + "/" if path != "" else "/"
    if path == "":
        return any(candidate != "" for candidate in rules)
    return any(candidate.startswith(prefix) for candidate in rules if candidate != path)


def _immediate_child_keys(node: Any) -> list[str]:
    if isinstance(node, dict):
        return list(node.keys())
    return []


def _project_node(
    *,
    source_node: Any,
    path: str,
    rules: dict[str, dict[str, Any]],
    withheld: dict[str, dict[str, Any]],
    drops: list[dict[str, Any]],
) -> Any | None:
    """Return published subtree value, or None when omitted (withhold/drop)."""
    rule = rules.get(path)
    if rule is None:
        raise ProjectionError(f"missing disposition rule for path {path or '/'}", code="PROJ209")

    action = rule["action"]
    if action in TERMINAL_ACTIONS and _has_descendant_rule(path, rules):
        raise ProjectionError(
            f"terminal action {action} at {path or '/'} cannot have descendant rules",
            code="PROJ210",
        )

    if action == "publish-subtree":
        if isinstance(source_node, dict):
            # Reject rules that try to both publish whole object and also address children.
            return copy.deepcopy(source_node)
        return copy.deepcopy(source_node)

    if action == "withhold-subtree":
        digest = withheld_digest_v2(pointer=path, subtree=source_node)
        meta: dict[str, Any] = {
            "path": path,
            "category": rule["category"],
            "algorithm": COMMITMENT_ALGORITHM_V2,
            "commitment": format_withheld_commitment(digest),
            "commitmentDigest": digest,
        }
        if rule.get("explanation"):
            meta["explanation"] = rule["explanation"]
        if rule.get("profileRuleId"):
            meta["profileRuleId"] = rule["profileRuleId"]
        withheld[path] = meta
        return None

    if action == "drop-by-profile":
        drops.append(
            {
                "path": path,
                "profileRuleId": rule["profileRuleId"],
                "explanation": rule["explanation"],
            }
        )
        return None

    # descend
    if isinstance(source_node, list):
        raise ProjectionError(
            f"descend into arrays is unsupported; treat arrays as atomic at {path}",
            code="PROJ214",
        )
    if not isinstance(source_node, dict):
        raise ProjectionError(
            f"descend requires an object at {path or '/'}; arrays are atomic",
            code="PROJ211",
        )

    out: dict[str, Any] = {}
    for key in sorted(source_node.keys()):
        child_path = _child_pointer(path, key)
        child_rule = rules.get(child_path)
        if child_rule is None:
            raise ProjectionError(
                f"incomplete disposition: missing rule for present child {child_path}",
                code="PROJ209",
            )
        child_value = _project_node(
            source_node=source_node[key],
            path=child_path,
            rules=rules,
            withheld=withheld,
            drops=drops,
        )
        if child_value is not None:
            out[key] = child_value
    return out


def _check_absent_optional_rules(source: dict[str, Any], rules: dict[str, dict[str, Any]]) -> None:
    for path, rule in rules.items():
        if path == "":
            continue
        if path_exists(source, path):
            continue
        if rule.get("whenAbsent") == "ignore":
            continue
        raise ProjectionError(
            f"rule targets absent path without whenAbsent=ignore: {path}",
            code="PROJ212",
        )


def _reject_generated_keys_from_source(confidential: dict[str, Any]) -> None:
    overlap = GENERATED_PUBLIC_KEYS & set(confidential)
    if overlap:
        raise ProjectionError(
            "confidential source must not supply generated projection fields: "
            + ", ".join(sorted(overlap)),
            code="PROJ216",
        )


def project_record_v2(confidential: dict[str, Any], spec: dict[str, Any]) -> ProjectionResult:
    """Apply a projection v2 spec deterministically to a confidential record."""
    if not isinstance(confidential, dict):
        raise ProjectionError("confidential record must be a JSON object", code="PROJ217")
    if spec.get("specVersion") != "2":
        raise ProjectionError("unsupported projection specVersion for v2 engine", code="PROJ218")
    if spec.get("domain") != PROJECTION_DOMAIN_V2:
        raise ProjectionError("projection domain mismatch for v2", code="PROJ219")
    profile_id = spec.get("profileId")
    if not isinstance(profile_id, str) or not profile_id:
        raise ProjectionError("projection v2 requires profileId", code="PROJ220")

    _reject_generated_keys_from_source(confidential)

    rules_list = spec.get("rules")
    if not isinstance(rules_list, list) or not rules_list:
        raise ProjectionError("projection v2 rules must be a non-empty array", code="PROJ221")
    rules = _index_rules(rules_list)
    _check_absent_optional_rules(confidential, rules)

    root_rule = rules.get("")
    if root_rule is None:
        # Implicit root descend: every top-level key must have a rule.
        root_action = "descend"
    else:
        root_action = root_rule["action"]

    withheld: dict[str, dict[str, Any]] = {}
    drops: list[dict[str, Any]] = []

    if root_action == "descend" and root_rule is None:
        projected_root = _project_node(
            source_node=confidential,
            path="",
            rules={**rules, "": {"path": "", "action": "descend"}},
            withheld=withheld,
            drops=drops,
        )
    else:
        projected_root = _project_node(
            source_node=confidential,
            path="",
            rules=rules,
            withheld=withheld,
            drops=drops,
        )

    if not isinstance(projected_root, dict):
        raise ProjectionError("projection v2 public output must be an object", code="PROJ222")

    # Ensure no generated keys leaked from publish-subtree of the whole root.
    for key in GENERATED_PUBLIC_KEYS:
        projected_root.pop(key, None)

    source_integrity_disposition: dict[str, Any] | None = None
    if "/integrity" in withheld:
        source_integrity_disposition = {
            "action": "withheld-subtree",
            "commitment": withheld["/integrity"]["commitment"],
        }
    elif any(item["path"] == "/integrity" for item in drops):
        source_integrity_disposition = {
            "action": "drop-by-profile",
            "profileRuleId": next(item["profileRuleId"] for item in drops if item["path"] == "/integrity"),
        }
    elif "integrity" in projected_root:
        source_integrity_disposition = {"action": "publish-subtree"}

    public = projected_root
    if withheld:
        public["withheldCommitments"] = {key: withheld[key] for key in sorted(withheld)}
    if source_integrity_disposition is not None:
        public["sourceIntegrityDisposition"] = source_integrity_disposition

    source_record_digest = digest_sha256_jcs(confidential)
    projection_spec_digest = digest_sha256_jcs(spec)
    withheld_for_envelope = {
        key: withheld[key]["commitment"] for key in sorted(withheld)
    }

    # Envelope binds public record *before* projectionIntegrity insertion.
    envelope = {
        "domain": PROJECTION_DOMAIN_V2,
        "specVersion": "2",
        "profileId": profile_id,
        "recordId": confidential.get("recordId"),
        "sourceRecordDigest": source_record_digest,
        "projectionSpecDigest": projection_spec_digest,
        "publicRecord": public,
        "withheldCommitments": withheld_for_envelope,
    }
    projection_digest = hashlib.sha256(_canonical_bytes(envelope)).hexdigest()
    public["projectionIntegrity"] = {
        "algorithm": PROJECTION_INTEGRITY_ALGORITHM,
        "digest": projection_digest,
        "sourceRecordDigest": source_record_digest,
        "projectionSpecDigest": projection_spec_digest,
        "profileId": profile_id,
    }

    return ProjectionResult(
        public_record=public,
        projection_digest=projection_digest,
        withheld_commitments={key: withheld[key] for key in sorted(withheld)},
        source_record_digest=source_record_digest,
        projection_spec_digest=projection_spec_digest,
    )


def verify_projection_v2(
    confidential: dict[str, Any],
    spec: dict[str, Any],
    public: dict[str, Any],
) -> dict[str, Any]:
    """Recompute projection and compare digests / public payload (fail closed)."""
    expected = project_record_v2(confidential, spec)
    integrity = public.get("projectionIntegrity")
    if not isinstance(integrity, dict):
        raise ProjectionError("public record missing projectionIntegrity", code="PROJ223")
    if integrity.get("algorithm") != PROJECTION_INTEGRITY_ALGORITHM:
        raise ProjectionError("projectionIntegrity algorithm mismatch", code="PROJ224")
    if integrity.get("digest") != expected.projection_digest:
        raise ProjectionError("projectionIntegrity digest mismatch", code="PROJ225")
    if integrity.get("sourceRecordDigest") != expected.source_record_digest:
        raise ProjectionError("sourceRecordDigest mismatch", code="PROJ226")
    if integrity.get("projectionSpecDigest") != expected.projection_spec_digest:
        raise ProjectionError("projectionSpecDigest mismatch", code="PROJ227")

    # Compare public records excluding projectionIntegrity which we already checked.
    left = copy.deepcopy(public)
    right = copy.deepcopy(expected.public_record)
    left.pop("projectionIntegrity", None)
    right.pop("projectionIntegrity", None)
    if _canonical_bytes(left) != _canonical_bytes(right):
        raise ProjectionError("public record does not match recomputed projection", code="PROJ228")
    return {
        "ok": True,
        "projectionDigestSha256": expected.projection_digest,
        "sourceRecordDigest": expected.source_record_digest,
        "projectionSpecDigest": expected.projection_spec_digest,
        "nonClaims": [
            "Projection integrity binds source bytes, spec, and public output; it does not prove redaction legitimacy.",
            "Withheld commitments are path-bound digests, not selective-disclosure proofs.",
            "Unsalted withheld digests may leak equality of low-entropy values.",
        ],
    }


def verify_withheld_v2(
    *,
    public: dict[str, Any],
    path: str,
    revealed_subtree: Any,
) -> dict[str, Any]:
    parse_json_pointer(path)
    commitments = public.get("withheldCommitments")
    if not isinstance(commitments, dict) or path not in commitments:
        raise ProjectionError(f"no withheld commitment for path {path}", code="PROJ229")
    meta = commitments[path]
    expected_raw = meta.get("commitment") or (
        f"{meta.get('algorithm', COMMITMENT_ALGORITHM_V2)}:{meta.get('commitmentDigest', '')}"
    )
    expected_digest = parse_withheld_commitment(str(expected_raw))
    actual = withheld_digest_v2(pointer=path, subtree=revealed_subtree)
    if actual != expected_digest:
        raise ProjectionError("revealed subtree does not reopen withheld commitment", code="PROJ230")
    return {
        "ok": True,
        "path": path,
        "commitment": format_withheld_commitment(actual),
        "nonClaims": [
            "Reopening a withheld digest proves only that the revealed subtree matches the path-bound commitment.",
            "It does not prove source completeness, redaction basis legitimacy, or uniqueness of the confidential record.",
        ],
    }


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def detect_spec_version(spec: dict[str, Any]) -> str:
    version = str(spec.get("specVersion", ""))
    if version in {"1", "2"}:
        return version
    raise ProjectionError(f"unsupported projection specVersion {version!r}", code="PROJ231")
