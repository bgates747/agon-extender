#!/usr/bin/env python3
"""Generate compact evidence for the pristine SETUP-003 Work 3 control build.

This script inspects an already-built temporary checkout. PlatformIO must have
been run with an isolated temporary PLATFORMIO_CORE_DIR so a similarly named
toolchain installed by another project cannot contaminate the control.
"""

from __future__ import annotations

import argparse
import configparser
import csv
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

import yaml


EXPECTED_COMMIT = "c7ac293d2aa81ddfa693390549bcd909069c8fc3"
EXPECTED_TAG = "v2.16.0"
EXPECTED_VDP_GL_COMMIT = "ac2dd5986daf496c43ae8e7fe41836274aec54a0"
GENERATOR_VERSION = "1.0.0"


def run(command: list[str], cwd: Path | None = None) -> str:
    return subprocess.run(
        command, cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_version(path: Path) -> str:
    metadata = path / "package.json"
    if not metadata.is_file():
        metadata = path / "platform.json"
    return str(json.loads(metadata.read_text())["version"])


def library_version(path: Path) -> str:
    return str(json.loads((path / "library.json").read_text())["version"])


def source_identity(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    match = re.search(r"/vdp-gl/(src/.+)$", normalized)
    if match:
        return f"vdp-gl:{match.group(1)}"
    match = re.search(r"/ESP32Time/(.+)$", normalized)
    if match:
        return f"ESP32Time:{match.group(1)}"
    match = re.search(r"/CRC/(src/.+)$", normalized)
    if match:
        return f"CRC:{match.group(1)}"
    if normalized.endswith("video/video.ino.cpp"):
        return "agon-vdp:video/video.ino"
    return None


def selected_command(database: list[dict[str, str]], suffix: str) -> list[str]:
    record = next(item for item in database if item["file"].endswith(suffix))
    return shlex.split(record["command"])


def flag_summary(tokens: list[str]) -> dict[str, object]:
    defines = sorted(token[2:] for token in tokens if token.startswith("-D"))
    includes = [token[2:] for token in tokens if token.startswith("-I")]
    return {
        "compiler": Path(tokens[0]).name,
        "language_standards": sorted(
            {token.removeprefix("-std=") for token in tokens if token.startswith("-std=")}
        ),
        "optimization": sorted(
            {token for token in tokens if re.fullmatch(r"-O(?:[0-3sg]|fast)", token)}
        ),
        "architecture_flags": sorted(
            token
            for token in tokens
            if token.startswith(("-mfix-", "-march=", "-mcmodel=", "-mlongcalls"))
        ),
        "defines": defines,
        "include_path_count": len(includes),
    }


def section_sizes(size_tool: Path, elf: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    for line in run([str(size_tool), "-A", str(elf)]).splitlines():
        match = re.match(r"^(\.[^\s]+)\s+(\d+)\s+", line)
        if match:
            result[match.group(1)] = int(match.group(2))
    return result


def application_partition_size(partitions: Path) -> int:
    with partitions.open(newline="", encoding="utf-8") as source:
        rows = csv.reader(line for line in source if not line.lstrip().startswith("#"))
        sizes = [int(row[4].strip(), 0) for row in rows if row[1].strip() == "app"]
    if not sizes:
        raise ValueError(f"no application partition found in {partitions}")
    return min(sizes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--platformio-core", required=True, type=Path)
    parser.add_argument(
        "--p4-compiledb",
        type=Path,
        default=Path("docs/tasks/SETUP-003/generated/compile-commands.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/tasks/SETUP-003/generated/control-build.yaml"),
    )
    args = parser.parse_args()
    source = args.source.resolve()
    core = args.platformio_core.resolve()

    commit = run(["git", "rev-parse", "HEAD"], source)
    tag = run(["git", "describe", "--tags", "--exact-match", "HEAD"], source)
    if commit != EXPECTED_COMMIT or tag != EXPECTED_TAG:
        parser.error(f"unexpected source identity: {tag} at {commit}")
    dirty = [
        line
        for line in run(["git", "status", "--porcelain=v1"], source).splitlines()
        if line != "?? compile_commands.json"
    ]
    if dirty:
        parser.error(f"source/configuration changes found after build: {dirty}")

    config_path = source / "platformio.ini"
    config = configparser.ConfigParser(inline_comment_prefixes=(";", "#"))
    config.read(config_path)
    environment = config["env:esp32dev"]

    platform_path = core / "platforms/espressif32"
    package_path = core / "packages"
    toolchain_path = package_path / "toolchain-xtensa-esp32"
    compiler = toolchain_path / "bin/xtensa-esp32-elf-g++"
    size_tool = toolchain_path / "bin/xtensa-esp32-elf-size"
    framework_path = package_path / "framework-arduinoespressif32"
    esptool_path = package_path / "tool-esptoolpy"

    dependencies = source / ".pio/libdeps/esp32dev"
    vdp_gl = dependencies / "vdp-gl"
    vdp_gl_commit = run(["git", "rev-parse", "HEAD"], vdp_gl)
    if vdp_gl_commit != EXPECTED_VDP_GL_COMMIT:
        parser.error(f"unexpected vdp-gl commit: {vdp_gl_commit}")

    build = source / ".pio/build/esp32dev"
    artifacts = {name: build / name for name in ("firmware.elf", "firmware.bin", "firmware.map")}
    for name, path in artifacts.items():
        if not path.is_file():
            parser.error(f"missing successful-build artifact: {name}")

    sections = section_sizes(size_tool, artifacts["firmware.elf"])
    ram_used = sections[".dram0.data"] + sections[".dram0.bss"]
    flash_used = sum(
        sections[name]
        for name in (".flash.text", ".flash.rodata", ".iram0.text", ".iram0.vectors", ".dram0.data")
    )
    board = json.loads((platform_path / "boards/esp32dev.json").read_text())
    app_partition_limit = application_partition_size(
        framework_path / "tools/partitions/default.csv"
    )

    stock_database = json.loads((source / "compile_commands.json").read_text())
    p4_database = json.loads(args.p4_compiledb.read_text())
    stock_sources = sorted(filter(None, (source_identity(item["file"]) for item in stock_database)))
    p4_sources = sorted(filter(None, (source_identity(item["file"]) for item in p4_database)))
    stock_dependencies = [item for item in stock_sources if not item.startswith("agon-vdp:")]
    p4_dependencies = [item for item in p4_sources if not item.startswith("agon-vdp:")]

    stock_flags = flag_summary(selected_command(stock_database, "vdp-gl/src/canvas.cpp"))
    p4_flags = flag_summary(selected_command(p4_database, "vdp-gl/src/canvas.cpp"))
    stock_defines = set(stock_flags.pop("defines"))
    p4_defines = set(p4_flags.pop("defines"))

    binary_header = artifacts["firmware.bin"].read_bytes()[:4]
    flash_modes = {0: "qio", 1: "qout", 2: "dio", 3: "dout"}

    document = {
        "schema_version": 1,
        "generator": {
            "name": "generate-control-build-evidence",
            "version": GENERATOR_VERSION,
            "regeneration_command": (
                ".venv/bin/python docs/tasks/SETUP-003/scripts/"
                "generate-control-build-evidence.py --source <temporary-v2.16.0-checkout> "
                "--platformio-core <isolated-temporary-platformio-core>"
            ),
        },
        "source": {
            "repository": "https://github.com/AgonPlatform/agon-vdp.git",
            "tag": tag,
            "commit": commit,
            "detached_head": True,
            "source_or_configuration_changes": dirty,
            "platformio_ini_sha256": sha256(config_path),
        },
        "environment": {
            "name": "esp32dev",
            "platform": environment["platform"],
            "board": environment["board"],
            "framework": environment["framework"],
            "configured_flash_mode": environment["board_build.flash_mode"],
            "configured_cpu_frequency": environment["board_build.f_cpu"],
            "configured_flash_frequency": environment["board_build.f_flash"],
            "build_flags": [line for line in environment["build_flags"].splitlines() if line],
            "build_unflags": [line for line in environment["build_unflags"].splitlines() if line],
            "platformio_core": run([sys.executable, "-m", "platformio", "--version"]),
        },
        "resolved_packages": {
            "espressif32": package_version(platform_path),
            "framework_arduinoespressif32": package_version(framework_path),
            "arduino_esp32": "2.0.14",
            "toolchain_xtensa_esp32": package_version(toolchain_path),
            "compiler": run([str(compiler), "-dumpfullversion"]),
            "tool_esptoolpy": package_version(esptool_path),
        },
        "resolved_libraries": {
            "vdp_gl": {
                "version": library_version(vdp_gl),
                "commit": vdp_gl_commit,
            },
            "ESP32Time": library_version(dependencies / "ESP32Time"),
            "CRC": library_version(dependencies / "CRC"),
            "WiFi": "2.0.0 (framework library)",
        },
        "build_result": {
            "status": "success",
            "upload_performed": False,
            "ram": {
                "used_bytes": ram_used,
                "limit_bytes": board["upload"]["maximum_ram_size"],
            },
            "application_flash": {
                "used_bytes": flash_used,
                "limit_bytes": app_partition_limit,
            },
            "configured_flash_mode": environment["board_build.flash_mode"],
            "encoded_image_flash_mode": flash_modes.get(binary_header[2], f"unknown-{binary_header[2]}"),
            "artifacts": {
                name: {"size_bytes": path.stat().st_size, "sha256": sha256(path)}
                for name, path in artifacts.items()
            },
        },
        "compilation_database": {
            "stock_total_entries": len(stock_database),
            "stock_indexed_project_and_dependency_sources": len(stock_sources),
            "p4_indexed_dependency_sources": len(p4_sources),
            "dependency_source_sets_identical": stock_dependencies == p4_dependencies,
            "stock_only_sources": sorted(set(stock_dependencies) - set(p4_dependencies)),
            "p4_only_sources": sorted(set(p4_dependencies) - set(stock_dependencies)),
            "stock_canvas_command": stock_flags,
            "p4_canvas_command": p4_flags,
            "common_defines": sorted(stock_defines & p4_defines),
            "stock_only_defines": sorted(stock_defines - p4_defines),
            "p4_only_defines": sorted(p4_defines - stock_defines),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "# Generated by docs/tasks/SETUP-003/scripts/generate-control-build-evidence.py; do not hand-edit.\n"
        + yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
