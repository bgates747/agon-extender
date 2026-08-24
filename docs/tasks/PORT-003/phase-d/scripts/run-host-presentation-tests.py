#!/usr/bin/env python3
"""Run PORT-003 Phase D production code against independent fixtures."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import load_data, sha256_file, write_canonical  # noqa: E402


FORMAT = {
    "PALETTE2": "NativePixelFormat::PALETTE2",
    "PALETTE4": "NativePixelFormat::PALETTE4",
    "PALETTE8": "NativePixelFormat::PALETTE8",
    "PALETTE16": "NativePixelFormat::PALETTE16",
    "SBGR2222": "NativePixelFormat::SBGR2222",
}


def values(items: list[int]) -> str:
    return ", ".join(str(value) for value in items)


def flatten_rgb(rows: list[list[list[int]]]) -> list[int]:
    return [channel for row in rows for pixel in row for channel in pixel]


def operation_lines(operation: dict[str, Any], state: str, label: str) -> list[str]:
    name = operation["op"]
    if name == "create":
        return [f'check({state}.createPalette({operation["palette_id"]}), "{label}: create");']
    if name == "delete":
        return [f'{state}.deletePalette({operation["palette_id"]});']
    if name == "set":
        red, green, blue = operation["rgb"]
        return [
            f'check({state}.setItemInPalette({operation["palette_id"]}, '
            f'{operation["index"]}, {red}, {green}, {blue}), "{label}: set");'
        ]
    if name == "update_lut":
        return [f"{state}.updateRGB2PaletteLUT();"]
    if name in {"signals", "reset_signals"}:
        pairs = operation.get("pairs", [[0, 0]])
        flat = [value for pair in pairs for value in pair]
        if not flat:
            return [f'check({state}.updateSignalList(nullptr, 0), "{label}: empty signals");']
        return [
            f"std::uint16_t signal_data_{label}[] = {{{values(flat)}}};",
            f'check({state}.updateSignalList(signal_data_{label}, {len(pairs)}), '
            f'"{label}: signals");',
        ]
    raise ValueError(f"unsupported operation {name}")


def emit_palette_case(case: dict[str, Any], ordinal: int) -> str:
    label = f"palette_{ordinal}"
    lines = [
        f"void test_{label}() {{",
        "  Tracking tracking;",
        "  {",
        "    PaletteState state(tracking.allocator());",
        f"    state.reset({FORMAT[case['format']]});",
    ]
    for index, operation in enumerate(case["operations"]):
        lines.extend(f"    {line}" for line in operation_lines(operation, "state", f"{label}_{index}"))
    expected = case["expected"]
    lines.append(
        f'    check(state.secondaryPaletteCount() == {max(0, len(expected["palettes"]) - 1)}, '
        f'"{case["id"]}: secondary count");'
    )
    for palette_id, palette in expected["palettes"].items():
        lines.extend([
            f"    std::array<std::uint8_t, {len(palette)}> expected_palette_{palette_id}"
            f"{{{{{values(palette)}}}}};",
            f"    std::array<std::uint8_t, {len(palette)}> actual_palette_{palette_id}{{}};",
            f"    check(state.copyPalette({palette_id}, actual_palette_{palette_id}.data(), "
            f"actual_palette_{palette_id}.size()), \"{case['id']}: copy palette {palette_id}\");",
            f"    check(actual_palette_{palette_id} == expected_palette_{palette_id}, "
            f"\"{case['id']}: palette {palette_id}\");",
        ])
    lines.append(
        f'    check(state.signalCount() == {len(expected["signals"])}, '
        f'"{case["id"]}: signal count");'
    )
    for index, signal in enumerate(expected["signals"]):
        lines.append(
            f"    check(state.signalAt({index}).end_row == {signal['end_row']} && "
            f"state.signalAt({index}).palette_id == {signal['palette_id']}, "
            f"\"{case['id']}: signal {index}\");"
        )
    for packed, expected_index in enumerate(expected["drawing_lut"]):
        red = (packed & 3) * 85
        green = ((packed >> 2) & 3) * 85
        blue = ((packed >> 4) & 3) * 85
        lines.append(
            f"    check(state.drawingIndex({red}, {green}, {blue}) == {expected_index}, "
            f"\"{case['id']}: LUT {packed}\");"
        )
    for row, palette in zip(expected.get("row_queries", []), expected.get("row_palettes", [])):
        for index, color in enumerate(palette):
            lines.append(
                f"    check(state.presentationColor({row}, {index}) == {color}, "
                f"\"{case['id']}: row {row} index {index}\");"
            )
    lines.extend([
        "  }",
        f'  check(tracking.live == 0, "{case["id"]}: teardown allocations");',
        f'  std::cout << "{case["id"]}\\n";',
        "}",
    ])
    return "\n".join(lines)


def emit_composition_case(case: dict[str, Any], ordinal: int) -> str:
    label = f"composition_{ordinal}"
    native = case["visible_native_bytes"]
    drawing = case["drawing_native_bytes"]
    expected_composed = flatten_rgb(case["expected_composed_rgb"])
    expected_readback = flatten_rgb(case["expected_readback_rgb"])
    lines = [
        f"void test_{label}() {{",
        "  Tracking tracking;",
        "  {",
        "    PaletteState state(tracking.allocator());",
        f"    state.reset({FORMAT[case['format']]});",
    ]
    for index, operation in enumerate(case["palette_operations"]):
        lines.extend(f"    {line}" for line in operation_lines(operation, "state", f"{label}_{index}"))
    lines.extend([
        f"    std::vector<std::uint8_t> visible{{{values(native)}}};",
        "    auto unchanged = visible;",
        f"    std::vector<std::uint8_t> drawing{{{values(drawing)}}};",
        f"    ModeDescriptor mode{{{case['width']}, {case['height']}, {FORMAT[case['format']]}, "
        f"{str(case['double_buffered']).lower()}, 0}};",
        f"    ConstPlaneView plane{{visible.data(), visible.size(), {len(native) // case['height']}}};",
        f"    PresentationRegion region{{0, 0, {case['width']}, {case['height']}}};",
        f"    std::vector<PresentationRGB888> output({case['width'] * case['height']});",
        f"    check(PresentationCompositor::composeBase(plane, mode, state, region, "
        f"output.data(), output.size()) == CompositionResult::Ok, \"{case['id']}: base\");",
    ])
    ordered = sorted(
        case["overlays"],
        key=lambda item: ({"text": 0, "hardware": 1, "mouse": 2, "software": 3}[item["role"]], item.get("index", 0)),
    )
    overlay_number = 0
    for overlay in ordered:
        if overlay["role"] == "software" or not overlay.get("visible", True) or not overlay.get("allow_draw", True):
            continue
        data_name = f"overlay_data_{label}_{overlay_number}"
        format_name = "OverlayPixelFormat::" + overlay["format"]
        paint_name = "OverlayPaint::Xor" if overlay.get("paint") == "XOR" else "OverlayPaint::Overwrite"
        lines.extend([
            f"    std::vector<std::uint8_t> {data_name}{{{values(overlay['data'])}}};",
            f"    OverlayView overlay_{overlay_number}{{{overlay['x']}, {overlay['y']}, "
            f"{overlay['width']}, {overlay['height']}, {format_name}, {paint_name}, "
            f"{data_name}.data(), {data_name}.size()}};",
            f"    check(PresentationCompositor::applyOverlay(region, output.data(), output.size(), "
            f"overlay_{overlay_number}) == CompositionResult::Ok, \"{case['id']}: overlay {overlay_number}\");",
        ])
        overlay_number += 1
    lines.extend([
        f"    std::array<std::uint8_t, {len(expected_composed)}> expected_composed"
        f"{{{{{values(expected_composed)}}}}};",
        "    for (std::size_t index = 0; index < output.size(); ++index) {",
        "      check(output[index].red == expected_composed[index * 3] &&",
        "            output[index].green == expected_composed[index * 3 + 1] &&",
        "            output[index].blue == expected_composed[index * 3 + 2],",
        f'            "{case["id"]}: composed RGB");',
        "    }",
        f"    std::array<std::uint8_t, {len(expected_readback)}> expected_readback"
        f"{{{{{values(expected_readback)}}}}};",
        f"    std::size_t drawing_stride = {len(drawing) // case['height']};",
        f"    for (std::size_t y = 0; y < {case['height']}; ++y) {{",
        f"      for (std::size_t x = 0; x < {case['width']}; ++x) {{",
        "        std::uint8_t logical = 0;",
        f"        check(NativePixelCodec::read(drawing.data() + y * drawing_stride, {case['width']}, "
        f"{FORMAT[case['format']]}, x, logical) == CodecResult::Ok, \"{case['id']}: readback decode\");",
        "        std::uint8_t packed = state.palette0Color(logical);",
        f"        std::size_t expected_index = (y * {case['width']} + x) * 3;",
        "        check((packed & 3) * 85 == expected_readback[expected_index] &&",
        "              ((packed >> 2) & 3) * 85 == expected_readback[expected_index + 1] &&",
        "              ((packed >> 4) & 3) * 85 == expected_readback[expected_index + 2],",
        f'              "{case["id"]}: readback RGB");',
        "      }",
        "    }",
        f'    check(visible == unchanged, "{case["id"]}: logical bytes unchanged");',
        "  }",
        f'  check(tracking.live == 0, "{case["id"]}: teardown allocations");',
        f'  std::cout << "{case["id"]}\\n";',
        "}",
    ])
    return "\n".join(lines)


def emit_allocation_case(case: dict[str, Any], ordinal: int) -> str:
    label = f"allocation_{ordinal}"
    lines = [
        f"void test_{label}() {{",
        f"  Tracking tracking{{0, 0, 0, {case['failure_on_allocation']}}};",
        "  {",
        "    PaletteState state(tracking.allocator());",
        f"    state.reset({FORMAT[case['format']]});",
    ]
    if "precondition" in case:
        lines.extend(f"    {line}" for line in operation_lines(case["precondition"], "state", f"{label}_pre"))
    operation = case["operation"]
    if operation["op"] == "create":
        expression = f"state.createPalette({operation['palette_id']})"
    elif operation["op"] == "signals":
        flat = [value for pair in operation["pairs"] for value in pair]
        lines.append(f"    std::uint16_t allocation_signals[] = {{{values(flat)}}};")
        expression = f"state.updateSignalList(allocation_signals, {len(operation['pairs'])})"
    else:
        raise ValueError(f"unsupported allocation operation {operation['op']}")
    expected = str(case["expected_result"]).lower()
    lines.append(f'    check({expression} == {expected}, "{case["id"]}: result");')
    if "expected_palettes" in case:
        palette = case["expected_palettes"]["0"]
        lines.extend([
            f"    std::array<std::uint8_t, {len(palette)}> expected{{{{{values(palette)}}}}};",
            f"    std::array<std::uint8_t, {len(palette)}> actual{{}};",
            f'    check(state.copyPalette(0, actual.data(), actual.size()), "{case["id"]}: copy");',
            f'    check(actual == expected, "{case["id"]}: preserved palette");',
        ])
    if "expected_signals" in case:
        lines.append(f'    check(state.signalCount() == {len(case["expected_signals"])}, "{case["id"]}: signal count");')
        for index, signal in enumerate(case["expected_signals"]):
            lines.append(
                f"    check(state.signalAt({index}).end_row == {signal['end_row']} && "
                f"state.signalAt({index}).palette_id == {signal['palette_id']}, "
                f"\"{case['id']}: preserved signal\");"
            )
    lines.extend([
        f'    check(tracking.live == {case["expected_live_allocations"]}, "{case["id"]}: live allocation");',
        "  }",
        f'  check(tracking.live == 0, "{case["id"]}: teardown allocations");',
        f'  std::cout << "{case["id"]}\\n";',
        "}",
    ])
    return "\n".join(lines)


def generated_source(data: dict[str, Any]) -> str:
    functions = []
    calls = []
    for index, case in enumerate(data["palette_cases"]):
        functions.append(emit_palette_case(case, index))
        calls.append(f"test_palette_{index}();")
    for index, case in enumerate(data["composition_cases"]):
        functions.append(emit_composition_case(case, index))
        calls.append(f"test_composition_{index}();")
    for index, case in enumerate(data["allocation_cases"]):
        functions.append(emit_allocation_case(case, index))
        calls.append(f"test_allocation_{index}();")
    return """// Generated in a temporary directory by run-host-presentation-tests.py.
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <vector>
#include "extender/display/palette_state.hpp"
#include "extender/display/presentation_compositor.hpp"
using namespace agon::extender::display;
struct Tracking {
  std::size_t attempts{};
  std::size_t live{};
  std::size_t releases{};
  std::size_t fail_on{};
  static void *allocate(void *context, std::size_t size) {
    auto &self = *static_cast<Tracking *>(context);
    ++self.attempts;
    if (self.fail_on != 0 && self.attempts == self.fail_on) return nullptr;
    void *result = std::malloc(size);
    if (result != nullptr) ++self.live;
    return result;
  }
  static void release(void *context, void *allocation) {
    if (allocation == nullptr) return;
    auto &self = *static_cast<Tracking *>(context);
    std::free(allocation);
    --self.live;
    ++self.releases;
  }
  Allocator allocator() { return {this, allocate, release}; }
};
void check(bool condition, char const *message) {
  if (!condition) { std::cerr << message << '\\n'; std::exit(1); }
}
""" + "\n\n".join(functions) + "\nint main() {\n  " + "\n  ".join(calls) + "\n}\n"


def compile_checked(command: list[str], label: str) -> None:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode == 0:
        return
    diagnostics = (result.stdout + result.stderr).splitlines()
    decisive = [line for line in diagnostics if "error:" in line or "undefined reference" in line]
    print("\n".join(decisive or diagnostics[-50:]), file=sys.stderr)
    raise RuntimeError(f"{label} compilation failed")


def run_checked(command: list[str], label: str, timeout: int = 20) -> list[str]:
    result = subprocess.run(
        command, text=True, capture_output=True, check=False, timeout=timeout,
        env={"ASAN_OPTIONS": "detect_leaks=0"},
    )
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"{label} failed with status {result.returncode}")
    return result.stdout.splitlines()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", default="g++")
    parser.add_argument(
        "--fixtures", type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-d/fixtures/presentation.yaml",
    )
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-d/evidence/host-presentation-results.yaml",
    )
    args = parser.parse_args()
    fixtures = load_data(args.fixtures.resolve())
    production_sources = [
        ROOT / "vdp/video/extender/display/native_pixel_codec.cpp",
        ROOT / "vdp/video/extender/display/palette_state.cpp",
        ROOT / "vdp/video/extender/display/presentation_compositor.cpp",
    ]
    matrix_output: list[str]
    unit_outputs: dict[str, list[str]] = {}
    with tempfile.TemporaryDirectory(prefix="agon-extender-phase-d-") as temporary_name:
        temporary = Path(temporary_name)
        source = temporary / "fixture_matrix.cpp"
        source.write_text(generated_source(fixtures), encoding="utf-8")
        matrix = temporary / "fixture-matrix"
        compile_checked([
            args.compiler, "-std=c++17", "-O1", "-g", "-Wall", "-Wextra",
            "-Werror", "-pedantic", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-I", str(ROOT / "vdp/video"),
            str(source), *(str(item) for item in production_sources), "-o", str(matrix),
        ], "fixture matrix")
        matrix_output = run_checked([str(matrix)], "fixture matrix")

        simple_tests = {
            "palette-state": (
                ROOT / "docs/tasks/PORT-003/phase-d/tests/palette_state_tests.cpp",
                production_sources[:2],
            ),
            "presentation-compositor": (
                ROOT / "docs/tasks/PORT-003/phase-d/tests/presentation_compositor_tests.cpp",
                production_sources,
            ),
        }
        for name, (test_source, sources) in simple_tests.items():
            binary = temporary / name
            compile_checked([
                args.compiler, "-std=c++17", "-O1", "-g", "-Wall", "-Wextra",
                "-Werror", "-pedantic", "-fsanitize=address,undefined",
                "-fno-omit-frame-pointer", "-I", str(ROOT / "vdp/video"),
                str(test_source), *(str(item) for item in sources), "-o", str(binary),
            ], name)
            unit_outputs[name] = run_checked([str(binary)], name)

        controller_sources = [
            ROOT / "docs/tasks/PORT-003/phase-d/tests/controller_presentation_tests.cpp",
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
        controller = temporary / "controller-presentation"
        compile_checked([
            args.compiler, "-std=c++17", "-O1", "-g", "-w",
            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-pthread",
            "-ffunction-sections", "-fdata-sections", "-DFABGL_EMULATED",
            "-I", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat"),
            "-I", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat"),
            "-I", str(ROOT / "vdp/video"), "-I", str(ROOT / "vdp/vendor/vdp-gl/src"),
            "-include", str(ROOT / "docs/tasks/PORT-003/phase-c/tests/compat/freertos/task.h"),
            "-include", str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat/host_preinclude.hpp"),
            *(str(item) for item in controller_sources), "-Wl,--gc-sections", "-o", str(controller),
        ], "controller presentation")
        unit_outputs["controller-presentation"] = run_checked(
            [str(controller)], "controller presentation"
        )

    expected_cases = [
        case["id"] for family in ("palette_cases", "composition_cases", "allocation_cases")
        for case in fixtures[family]
    ]
    if matrix_output != expected_cases:
        raise RuntimeError("fixture matrix output does not match the complete fixture order")
    result = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_d_host_presentation_results",
        "generated_by": "docs/tasks/PORT-003/phase-d/scripts/run-host-presentation-tests.py",
        "diagnostic_status": "host ASan/UBSan; explicit project-allocation accounting; LSAN unavailable under managed tracing",
        "fixture_input": {
            "path": args.fixtures.resolve().relative_to(ROOT).as_posix(),
            "sha256": sha256_file(args.fixtures.resolve()),
        },
        "production_sources": [
            {"path": item.relative_to(ROOT).as_posix(), "sha256": sha256_file(item)}
            for item in production_sources
        ],
        "matrix_passes": matrix_output,
        "unit_outputs": unit_outputs,
        "summary": {
            "palette_case_count": len(fixtures["palette_cases"]),
            "composition_case_count": len(fixtures["composition_cases"]),
            "allocation_case_count": len(fixtures["allocation_cases"]),
            "fixed_harness_count": len(unit_outputs),
            "failure_count": 0,
            "passed": True,
        },
    }
    write_canonical(args.output.resolve(), result)
    print(f"passed {len(matrix_output)} fixtures and {len(unit_outputs)} fixed harnesses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
