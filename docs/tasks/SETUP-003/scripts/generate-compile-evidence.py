#!/usr/bin/env python3
"""Generate compact SETUP-003 Work 4 evidence from PlatformIO compiledb.

The complete PlatformIO database includes thousands of ESP-IDF implementation
units and embeds host-specific absolute paths. This extractor retains commands
for the VDP sketch and its declared libraries, normalizes machine-local paths,
and asks the target compiler for the actual video.ino dependency closure and
include tree. It deliberately does not repair preprocessing failures.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess


SCHEMA_VERSION = 1
GENERATOR_VERSION = "1.0.0"
EXPECTED_RELEASE_TAG = "v2.16.0"
EXPECTED_RELEASE_COMMIT = "c7ac293d2aa81ddfa693390549bcd909069c8fc3"


def normalize(value: str, source: Path, packages: Path) -> str:
    return value.replace(str(source), "${AGON_VDP_SOURCE}").replace(
        str(packages), "${PLATFORMIO_PACKAGES_DIR}"
    )


def selected(file_name: str, source: Path) -> bool:
    absolute = Path(file_name)
    if absolute.is_absolute():
        try:
            relative = absolute.relative_to(source)
        except ValueError:
            return False
        return relative.parts[:1] == ("video",)
    return file_name.startswith(".pio/libdeps/")


def dependency_command(command: str, source_file: str, compiler: Path) -> list[str]:
    args = shlex.split(command)
    result = [str(compiler)]
    skip = False
    for index, arg in enumerate(args[1:], start=1):
        if skip:
            skip = False
            continue
        if arg == "-o":
            skip = True
        elif arg == "-c" or arg == source_file:
            continue
        else:
            result.append(arg)
    return result


def parse_make_dependencies(text: str) -> list[str]:
    logical = text.replace("\\\n", " ")
    _, _, dependencies = logical.partition(":")
    return shlex.split(dependencies)


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("docs/tasks/SETUP-003/generated"))
    parser.add_argument(
        "--toolchain-bin",
        type=Path,
        default=Path.home() / ".platformio/packages/toolchain-riscv32-esp/bin",
    )
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    database_path = source / "compile_commands.json"
    compiler = args.toolchain_bin.resolve() / "riscv32-esp-elf-g++"
    packages = args.toolchain_bin.resolve().parent.parent

    database = json.loads(database_path.read_text(encoding="utf-8"))
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=source, text=True, capture_output=True, check=True
    ).stdout.strip()
    if commit != EXPECTED_RELEASE_COMMIT:
        parser.error(f"source is {commit}, expected {EXPECTED_RELEASE_COMMIT}")
    compiler_version = subprocess.run(
        [str(compiler), "--version"], text=True, capture_output=True, check=True
    ).stdout.splitlines()[0]
    retained = [entry for entry in database if selected(entry["file"], source)]
    normalized = [
        {
            key: normalize(str(entry[key]), source, packages)
            for key in ("directory", "file", "output", "command")
        }
        for entry in retained
    ]
    normalized.sort(key=lambda entry: entry["file"])
    output.mkdir(parents=True, exist_ok=True)
    (output / "compile-commands.json").write_text(
        json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    video = next(entry for entry in database if entry["file"].endswith("video.ino.cpp"))
    # PlatformIO records its transient generated .ino.cpp but removes that file
    # after compiledb/build. Preprocessing the original sketch as C++ preserves
    # its include behavior without fabricating Arduino prototypes.
    dependency_subject = video["file"]
    source_subject = dependency_subject
    if not (source / source_subject).exists() and source_subject.endswith(".ino.cpp"):
        source_subject = source_subject.removesuffix(".cpp")
    base = dependency_command(video["command"], dependency_subject, compiler)
    base.extend(["-x", "c++", "-fdiagnostics-color=never"])
    dependencies = subprocess.run(
        [*base, "-M", "-MG", source_subject],
        cwd=source,
        text=True,
        capture_output=True,
        check=False,
    )
    closure = sorted(
        {
            normalize(path, source, packages)
            for path in parse_make_dependencies(dependencies.stdout)
        }
    )
    include_tree = subprocess.run(
        [*base, "-H", "-E", "-o", os.devnull, source_subject],
        cwd=source,
        text=True,
        capture_output=True,
        check=False,
    )
    tree: list[tuple[int, str]] = []
    for line in include_tree.stderr.splitlines():
        match = re.match(r"^(\.+) (.+)$", line)
        if match:
            tree.append((len(match.group(1)), normalize(match.group(2), source, packages)))
    diagnostics = [
        normalize(line, source, packages)
        for line in include_tree.stderr.splitlines()
        if "fatal error:" in line or "compilation terminated" in line
    ]

    lines = [
        "# Generated by docs/tasks/SETUP-003/scripts/generate-compile-evidence.py; do not hand-edit.",
        f"schema_version: {SCHEMA_VERSION}",
        "generator:",
        "  name: generate-compile-evidence",
        f"  version: {yaml_string(GENERATOR_VERSION)}",
        "  regeneration_command: >-",
        "    .venv/bin/python docs/tasks/SETUP-003/scripts/generate-compile-evidence.py",
        "    --source <official-agon-vdp-checkout>",
        "source:",
        f"  release_tag: {yaml_string(EXPECTED_RELEASE_TAG)}",
        f"  commit: {yaml_string(commit)}",
        "tools:",
        "  platformio_core: \"6.1.19\"",
        f"  target_compiler: {yaml_string(compiler_version)}",
        "dependencies:",
        "  vdp-gl: \"1.0.5 tag all-the-plots at ac2dd5986daf496c43ae8e7fe41836274aec54a0\"",
        "  ESP32Time: \"2.0.6\"",
        "  CRC: \"1.0.4\"",
        "outputs:",
        "  - docs/tasks/SETUP-003/generated/compile-commands.json",
        "  - docs/tasks/SETUP-003/generated/includes.yaml",
        "scope:",
        f"  complete_database_entries: {len(database)}",
        f"  retained_project_dependency_entries: {len(retained)}",
        f"  compiledb_subject: {dependency_subject}",
        f"  preprocessor_subject: {source_subject}",
        "  generated_sketch_cpp_retained_by_platformio: false",
        "  dependency_semantics: compiler_transitive_closure",
        f"  dependency_command_exit: {dependencies.returncode}",
        f"  include_tree_command_exit: {include_tree.returncode}",
        "path_placeholders:",
        "  AGON_VDP_SOURCE: official v2.16.0 checkout",
        "  PLATFORMIO_PACKAGES_DIR: PlatformIO packages directory",
        "dependency_closure:",
    ]
    lines.extend(f"  - {yaml_string(item)}" for item in closure)
    lines.append("include_tree:")
    for depth, path in tree:
        lines.append(f"  - depth: {depth}")
        lines.append(f"    path: {yaml_string(path)}")
    lines.append("terminal_diagnostics:")
    lines.extend(f"  - {yaml_string(item)}" for item in diagnostics)
    (output / "includes.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
