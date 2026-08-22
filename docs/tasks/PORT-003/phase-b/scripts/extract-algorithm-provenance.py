#!/usr/bin/env python3
"""Generate exact upstream algorithm provenance for PORT-003 Phase B.

This is task-local analysis machinery, not firmware.  It deliberately records
the immutable old concrete-controller implementations that inform the P4 port
without making those physical VGA controllers build dependencies.  Anonymous
lambdas are covered by their owning callable's exact source span; promoting
them to independent records would invent an API boundary that upstream does
not have.
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

from dependency_model import (  # noqa: E402
    load_data,
    sha256_file,
    source_span,
    typed_id,
    write_canonical,
)


GENERATOR_VERSION = "1.0.0"
SOURCE_ID = "source:vdp-gl:all-the-plots"
EXPECTED_COMMIT = "ac2dd5986daf496c43ae8e7fe41836274aec54a0"
SYMBOL_INDEX = "docs/tasks/SETUP-003/generated/symbols.yaml"

DEPTHS = (2, 4, 8, 16, 64)
DEPTH_FILES = {
    f"src/dispdrivers/vga{depth}controller.{suffix}"
    for depth in DEPTHS
    for suffix in ("cpp", "h")
}
COMMON_FILES = {"src/displaycontroller.cpp", "src/displaycontroller.h"}
SUPPORT_FILES = {
    "src/dispdrivers/vgabasecontroller.cpp",
    "src/dispdrivers/vgabasecontroller.h",
    "src/dispdrivers/vgapalettedcontroller.cpp",
    "src/dispdrivers/vgapalettedcontroller.h",
}
UTILITY_FILES = {"src/fabutils.cpp"}
SELECTED_FILES = COMMON_FILES | SUPPORT_FILES | DEPTH_FILES | UTILITY_FILES

PHASE_B_UTILITY_NAMES = {
    "getBit",
    "getCircleQuadrant",
    "isqrt",
    "quadrantContainsArcPixel",
}

DISPOSITIONS = {
    "retain-common": "Compile the upstream common renderer unchanged when its bounded closure permits it.",
    "adapt-depth-algorithm": "Port the proven algorithm into project-owned depth/storage code with exact inline provenance.",
    "replace-platform": "Replace classic ESP32 allocation, lifecycle, or physical-controller ownership with a P4 project contract.",
    "defer-phase-c": "Defer frame timing, swap-at-frame-edge, queues, or background execution to Phase C.",
    "defer-phase-d": "Defer palette, Copper, cursor, sprite, or presentation-overlay behavior to Phase D.",
    "exclude-physical": "Do not compile classic VGA GPIO, I2S, DMA, modeline, scanline, or ISR machinery.",
}

PHASE_C_NAMES = {
    "addPrimitive",
    "enableBackgroundPrimitiveExecution",
    "getPrimitive",
    "getPrimitiveISR",
    "primitiveExecTask",
    "primitiveReplaceDynamicBuffers",
    "primitivesExecutionWait",
    "processPrimitives",
    "resumeBackgroundPrimitiveExecution",
    "setDoubleBuffered",
    "setProcessPrimitivesOnBlank",
    "suspendBackgroundPrimitiveExecution",
    "swapBuffers",
    "waitForPrimitives",
}

PHASE_D_NAMES = {
    "createPalette",
    "createSignalList",
    "decorateScanLinePixels",
    "deletePalette",
    "deleteSignalList",
    "drawSpriteScanLine",
    "getPaletteSize",
    "getSignalsForScanline",
    "getSprite",
    "hideSprites",
    "rawDrawSpriteScanline",
    "refreshSprites",
    "removeSprites",
    "setItemInPalette",
    "setMouseCursor",
    "setMouseCursorPos",
    "setPaletteItem",
    "setSprites",
    "setupDefaultPalette",
    "showSprites",
    "spritesCount",
    "updateRGB2PaletteLUT",
    "updateSignalList",
}

PLATFORM_NAMES = {
    "allocateViewPort",
    "begin",
    "checkViewPortSize",
    "end",
    "freeBuffers",
    "freeViewPort",
    "init",
    "setResolution",
}

PHYSICAL_NAMES = {
    "ISRHandler",
    "calcRequiredDMABuffersCount",
    "calculateAvailableCyclesForDrawings",
    "convertModelineToTimings",
    "fill",
    "fillHorizBuffers",
    "fillVertBuffers",
    "getDMABuffer",
    "isMultiScanBlackLine",
    "moveScreen",
    "onSetupDMABuffer",
    "packSignals",
    "setDMABufferBlank",
    "setDMABuffersCount",
    "setDMABufferView",
    "setupGPIO",
    "shrinkScreen",
    "startGPIOStream",
}


def clean_cpp(text: str) -> str:
    """Blank comments and literals while preserving byte count and newlines."""

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
                index += 1
                state = "literal"
                continue
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


def line_offsets(text: str) -> list[int]:
    offsets = [0]
    offsets.extend(match.end() for match in re.finditer("\n", text))
    return offsets


def callable_end_line(cleaned: str, offsets: list[int], start_line: int) -> int:
    """Return the exact inclusive end line of a function body or declaration."""

    if start_line < 1 or start_line > len(offsets):
        raise ValueError(f"invalid callable start line {start_line}")
    start = offsets[start_line - 1]
    opening = -1
    for index in range(start, min(len(cleaned), start + 65536)):
        char = cleaned[index]
        if char == ";":
            return cleaned.count("\n", 0, index) + 1
        if char == "{":
            opening = index
            break
    if opening < 0:
        raise ValueError(f"no declaration terminator or body within 64 KiB of line {start_line}")
    depth = 0
    for index in range(opening, len(cleaned)):
        if cleaned[index] == "{":
            depth += 1
        elif cleaned[index] == "}":
            depth -= 1
            if depth == 0:
                return cleaned.count("\n", 0, index) + 1
    raise ValueError(f"unterminated callable body at line {start_line}")


def family_for(path: str) -> str:
    if path in UTILITY_FILES:
        return "common-geometry"
    if path in COMMON_FILES:
        return "common-renderer"
    if "vgabasecontroller" in path:
        return "classic-vga-base"
    if "vgapalettedcontroller" in path:
        return "classic-paletted-base"
    match = re.search(r"vga(2|4|8|16|64)controller", path)
    if match:
        return f"native-depth-{match.group(1)}"
    raise ValueError(path)


def classify(path: str, name: str, scope: str | None = None) -> tuple[str, str]:
    family = family_for(path)
    if name in PHASE_C_NAMES or "BackgroundPrimitive" in name:
        return "defer-phase-c", "Frame service or asynchronous primitive behavior is outside Phase B."
    if (
        name in PHASE_D_NAMES
        or name.startswith(("RGB888toPalette", "RGB2222toPalette"))
        or scope == "fabgl::Sprite"
    ):
        return "defer-phase-d", "Presentation palette, Copper, cursor, or sprite behavior is outside Phase B."
    if name in PLATFORM_NAMES:
        return "replace-platform", "P4 storage and lifecycle require project-owned transactional contracts."
    if name in PHYSICAL_NAMES:
        return "exclude-physical", "The callable implements a classic physical VGA transport assumption."
    if family == "classic-vga-base":
        if name in {"packHVSync", "preparePixelWithSync", "preparePixel", "createRawPixel", "createBlankRawPixel"}:
            return "adapt-depth-algorithm", "Retain only the proven native-save or logical-pixel bit contract."
        return "exclude-physical", "The classic VGA base has no logical-storage role in the P4 controller."
    if family == "classic-paletted-base":
        if name in {"nativePixelFormat", "colorsCount"}:
            return "adapt-depth-algorithm", "The value informs the preserved native-format contract."
        return "defer-phase-d", "The remaining paletted-base behavior belongs to presentation composition."
    if family.startswith("native-depth-"):
        if (
            name in {"instance", "operator ="}
            or name.startswith("~")
            or re.fullmatch(r"VGA(?:2|4|8|16|64)Controller", name)
        ):
            return "replace-platform", "The old concrete controller lifecycle and inheritance are not retained."
        return "adapt-depth-algorithm", "This depth-specific operation informs project-owned native storage code."
    return "retain-common", "The callable is part of the retained common bitmap/controller algorithm surface."


def relevant_symbol(record: dict[str, Any]) -> bool:
    if record.get("owner") != "vdp-gl" or record.get("path") not in SELECTED_FILES:
        return False
    if record.get("kind") not in {"function", "prototype"}:
        return False
    if str(record.get("name", "")).startswith("__anon"):
        return False
    if record.get("path") in UTILITY_FILES:
        return record.get("name") in PHASE_B_UTILITY_NAMES
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--symbols",
        type=Path,
        default=ROOT / SYMBOL_INDEX,
    )
    parser.add_argument(
        "--vdp-gl-root",
        type=Path,
        default=ROOT / "vdp/vendor/vdp-gl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "docs/tasks/PORT-003/phase-b/evidence/algorithm-provenance.yaml",
    )
    args = parser.parse_args()

    symbols_path = args.symbols.resolve()
    source_root = args.vdp_gl_root.resolve()
    symbols = load_data(symbols_path)
    if symbols["source"]["release_tag"] != "v2.16.0":
        raise ValueError("symbol index does not describe agon-vdp v2.16.0")
    if symbols["source"]["vdp_gl_commit"] != EXPECTED_COMMIT:
        raise ValueError("symbol index does not describe the pinned vdp-gl commit")

    missing = sorted(path for path in SELECTED_FILES if not (source_root / path).is_file())
    if missing:
        raise FileNotFoundError(f"missing selected source files: {missing}")

    cache: dict[str, tuple[str, list[int]]] = {}
    records: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str, str]] = set()
    for symbol in symbols["symbols"]:
        if not relevant_symbol(symbol):
            continue
        path = str(symbol["path"])
        name = str(symbol["name"])
        line = int(symbol["line"])
        key = (path, line, name, str(symbol["kind"]))
        if key in seen:
            raise ValueError(f"duplicate symbol tuple: {key}")
        seen.add(key)
        if path not in cache:
            text = (source_root / path).read_text(encoding="utf-8", errors="replace")
            cache[path] = clean_cpp(text), line_offsets(text)
        cleaned, offsets = cache[path]
        end_line = callable_end_line(cleaned, offsets, line)
        scope = symbol.get("scope")
        disposition, rationale = classify(path, name, str(scope) if scope else None)
        qualified_name = f"{scope}::{name}" if scope else name
        records.append(
            {
                "id": typed_id("algorithm", "vdp-gl", path, line, qualified_name),
                "family": family_for(path),
                "symbol": name,
                "qualified_name": qualified_name,
                "kind": symbol["kind"],
                "role": symbol["role"],
                "signature": symbol.get("signature"),
                "disposition": disposition,
                "rationale": rationale,
                "span": source_span(SOURCE_ID, source_root, path, line, end_line, qualified_name),
            }
        )

    records.sort(key=lambda item: item["id"])
    disposition_counts = Counter(item["disposition"] for item in records)
    family_counts = Counter(item["family"] for item in records)
    source_files = [
        {
            "path": path,
            "sha256": sha256_file(source_root / path),
            "family": family_for(path),
        }
        for path in sorted(SELECTED_FILES)
    ]
    data = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_b_algorithm_provenance",
        "generated_by": "docs/tasks/PORT-003/phase-b/scripts/extract-algorithm-provenance.py",
        "generator_version": GENERATOR_VERSION,
        "diagnostic_status": "source-derived design evidence; not behavior qualification",
        "source": {
            "source_id": SOURCE_ID,
            "identity": "all-the-plots",
            "commit": EXPECTED_COMMIT,
            "root_placeholder": "${VDP_GL_VENDOR_ROOT}",
        },
        "inputs": [
            {
                "path": SYMBOL_INDEX,
                "sha256": sha256_file(symbols_path),
                "role": "pinned Universal Ctags symbol starts and declarations",
            }
        ],
        "scope": {
            "files": source_files,
            "anonymous_callable_policy": "covered by exact owning-callable spans",
            "dispositions": [
                {"id": name, "meaning": meaning}
                for name, meaning in DISPOSITIONS.items()
            ],
        },
        "algorithms": records,
        "summary": {
            "file_count": len(source_files),
            "algorithm_count": len(records),
            "counts_by_family": dict(sorted(family_counts.items())),
            "counts_by_disposition": dict(sorted(disposition_counts.items())),
        },
    }
    write_canonical(args.output.resolve(), data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
