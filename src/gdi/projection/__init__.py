"""Projection package compatibility wrap.

Projection v1/v2 source remains schema-versioned under ``projection/src`` in the
repository. Release wheels carry the same files as immutable package data and
this module resolves either layout without relying on the current working tree.
"""

from __future__ import annotations

import importlib
import sys

from gdi.resources import resource_path

_PROJECTION_SRC = resource_path("projection", "src")
if str(_PROJECTION_SRC) not in sys.path:
    sys.path.insert(0, str(_PROJECTION_SRC))

_project_v1 = importlib.import_module("project")
_project_v2 = importlib.import_module("project_v2")

ProjectionErrorV1 = _project_v1.ProjectionError
project_record = _project_v1.project_record
ProjectionErrorV2 = _project_v2.ProjectionError
project_record_v2 = _project_v2.project_record_v2
verify_projection_v2 = _project_v2.verify_projection_v2
verify_withheld_v2 = _project_v2.verify_withheld_v2
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
