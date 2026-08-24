#!/usr/bin/env python3
"""Build and execute retained Teletext over the P4 facade and Canvas."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import sha256_file, write_canonical  # noqa: E402


SOURCES = [
    "docs/tasks/PORT-003/phase-e/tests/teletext_integration_tests.cpp",
    "vdp/video/extender/display/logical_frame_service.cpp",
    "vdp/video/extender/display/native_pixel_codec.cpp",
    "vdp/video/extender/display/plane_storage.cpp",
    "vdp/video/extender/display/palette_state.cpp",
    "vdp/video/extender/display/presentation_compositor.cpp",
    "vdp/video/extender/display/p4_display_controller.cpp",
    "vdp/video/extender/display/screen_facade_adapter.cpp",
    "vdp/video/extender/display/screen_facade_p4_binding.cpp",
    "vdp/video/extender/display/cursor_position_adapter.cpp",
    "vdp/video/extender/port/fabutils_port.cpp",
    "vdp/vendor/vdp-gl/src/canvas.cpp",
    "vdp/vendor/vdp-gl/src/displaycontroller.cpp",
]
SOURCE_INPUTS = [
    "vdp/video/agon_screen.h",
    "vdp/video/agon_ttxt.h",
    "vdp/video/ttxtfont.h",
    "vdp/video/agon_palette.h",
]


def main() -> int:
    output = ROOT / "docs/tasks/PORT-003/phase-e/evidence/teletext-integration-results.yaml"
    compiler = subprocess.run(
        ["g++", "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    command = [
        "g++", "-std=c++17", "-O1", "-g", "-w",
        "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-pthread",
        "-ffunction-sections", "-fdata-sections", "-DFABGL_EMULATED",
        "-I", str(ROOT / "docs/tasks/PORT-003/phase-e/tests/compat"),
        "-I", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat"),
        "-I", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat"),
        "-I", str(ROOT / "vdp/video"),
        "-I", str(ROOT / "vdp/vendor/vdp-gl/src"),
        "-include", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat/freertos/task.h"),
        "-include", str(ROOT / "docs/tasks/PORT-003/phase-e/tests/compat/host_preinclude.hpp"),
        *(str(ROOT / source) for source in SOURCES),
        "-Wl,--gc-sections",
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix="port-003-phase-e-teletext-") as directory:
        binary = Path(directory) / "teletext-integration"
        compile_process = subprocess.run(
            [*command, "-o", str(binary)], text=True, capture_output=True
        )
        if compile_process.returncode != 0:
            diagnostics = (compile_process.stdout + compile_process.stderr).splitlines()
            decisive = [
                line for line in diagnostics
                if "error:" in line or "undefined reference" in line or "collect2:" in line
            ]
            print("\n".join(decisive or diagnostics[-50:]), file=sys.stderr)
            return 1
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        expected = {
            "success": ["teletext-init-pass", "teletext-exit-pass"],
            "failure": ["teletext-allocation-failure-pass"],
        }
        for scenario, expected_lines in expected.items():
            process = subprocess.run(
                [str(binary), scenario], text=True, capture_output=True,
                env=environment, timeout=20
            )
            lines = process.stdout.splitlines()
            status = "pass" if process.returncode == 0 and lines == expected_lines else "fail"
            results.append(
                {
                    "id": scenario,
                    "status": status,
                    "output": lines,
                    "returncode": process.returncode,
                    "stderr": process.stderr.strip(),
                }
            )
    artifact = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_e_teletext_integration_results",
        "generated_by": "docs/tasks/PORT-003/phase-e/scripts/run-teletext-integration.py",
        "compiler": compiler,
        "sanitizers": ["address", "undefined"],
        "leak_sanitizer": "disabled: retained Teletext owns process-lifetime global buffers and exposes no teardown API",
        "production_and_harness_sources": [
            {"path": source, "sha256": sha256_file(ROOT / source)} for source in SOURCES
        ],
        "retained_header_inputs": [
            {"path": source, "sha256": sha256_file(ROOT / source)}
            for source in SOURCE_INPUTS
        ],
        "results": results,
        "summary": {
            "passed": sum(result["status"] == "pass" for result in results),
            "failed": sum(result["status"] != "pass" for result in results),
        },
    }
    write_canonical(output, artifact)
    if artifact["summary"]["failed"]:
        for result in results:
            if result["status"] != "pass":
                print(f"{result['id']}: rc={result['returncode']} output={result['output']} stderr={result['stderr']}", file=sys.stderr)
        return 1
    print("retained Teletext: init, exit, and allocation failure passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
