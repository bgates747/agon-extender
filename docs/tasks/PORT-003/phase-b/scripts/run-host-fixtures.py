#!/usr/bin/env python3
"""Compile host adapters and compare production output to Phase B fixtures."""

from __future__ import annotations

import argparse
from collections import Counter
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))

from dependency_model import load_data, sha256_file, write_canonical  # noqa: E402


def compile_binary(
    compiler: str, output: Path, sources: list[Path], *, retained_renderer: bool = False
) -> None:
    command = [
        compiler,
        "-std=c++17",
        "-O1",
        "-g",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        "-fsanitize=address,undefined",
        "-fno-omit-frame-pointer",
        "-ffunction-sections",
        "-fdata-sections",
        "-I",
        str(ROOT / "vdp/video"),
        "-I",
        str(ROOT / "vdp/vendor/vdp-gl/src"),
        "-I",
        str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat"),
        "-DFABGL_EMULATED",
        "-include",
        "host_preinclude.hpp",
        *map(str, sources),
        "-Wl,--gc-sections",
        "-o",
        str(output),
    ]
    if retained_renderer:
        # The immutable upstream units carry warnings outside project control;
        # project sources remain warning-clean in the ordinary P4 build.
        command.remove("-Werror")
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, command)


def parse_output(text: str) -> dict[str, str]:
    return dict(line.split("=", 1) for line in text.splitlines() if "=" in line)


def hex_bytes(values: list[int]) -> str:
    return "".join(f"{value:02x}" for value in values)


def run_native(binary: Path, fixture: dict[str, Any]) -> list[str]:
    if fixture["id"].startswith("codec-"):
        operation = "sequence"
        argument = ";".join(
            f"{item['x']},{item['y']},{item['value']}" for item in fixture["operations"]
        )
    else:
        operation = "clear"
        argument = str(fixture["value"])
    environment = os.environ.copy()
    # LSAN cannot inspect a process under this managed execution boundary.
    # ASan/UBSan remain active; PlaneStorage separately accounts every live
    # allocation and fails on leaks, unknown frees, or double frees.
    environment["ASAN_OPTIONS"] = "detect_leaks=0"
    result = subprocess.run(
        [
            str(binary),
            operation,
            fixture["format"],
            str(fixture["width"]),
            str(fixture["height"]),
            argument,
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=environment,
    )
    observed = parse_output(result.stdout)
    failures = []
    if observed.get("bytes") != hex_bytes(fixture["expected_native_bytes"]):
        failures.append("native-bytes")
    expected_pixels = fixture.get("expected_pixels")
    if expected_pixels is not None:
        flattened = ",".join(str(value) for row in expected_pixels for value in row)
        if observed.get("pixels") != flattened:
            failures.append("logical-readback")
    if fixture["format"] == "SBGR2222" and "expected_native_save" in fixture:
        for sync, expected in fixture["expected_native_save"].items():
            key = "save" + sync.removeprefix("0x").lower()
            if observed.get(key) != hex_bytes(expected):
                failures.append(f"native-save-{sync}")
    return failures


def encode_operation(operation: dict[str, Any]) -> str:
    order = {
        "set_pixel": ("x", "y", "value"),
        "seed_formula": ("x_factor", "y_factor", "maximum"),
        "line": ("x1", "y1", "x2", "y2", "value"),
        "fill_row": ("y", "x1", "x2", "value"),
        "copy_rect": ("x1", "y1", "x2", "y2", "dest_x", "dest_y"),
        "vscroll": ("x1", "y1", "x2", "y2", "amount"),
        "hscroll": ("x1", "y1", "x2", "y2", "amount"),
        "set_origin": ("x", "y"),
        "set_clip": ("x1", "y1", "x2", "y2"),
        "fill_rect": ("x1", "y1", "x2", "y2", "value"),
        "invert_rect": ("x1", "y1", "x2", "y2"),
        "paint_pixel": ("mode", "x", "y", "value"),
        "clear": ("value",),
        "glyph": ("x", "y", "pen", "brush", "fill_background", "rows"),
        "flood_fill": ("x", "y", "match", "value", "scan_to_match"),
        "ellipse": ("x", "y", "width", "height", "value"),
        "arc": ("x", "y", "x1", "y1", "x2", "y2", "value"),
        "segment": ("x", "y", "x1", "y1", "x2", "y2", "value"),
        "sector": ("x", "y", "x1", "y1", "x2", "y2", "value"),
        "bitmap_mask": ("x", "y", "width", "height", "value", "data"),
        "bitmap_rgba2222": ("x", "y", "width", "height", "data"),
        "bitmap_rgba8888": ("x", "y", "width", "height", "data"),
        "bitmap_native": ("x", "y", "width", "height", "data"),
        "bitmap_transform_rgba2222": ("x", "y", "width", "height", "data"),
    }
    name = operation["op"]
    return ",".join([name, *(str(operation[field]) for field in order[name])])


def run_renderer(binary: Path, fixture: dict[str, Any]) -> list[str]:
    environment = os.environ.copy()
    environment["ASAN_OPTIONS"] = "detect_leaks=0"
    result = subprocess.run(
        [
            str(binary),
            fixture["format"],
            str(fixture["width"]),
            str(fixture["height"]),
            "1" if fixture.get("double_buffered", False) else "0",
            *(encode_operation(operation) for operation in fixture["operations"]),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=environment,
    )
    if result.returncode:
        raise RuntimeError(
            f"renderer fixture {fixture['id']} exited {result.returncode}: {result.stderr.strip()}"
        )
    observed = parse_output(result.stdout)
    failures = []
    if observed.get("bytes") != hex_bytes(fixture["expected_native_bytes"]):
        failures.append("native-bytes")
    if observed.get("readback") != hex_bytes(fixture["expected_readback_rgb"]):
        failures.append("logical-readback")
    if observed.get("visible") != hex_bytes(fixture.get("expected_visible_bytes", fixture["expected_native_bytes"])):
        failures.append("visible-plane")
    if observed.get("native_save") != hex_bytes(fixture["expected_native_save"]):
        failures.append("native-save")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", default="g++")
    parser.add_argument(
        "--native-fixtures",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-b/fixtures/native-codecs.yaml",
    )
    parser.add_argument(
        "--primitive-fixtures",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-b/fixtures/primitives.yaml",
    )
    parser.add_argument(
        "--host-output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-b/evidence/host-fixture-results.yaml",
    )
    parser.add_argument(
        "--allocation-output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-b/evidence/allocation-failure-results.yaml",
    )
    args = parser.parse_args()

    native_sources = [
        ROOT / "docs/tasks/PORT-003/phase-b/tests/native_pixel_codec_tests.cpp",
        ROOT / "vdp/video/extender/display/native_pixel_codec.cpp",
    ]
    storage_sources = [
        ROOT / "docs/tasks/PORT-003/phase-b/tests/plane_storage_tests.cpp",
        ROOT / "vdp/video/extender/display/native_pixel_codec.cpp",
        ROOT / "vdp/video/extender/display/plane_storage.cpp",
    ]
    renderer_sources = [
        ROOT / "docs/tasks/PORT-003/phase-b/tests/renderer_fixture_tests.cpp",
        ROOT / "vdp/video/extender/display/native_pixel_codec.cpp",
        ROOT / "vdp/video/extender/display/plane_storage.cpp",
        ROOT / "vdp/video/extender/display/palette_state.cpp",
        ROOT / "vdp/video/extender/display/presentation_compositor.cpp",
        ROOT / "vdp/video/extender/display/p4_display_controller.cpp",
        ROOT / "vdp/video/extender/port/fabutils_port.cpp",
        ROOT / "vdp/vendor/vdp-gl/src/canvas.cpp",
        ROOT / "vdp/vendor/vdp-gl/src/displaycontroller.cpp",
    ]
    fixture_data = load_data(args.native_fixtures.resolve())
    primitive_data = load_data(args.primitive_fixtures.resolve())
    with tempfile.TemporaryDirectory(prefix="agon-extender-phase-b-") as temporary:
        temporary_path = Path(temporary)
        native_binary = temporary_path / "native-pixel-tests"
        storage_binary = temporary_path / "plane-storage-tests"
        renderer_binary = temporary_path / "renderer-tests"
        compile_binary(args.compiler, native_binary, native_sources)
        compile_binary(args.compiler, storage_binary, storage_sources)
        compile_binary(args.compiler, renderer_binary, renderer_sources, retained_renderer=True)
        failures = []
        counts = Counter()
        for fixture in fixture_data["fixtures"]:
            observed_failures = run_native(native_binary, fixture)
            counts[fixture["format"]] += 1
            if observed_failures:
                failures.append({"fixture_id": fixture["id"], "mismatches": observed_failures})
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "detect_leaks=0"
        contract = subprocess.run(
            [str(native_binary), "contract"],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
            env=environment,
        )
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "detect_leaks=0"
        allocation = subprocess.run(
            [str(storage_binary)],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
            env=environment,
        )
        renderer_failures = []
        renderer_counts = Counter()
        for fixture in primitive_data["fixtures"]:
            observed_failures = run_renderer(renderer_binary, fixture)
            renderer_counts[fixture["format"]] += 1
            if observed_failures:
                renderer_failures.append(
                    {"fixture_id": fixture["id"], "mismatches": observed_failures}
                )

    host_data = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_b_host_fixture_results",
        "generated_by": "docs/tasks/PORT-003/phase-b/scripts/run-host-fixtures.py",
        "diagnostic_status": "host ASan/UBSan behavior qualification; LSAN unavailable under managed tracing",
        "fixture_input": {
            "path": args.native_fixtures.resolve().relative_to(ROOT).as_posix(),
            "sha256": sha256_file(args.native_fixtures.resolve()),
            "fixture_set_sha256": fixture_data["fixture_set_sha256"],
            "oracle_class": fixture_data["oracle_class"],
        },
        "primitive_fixture_input": {
            "path": args.primitive_fixtures.resolve().relative_to(ROOT).as_posix(),
            "sha256": sha256_file(args.primitive_fixtures.resolve()),
            "fixture_set_sha256": primitive_data["fixture_set_sha256"],
            "oracle_class": primitive_data["oracle_class"],
        },
        "production_sources": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}
            for path in dict.fromkeys([*native_sources, *renderer_sources])
        ],
        "summary": {
            "fixture_count": sum(counts.values()),
            "counts_by_format": dict(sorted(counts.items())),
            "primitive_fixture_count": sum(renderer_counts.values()),
            "primitive_counts_by_format": dict(sorted(renderer_counts.items())),
            "failure_count": len(failures) + len(renderer_failures),
            "passed": not failures and not renderer_failures,
        },
        "invalid_operation_contract": contract.stdout.strip(),
        "failures": failures + renderer_failures,
    }
    allocation_data = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_b_allocation_failure_results",
        "generated_by": "docs/tasks/PORT-003/phase-b/scripts/run-host-fixtures.py",
        "diagnostic_status": "host ASan/UBSan plus explicit live-allocation accounting; LSAN unavailable under managed tracing",
        "production_sources": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}
            for path in storage_sources
        ],
        "covered_boundaries": [
            "first-plane allocation failure preserves installed state",
            "second-plane allocation failure frees temporary first plane and preserves installed state",
            "successful replacement releases old allocations after commit",
            "single/double drawing-visible identity",
            "zero initialization",
            "move ownership",
            "idempotent release",
            "dimension/sync/overflow/allocator validation",
        ],
        "program_output": allocation.stdout.splitlines(),
        "passed": "validation-pass" in allocation.stdout,
    }
    write_canonical(args.host_output.resolve(), host_data)
    write_canonical(args.allocation_output.resolve(), allocation_data)
    if failures or renderer_failures or not allocation_data["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
