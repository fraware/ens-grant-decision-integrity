#!/usr/bin/env python3
"""Compatibility shim — implementation lives in gdi.source.artifact."""

from __future__ import annotations

from gdi.source.artifact import *  # noqa: F403
from gdi.source.artifact import main

if __name__ == "__main__":
    raise SystemExit(main())
