#!/usr/bin/env python3
"""Compatibility shim — implementation lives in gdi.corpus.metrics."""

from __future__ import annotations

from gdi.corpus.metrics import *  # noqa: F403
from gdi.corpus.metrics import main

if __name__ == "__main__":
    raise SystemExit(main())
