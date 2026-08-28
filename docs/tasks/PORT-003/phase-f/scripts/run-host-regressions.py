#!/usr/bin/env python3
"""Run the complete PORT-003 Phase F nonphysical regression gate."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import sha256_file, write_canonical  # noqa: E402

OUTPUT = ROOT / "docs/tasks/PORT-003/phase-f/evidence/host-regression-results.yaml"
VIDEO = ROOT / "vdp/video"
COMPATIBILITY_FLAGS = [
    "-DFABGL_EMULATED",
    "-I", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat"),
    "-I", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat"),
    "-I", str(VIDEO),
    "-I", str(ROOT / "vdp/vendor/vdp-gl/src"),
    "-include", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat/freertos/task.h"),
    "-include", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat/host_preinclude.hpp"),
]
CONTROLLER_SOURCES = [
    "vdp/video/extender/display/logical_frame_service.cpp",
    "vdp/video/extender/display/native_pixel_codec.cpp",
    "vdp/video/extender/display/plane_storage.cpp",
    "vdp/video/extender/display/palette_state.cpp",
    "vdp/video/extender/display/presentation_compositor.cpp",
    "vdp/video/extender/display/presentation_snapshot_pool.cpp",
    "vdp/video/extender/display/p4_display_controller.cpp",
    "vdp/video/extender/port/fabutils_port.cpp",
    "vdp/vendor/vdp-gl/src/canvas.cpp",
    "vdp/vendor/vdp-gl/src/displaycontroller.cpp",
]


def normalized(command: list[str]) -> list[str]:
    root = str(ROOT) + "/"
    return [
        "<project-root>" if part == str(ROOT)
        else part.removeprefix(root) if part.startswith(root)
        else part
        for part in command
    ]


def run(command: list[str], label: str, timeout: int = 300,
        environment: dict[str, str] | None = None) -> dict[str, Any]:
    print(f"[{label}]", flush=True)
    process = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=environment,
    )
    if process.returncode != 0:
        print(process.stdout, file=sys.stderr)
        print(process.stderr, file=sys.stderr)
        raise RuntimeError(f"{label} failed with status {process.returncode}")
    result = {
        "id": label,
        "status": "pass",
        "command": normalized(command),
        "output": process.stdout.splitlines(),
    }
    test_count = re.search(r"Ran (\d+) tests?", process.stderr)
    if test_count is not None:
        result["test_count"] = int(test_count.group(1))
    return result


def compile_and_run(binary: Path, sources: list[str], label: str,
                    extra_flags: list[str] | None = None) -> dict[str, Any]:
    command = [
        "g++", "-std=c++17", "-O1", "-g", "-pthread",
        "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
        "-ffunction-sections", "-fdata-sections",
        *(extra_flags or []),
        *(str(ROOT / source) for source in sources),
        "-Wl,--gc-sections", "-o", str(binary),
    ]
    run(command, f"{label}-compile")
    environment = os.environ.copy()
    environment["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1"
    environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
    execution = run([str(binary)], label, timeout=120, environment=environment)
    execution["command"] = ["<temporary-host-binary>"]
    execution["sources"] = [
        {"path": source, "sha256": sha256_file(ROOT / source)}
        for source in sources
    ]
    return execution


def main() -> int:
    python = sys.executable
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="port-003-phase-f-host-") as directory:
        temporary = Path(directory)
        results.append(compile_and_run(
            temporary / "snapshot-pool-tests",
            [
                "vdp/video/extender/display/presentation_snapshot_pool.cpp",
                "docs/tasks/PORT-003/phase-f/tests/snapshot_pool_tests.cpp",
            ],
            "phase-f-snapshot-pool",
            ["-Wall", "-Wextra", "-Werror", "-pedantic", "-I", str(VIDEO)],
        ))
        results.append(compile_and_run(
            temporary / "snapshot-controller-tests",
            [
                "docs/tasks/PORT-003/phase-f/tests/snapshot_controller_tests.cpp",
                *CONTROLLER_SOURCES,
            ],
            "phase-f-snapshot-controller",
            ["-w", *COMPATIBILITY_FLAGS],
        ))

    scripted = [
        ([python, "docs/tasks/PORT-003/phase-f/scripts/run-network-host-tests.py",
          "--project-root", str(ROOT)], "phase-f-network-provider"),
        ([python, "docs/tasks/PORT-003/phase-f/scripts/run-browser-tests.py"],
         "phase-f-real-browser"),
        ([python, "docs/tasks/PORT-003/phase-f/scripts/check-snapshot-model.py",
          "--input", "docs/tasks/PORT-003/phase-f/fixtures/snapshot-pool-model.yaml",
          "--output", "docs/tasks/PORT-003/phase-f/evidence/snapshot-model-check.yaml",
          "--depth", "12"],
         "phase-f-independent-snapshot-model"),
        ([python, "docs/tasks/PORT-003/phase-f/scripts/check-evf1-contract.py",
          "--input", "docs/tasks/PORT-003/phase-f/fixtures/evf1-contract.yaml",
          "--output", "docs/tasks/PORT-003/phase-f/evidence/evf1-contract-check.yaml"],
         "phase-f-independent-evf1-contract"),
        ([python, "docs/tasks/PORT-003/phase-f/scripts/check-network-contract.py",
          "--input", "docs/tasks/PORT-003/phase-f/network-service-contract.yaml",
          "--output", "docs/tasks/PORT-003/phase-f/evidence/network-contract-check.yaml"],
         "phase-f-independent-network-contract"),
        ([python, "docs/tasks/PORT-003/phase-f/scripts/check-independent-fixtures.py",
          "--input", "docs/tasks/PORT-003/phase-f/fixtures/independent-fixtures.yaml",
          "--expected-svg", "docs/tasks/PORT-003/phase-f/fixtures/visible-vdu-command-expected.svg",
          "--output", "docs/tasks/PORT-003/phase-f/evidence/independent-fixtures-check.yaml"],
         "phase-f-independent-fixtures"),
        ([python, "docs/tasks/PORT-003/phase-e/scripts/run-host-mode-tests.py"],
         "phase-a-through-e-host-matrix"),
    ]
    for command, label in scripted:
        results.append(run(command, label, timeout=600))

    for directory, label in [
        ("docs/tasks/PORT-003/phase-f/tests", "phase-f-qualification-tool-tests"),
        ("docs/dependencies/tests", "dependency-tool-tests"),
        ("docs/tasks/PORT-003/phase-a/tests", "phase-a-permanent-tests"),
        ("docs/tasks/PORT-003/phase-b/tests", "phase-b-permanent-tests"),
        ("docs/tasks/PORT-003/phase-c/tests", "phase-c-permanent-tests"),
        ("docs/tasks/PORT-003/phase-d/tests", "phase-d-permanent-tests"),
        ("docs/tasks/PORT-003/phase-e/tests", "phase-e-permanent-tests"),
    ]:
        results.append(run(
            [python, "-m", "unittest", "discover", "-s", directory, "-v"],
            label,
            timeout=300,
        ))

    compiler = subprocess.run(
        ["g++", "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    artifact = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_host_regression_results",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/run-host-regressions.py",
        "diagnostic_status": "host sanitizer, real-browser, contract, and Phase A-E regressions; no target runtime or hardware claim",
        "python": sys.version.splitlines()[0],
        "compiler": compiler,
        "coverage": {
            "null_or_disconnected_consumer": ["phase-f-snapshot-pool", "phase-f-network-provider"],
            "fast_consumer": ["phase-f-network-provider"],
            "slow_consumer_and_latest_collapse": ["phase-f-snapshot-pool", "phase-f-network-provider"],
            "slot_exhaustion_and_allocation_failure": ["phase-f-snapshot-pool"],
            "mode_changes_through_1024x768": ["phase-f-snapshot-controller", "phase-a-through-e-host-matrix"],
            "malformed_frames": ["phase-f-real-browser", "phase-f-independent-fixtures"],
            "sequence_rollover": ["phase-f-real-browser", "phase-f-independent-fixtures"],
            "repeated_start_stop": ["phase-f-network-provider", "phase-a-through-e-host-matrix"],
            "sustained_bounded_operation": ["phase-f-snapshot-pool", "phase-f-network-provider"],
        },
        "results": results,
        "summary": {"passed": len(results), "failed": 0},
    }
    write_canonical(OUTPUT, artifact)
    print(f"Phase F host regression gate: {len(results)} gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
