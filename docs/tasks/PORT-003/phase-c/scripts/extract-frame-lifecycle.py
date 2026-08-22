#!/usr/bin/env python3
"""Extract the bounded upstream frame/queue lifecycle used by PORT-003 Phase C.

This is task-local evidence machinery, not firmware.  It fingerprints behavior
that must remain recognizable while distinguishing it from the classic VGA
interrupt, DMA, and Xtensa scheduling mechanisms that must not enter the P4
build.
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


SYMBOL_INDEX = "docs/tasks/SETUP-003/generated/symbols.yaml"
VDP_GL_COMMIT = "ac2dd5986daf496c43ae8e7fe41836274aec54a0"

# owner, path, start line, symbol, disposition, rationale
CALLABLES = (
    ("agon-vdp", "video/agon_screen.h", 477, "waitPlotCompletion", "retain-facade-contract", "Official completion facade delegates to Canvas."),
    ("agon-vdp", "video/agon_screen.h", 484, "switchBuffer", "retain-facade-contract", "Official single/double-buffer behavior requires a logical frame edge."),
    ("agon-vdp", "video/context.h", 1312, "checkForVSYNC", "retain-facade-contract", "Official contexts observe frame-counter changes and frame waits."),
    ("vdp-gl", "src/canvas.cpp", 85, "waitCompletion", "retain-common-contract", "Caller-visible completion delegates to the retained queue-depth poll."),
    ("vdp-gl", "src/canvas.cpp", 99, "beginUpdate", "retain-common-contract", "Canvas exposes nested rendering suspension."),
    ("vdp-gl", "src/canvas.cpp", 105, "endUpdate", "retain-common-contract", "Canvas resumes rendering after an update scope."),
    ("vdp-gl", "src/canvas.cpp", 647, "swapBuffers", "retain-common-contract", "Canvas submits a notifying swap and waits for completion."),
    ("vdp-gl", "src/canvas.cpp", 713, "noOp", "retain-common-contract", "Official single-buffer frame waits enqueue a Flush marker."),
    ("vdp-gl", "src/displaycontroller.cpp", 495, "setDoubleBuffered", "retain-common-contract", "Queue capacity and plane mode remain coupled in common code."),
    ("vdp-gl", "src/displaycontroller.cpp", 525, "addPrimitive", "retain-common-contract", "Retain submission, dynamic payload ownership, immediate drawing, and swap notification."),
    ("vdp-gl", "src/displaycontroller.cpp", 547, "primitiveReplaceDynamicBuffers", "retain-common-contract", "Queued path and transform payloads require owned lifetime until execution."),
    ("vdp-gl", "src/displaycontroller.cpp", 590, "getPrimitiveISR", "exclude-physical-trigger", "ISR dequeue is tied to the old physical execution path."),
    ("vdp-gl", "src/displaycontroller.cpp", 596, "getPrimitive", "retain-common-contract", "The P4 frame task uses the existing task-context dequeue unchanged."),
    ("vdp-gl", "src/displaycontroller.cpp", 603, "waitForPrimitives", "retain-common-contract", "Retain the upstream helper's queue non-empty wait."),
    ("vdp-gl", "src/displaycontroller.cpp", 610, "primitivesExecutionWait", "retain-common-contract", "Retain upstream queue-depth completion behavior in the strict baseline."),
    ("vdp-gl", "src/displaycontroller.cpp", 622, "enableBackgroundPrimitiveExecution", "retain-common-contract", "Retain upstream mode switching, queue drain, and platform suspension calls."),
    ("vdp-gl", "src/displaycontroller.cpp", 638, "processPrimitives", "retain-common-contract", "Retain immediate draining, payload lifetime, and trailing Refresh behavior."),
    ("vdp-gl", "src/dispdrivers/vgabasecontroller.cpp", 346, "suspendBackgroundPrimitiveExecution", "replace-platform-task", "Busy-wait suspension over VGA task flags is not a P4 synchronization contract."),
    ("vdp-gl", "src/dispdrivers/vgabasecontroller.cpp", 356, "resumeBackgroundPrimitiveExecution", "replace-platform-task", "The P4 service requires project-owned nested suspension."),
    ("vdp-gl", "src/dispdrivers/vgabasecontroller.cpp", 769, "swapBuffers", "adapt-logical-swap", "Only logical drawing/visible identity exchange is retained."),
    ("vdp-gl", "src/dispdrivers/vgabasecontroller.cpp", 781, "primitiveExecTask", "replace-platform-task", "Retain bounded task-context execution but replace VSYNC notification and Xtensa cycle budgets."),
    ("vdp-gl", "src/dispdrivers/vgacontroller.cpp", 131, "VSyncInterrupt", "exclude-physical-trigger", "The old I2S EOF ISR supplies timing and rendering and must not enter the P4 build."),
)

# owner, path, first line, last line, label, disposition, rationale
REGIONS = (
    ("agon-vdp", "video/context.h", 19, 19, "last-frame-counter-global", "retain-facade-contract", "Official contexts retain the last observed frame count."),
    ("agon-vdp", "video/context.h", 1013, 1021, "frame-counter-variable-writes", "retain-facade-contract", "VDP variables write the low/high halves of the live 32-bit counter."),
    ("vdp-gl", "src/displaycontroller.h", 211, 218, "swap-primitive-contract", "retain-common-contract", "SwapBuffers carries the waiting task identity."),
    ("vdp-gl", "src/displaycontroller.h", 1208, 1214, "queue-and-background-state", "retain-common-contract", "Private queue/background state remains owned by unchanged common code."),
    ("vdp-gl", "src/dispdrivers/vgabasecontroller.h", 289, 292, "writable-frame-counter", "retain-facade-contract", "The official facade expects a directly writable 32-bit-compatible field."),
    ("vdp-gl", "src/displaycontroller.cpp", 927, 938, "swap-execution-and-notification", "retain-common-contract", "Retain visibility change followed by immediate submitter notification."),
    ("vdp-gl", "src/dispdrivers/vga2controller.cpp", 775, 783, "vga2-frame-edge", "exclude-physical-trigger", "Physical scan completion increments the counter and wakes the old task."),
    ("vdp-gl", "src/dispdrivers/vga4controller.cpp", 809, 817, "vga4-frame-edge", "exclude-physical-trigger", "Physical scan completion increments the counter and wakes the old task."),
    ("vdp-gl", "src/dispdrivers/vga8controller.cpp", 774, 782, "vga8-frame-edge", "exclude-physical-trigger", "Physical scan completion increments the counter and wakes the old task."),
    ("vdp-gl", "src/dispdrivers/vga16controller.cpp", 817, 825, "vga16-frame-edge", "exclude-physical-trigger", "Physical scan completion increments the counter and wakes the old task."),
    ("vdp-gl", "src/dispdrivers/vga64controller.cpp", 741, 749, "vga64-frame-edge", "exclude-physical-trigger", "Physical scan completion increments the counter and wakes the old task."),
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
        raise ValueError(f"no body or terminator near line {start_line}")
    depth = 0
    for index in range(opening, len(cleaned)):
        if cleaned[index] == "{":
            depth += 1
        elif cleaned[index] == "}":
            depth -= 1
            if depth == 0:
                return cleaned.count("\n", 0, index) + 1
    raise ValueError(f"unterminated body at line {start_line}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", type=Path, default=ROOT / SYMBOL_INDEX)
    parser.add_argument("--agon-vdp-root", type=Path, default=ROOT / "vdp")
    parser.add_argument("--vdp-gl-root", type=Path, default=ROOT / "vdp/vendor/vdp-gl")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/tasks/PORT-003/phase-c/evidence/frame-lifecycle.yaml")
    args = parser.parse_args()

    symbols = load_data(args.symbols.resolve())
    if symbols["source"]["release_tag"] != "v2.16.0" or symbols["source"]["vdp_gl_commit"] != VDP_GL_COMMIT:
        raise ValueError("symbol index is not the accepted official baseline")
    roots = {"agon-vdp": args.agon_vdp_root.resolve(), "vdp-gl": args.vdp_gl_root.resolve()}
    source_ids = {"agon-vdp": "source:agon-vdp:v2.16.0", "vdp-gl": "source:vdp-gl:all-the-plots"}

    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int, str]] = set()
    for owner, path, line, name, disposition, rationale in CALLABLES:
        matches = [
            item for item in symbols["symbols"]
            if item.get("owner") == owner and item.get("path") == path
            and int(item.get("line", 0)) == line and item.get("name") == name
        ]
        if len(matches) != 1:
            raise ValueError(f"expected one symbol for {(owner, path, line, name)}, found {len(matches)}")
        source = roots[owner] / path
        end_line = callable_end_line(source.read_text(encoding="utf-8", errors="replace"), line)
        key = (owner, path, line, name)
        if key in seen:
            raise ValueError(f"duplicate lifecycle record {key}")
        seen.add(key)
        records.append({
            "id": typed_id("frame-lifecycle", owner, path, line, name),
            "owner": owner,
            "kind": "callable",
            "symbol": name,
            "qualified_name": f"{matches[0].get('scope')}::{name}" if matches[0].get("scope") else name,
            "signature": matches[0].get("signature"),
            "disposition": disposition,
            "rationale": rationale,
            "span": source_span(source_ids[owner], roots[owner], path, line, end_line, name),
        })

    for owner, path, first, last, label, disposition, rationale in REGIONS:
        source = roots[owner] / path
        records.append({
            "id": typed_id("frame-lifecycle", owner, path, first, label),
            "owner": owner,
            "kind": "source-region",
            "symbol": label,
            "disposition": disposition,
            "rationale": rationale,
            "span": source_span(source_ids[owner], roots[owner], path, first, last, label),
        })

    records.sort(key=lambda item: item["id"])
    identity = [(item["owner"], item["span"]["path"], item["span"]["start_line"], item["symbol"]) for item in records]
    if len(identity) != len(set(identity)):
        raise ValueError("duplicate lifecycle identity tuple")
    files = sorted({(item["owner"], item["span"]["path"]) for item in records})
    counts = Counter(item["disposition"] for item in records)
    data = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_c_frame_lifecycle_provenance",
        "generated_by": "docs/tasks/PORT-003/phase-c/scripts/extract-frame-lifecycle.py",
        "diagnostic_status": "source-derived design evidence; not runtime qualification",
        "inputs": [{"path": SYMBOL_INDEX, "sha256": sha256_file(args.symbols.resolve())}],
        "sources": [
            {"owner": owner, "path": path, "sha256": sha256_file(roots[owner] / path)}
            for owner, path in files
        ],
        "records": records,
        "findings": {
            "queue_depth_wait_behavior": "primitivesExecutionWait observes queued count only; dequeued execution is not represented",
            "derived_override_limit": "queue and background state are private and completion methods are non-virtual",
            "swap_order": "logical swap precedes submitter notification",
            "frame_edge_order": "old controllers increment frameCounter before waking or executing frame-bounded primitive work",
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
