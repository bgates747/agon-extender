#!/usr/bin/env python3
"""Run the complete Phase E host and cross-phase regression matrix."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import sha256_file, write_canonical  # noqa: E402

OUTPUT = ROOT / "docs/tasks/PORT-003/phase-e/evidence/host-mode-results.yaml"
FIXED_SOURCES = [
    "docs/tasks/PORT-003/phase-e/tests/screen_facade_adapter_tests.cpp",
    "vdp/video/extender/display/logical_frame_service.cpp",
    "vdp/video/extender/display/native_pixel_codec.cpp",
    "vdp/video/extender/display/plane_storage.cpp",
    "vdp/video/extender/display/palette_state.cpp",
    "vdp/video/extender/display/presentation_compositor.cpp",
    "vdp/video/extender/display/presentation_snapshot_pool.cpp",
    "vdp/video/extender/display/p4_display_controller.cpp",
    "vdp/video/extender/display/screen_facade_adapter.cpp",
    "vdp/video/extender/display/cursor_position_adapter.cpp",
    "vdp/video/extender/port/fabutils_port.cpp",
    "vdp/vendor/vdp-gl/src/canvas.cpp",
    "vdp/vendor/vdp-gl/src/displaycontroller.cpp",
]
EVIDENCE = [
    "docs/tasks/PORT-003/phase-e/evidence/mode-facade-matrix-results.yaml",
    "docs/tasks/PORT-003/phase-e/evidence/official-mode-lifecycle-results.yaml",
    "docs/tasks/PORT-003/phase-e/evidence/teletext-integration-results.yaml",
    "docs/tasks/PORT-003/phase-b/evidence/host-fixture-results.yaml",
    "docs/tasks/PORT-003/phase-b/evidence/allocation-failure-results.yaml",
    "docs/tasks/PORT-003/phase-c/evidence/host-frame-results.yaml",
    "docs/tasks/PORT-003/phase-d/evidence/host-presentation-results.yaml",
]


def run_checked(command: list[str], label: str) -> dict[str, Any]:
    process = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, timeout=180
    )
    if process.returncode != 0:
        print(process.stdout, file=sys.stderr)
        print(process.stderr, file=sys.stderr)
        raise RuntimeError(f"{label} failed with status {process.returncode}")
    return {
        "id": label,
        "status": "pass",
        "command": [
            path.removeprefix(str(ROOT) + "/") if path.startswith(str(ROOT) + "/") else path
            for path in command
        ],
        "output": process.stdout.splitlines(),
    }


def main() -> int:
    compiler = subprocess.run(
        ["g++", "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    results = []
    with tempfile.TemporaryDirectory(prefix="port-003-phase-e-fixed-") as directory:
        binary = Path(directory) / "screen-facade-adapter-tests"
        compile_command = [
            "g++", "-std=c++17", "-O1", "-g", "-w",
            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-pthread",
            "-ffunction-sections", "-fdata-sections", "-DFABGL_EMULATED",
            "-I", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat"),
            "-I", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat"),
            "-I", str(ROOT / "vdp/video"),
            "-I", str(ROOT / "vdp/vendor/vdp-gl/src"),
            "-include", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat/freertos/task.h"),
            "-include", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat/host_preinclude.hpp"),
            *(str(ROOT / source) for source in FIXED_SOURCES),
            "-Wl,--gc-sections", "-o", str(binary),
        ]
        compilation = subprocess.run(compile_command, text=True, capture_output=True)
        if compilation.returncode != 0:
            diagnostics = (compilation.stdout + compilation.stderr).splitlines()
            decisive = [line for line in diagnostics if "error:" in line or "undefined reference" in line]
            print("\n".join(decisive or diagnostics[-50:]), file=sys.stderr)
            return 1
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        fixed = subprocess.run(
            [str(binary)], text=True, capture_output=True, env=environment, timeout=30
        )
        expected = [
            "modeline-depth-pass",
            "transactional-facade-pass",
            "official-frame-counter-pass",
            "cursor-position-endpoint-pass",
        ]
        if fixed.returncode != 0 or fixed.stdout.splitlines() != expected:
            print(fixed.stdout, file=sys.stderr)
            print(fixed.stderr, file=sys.stderr)
            return 1
        results.append(
            {
                "id": "fixed-facade-failure-and-endpoint-harness",
                "status": "pass",
                "output": expected,
            }
        )

    python = sys.executable
    for script, label in [
        ("docs/tasks/PORT-003/phase-e/scripts/run-mode-facade-matrix.py", "phase-e-all-mode-facade"),
        ("docs/tasks/PORT-003/phase-e/scripts/run-official-mode-lifecycle.py", "phase-e-exact-vdu-lifecycle"),
        ("docs/tasks/PORT-003/phase-e/scripts/run-teletext-integration.py", "phase-e-retained-teletext"),
        ("docs/tasks/PORT-003/phase-b/scripts/run-host-fixtures.py", "phase-b-native-renderer-regression"),
        ("docs/tasks/PORT-003/phase-c/scripts/run-host-frame-tests.py", "phase-c-logical-frame-regression"),
        ("docs/tasks/PORT-003/phase-d/scripts/run-host-presentation-tests.py", "phase-d-presentation-regression"),
    ]:
        results.append(run_checked([python, str(ROOT / script)], label))
    results.append(
        run_checked(
            [
                python, "-m", "unittest", "discover", "-s",
                str(ROOT / "docs/tasks/PORT-003/phase-e/tests"),
                "-p", "test_[mot]*.py", "-v",
            ],
            "phase-e-permanent-python-tests",
        )
    )
    for path in EVIDENCE:
        if not (ROOT / path).is_file():
            raise FileNotFoundError(path)
    artifact = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_e_host_mode_results",
        "generated_by": "docs/tasks/PORT-003/phase-e/scripts/run-host-mode-tests.py",
        "compiler": compiler,
        "diagnostic_status": "host ASan/UBSan and deterministic cross-phase regression; no target or hardware claim",
        "fixed_harness_sources": [
            {"path": source, "sha256": sha256_file(ROOT / source)}
            for source in FIXED_SOURCES
        ],
        "evidence_inputs": [
            {"path": path, "sha256": sha256_file(ROOT / path)} for path in EVIDENCE
        ],
        "results": results,
        "summary": {"passed": len(results), "failed": 0},
    }
    write_canonical(OUTPUT, artifact)
    print(f"Phase E host matrix: {len(results)} gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
