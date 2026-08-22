#!/usr/bin/env python3
"""Generate independent mathematical PORT-003 Phase B fixtures.

This oracle knows the published packed-bit contract and logical drawing
semantics only.  It must never import, execute, or parse output from production
codec/controller code.  Production results are compared with these artifacts
later by run-host-fixtures.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))

from dependency_model import canonical_yaml, write_canonical  # noqa: E402


GENERATOR = "docs/tasks/PORT-003/phase-b/scripts/generate-fixtures.py"
GENERATOR_VERSION = "1.0.0"
SOURCE_TAG = "agon-vdp-v2.16.0"
PROFILE = "port-003-phase-b-synchronous"

FORMATS = {
    "PALETTE2": (1, 1),
    "PALETTE4": (2, 3),
    "PALETTE8": (3, 7),
    "PALETTE16": (4, 15),
    "SBGR2222": (8, 63),
}

PALETTES = {
    "PALETTE2": [(0, 0, 0), (3, 3, 3)],
    "PALETTE4": [(0, 0, 0), (0, 0, 3), (0, 3, 0), (3, 3, 3)],
    "PALETTE8": [(0, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 2),
                 (3, 0, 0), (0, 3, 0), (0, 0, 3), (3, 3, 3)],
    "PALETTE16": [(0, 0, 0), (2, 0, 0), (0, 2, 0), (2, 2, 0),
                  (0, 0, 2), (2, 0, 2), (0, 2, 2), (2, 2, 2),
                  (1, 1, 1), (3, 0, 0), (0, 3, 0), (3, 3, 0),
                  (0, 0, 3), (3, 0, 3), (0, 3, 3), (3, 3, 3)],
}


def payload_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def stride_for(width: int, bits: int) -> int:
    return (width * bits + 7) // 8


def encode_pixels(pixels: list[list[int]], bits: int) -> list[int]:
    """Encode rows as an MSB-first bitstream, independently of production."""

    width = len(pixels[0])
    stride = stride_for(width, bits)
    output: list[int] = []
    for row in pixels:
        encoded = [0] * stride
        if bits == 8:
            encoded[:] = [value & 0x3F for value in row]
        else:
            for x, value in enumerate(row):
                # PALETTE8's three-bit pixels straddle byte boundaries, so the
                # oracle deliberately models the published bitstream one bit
                # at a time instead of borrowing an implementation-shaped
                # word load/shift trick from the old controller.
                for source_bit in range(bits):
                    stream_bit = x * bits + source_bit
                    bit_value = (value >> (bits - 1 - source_bit)) & 1
                    encoded[stream_bit // 8] |= bit_value << (7 - stream_bit % 8)
        output.extend(encoded)
    return output


def codec_case(format_name: str, width: int, height: int) -> dict[str, Any]:
    bits, maximum = FORMATS[format_name]
    pixels = [[0 for _ in range(width)] for _ in range(height)]
    operations = []
    for y in range(height):
        for x in range(width):
            value = ((y * width + x) * 5 + 3) % (maximum + 1)
            operations.append({"x": x, "y": y, "value": value})
            pixels[y][x] = value
    for value in range(maximum + 1):
        x = value % width
        y = (value // width) % height
        operations.append({"x": x, "y": y, "value": value})
        pixels[y][x] = value
    encoded = encode_pixels(pixels, bits)
    case = {
        "id": f"codec-{format_name.lower()}-{width}x{height}",
        "format": format_name,
        "width": width,
        "height": height,
        "stride": stride_for(width, bits),
        "operations": operations,
        "expected_pixels": pixels,
        "expected_native_bytes": encoded,
    }
    if format_name == "SBGR2222":
        case["expected_native_save"] = {
            f"0x{sync:02X}": [byte | sync for byte in encoded]
            for sync in (0x00, 0x40, 0x80, 0xC0)
        }
    case["content_sha256"] = payload_hash(case)
    return case


def clear_case(format_name: str, value: int) -> dict[str, Any]:
    bits, _ = FORMATS[format_name]
    width = 17
    height = 2
    pixels = [[value for _ in range(width)] for _ in range(height)]
    case = {
        "id": f"clear-{format_name.lower()}-{value}",
        "format": format_name,
        "width": width,
        "height": height,
        "value": value,
        "expected_native_bytes": encode_pixels(pixels, bits),
    }
    case["content_sha256"] = payload_hash(case)
    return case


def blank(width: int, height: int) -> list[list[int]]:
    return [[0 for _ in range(width)] for _ in range(height)]


def draw_line(pixels: list[list[int]], x1: int, y1: int, x2: int, y2: int, value: int) -> None:
    dx = abs(x2 - x1)
    sx = 1 if x1 < x2 else -1
    dy = -abs(y2 - y1)
    sy = 1 if y1 < y2 else -1
    error = dx + dy
    while True:
        pixels[y1][x1] = value
        if x1 == x2 and y1 == y2:
            return
        twice = 2 * error
        if twice >= dy:
            error += dy
            x1 += sx
        if twice <= dx:
            error += dx
            y1 += sy


def draw_ellipse(pixels: list[list[int]], center_x: int, center_y: int,
                 width: int, height: int, value: int) -> None:
    """Independent integer McIlroy ellipse used by the published common contract."""

    half_width, half_height = width // 2, height // 2
    a2, b2 = half_width * half_width, half_height * half_height
    crit1 = -(a2 // 4 + half_width % 2 + b2)
    crit2 = -(b2 // 4 + half_height % 2 + a2)
    crit3 = -(b2 // 4 + half_height % 2)
    d2xt, d2yt = 2 * b2, 2 * a2
    x, y, t, dxt, dyt = 0, half_height, -a2 * half_height, 0, -2 * a2 * half_height
    while y >= 0 and x <= half_width:
        for px, py in {
            (center_x - x, center_y - y), (center_x - x, center_y + y),
            (center_x + x, center_y - y), (center_x + x, center_y + y),
        }:
            if 0 <= py < len(pixels) and 0 <= px < len(pixels[0]):
                pixels[py][px] = value
        if t + b2 * x <= crit1 or t + a2 * y <= crit3:
            x += 1
            dxt += d2xt
            t += dxt
        elif t - a2 * y > crit2:
            y -= 1
            dyt += d2yt
            t += dyt
        else:
            x += 1
            dxt += d2xt
            t += dxt
            y -= 1
            dyt += d2yt
            t += dyt


def rgb_for(format_name: str, value: int) -> tuple[int, int, int]:
    if format_name in PALETTES:
        return tuple(component * 85 for component in PALETTES[format_name][value])
    return ((value & 3) * 85, ((value >> 2) & 3) * 85, ((value >> 4) & 3) * 85)


def native_save(format_name: str, pixels: list[list[int]]) -> list[int]:
    result = []
    for row in pixels:
        for value in row:
            red, green, blue = rgb_for(format_name, value)
            result.append(0xC0 | (red >> 6) | ((green >> 6) << 2) | ((blue >> 6) << 4))
    return result


def primitive_cases(format_name: str) -> list[dict[str, Any]]:
    bits, maximum = FORMATS[format_name]
    width, height = 11, 9
    cases: list[dict[str, Any]] = []

    def add(name: str, operations: list[dict[str, Any]], pixels: list[list[int]]) -> None:
        case = {
            "id": f"primitive-{format_name.lower()}-{name}",
            "format": format_name,
            "width": width,
            "height": height,
            "operations": operations,
            "expected_pixels": pixels,
            "expected_native_bytes": encode_pixels(pixels, bits),
            "expected_readback_rgb": [
                component
                for row in pixels
                for value in row
                for component in rgb_for(format_name, value)
            ],
            "expected_native_save": native_save(format_name, pixels),
        }
        case["content_sha256"] = payload_hash(case)
        cases.append(case)

    pixels = blank(width, height)
    points = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1), (5, 4)]
    for index, (x, y) in enumerate(points):
        pixels[y][x] = (maximum - index) & maximum
    add("set-pixel-edges", [{"op": "set_pixel", "x": x, "y": y, "value": pixels[y][x]} for x, y in points], pixels)

    pixels = blank(width, height)
    draw_line(pixels, 0, height - 1, width - 1, 0, maximum)
    add("line-negative-slope", [{"op": "line", "x1": 0, "y1": height - 1, "x2": width - 1, "y2": 0, "value": maximum}], pixels)

    pixels = blank(width, height)
    value = max(1, maximum // 2)
    for x in range(2, 9):
        pixels[4][x] = value
    add("fill-row", [{"op": "fill_row", "y": 4, "x1": 2, "x2": 8, "value": value}], pixels)

    pixels = [[(x + y * 3) & maximum for x in range(width)] for y in range(height)]
    original = [row[:] for row in pixels]
    for y in range(3):
        for x in range(5):
            pixels[5 + y][4 + x] = original[1 + y][1 + x]
    add("overlap-safe-copy", [{"op": "seed_formula", "x_factor": 1, "y_factor": 3, "maximum": maximum}, {"op": "copy_rect", "x1": 1, "y1": 1, "x2": 5, "y2": 3, "dest_x": 4, "dest_y": 5}], pixels)

    pixels = [[(x + y) & maximum for x in range(width)] for y in range(height)]
    region = [row[2:9] for row in pixels[2:7]]
    shifted = [[0] * 7 for _ in range(5)]
    for y in range(5):
        for x in range(7):
            source_y = y - 2
            if 0 <= source_y < 5:
                shifted[y][x] = region[source_y][x]
    for y in range(5):
        pixels[2 + y][2:9] = shifted[y]
    add("vscroll-region", [{"op": "seed_formula", "x_factor": 1, "y_factor": 1, "maximum": maximum}, {"op": "vscroll", "x1": 2, "y1": 2, "x2": 8, "y2": 6, "amount": 2}], pixels)

    pixels = [[(x * 3 + y) & maximum for x in range(width)] for y in range(height)]
    for y in range(1, 8):
        source = pixels[y][1:10]
        pixels[y][1:10] = source[3:] + [0, 0, 0]
    add("hscroll-region", [{"op": "seed_formula", "x_factor": 3, "y_factor": 1, "maximum": maximum}, {"op": "hscroll", "x1": 1, "y1": 1, "x2": 9, "y2": 7, "amount": -3}], pixels)

    pixels = blank(width, height)
    for x in range(2, 8):
        pixels[3][x] = maximum
    add("origin-and-clipping", [
        {"op": "set_origin", "x": 2, "y": 1},
        {"op": "set_clip", "x1": 0, "y1": 0, "x2": 5, "y2": 4},
        {"op": "line", "x1": -3, "y1": 2, "x2": 8, "y2": 2, "value": maximum},
    ], pixels)

    pixels = blank(width, height)
    fill_value = max(1, maximum // 2)
    for y in range(2, 6):
        for x in range(3, 9):
            pixels[y][x] = fill_value
    add("fill-rectangle", [{"op": "fill_rect", "x1": 3, "y1": 2, "x2": 8, "y2": 5, "value": fill_value}], pixels)

    pixels = [[(x + y) & maximum for x in range(width)] for y in range(height)]
    for y in range(2, 7):
        for x in range(2, 9):
            pixels[y][x] ^= maximum
    add("invert-rectangle", [
        {"op": "seed_formula", "x_factor": 1, "y_factor": 1, "maximum": maximum},
        {"op": "invert_rect", "x1": 2, "y1": 2, "x2": 8, "y2": 6},
    ], pixels)

    pixels = blank(width, height)
    paint_operations = []
    old = maximum
    value = 1 if maximum > 1 else maximum
    modes = {
        "Set": value,
        "OR": old | value,
        "AND": old & value,
        "XOR": old ^ value,
        "Invert": old ^ maximum,
        "NoOp": old,
        "ANDNOT": old & ((~value) & maximum),
        "ORNOT": old | ((~value) & maximum),
    }
    for x, (mode, expected) in enumerate(modes.items(), start=1):
        paint_operations.append({"op": "set_pixel", "x": x, "y": 4, "value": old})
        paint_operations.append({"op": "paint_pixel", "mode": mode, "x": x, "y": 4, "value": value})
        pixels[4][x] = expected & maximum
    add("paint-modes", paint_operations, pixels)

    pixels = [[maximum for _ in range(width)] for _ in range(height)]
    clear_value = max(1, maximum // 2)
    pixels = [[clear_value for _ in range(width)] for _ in range(height)]
    add("clear", [
        {"op": "fill_rect", "x1": 0, "y1": 0, "x2": width - 1, "y2": height - 1, "value": maximum},
        {"op": "clear", "value": clear_value},
    ], pixels)

    pixels = blank(width, height)
    glyph_bits = [0xA0, 0x40, 0xE0]
    # The light upstream glyph loop performs a 32-bit lookahead from each
    # one-byte row. Three trailing zero bytes make that reviewed read contract
    # defined without changing the one-byte row stride.
    glyph_rows = [*glyph_bits, 0, 0, 0]
    for gy, bits_row in enumerate(glyph_bits):
        for gx in range(3):
            if bits_row & (0x80 >> gx):
                pixels[2 + gy][3 + gx] = maximum
    add("glyph", [{"op": "glyph", "x": 3, "y": 2, "pen": maximum,
                    "brush": 0, "fill_background": 0,
                    "rows": ":".join(str(value) for value in glyph_rows)}], pixels)

    pixels = blank(width, height)
    for x in range(2, 9):
        pixels[2][x] = pixels[6][x] = maximum
    for y in range(2, 7):
        pixels[y][2] = pixels[y][8] = maximum
    operations = [
        {"op": "set_pixel", "x": x, "y": y, "value": maximum}
        for y in range(height) for x in range(width) if pixels[y][x] == maximum
    ]
    for y in range(3, 6):
        for x in range(3, 8):
            pixels[y][x] = maximum
    operations.append({"op": "flood_fill", "x": 4, "y": 4, "match": 0,
                       "value": maximum, "scan_to_match": 0})
    add("flood-fill", operations, pixels)

    pixels = blank(width, height)
    draw_ellipse(pixels, 5, 4, 6, 4, maximum)
    add("ellipse", [{"op": "ellipse", "x": 5, "y": 4, "width": 6,
                     "height": 4, "value": maximum}], pixels)

    for name, coordinates in {
        "arc": [(5, 3), (4, 4)],
        # Source-derived radius-one row coverage from the reviewed chord/radius
        # walkers: filled variants use half-open scan transitions at the end.
        "segment": [(5, 3)],
        "sector": [(5, 3), (5, 4)],
    }.items():
        pixels = blank(width, height)
        for x, y in coordinates:
            pixels[y][x] = maximum
        add(name, [{"op": name, "x": 5, "y": 4, "x1": 5, "y1": 3,
                    "x2": 4, "y2": 4, "value": maximum}], pixels)
        cases[-1]["oracle_class"] = (
            "independent mathematical model" if name == "arc"
            else "reviewed source-derived radius-one expectation"
        )
        cases[-1]["oracle_provenance"] = (
            "vdp-gl all-the-plots src/displaycontroller.h genericFillSegment/genericFillSector"
        )
        cases[-1]["content_sha256"] = payload_hash({
            key: value for key, value in cases[-1].items() if key != "content_sha256"
        })

    pixels = blank(width, height)
    mask_rows = [0xA0, 0x60]
    for bx, by in ((0, 0), (2, 0), (1, 1), (2, 1)):
        pixels[2 + by][2 + bx] = maximum
    add("bitmap-mask", [{"op": "bitmap_mask", "x": 2, "y": 2, "width": 3,
                         "height": 2, "value": maximum,
                         "data": ":".join(str(value) for value in mask_rows)}], pixels)

    source_values = [maximum, 0, max(1, maximum // 2), maximum]
    for bitmap_kind in ("native", "rgba2222", "rgba8888"):
        pixels = blank(width, height)
        data = []
        for index, logical in enumerate(source_values):
            bx, by = index % 2, index // 2
            pixels[2 + by][4 + bx] = logical
            red, green, blue = rgb_for(format_name, logical)
            if bitmap_kind == "native":
                data.append(logical)
            elif bitmap_kind == "rgba2222":
                data.append(0xC0 | (red >> 6) | ((green >> 6) << 2) | ((blue >> 6) << 4))
            else:
                data.extend((red, green, blue, 255))
        add(f"bitmap-{bitmap_kind}", [{"op": f"bitmap_{bitmap_kind}", "x": 4,
            "y": 2, "width": 2, "height": 2,
            "data": ":".join(str(value) for value in data)}], pixels)

    pixels = blank(width, height)
    transform_values = [maximum, 0, max(1, maximum // 2), maximum]
    transform_data = []
    for index, logical in enumerate(transform_values):
        red, green, blue = rgb_for(format_name, logical)
        transform_data.append(0xC0 | (red >> 6) | ((green >> 6) << 2) | ((blue >> 6) << 4))
        pixels[2 + index // 2][4 + index % 2] = logical
    add("bitmap-transform-identity", [{"op": "bitmap_transform_rgba2222", "x": 4,
        "y": 2, "width": 2, "height": 2,
        "data": ":".join(str(value) for value in transform_data)}], pixels)

    pixels = blank(width, height)
    pixels[4][5] = maximum
    case_count = len(cases)
    add("double-buffer-drawing-plane", [{"op": "set_pixel", "x": 5, "y": 4,
                                          "value": maximum}], pixels)
    cases[case_count]["double_buffered"] = True
    cases[case_count]["expected_visible_bytes"] = [0] * (stride_for(width, bits) * height)
    cases[case_count]["content_sha256"] = payload_hash({
        key: value for key, value in cases[case_count].items() if key != "content_sha256"
    })
    return cases


def artifact(kind: str, fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    data = {
        "schema_version": "1.0.0",
        "artifact_kind": kind,
        "generated_by": GENERATOR,
        "generator_version": GENERATOR_VERSION,
        "source_tag": SOURCE_TAG,
        "profile": PROFILE,
        "oracle_class": "independent mathematical model",
        "implementation_output_prohibited": True,
        "fixtures": fixtures,
    }
    data["fixture_set_sha256"] = payload_hash(fixtures)
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--native-output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-b/fixtures/native-codecs.yaml",
    )
    parser.add_argument(
        "--primitives-output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-b/fixtures/primitives.yaml",
    )
    args = parser.parse_args()

    widths = (1, 2, 3, 7, 8, 9, 15, 16, 17)
    codec_fixtures = [
        codec_case(format_name, width, 3)
        for format_name in FORMATS
        for width in widths
    ]
    codec_fixtures.extend(
        clear_case(format_name, value)
        for format_name, (_, maximum) in FORMATS.items()
        for value in range(maximum + 1)
    )
    primitive_fixtures = [
        case for format_name in FORMATS for case in primitive_cases(format_name)
    ]
    write_canonical(args.native_output.resolve(), artifact("port_003_phase_b_native_codec_fixtures", codec_fixtures))
    write_canonical(args.primitives_output.resolve(), artifact("port_003_phase_b_primitive_fixtures", primitive_fixtures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
