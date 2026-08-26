"""Locate verifier data in a source checkout or installed wheel.

The wheel installs schemas, profiles, claim registries, and compatibility source
modules under ``<sys.prefix>/ens_gdi``. Source checkouts retain their historical
repository layout. Runtime code must use this module instead of assuming either
layout.
"""

from __future__ import annotations

import os
import sysconfig
from functools import lru_cache
from pathlib import Path


class ResourceError(RuntimeError):
    """Raised when the verifier's immutable packaged data cannot be located."""


@lru_cache(maxsize=1)
def data_root() -> Path:
    override = os.environ.get("GDI_DATA_ROOT")
    if override:
        root = Path(override).expanduser().resolve()
        if root.is_dir():
            return root
        raise ResourceError(f"GDI_DATA_ROOT is not a directory: {root}")

    source_root = Path(__file__).resolve().parents[2]
    if (source_root / "schema").is_dir() and (source_root / "claims").is_dir():
        return source_root

    installed_root = Path(sysconfig.get_path("data")) / "ens_gdi"
    if (installed_root / "schema").is_dir() and (installed_root / "claims").is_dir():
        return installed_root

    raise ResourceError(
        "verifier data root not found; reinstall the package or set GDI_DATA_ROOT"
    )


def resource_path(*parts: str) -> Path:
    path = data_root().joinpath(*parts)
    if not path.exists():
        joined = "/".join(parts)
        raise ResourceError(f"required verifier resource is missing: {joined}")
    return path
