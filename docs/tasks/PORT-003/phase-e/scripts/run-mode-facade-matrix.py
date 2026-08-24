#!/usr/bin/env python3
"""Exercise all official mode variants through one repeatedly configured facade."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import sha256_file, write_canonical  # noqa: E402

FIXTURES = ROOT / "docs/tasks/PORT-003/phase-e/fixtures/modes-and-lifecycle.yaml"
PROVENANCE = ROOT / "docs/tasks/PORT-003/phase-e/evidence/mode-provenance.yaml"
OUTPUT = ROOT / "docs/tasks/PORT-003/phase-e/evidence/mode-facade-matrix-results.yaml"
SOURCES = [
    "docs/tasks/PORT-003/phase-e/tests/mode_facade_matrix_tests.cpp",
    "vdp/video/extender/display/logical_frame_service.cpp",
    "vdp/video/extender/display/native_pixel_codec.cpp",
    "vdp/video/extender/display/plane_storage.cpp",
    "vdp/video/extender/display/palette_state.cpp",
    "vdp/video/extender/display/presentation_compositor.cpp",
    "vdp/video/extender/display/p4_display_controller.cpp",
    "vdp/video/extender/display/screen_facade_adapter.cpp",
    "vdp/video/extender/port/fabutils_port.cpp",
    "vdp/vendor/vdp-gl/src/canvas.cpp",
    "vdp/vendor/vdp-gl/src/displaycontroller.cpp",
]


def modelines(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split(maxsplit=2)
        if len(fields) == 3 and fields[0] == "#define" and fields[1][0].isalpha():
            try:
                value = ast.literal_eval(fields[2])
            except (SyntaxError, ValueError):
                continue
            if isinstance(value, str) and value.startswith('"') and "Hz\"" in value:
                result[fields[1]] = value
    return result


def parse(output: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    observations = []
    teardown = None
    for line in output.splitlines():
        fields = line.split("\t")
        if fields[0] == "O" and len(fields) == 12:
            observations.append(
                {
                    "ordinal": int(fields[1]),
                    "result": int(fields[2]),
                    "width": int(fields[3]),
                    "height": int(fields[4]),
                    "native_format": fields[5],
                    "double_buffered": bool(int(fields[6])),
                    "refresh_hz": int(fields[7]),
                    "period_microseconds": int(fields[8]),
                    "screen_height": int(fields[9]),
                    "viewport_height": int(fields[10]),
                    "live_allocations": int(fields[11]),
                }
            )
        elif fields[0] == "T" and len(fields) == 5:
            teardown = {
                "live_allocations": int(fields[1]),
                "allocation_attempts": int(fields[2]),
                "service_starts": int(fields[3]),
                "service_stops": int(fields[4]),
            }
        else:
            raise ValueError(f"unexpected facade matrix output: {line!r}")
    if teardown is None:
        raise ValueError("missing facade matrix teardown")
    return observations, teardown


def main() -> int:
    fixtures = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    provenance = yaml.safe_load(PROVENANCE.read_text(encoding="utf-8"))
    fixture_modes = fixtures["mode_cases"]
    source_modes = provenance["mode_table"]
    if len(fixture_modes) != len(source_modes):
        raise ValueError("fixture/provenance mode counts differ")
    definitions = modelines(ROOT / "vdp/vendor/vdp-gl/src/fabglconf.h")
    protocol = []
    for expected, source in zip(fixture_modes, source_modes):
        source_key = (source["mode"], str(source["legacy_modes"]).lower())
        expected_key = (expected["mode"], str(expected["legacy_modes"]).lower())
        if source_key != expected_key:
            raise ValueError(f"mode ordering differs: {source_key} != {expected_key}")
        protocol.append(
            f"{expected['colours']}|{int(expected['double_buffered'])}|{definitions[source['modeline']]}"
        )
    protocol.append("END")

    compiler = subprocess.run(
        ["g++", "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    with tempfile.TemporaryDirectory(prefix="port-003-phase-e-modes-") as directory:
        binary = Path(directory) / "mode-facade-matrix"
        command = [
            "g++", "-std=c++17", "-O1", "-g", "-w",
            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-pthread",
            "-ffunction-sections", "-fdata-sections", "-DFABGL_EMULATED",
            "-I", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat"),
            "-I", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat"),
            "-I", str(ROOT / "vdp/video"),
            "-I", str(ROOT / "vdp/vendor/vdp-gl/src"),
            "-include", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat/freertos/task.h"),
            "-include", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat/host_preinclude.hpp"),
            *(str(ROOT / source) for source in SOURCES),
            "-Wl,--gc-sections", "-o", str(binary),
        ]
        compilation = subprocess.run(command, text=True, capture_output=True)
        if compilation.returncode != 0:
            diagnostics = (compilation.stdout + compilation.stderr).splitlines()
            decisive = [line for line in diagnostics if "error:" in line or "undefined reference" in line]
            print("\n".join(decisive or diagnostics[-50:]), file=sys.stderr)
            return 1
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        process = subprocess.run(
            [str(binary)], input="\n".join(protocol) + "\n", text=True,
            capture_output=True, env=environment, timeout=30
        )
        if process.returncode != 0:
            print(process.stderr, file=sys.stderr)
            return 1
        observations, teardown = parse(process.stdout)

    failures = []
    cases = []
    for expected, observed in zip(fixture_modes, observations):
        expected_observation = {
            "width": expected["width"],
            "height": expected["height"],
            "native_format": expected["native_format"],
            "double_buffered": expected["double_buffered"],
            "refresh_hz": expected["refresh_hz"],
            "period_microseconds": expected["period_microseconds"],
            "screen_height": expected["height"],
            "viewport_height": expected["height"],
        }
        comparable = {key: observed[key] for key in expected_observation}
        status = "pass" if observed["result"] == 0 and comparable == expected_observation else "fail"
        if status == "fail":
            failures.append({"id": expected["id"], "expected": expected_observation, "observed": observed})
        cases.append({"id": expected["id"], "status": status, "observed": observed})
    if len(observations) != len(fixture_modes):
        failures.append({"id": "mode-count", "expected": len(fixture_modes), "observed": len(observations)})
    expected_plane_live = 2 if fixture_modes[-1]["double_buffered"] else 1
    if teardown["live_allocations"] != 0 or teardown["service_starts"] != len(fixture_modes) or teardown["service_stops"] != len(fixture_modes) - 1 or cases[-1]["observed"]["live_allocations"] != expected_plane_live:
        failures.append({"id": "teardown-or-service-lifecycle", "observed": teardown})

    artifact = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_e_mode_facade_matrix_results",
        "generated_by": "docs/tasks/PORT-003/phase-e/scripts/run-mode-facade-matrix.py",
        "compiler": compiler,
        "sanitizers": ["address", "undefined"],
        "fixture_input": {"path": FIXTURES.relative_to(ROOT).as_posix(), "sha256": sha256_file(FIXTURES)},
        "provenance_input": {"path": PROVENANCE.relative_to(ROOT).as_posix(), "sha256": sha256_file(PROVENANCE)},
        "sources": [{"path": source, "sha256": sha256_file(ROOT / source)} for source in SOURCES],
        "cases": cases,
        "teardown": teardown,
        "failures": failures,
        "summary": {"passed": len(cases) - len([case for case in cases if case["status"] != "pass"]), "failed": len(failures)},
    }
    write_canonical(OUTPUT, artifact)
    if failures:
        print(f"mode facade matrix failed: {failures}", file=sys.stderr)
        return 1
    print(f"mode facade matrix: {len(cases)} repeated configurations passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
