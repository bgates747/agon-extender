#!/usr/bin/env python3
"""Compile and run the production P4 data-plane core under host sanitizers."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[5]
COMPILE_TIMEOUT_SECONDS = 120
RUN_TIMEOUT_SECONDS = 30
TIMEOUT_EXIT_STATUS = 124


def main() -> int:
    sources = [
        ROOT / "vdp/video/extender/transport/p4_parallel_data_plane.cpp",
        ROOT / "vdp/video/extender/transport/extender_vdp_stream.cpp",
        ROOT / (
            "docs/tasks/PORT-008/production-equivalence/tests/"
            "p4_data_plane_tests.cpp"
        ),
    ]
    with tempfile.TemporaryDirectory(
        prefix="port-008-p4-data-plane-"
    ) as temporary:
        binary = Path(temporary) / "p4-data-plane-tests"
        command = [
            os.environ.get("CXX", "g++"),
            "-std=c++17",
            "-O1",
            "-g",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-pthread",
            "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer",
            "-I",
            str(
                ROOT
                / "docs/tasks/PORT-008/production-equivalence/tests/compat"
            ),
            "-I",
            str(ROOT / "vdp/video"),
            *(str(source) for source in sources),
            "-o",
            str(binary),
        ]
        try:
            compile_result = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=COMPILE_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            sys.stderr.write(
                "p4-production-data-plane: host compile timed out after "
                f"{COMPILE_TIMEOUT_SECONDS} seconds\n"
            )
            return TIMEOUT_EXIT_STATUS
        if compile_result.returncode != 0:
            sys.stderr.write(compile_result.stdout)
            sys.stderr.write(compile_result.stderr)
            return compile_result.returncode

        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        try:
            run_result = subprocess.run(
                [str(binary)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                env=environment,
                check=False,
                timeout=RUN_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            sys.stderr.write(
                "p4-production-data-plane: host test timed out after "
                f"{RUN_TIMEOUT_SECONDS} seconds\n"
            )
            return TIMEOUT_EXIT_STATUS
        sys.stdout.write(run_result.stdout)
        sys.stderr.write(run_result.stderr)
        return run_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
