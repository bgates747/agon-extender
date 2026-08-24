#!/usr/bin/env python3
"""Extract bounded Phase E mode/lifecycle provenance from immutable inputs."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import sha256_file, write_canonical  # noqa: E402


SOURCE_FUNCTIONS = (
    ("screen-factory", "video/agon_screen.h", "getVGAController"),
    ("screen-controller-update", "video/agon_screen.h", "updateVGAController"),
    ("screen-resolution", "video/agon_screen.h", "changeResolution"),
    ("screen-mode-table", "video/agon_screen.h", "changeMode"),
    ("screen-palette-set", "video/agon_screen.h", "setLogicalPalette"),
    ("screen-palette-reset", "video/agon_screen.h", "restorePalette"),
    ("screen-completion", "video/agon_screen.h", "waitPlotCompletion"),
    ("screen-buffer-swap", "video/agon_screen.h", "switchBuffer"),
    ("screen-cursor-position", "video/agon_screen.h", "setMouseCursorPos"),
    ("vdu-mode-lifecycle", "video/vdu.h", "VDUStreamProcessor::vdu_mode"),
    ("mode-information-packet", "video/vdu_sys.h", "VDUStreamProcessor::sendModeInformation"),
    ("context-mode-reset", "video/vdu_context.h", "VDUStreamProcessor::resetAllContexts"),
    ("context-frame-observation", "video/context.h", "Context::checkForVSYNC"),
    ("teletext-initialization", "video/agon_ttxt.h", "agon_ttxt::init"),
    ("mouse-positioner-reset", "video/agon_ps2.h", "resetMousePositioner"),
)

DOCUMENT_SECTIONS = (
    ("vdu-22-contract", "docs/vdp/VDU-Commands.md", "## `VDU 22, n`", "## `VDU 23"),
    ("screen-mode-contract", "docs/vdp/Screen-Modes.md", "# Screen Modes", None),
    ("mode-packet-contract", "docs/vdp/System-Commands.md", "## `VDU 23, 0, &86`", "## `VDU 23, 0, &87`"),
    ("context-reset-contract", "docs/vdp/Context-Management-API.md", "# VDU 23, 0, &C8: Context Management API", None),
    ("callback-contract", "docs/vdp/Buffered-Commands-API.md", "## Command 80", "## Command 81"),
)


def git_commit(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_function(path: Path, name: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"(?:^|\n)[^\n;]*\b{re.escape(name)}\s*\([^;]*?\)\s*\{{", text)
    if match is None:
        raise ValueError(f"{path}: function not found: {name}")
    start = match.start() + (1 if text[match.start():].startswith("\n") else 0)
    brace = text.find("{", start, match.end())
    depth = 0
    in_string = False
    escaped = False
    index = brace
    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                snippet = text[start:end]
                return {
                    "start_line": line_number(text, start),
                    "end_line": line_number(text, end - 1),
                    "sha256": __import__("hashlib").sha256(snippet.encode()).hexdigest(),
                }
        index += 1
    raise ValueError(f"{path}: unterminated function: {name}")


def extract_section(path: Path, start_marker: str, end_marker: str | None) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    start = text.find(start_marker)
    if start < 0:
        raise ValueError(f"{path}: section not found: {start_marker}")
    end = text.find(end_marker, start + len(start_marker)) if end_marker else len(text)
    if end < 0:
        raise ValueError(f"{path}: section end not found: {end_marker}")
    snippet = text[start:end].rstrip() + "\n"
    return {
        "start_line": line_number(text, start),
        "end_line": line_number(text, end - 1),
        "sha256": __import__("hashlib").sha256(snippet.encode()).hexdigest(),
    }


def modelines(vdp_gl: Path) -> dict[str, dict[str, int]]:
    path = vdp_gl / "src/fabglconf.h"
    text = path.read_text(encoding="utf-8")
    result = {}
    pattern = re.compile(
        r'^#define\s+(\w+)\s+"\\"(\d+)x(\d+)@(\d+)Hz\\"[^\n]*"$', re.MULTILINE
    )
    for match in pattern.finditer(text):
        result[match.group(1)] = {
            "width": int(match.group(2)),
            "height": int(match.group(3)),
            "refresh_hz": int(match.group(4)),
        }
    if not result:
        raise ValueError(f"{path}: no modelines parsed")
    return result


def parse_resolution_call(text: str, modeline_data: dict[str, dict[str, int]]) -> dict[str, Any]:
    match = re.search(r"changeResolution\((\d+),\s*(\w+)(?:,\s*(true|false))?\)", text)
    if match is None:
        raise ValueError(f"unrecognized mode body: {text.strip()}")
    name = match.group(2)
    if name not in modeline_data:
        raise ValueError(f"unknown modeline: {name}")
    return {
        "colours": int(match.group(1)),
        "modeline": name,
        **modeline_data[name],
        "double_buffered": match.group(3) == "true",
    }


def mode_table(agon_vdp: Path, vdp_gl: Path) -> list[dict[str, Any]]:
    path = agon_vdp / "video/agon_screen.h"
    text = path.read_text(encoding="utf-8")
    function = extract_function(path, "changeMode")
    lines = text.splitlines(keepends=True)
    body = "".join(lines[function["start_line"] - 1:function["end_line"]])
    modeline_data = modelines(vdp_gl)
    records: list[dict[str, Any]] = []
    cases = list(re.finditer(r"\bcase\s+(\d+)\s*:", body))
    for index, case in enumerate(cases):
        mode = int(case.group(1))
        end = cases[index + 1].start() if index + 1 < len(cases) else body.find("\n\n\t}", case.end())
        case_body = body[case.end():end]
        if mode <= 3 and "legacyModes == true" in case_body:
            true_body, false_body = case_body.split("} else {", 1)
            records.append({"mode": mode, "legacy_modes": True, **parse_resolution_call(true_body, modeline_data)})
            records.append({"mode": mode, "legacy_modes": False, **parse_resolution_call(false_body, modeline_data)})
        else:
            record = {"mode": mode, "legacy_modes": "either", **parse_resolution_call(case_body, modeline_data)}
            if mode == 7:
                record["teletext"] = True
            records.append(record)
    expected_modes = set(range(31)) | {129, 130, 132, 133, 134, 136, 137, 138, 139, 140, 141, 142, 143, 145, 146, 149, 150, 151, 153, 154, 156, 157, 158}
    if {record["mode"] for record in records} != expected_modes:
        raise ValueError("parsed mode IDs differ from the pinned complete mode switch")
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agon-vdp", type=Path, default=ROOT.parents[1] / "agon-vdp")
    parser.add_argument("--agon-docs", type=Path, default=ROOT.parents[1] / "agon-docs")
    parser.add_argument("--vdp-gl", type=Path, default=ROOT / "vdp/vendor/vdp-gl")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/tasks/PORT-003/phase-e/evidence/mode-provenance.yaml")
    args = parser.parse_args()
    agon_vdp, agon_docs, vdp_gl = args.agon_vdp.resolve(), args.agon_docs.resolve(), args.vdp_gl.resolve()
    expected_commit = "c7ac293d2aa81ddfa693390549bcd909069c8fc3"
    if git_commit(agon_vdp) != expected_commit:
        raise ValueError("agon-vdp root is not checked out at v2.16.0")
    records = []
    for record_id, relative, function in SOURCE_FUNCTIONS:
        path = agon_vdp / relative
        records.append({
            "id": record_id, "owner": "agon-vdp", "path": relative,
            "function": function, "file_sha256": sha256_file(path),
            **extract_function(path, function),
        })
    documents = []
    for record_id, relative, start, end in DOCUMENT_SECTIONS:
        path = agon_docs / relative
        documents.append({
            "id": record_id, "owner": "agon-docs", "path": relative,
            "file_sha256": sha256_file(path), **extract_section(path, start, end),
        })
    output = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_e_mode_provenance",
        "generated_by": "docs/tasks/PORT-003/phase-e/scripts/extract-mode-provenance.py",
        "source_identities": {
            "agon_vdp": {"identity": "v2.16.0", "commit": expected_commit},
            "vdp_gl": {"identity": "all-the-plots", "commit": "ac2dd5986daf496c43ae8e7fe41836274aec54a0"},
        },
        "source_regions": records,
        "documentation_regions": documents,
        "mode_table": mode_table(agon_vdp, vdp_gl),
    }
    write_canonical(args.output.resolve(), output)
    print(f"wrote {len(records)} source regions, {len(documents)} documentation regions, and {len(output['mode_table'])} mode variants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
