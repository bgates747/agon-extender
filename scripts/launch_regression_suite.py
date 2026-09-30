#!/usr/bin/env python3
"""Compatibility entry point for qualification/launch_offline.py."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[1] / "qualification/launch_offline.py"),
               run_name="__main__")
