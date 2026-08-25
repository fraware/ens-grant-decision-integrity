#!/usr/bin/env python3
"""Compatibility shim — implementation lives in gdi.source.policy_pins."""

from __future__ import annotations

from gdi.source.policy_pins import *  # noqa: F403
from gdi.source.policy_pins import main

if __name__ == "__main__":
    raise SystemExit(main())
