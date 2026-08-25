#!/usr/bin/env python3
"""Compatibility shim — implementation lives in gdi.corpus.study_status."""

from __future__ import annotations

from gdi.corpus.study_status import *  # noqa: F403
from gdi.corpus.study_status import main

if __name__ == "__main__":
    raise SystemExit(main())
