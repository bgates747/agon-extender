#!/usr/bin/env python3
"""Build and run the bounded network/provider host test under sanitizers."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    video = root / "vdp" / "video"
    test = root / "docs/tasks/PORT-003/phase-f/tests/network_service_tests.cpp"
    sources = [
        video / "extender/network/opaque_message.cpp",
        video / "extender/network/browser_video_service_core.cpp",
        video / "extender/display/presentation_snapshot_pool.cpp",
        video / "extender/web/browser_video_provider.cpp",
        test,
    ]
    with tempfile.TemporaryDirectory(prefix="port-003-phase-f-network-") as tmp:
        executable = Path(tmp) / "network-service-tests"
        command = [
            "g++",
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-pthread",
            "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer",
            "-I",
            str(video),
            *map(str, sources),
            "-o",
            str(executable),
        ]
        subprocess.run(command, check=True)
        subprocess.run([str(executable)], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
