"""Phase II compatibility runtime.

The schema-versioned implementation remains under ``phase2/src``. Release wheels
carry the same source and schemas as immutable package data. This module exposes
only verification, not authority or policy selection.
"""

from __future__ import annotations

import sys
from typing import Any

from gdi.resources import resource_path


def _ensure_runtime() -> None:
    phase2_src = resource_path("phase2", "src")
    if str(phase2_src) not in sys.path:
        sys.path.insert(0, str(phase2_src))


def verify_graph_bundle(
    bundle: dict[str, Any],
    *,
    fixture_private_key_pem: str | bytes | None = None,
    trust_root_pem: str | None = None,
    trust_policy: dict[str, Any] | None = None,
) -> Any:
    """Verify one Phase II evidence graph using externally supplied trust inputs."""
    _ensure_runtime()
    from graph import verify_graph  # type: ignore[import-not-found]

    return verify_graph(
        bundle,
        fixture_private_key_pem=fixture_private_key_pem,
        trust_root_pem=trust_root_pem,
        trust_policy=trust_policy,
    )


def phase2_error_type() -> type[Exception]:
    _ensure_runtime()
    from support import Phase2Error  # type: ignore[import-not-found]

    return Phase2Error


__all__ = ["phase2_error_type", "verify_graph_bundle"]
