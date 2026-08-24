#!/usr/bin/env python3
"""Extract exact palette/Copper/overlay provenance for PORT-003 Phase D.

This task-local generator fingerprints observable source contracts separately
from the classic VGA signal-table, DMA, and ISR mechanisms that implement them
upstream. It is evidence machinery, not firmware and not a behavior oracle.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))

from dependency_model import sha256_file, source_span, typed_id, write_canonical  # noqa: E402


# owner, path, first line, symbol, disposition, rationale
CALLABLES = (
    ("agon-vdp", "video/agon_screen.h", 51, "updateRGB2PaletteLUT", "retain-facade-contract", "The official facade explicitly rebuilds palette-0 drawing quantization."),
    ("agon-vdp", "video/agon_screen.h", 60, "createPalette", "retain-facade-contract", "The official facade gates secondary palette creation by color depth."),
    ("agon-vdp", "video/agon_screen.h", 69, "deletePalette", "retain-facade-contract", "The official facade gates secondary palette deletion by color depth."),
    ("agon-vdp", "video/agon_screen.h", 78, "setItemInPalette", "retain-facade-contract", "The official facade exposes palette-ID entry mutation."),
    ("agon-vdp", "video/agon_screen.h", 87, "updateSignalList", "retain-facade-contract", "The official facade exposes Copper row/palette selection."),
    ("agon-vdp", "video/agon_screen.h", 105, "setPaletteItem", "retain-facade-contract", "Ordinary palette mutation targets palette 0."),
    ("agon-vdp", "video/agon_screen.h", 115, "getPaletteIndex", "retain-facade-contract", "Official reverse lookup returns the first matching logical entry."),
    ("agon-vdp", "video/agon_screen.h", 134, "setLogicalPalette", "retain-facade-contract", "VDU 19 updates the public physical palette and explicitly rebuilds drawing lookup."),
    ("agon-vdp", "video/agon_screen.h", 163, "resetPalette", "retain-facade-contract", "Palette reset populates the active logical depth and rebuilds drawing lookup."),
    ("agon-vdp", "video/agon_screen.h", 172, "restorePalette", "retain-facade-contract", "Mode integration restores official per-depth defaults outside Teletext."),
    ("agon-vdp", "video/vdu_sys.h", 728, "vdu_sys_copper", "retain-parser-contract", "Official Copper commands consume palette IDs, entries, and buffer-backed signal lists."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 142, "setResolution", "split-observable-from-physical", "Palette/list reset is retained; VGA viewport, DMA, GPIO, and ISR startup are excluded."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 192, "getPaletteSize", "retain-algorithm", "Native format selects the 2/4/8/16 palette size."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 208, "setPaletteItem", "retain-algorithm", "Default palette mutation delegates to palette ID 0."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 214, "setItemInPalette", "retain-algorithm", "Missing palettes are created, indices wrap, and output is RGB222-quantized."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 232, "updateRGB2PaletteLUT", "retain-algorithm", "Drawing quantization uses HSV distance and its exact tie rule."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 261, "createPalette", "retain-algorithm", "Secondary creation copies palette 0 and may fail allocation."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 285, "deletePalette", "retain-observable-intent", "ID 0 is protected, 65535 means all secondary palettes, and active spans fall back to palette 0."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 321, "updateSignalList", "retain-algorithm", "Row counts accumulate and unknown IDs resolve to palette 0."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 361, "createSignalList", "retain-algorithm", "Additional row spans retain cumulative boundaries and resolved palettes."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 385, "getSignalsForScanline", "retain-algorithm", "The last span extends through all later scanlines."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 405, "decorateScanLinePixels", "replace-platform-compositor", "The visible-row decoration point is retained through the central compositor, not DMA scanout."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 409, "rawDrawSpriteScanline", "adapt-overlay-algorithm", "Retain clipping, alpha, RGB222 conversion, overwrite, and XOR without VGA signal bytes."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 480, "drawSpriteScanLine", "adapt-overlay-algorithm", "Retain text/sprite/mouse order and hardware filtering."),
    ("vdp-gl", "src/displaycontroller.cpp", 652, "setSprites", "retain-common-contract", "Unchanged common code allocates software-sprite backgrounds and excludes hardware sprites from that storage."),
    ("vdp-gl", "src/displaycontroller.cpp", 700, "hideSprites", "retain-common-contract", "Unchanged common code restores software-sprite backgrounds in single-buffer modes."),
    ("vdp-gl", "src/displaycontroller.cpp", 726, "showSprites", "retain-common-contract", "Unchanged common code draws only non-hardware sprites into logical storage."),
    ("vdp-gl", "src/displaycontroller.cpp", 762, "setMouseCursor", "retain-common-contract", "The retained controller owns mouse cursor frame, hotspot, and visibility state."),
    ("vdp-gl", "src/displaycontroller.cpp", 786, "setMouseCursorPos", "retain-common-contract", "The retained controller applies the selected mouse hotspot to cursor position."),
    ("vdp-gl", "src/dispdrivers/vga2controller.cpp", 106, "setupDefaultPalette", "retain-depth-default", "Two-color controller default."),
    ("vdp-gl", "src/dispdrivers/vga4controller.cpp", 132, "setupDefaultPalette", "retain-depth-default", "Four-color controller default."),
    ("vdp-gl", "src/dispdrivers/vga8controller.cpp", 139, "setupDefaultPalette", "retain-depth-default", "Eight-color controller default."),
    ("vdp-gl", "src/dispdrivers/vga16controller.cpp", 124, "setupDefaultPalette", "retain-depth-default", "Sixteen-color controller default."),
    ("vdp-gl", "src/dispdrivers/vga2controller.cpp", 563, "readScreen", "retain-readback-contract", "Paletted readback resolves logical bytes through palette 0, not Copper scanout."),
    ("vdp-gl", "src/dispdrivers/vga4controller.cpp", 593, "readScreen", "retain-readback-contract", "Paletted readback resolves logical bytes through palette 0, not Copper scanout."),
    ("vdp-gl", "src/dispdrivers/vga8controller.cpp", 540, "readScreen", "retain-readback-contract", "Paletted readback resolves logical bytes through palette 0, not Copper scanout."),
    ("vdp-gl", "src/dispdrivers/vga16controller.cpp", 587, "readScreen", "retain-readback-contract", "Paletted readback resolves logical bytes through palette 0, not Copper scanout."),
    ("vdp-gl", "src/dispdrivers/vga64controller.cpp", 552, "readScreen", "retain-readback-contract", "Fixed 64-color readback expands direct RGB222 logical values."),
)


# owner, path, first, last, label, disposition, rationale
REGIONS = (
    ("agon-vdp", "video/agon_palette.h", 14, 69, "official-palette-defaults-and-rgb222-table", "retain-facade-data", "Official mode palettes and the 64-color RGB222 lookup remain authoritative."),
    ("vdp-gl", "src/displaycontroller.h", 651, 688, "sprite-state-contract", "retain-common-contract", "Sprite position, frame, visibility, hardware flag, and paint mode feed retained common or composed paths."),
    ("vdp-gl", "src/displaycontroller.h", 1047, 1051, "text-cursor-binding", "retain-common-contract", "The retained controller stores the optional hardware text cursor sprite."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 63, 92, "palette-construction-and-destruction", "replace-allocation-mechanism", "Project-owned allocator state replaces internal-memory signal tables while preserving observable lifetime."),
    ("vdp-gl", "src/dispdrivers/vgapalettedcontroller.cpp", 177, 190, "dma-row-signal-selection", "exclude-physical-engine", "DMA row setup and scan buffers are classic VGA implementation only."),
    ("vdp-gl", "src/dispdrivers/vga2controller.cpp", 113, 125, "vga2-packed-signal-table", "exclude-physical-engine", "Packed sync/output signal tables are replaced by RGB888 composition."),
    ("vdp-gl", "src/dispdrivers/vga4controller.cpp", 141, 153, "vga4-packed-signal-table", "exclude-physical-engine", "Packed sync/output signal tables are replaced by RGB888 composition."),
    ("vdp-gl", "src/dispdrivers/vga8controller.cpp", 152, 163, "vga8-packed-signal-table", "exclude-physical-engine", "Packed sync/output signal tables are replaced by RGB888 composition."),
    ("vdp-gl", "src/dispdrivers/vga16controller.cpp", 133, 142, "vga16-packed-signal-table", "exclude-physical-engine", "Packed sync/output signal tables are replaced by RGB888 composition."),
)


def clean_cpp(text: str) -> str:
    output = list(text)
    index = 0
    state = "code"
    quote = ""
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and following == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "line-comment"
                continue
            if char == "/" and following == "*":
                output[index] = output[index + 1] = " "
                index += 2
                state = "block-comment"
                continue
            if char in {'"', "'"}:
                quote = char
                output[index] = " "
                state = "literal"
        elif state == "line-comment":
            if char == "\n":
                state = "code"
            else:
                output[index] = " "
        elif state == "block-comment":
            if char == "*" and following == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "code"
                continue
            if char != "\n":
                output[index] = " "
        else:
            if char == "\\" and following:
                output[index] = " "
                if following != "\n":
                    output[index + 1] = " "
                index += 2
                continue
            if char == quote:
                output[index] = " "
                state = "code"
            elif char != "\n":
                output[index] = " "
        index += 1
    return "".join(output)


def callable_end_line(text: str, start_line: int) -> int:
    cleaned = clean_cpp(text)
    offsets = [0]
    offsets.extend(match.end() for match in re.finditer("\n", text))
    start = offsets[start_line - 1]
    opening = -1
    for index in range(start, min(len(cleaned), start + 65536)):
        if cleaned[index] == ";":
            return cleaned.count("\n", 0, index) + 1
        if cleaned[index] == "{":
            opening = index
            break
    if opening < 0:
        raise ValueError(f"no callable body near line {start_line}")
    depth = 0
    for index in range(opening, len(cleaned)):
        if cleaned[index] == "{":
            depth += 1
        elif cleaned[index] == "}":
            depth -= 1
            if depth == 0:
                return cleaned.count("\n", 0, index) + 1
    raise ValueError(f"unterminated callable at line {start_line}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agon-vdp-root", type=Path, default=ROOT / "vdp")
    parser.add_argument("--vdp-gl-root", type=Path, default=ROOT / "vdp/vendor/vdp-gl")
    parser.add_argument(
        "--agon-docs-root",
        type=Path,
        default=ROOT.parents[1] / "agon-docs",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-d/evidence/presentation-provenance.yaml",
    )
    args = parser.parse_args()
    roots = {"agon-vdp": args.agon_vdp_root.resolve(), "vdp-gl": args.vdp_gl_root.resolve()}
    source_ids = {"agon-vdp": "source:agon-vdp:v2.16.0", "vdp-gl": "source:vdp-gl:all-the-plots"}

    records: list[dict[str, Any]] = []
    for owner, path, first, symbol, disposition, rationale in CALLABLES:
        source = roots[owner] / path
        end = callable_end_line(source.read_text(encoding="utf-8", errors="replace"), first)
        records.append({
            "id": typed_id("presentation-provenance", owner, path, first, symbol),
            "owner": owner,
            "kind": "callable",
            "symbol": symbol,
            "disposition": disposition,
            "rationale": rationale,
            "span": source_span(source_ids[owner], roots[owner], path, first, end, symbol),
        })
    for owner, path, first, last, label, disposition, rationale in REGIONS:
        records.append({
            "id": typed_id("presentation-provenance", owner, path, first, label),
            "owner": owner,
            "kind": "source-region",
            "symbol": label,
            "disposition": disposition,
            "rationale": rationale,
            "span": source_span(source_ids[owner], roots[owner], path, first, last, label),
        })
    records.sort(key=lambda item: item["id"])
    identities = [(item["owner"], item["span"]["path"], item["span"]["start_line"], item["symbol"]) for item in records]
    if len(identities) != len(set(identities)):
        raise ValueError("duplicate presentation provenance identity")
    files = sorted({(item["owner"], item["span"]["path"]) for item in records})
    counts = Counter(item["disposition"] for item in records)
    docs_path = args.agon_docs_root.resolve() / "docs/vdp/Copper-API.md"
    data = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_d_presentation_provenance",
        "generated_by": "docs/tasks/PORT-003/phase-d/scripts/extract-presentation-provenance.py",
        "diagnostic_status": "source-derived design evidence; not runtime qualification",
        "documentation": [{"path": "docs/vdp/Copper-API.md", "sha256": sha256_file(docs_path)}],
        "sources": [{"owner": owner, "path": path, "sha256": sha256_file(roots[owner] / path)} for owner, path in files],
        "records": records,
        "findings": {
            "logical_presentation_split": "palette 0 owns drawing lookup and logical readback; Copper selects presentation palettes only",
            "software_hardware_split": "unchanged common code draws software sprites into logical storage; scanout code overlays hardware sprites and cursors",
            "overlay_order": "text cursor, ascending hardware sprites, then mouse cursor",
            "excluded_mechanism": "classic packed signal maps, DMA rows, GPIO/I2S, and scanline ISR are not retained",
        },
        "summary": {
            "record_count": len(records),
            "source_file_count": len(files),
            "counts_by_disposition": dict(sorted(counts.items())),
        },
    }
    write_canonical(args.output.resolve(), data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
