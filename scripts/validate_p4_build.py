#!/usr/bin/env python3
"""Validate a native P4 build from compile and Ninja action evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import sys


ROOT = Path(__file__).resolve().parents[1]
VDP = ROOT / "vdp"
PROFILES = VDP / "build/p4-profiles.json"


def fail(message: str) -> None:
    raise SystemExit(f"native P4 validation FAIL: {message}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--lcd", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    document = json.loads(PROFILES.read_text())
    if args.profile not in document["profiles"]:
        parser.error("unknown profile")
    profile = document["profiles"][args.profile]
    compile_path = output / "build/compile_commands.json"
    ninja_path = output / "build/build.ninja"
    if not compile_path.is_file() or not ninja_path.is_file():
        fail("missing compile_commands.json or build.ninja")

    commands = json.loads(compile_path.read_text())
    by_source: dict[Path, list[dict]] = {}
    for command in commands:
        source = Path(command["file"]).resolve()
        by_source.setdefault(source, []).append(command)
    selected = [(VDP / item).resolve() for item in profile["sources"]]
    forbidden = [(VDP / item).resolve() for item in profile["forbidden_sources"]]
    problems: list[str] = []
    selected_commands: list[dict] = []
    for source in selected:
        found = by_source.get(source, [])
        if len(found) != 1:
            problems.append(f"{source.relative_to(VDP)} compiled {len(found)} times")
        else:
            selected_commands.append(found[0])
    for source in forbidden:
        if by_source.get(source):
            problems.append(f"forbidden source compiled: {source.relative_to(VDP)}")

    required_definitions = ["AGON_EXTENDER_NATIVE_BUILD=1", *profile["definitions"]]
    if args.lcd:
        required_definitions.append("AGON_EXTENDER_LCD=1")
    for command in selected_commands:
        argv = command.get("arguments") or shlex.split(command["command"])
        joined = "\n".join(argv)
        missing = [item for item in required_definitions if f"-D{item}" not in joined]
        if missing:
            problems.append(f"{Path(command['file']).name} missing definitions: {missing}")
        if "-std=gnu++17" not in argv and Path(command["file"]).suffix != ".c":
            problems.append(f"{Path(command['file']).name} missing C++17 boundary")

    ninja = ninja_path.read_text().replace("$\n  ", "")
    archive_lines = [line for line in ninja.splitlines()
                     if line.startswith("build esp-idf/agon_vdp/libagon_vdp.a:")]
    if len(archive_lines) != 1:
        problems.append(f"application archive edges: {len(archive_lines)}")
        archive_line = ""
    else:
        archive_line = archive_lines[0]
    for command in selected_commands:
        obj = command.get("output")
        if not obj:
            problems.append(f"compile command has no output: {command['file']}")
        elif obj not in archive_line:
            problems.append(f"object absent from application archive: {obj}")
    elf_lines = [line for line in ninja.splitlines()
                 if line.startswith("build agon_extender.elf:")]
    if len(elf_lines) != 1 or "esp-idf/agon_vdp/libagon_vdp.a" not in elf_lines[0]:
        problems.append("application archive absent from ELF link edge")
    if problems:
        fail("; ".join(problems))

    report = {
        "schema_version": 1,
        "profile": args.profile,
        "lcd": args.lcd,
        "compile_actions": len(commands),
        "selected_sources": len(selected),
        "forbidden_sources": len(forbidden),
        "selected_compile_count": len(selected_commands),
        "archive_edge": "esp-idf/agon_vdp/libagon_vdp.a",
        "elf_edge": "agon_extender.elf",
        "result": "PASS",
    }
    report_path = output / "validation.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"native P4 validation PASS: {report_path}")


if __name__ == "__main__":
    main()
