#!/usr/bin/env python3
"""Generate independent PORT-003 Phase D palette/composition fixtures.

This source-derived model implements only the frozen public contracts. It must
not import production headers, execute production binaries, or parse production
output. The later host runner compares production results with this artifact.
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
from dependency_model import write_canonical  # noqa: E402


GENERATOR = "docs/tasks/PORT-003/phase-d/scripts/generate-presentation-fixtures.py"
FORMATS = {
    "PALETTE2": (1, 2),
    "PALETTE4": (2, 4),
    "PALETTE8": (3, 8),
    "PALETTE16": (4, 16),
    "SBGR2222": (8, 64),
}
DEFAULTS = {
    "PALETTE2": [0x00, 0x3F],
    "PALETTE4": [0x00, 0x30, 0x0C, 0x3F],
    "PALETTE8": [0x00, 0x02, 0x08, 0x20, 0x03, 0x0C, 0x30, 0x3F],
    "PALETTE16": [
        0x00, 0x02, 0x08, 0x0A, 0x20, 0x22, 0x28, 0x2A,
        0x15, 0x03, 0x0C, 0x0F, 0x30, 0x33, 0x3C, 0x3F,
    ],
}


def payload_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def packed_rgb(red: int, green: int, blue: int) -> int:
    return (red >> 6) | ((green >> 6) << 2) | ((blue >> 6) << 4)


def rgb888(packed: int) -> list[int]:
    return [(packed & 3) * 85, ((packed >> 2) & 3) * 85, ((packed >> 4) & 3) * 85]


def rgb222_to_hsv(red: int, green: int, blue: int) -> tuple[float, float, float]:
    """Mirror upstream rgb222_to_hsv arithmetic, including its hue branch."""
    r, g, b = red / 3.0, green / 3.0, blue / 3.0
    maximum, minimum = max(r, g, b), min(r, g, b)
    difference = maximum - minimum
    if maximum == minimum:
        hue = 0.0
    elif maximum == r:
        hue = (60.0 * ((g - b) / difference) + 360.0) % 360.0
    elif maximum == g:
        hue = (60.0 * ((b - r) / difference) + 120.0) % 360.0
    else:
        hue = (60.0 * ((r - g) / difference) + 240.0) % 360.0
    saturation = 0.0 if maximum == 0 else (difference / maximum) * 100.0
    return hue, saturation, maximum * 100.0


def nearest_lut(primary: list[int]) -> list[int]:
    result = []
    palette_hsv = [
        rgb222_to_hsv(p & 3, (p >> 2) & 3, (p >> 4) & 3)
        for p in primary
    ]
    for packed in range(64):
        source = rgb222_to_hsv(packed & 3, (packed >> 2) & 3, (packed >> 4) & 3)
        best_index = 0
        best_distance = float("inf")
        for index, target in enumerate(palette_hsv):
            distance = int(
                (source[0] - target[0]) ** 2
                + (source[1] - target[1]) ** 2
                + (source[2] - target[2]) ** 2
            )
            if distance <= best_distance:
                best_index = index
                best_distance = distance
                if distance == 0:
                    break
        result.append(best_index)
    return result


class PaletteModel:
    def __init__(self, format_name: str):
        self.format = format_name
        self.size = FORMATS[format_name][1] if format_name != "SBGR2222" else 0
        self.palettes: dict[int, list[int]] = {}
        self.signals = [{"end_row": 0, "palette_id": 0}]
        self.lut: list[int] = []
        if self.size:
            self.palettes[0] = list(DEFAULTS[format_name])
            self.lut = nearest_lut(self.palettes[0])

    def create(self, palette_id: int) -> bool:
        if not self.size:
            return False
        if palette_id == 0:
            return True
        self.palettes[palette_id] = list(self.palettes[0])
        return True

    def delete(self, palette_id: int) -> None:
        if not self.size or palette_id == 0:
            return
        ids = [item for item in self.palettes if item != 0] if palette_id == 65535 else [palette_id]
        for item in ids:
            if item in self.palettes:
                del self.palettes[item]
                for signal in self.signals:
                    if signal["palette_id"] == item:
                        signal["palette_id"] = 0

    def set_item(self, palette_id: int, index: int, red: int, green: int, blue: int) -> bool:
        if not self.size:
            return False
        if palette_id not in self.palettes and not self.create(palette_id):
            return False
        self.palettes[palette_id][index % self.size] = packed_rgb(red, green, blue)
        return True

    def update_lut(self) -> None:
        if self.size:
            self.lut = nearest_lut(self.palettes[0])

    def update_signals(self, pairs: list[list[int]]) -> None:
        if not self.size:
            return
        if not pairs:
            self.signals = self.signals[:1]
            return
        row = 0
        replacement = []
        for rows, palette_id in pairs:
            row += rows
            replacement.append({
                "end_row": row,
                "palette_id": palette_id if palette_id in self.palettes else 0,
            })
        self.signals = replacement

    def row_palette(self, row: int) -> list[int]:
        for signal in self.signals:
            if row < signal["end_row"]:
                return self.palettes[signal["palette_id"]]
        return self.palettes[self.signals[-1]["palette_id"]]

    def apply(self, operation: dict[str, Any]) -> None:
        name = operation["op"]
        if name == "create":
            self.create(operation["palette_id"])
        elif name == "delete":
            self.delete(operation["palette_id"])
        elif name == "set":
            self.set_item(operation["palette_id"], operation["index"], *operation["rgb"])
        elif name == "update_lut":
            self.update_lut()
        elif name == "signals":
            self.update_signals(operation["pairs"])
        elif name == "reset_signals":
            self.update_signals([[0, 0]])
        else:
            raise ValueError(f"unknown palette operation {name}")

    def expected(self, rows: list[int] | None = None) -> dict[str, Any]:
        result = {
            "palettes": {str(key): value for key, value in sorted(self.palettes.items())},
            "signals": self.signals,
            "drawing_lut": self.lut,
        }
        if rows is not None and self.size:
            result["row_queries"] = rows
            result["row_palettes"] = [self.row_palette(row) for row in rows]
        return result


def encode_pixels(pixels: list[list[int]], bits: int) -> list[int]:
    stride = (len(pixels[0]) * bits + 7) // 8
    output: list[int] = []
    for row in pixels:
        encoded = [0] * stride
        if bits == 8:
            encoded[:] = [value & 0x3F for value in row]
        else:
            for x, value in enumerate(row):
                for source_bit in range(bits):
                    stream_bit = x * bits + source_bit
                    bit = (value >> (bits - source_bit - 1)) & 1
                    encoded[stream_bit // 8] |= bit << (7 - stream_bit % 8)
        output.extend(encoded)
    return output


def base_rgb(model: PaletteModel, pixels: list[list[int]], copper: bool) -> list[list[list[int]]]:
    result = []
    for y, row in enumerate(pixels):
        palette = model.row_palette(y) if copper and model.size else model.palettes.get(0)
        result.append([rgb888(value if palette is None else palette[value % len(palette)]) for value in row])
    return result


def overlay_pixel(overlay: dict[str, Any], source_index: int) -> tuple[int, bool]:
    if overlay["format"] == "RGBA2222":
        value = overlay["data"][source_index]
        return value & 0x3F, bool(value & 0xC0)
    offset = source_index * 4
    red, green, blue, alpha = overlay["data"][offset : offset + 4]
    return packed_rgb(red, green, blue), alpha != 0


def compose_overlays(base: list[list[list[int]]], overlays: list[dict[str, Any]]) -> list[list[list[int]]]:
    output = [[list(pixel) for pixel in row] for row in base]
    role_order = {"text": 0, "hardware": 1, "mouse": 2, "software": 3}
    ordered = sorted(overlays, key=lambda item: (role_order[item["role"]], item.get("index", 0)))
    height, width = len(output), len(output[0])
    for overlay in ordered:
        if overlay["role"] == "software" or not overlay.get("visible", True) or not overlay.get("allow_draw", True):
            continue
        for sy in range(overlay["height"]):
            y = overlay["y"] + sy
            if not 0 <= y < height:
                continue
            for sx in range(overlay["width"]):
                x = overlay["x"] + sx
                if not 0 <= x < width:
                    continue
                packed, opaque = overlay_pixel(overlay, sy * overlay["width"] + sx)
                if not opaque:
                    continue
                if overlay["format"] == "RGBA2222" and overlay.get("paint", "Set") == "XOR":
                    current = packed_rgb(*output[y][x])
                    output[y][x] = rgb888(current ^ packed)
                else:
                    output[y][x] = rgb888(packed)
    return output


def palette_case(case_id: str, format_name: str, operations: list[dict[str, Any]], rows: list[int] | None = None) -> dict[str, Any]:
    model = PaletteModel(format_name)
    for operation in operations:
        model.apply(operation)
    case = {
        "id": case_id,
        "format": format_name,
        "operations": operations,
        "expected": model.expected(rows),
    }
    case["content_sha256"] = payload_hash(case)
    return case


def composition_case(
    case_id: str,
    format_name: str,
    pixels: list[list[int]],
    operations: list[dict[str, Any]],
    overlays: list[dict[str, Any]],
    *,
    double_buffered: bool = False,
    drawing_pixels: list[list[int]] | None = None,
) -> dict[str, Any]:
    model = PaletteModel(format_name)
    for operation in operations:
        model.apply(operation)
    bits = FORMATS[format_name][0]
    readback = base_rgb(
        model, drawing_pixels if drawing_pixels is not None else pixels, False
    )
    presented_base = base_rgb(model, pixels, True)
    composed = compose_overlays(presented_base, overlays)
    case = {
        "id": case_id,
        "format": format_name,
        "width": len(pixels[0]),
        "height": len(pixels),
        "double_buffered": double_buffered,
        "selected_plane": "visible",
        "visible_pixels": pixels,
        "drawing_pixels": drawing_pixels if drawing_pixels is not None else pixels,
        "visible_native_bytes": encode_pixels(pixels, bits),
        "drawing_native_bytes": encode_pixels(drawing_pixels if drawing_pixels is not None else pixels, bits),
        "palette_operations": operations,
        "overlays": overlays,
        "expected_readback_rgb": readback,
        "expected_composed_rgb": composed,
    }
    case["content_sha256"] = payload_hash(case)
    return case


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-d/fixtures/presentation.yaml",
    )
    args = parser.parse_args()

    palette_cases = [
        palette_case(f"defaults-{name.lower()}", name, [])
        for name in ("PALETTE2", "PALETTE4", "PALETTE8", "PALETTE16", "SBGR2222")
    ]
    palette_cases.extend([
        palette_case(
            "palette4-copy-wrap-implicit-and-explicit-lut",
            "PALETTE4",
            [
                {"op": "set", "palette_id": 0, "index": 5, "rgb": [255, 0, 255]},
                {"op": "create", "palette_id": 42},
                {"op": "set", "palette_id": 0, "index": 1, "rgb": [0, 0, 255]},
                {"op": "set", "palette_id": 7, "index": 6, "rgb": [255, 255, 0]},
                {"op": "update_lut"},
            ],
        ),
        palette_case(
            "palette8-delete-referenced-and-all",
            "PALETTE8",
            [
                {"op": "create", "palette_id": 10},
                {"op": "create", "palette_id": 20},
                {"op": "signals", "pairs": [[2, 10], [2, 20]]},
                {"op": "delete", "palette_id": 10},
                {"op": "delete", "palette_id": 65535},
            ],
            [0, 1, 2, 99],
        ),
        palette_case(
            "palette2-unknown-zero-row-and-late-create",
            "PALETTE2",
            [
                {"op": "create", "palette_id": 5},
                {"op": "signals", "pairs": [[0, 5], [2, 99], [1, 5]]},
                {"op": "create", "palette_id": 99},
            ],
            [0, 1, 2, 3, 100],
        ),
        palette_case(
            "palette16-reset-and-empty-update",
            "PALETTE16",
            [
                {"op": "create", "palette_id": 9},
                {"op": "signals", "pairs": [[3, 9], [4, 0]]},
                {"op": "signals", "pairs": []},
                {"op": "reset_signals"},
            ],
            [0, 999],
        ),
    ])

    compositions = []
    for name in FORMATS:
        maximum = FORMATS[name][1] - 1
        pixels = [[(x * 3 + y * 5) & maximum for x in range(7)] for y in range(3)]
        compositions.append(composition_case(f"base-{name.lower()}", name, pixels, [], []))

    copper_pixels = [[(x + y) & 3 for x in range(6)] for y in range(6)]
    copper_ops = [
        {"op": "create", "palette_id": 10},
        {"op": "set", "palette_id": 10, "index": 1, "rgb": [255, 0, 255]},
        {"op": "create", "palette_id": 20},
        {"op": "set", "palette_id": 20, "index": 2, "rgb": [0, 255, 255]},
        {"op": "signals", "pairs": [[2, 0], [2, 10], [0, 99], [1, 20]]},
    ]
    compositions.append(composition_case("copper-row-boundaries", "PALETTE4", copper_pixels, copper_ops, []))

    overlays = [
        {"role": "software", "index": 0, "x": 0, "y": 0, "width": 2, "height": 1, "format": "RGBA2222", "paint": "Set", "visible": True, "allow_draw": True, "data": [0xF0, 0xF0]},
        {"role": "hardware", "index": 1, "x": 1, "y": 0, "width": 3, "height": 2, "format": "RGBA2222", "paint": "Set", "visible": True, "allow_draw": True, "data": [0xF0, 0x00, 0xCC, 0xC3, 0xFF, 0xC0]},
        {"role": "text", "x": 0, "y": 0, "width": 3, "height": 1, "format": "RGBA2222", "paint": "XOR", "visible": True, "allow_draw": True, "data": [0xC3, 0xCC, 0x00]},
        {"role": "hardware", "index": 0, "x": -1, "y": 1, "width": 3, "height": 2, "format": "RGBA8888", "paint": "Set", "visible": True, "allow_draw": True, "data": [255, 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 0, 255, 255, 0, 255, 255, 0, 255, 255, 0, 255, 255, 255]},
        {"role": "hardware", "index": 2, "x": 0, "y": 0, "width": 1, "height": 1, "format": "RGBA2222", "paint": "Set", "visible": True, "allow_draw": False, "data": [0xFF]},
        {"role": "mouse", "x": 2, "y": 1, "width": 3, "height": 2, "format": "RGBA2222", "paint": "Set", "visible": True, "allow_draw": True, "data": [0xCF, 0x00, 0xF0, 0xC3, 0xCC, 0xFF]},
    ]
    overlay_ops = [
        {"op": "create", "palette_id": 10},
        {"op": "set", "palette_id": 10, "index": 1, "rgb": [255, 255, 0]},
        {"op": "signals", "pairs": [[1, 0], [1, 10]]},
    ]
    overlay_pixels = [[(x + 2 * y) & 3 for x in range(6)] for y in range(4)]
    compositions.append(composition_case("overlay-order-alpha-xor-clipping", "PALETTE4", overlay_pixels, overlay_ops, overlays))

    visible = [[0, 1, 2, 3], [4, 5, 6, 7]]
    drawing = [[7, 6, 5, 4], [3, 2, 1, 0]]
    compositions.append(composition_case("double-buffer-visible-plane", "PALETTE8", visible, [], [], double_buffered=True, drawing_pixels=drawing))

    allocation_cases = [
        {
            "id": "secondary-palette-allocation-failure",
            "format": "PALETTE4",
            "failure_on_allocation": 1,
            "operation": {"op": "create", "palette_id": 77},
            "expected_result": False,
            "expected_palettes": {"0": DEFAULTS["PALETTE4"]},
            "expected_live_allocations": 0,
        },
        {
            "id": "signal-list-allocation-failure",
            "format": "PALETTE4",
            "precondition": {"op": "signals", "pairs": [[2, 0]]},
            "failure_on_allocation": 1,
            "operation": {"op": "signals", "pairs": [[1, 0], [1, 0]]},
            "expected_result": False,
            "expected_signals": [{"end_row": 2, "palette_id": 0}],
            "expected_live_allocations": 0,
        },
    ]
    for case in allocation_cases:
        case["content_sha256"] = payload_hash(case)

    data = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_d_independent_presentation_fixtures",
        "generated_by": GENERATOR,
        "generator_version": "1.0.0",
        "source_profile": "agon-vdp-v2.16.0-vdp-gl-all-the-plots",
        "oracle_class": "reviewed source-derived model independent of production code and output",
        "palette_cases": palette_cases,
        "composition_cases": compositions,
        "allocation_cases": allocation_cases,
        "summary": {
            "palette_case_count": len(palette_cases),
            "composition_case_count": len(compositions),
            "allocation_case_count": len(allocation_cases),
            "formats": sorted(FORMATS),
        },
    }
    write_canonical(args.output.resolve(), data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
