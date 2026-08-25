"""Projection package wrap — implementation lives under projection/src."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECTION_SRC = Path(__file__).resolve().parents[2] / "projection" / "src"
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
