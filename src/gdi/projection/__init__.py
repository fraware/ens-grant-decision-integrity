"""Projection package compatibility wrap.

Projection v1/v2 source remains schema-versioned under ``projection/src`` in the
repository. Release wheels carry the same files as immutable package data and
this module resolves either layout without relying on the current working tree.
"""

from __future__ import annotations

import sys

from gdi.resources import resource_path

_PROJECTION_SRC = resource_path("projection", "src")
if str(_PROJECTION_SRC) not in sys.path:
    sys.path.insert(0, str(_PROJECTION_SRC))

from project import ProjectionError as ProjectionErrorV1  # noqa: E402
from project import project_record  # noqa: E402
from project_v2 import ProjectionError as ProjectionErrorV2  # noqa: E402
from project_v2 import project_record_v2  # noqa: E402
from project_v2 import verify_projection_v2  # noqa: E402
from project_v2 import verify_withheld_v2  # noqa: E402

ProjectionError = ProjectionErrorV2

__all__ = [
    "ProjectionError",
    "ProjectionErrorV1",
    "ProjectionErrorV2",
    "project_record",
    "project_record_v2",
    "verify_projection_v2",
    "verify_withheld_v2",
]
