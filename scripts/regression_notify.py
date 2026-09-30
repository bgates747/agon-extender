#!/usr/bin/env python3
"""Compatibility launcher for the canonical qualification notifier."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[1] / "qualification/notify.py"),
               run_name="__main__")
