#!/usr/bin/env python3
"""Compile the Phase C host harness and compare production traces to fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import load_data, sha256_file, write_canonical  # noqa: E402


def compile_checked(command: list[str], label: str) -> None:
    """Keep inherited-header warning volume out of routine qualification output."""
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode == 0:
        return
    # vdp-gl's intentionally retained GNU extensions produce hundreds of host
    # diagnostics. The useful compile/link failure is at the end.
    diagnostic = (result.stdout + result.stderr).splitlines()
    decisive = [
        line for line in diagnostic
        if "error:" in line or "undefined reference" in line
        or "multiple definition" in line or "collect2:" in line
    ]
    print("\n".join(decisive or diagnostic[-40:]), file=sys.stderr)
    raise RuntimeError(f"{label} compilation failed with status {result.returncode}")


def command_for(fixture: dict[str, Any]) -> tuple[str, int]:
    initial = fixture["initial"]
    budgets = {int(op.get("budget", 64)) for op in fixture["operations"] if op["op"] == "service"}
    budget = budgets.pop() if budgets else 64
    if budgets:
        raise ValueError(f"{fixture['id']}: varying service budgets are unsupported")
    lines = [f"INIT {int(initial.get('double_buffered', False))} {int(initial.get('frame_counter', 0))} {budget}"]
    submitted = 0
    for op in fixture["operations"]:
        name = op["op"]
        if name == "submit":
            if not initial.get("double_buffered", False) or op["kind"] == "swap":
                submitted += 1
            lines.append(f"SUBMIT {op['kind']} {int(op.get('dynamic', False))}")
        elif name == "tick": lines.append(f"TICK {int(op.get('count', 1))}")
        elif name == "service": lines.append(f"SERVICE {int(op.get('budget', 64))}")
        elif name == "start-one": lines.append("START_ONE")
        elif name == "finish-one": lines.append("FINISH_ONE")
        elif name == "wait": lines.append(f"WAIT {int(op.get('sequence', submitted))}")
        elif name == "write-frame-counter": lines.append(f"WRITE_FRAME {int(op['value'])}")
        elif name == "register": lines.append(f"REGISTER {op['consumer']}")
        elif name == "consume": lines.append(f"CONSUME {op['consumer']}")
        elif name == "disconnect": lines.append(f"DISCONNECT {op['consumer']}")
        elif name == "reconnect": lines.append(f"RECONNECT {op['consumer']}")
        elif name == "stop": lines.append("STOP")
        else: raise ValueError(f"{fixture['id']}: unknown operation {name}")
    lines.append("END")
    return "\n".join(lines) + "\n", budget


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", default="g++")
    parser.add_argument("--fixtures", type=Path, default=ROOT / "docs/tasks/PORT-003/phase-c/fixtures/frame-traces.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/tasks/PORT-003/phase-c/evidence/host-frame-results.yaml")
    args = parser.parse_args()
    data = load_data(args.fixtures.resolve())
    sources = [
        ROOT / "docs/tasks/PORT-003/phase-c/tests/logical_frame_service_tests.cpp",
        ROOT / "vdp/video/extender/display/logical_frame_service.cpp",
    ]
    failures: list[dict[str, Any]] = []
    passes: list[str] = []
    controller_output: list[str] = []
    stress_output: list[str] = []
    with tempfile.TemporaryDirectory(prefix="agon-extender-phase-c-") as temporary:
        binary = Path(temporary) / "logical-frame-tests"
        compile_checked([
            args.compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-pthread",
            "-I", str(ROOT / "vdp/video"), *(str(source) for source in sources),
            "-o", str(binary),
        ], "logical frame harness")
        for fixture in data["fixtures"]:
            protocol, _ = command_for(fixture)
            run = subprocess.run(
                [str(binary)], input=protocol, text=True, capture_output=True,
                env={"ASAN_OPTIONS": "detect_leaks=0"}, check=False,
            )
            if run.returncode != 0:
                failures.append({"id": fixture["id"], "reason": "process", "stderr": run.stderr.strip()})
                continue
            observed = json.loads(run.stdout)
            expected = {"events": fixture["expected_events"], "final": fixture["expected_final"]}
            if observed != expected:
                failures.append({"id": fixture["id"], "reason": "mismatch", "observed": observed, "expected": expected})
            else:
                passes.append(fixture["id"])
        controller_sources = [
            ROOT / "docs/tasks/PORT-003/phase-c/tests/controller_frame_tests.cpp",
            ROOT / "vdp/video/extender/display/logical_frame_service.cpp",
            ROOT / "vdp/video/extender/display/native_pixel_codec.cpp",
            ROOT / "vdp/video/extender/display/plane_storage.cpp",
            ROOT / "vdp/video/extender/display/palette_state.cpp",
            ROOT / "vdp/video/extender/display/presentation_compositor.cpp",
            ROOT / "vdp/video/extender/display/p4_display_controller.cpp",
            ROOT / "vdp/video/extender/port/fabutils_port.cpp",
            ROOT / "vdp/vendor/vdp-gl/src/canvas.cpp",
            ROOT / "vdp/vendor/vdp-gl/src/displaycontroller.cpp",
        ]
        controller_binary = Path(temporary) / "controller-frame-tests"
        compile_checked([
            args.compiler, "-std=c++17", "-O1", "-g", "-Wall", "-Wextra", "-pedantic",
            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-pthread",
            "-ffunction-sections", "-fdata-sections", "-DFABGL_EMULATED",
            "-I", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat"),
            "-I", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat"),
            "-I", str(ROOT / "vdp/video"), "-I", str(ROOT / "vdp/vendor/vdp-gl/src"),
            "-include", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat/freertos/task.h"),
            "-include", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat/host_preinclude.hpp"),
            *(str(source) for source in controller_sources), "-Wl,--gc-sections",
            "-o", str(controller_binary),
        ], "retained controller harness")
        try:
            controller_run = subprocess.run(
                [str(controller_binary)], text=True, capture_output=True,
                env={"ASAN_OPTIONS": "detect_leaks=0"}, check=False, timeout=10,
            )
        except subprocess.TimeoutExpired as error:
            failures.append({
                "id": "retained-controller-integration",
                "reason": "timeout",
                "stdout": error.stdout or "",
                "stderr": error.stderr or "",
            })
            controller_output = []
            controller_run = None
        if controller_run is not None:
            controller_output = controller_run.stdout.splitlines()
        expected_controller = [
            "upstream-queue-wait-pass", "double-buffer-swap-pass",
            "single-buffer-edge-stop-pass", "suspension-counter-pass",
            "drain-restart-reconfigure-pass",
        ]
        if controller_run is not None and (controller_run.returncode != 0 or controller_output != expected_controller):
            failures.append({"id": "retained-controller-integration", "reason": "process-or-output", "returncode": controller_run.returncode, "stdout": controller_run.stdout.strip(), "stderr": controller_run.stderr.strip()})
        stress_sources = [
            ROOT / "docs/tasks/PORT-003/phase-c/tests/frame_service_stress_tests.cpp",
            ROOT / "vdp/video/extender/display/logical_frame_service.cpp",
        ]
        stress_binary = Path(temporary) / "frame-service-stress-tests"
        compile_checked([
            args.compiler, "-std=c++17", "-O1", "-g", "-Wall", "-Wextra",
            "-Werror", "-pedantic", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-pthread", "-I", str(ROOT / "vdp/video"),
            *(str(source) for source in stress_sources), "-o", str(stress_binary),
        ], "logical frame stress harness")
        stress_run = subprocess.run(
            [str(stress_binary)], text=True, capture_output=True,
            env={"ASAN_OPTIONS": "detect_leaks=0"}, check=False, timeout=20,
        )
        stress_output = stress_run.stdout.splitlines()
        expected_stress = [
            "concurrent-tick-burst-pass", "saturation-lifecycle-pass",
            "bounded-consumer-registry-pass",
        ]
        if stress_run.returncode != 0 or stress_output != expected_stress:
            failures.append({"id": "logical-frame-stress", "reason": "process-or-output", "returncode": stress_run.returncode, "stdout": stress_run.stdout.strip(), "stderr": stress_run.stderr.strip()})
    result = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_c_host_frame_results",
        "generated_by": "docs/tasks/PORT-003/phase-c/scripts/run-host-frame-tests.py",
        "diagnostic_status": "host ASan/UBSan deterministic logical-frame qualification; LSAN unavailable under managed tracing",
        "fixture_input": {"path": args.fixtures.resolve().relative_to(ROOT).as_posix(), "sha256": sha256_file(args.fixtures.resolve()), "fixture_set_sha256": data["fixture_set_sha256"]},
        "production_sources": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)} for path in sources],
        "retained_controller_sources": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)} for path in controller_sources],
        "retained_controller_output": controller_output,
        "stress_output": stress_output,
        "summary": {"fixture_count": len(data["fixtures"]), "pass_count": len(passes), "controller_case_count": 5, "stress_case_count": 3, "failure_count": len(failures), "passed": not failures},
        "passes": passes,
        "failures": failures,
    }
    write_canonical(args.output.resolve(), result)
    if failures:
        print(f"{len(failures)} host frame fixture(s) failed", file=sys.stderr)
        return 1
    print(f"passed {len(passes)} host frame fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
