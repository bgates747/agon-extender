#!/usr/bin/env python3
"""Provision BUILD-001's pinned ESP-IDF tool closure under ignored project state."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
TOOL_ROOT = ROOT / "agents/build001/native-tools"
IDF = TOOL_ROOT / "esp-idf"
TOOLS = TOOL_ROOT / "espressif"
PYTHON_ENV = TOOL_ROOT / "python-env"
TAG = "v5.5.5"
COMMIT = "b774170ff46c393eeb5e495ea37936038d3f4f4f"


def main() -> None:
    TOOL_ROOT.mkdir(parents=True, exist_ok=True)
    if not IDF.exists():
        subprocess.run([
            "git", "clone", "--branch", TAG, "--depth", "1",
            "--recurse-submodules", "--shallow-submodules",
            "https://github.com/espressif/esp-idf.git", str(IDF),
        ], check=True)
    actual = subprocess.check_output(
        ["git", "-C", str(IDF), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != COMMIT:
        raise SystemExit(f"wrong ESP-IDF checkout: {actual}")
    env = os.environ.copy()
    env.update({"IDF_TOOLS_PATH": str(TOOLS),
                "IDF_PYTHON_ENV_PATH": str(PYTHON_ENV)})
    subprocess.run([str(IDF / "install.sh"), "esp32p4"], env=env, check=True)
    print(f"pinned ESP-IDF tools ready: {TOOL_ROOT}")


if __name__ == "__main__":
    main()
