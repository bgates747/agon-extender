#!/usr/bin/env python3
"""Build one manifest-selected P4 profile with native ESP-IDF; never flash."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
VDP = ROOT / "vdp"
MANIFEST = VDP / "build/p4-profiles.json"
IDF = ROOT / "agents/build001/native-tools/esp-idf"
TOOLS = ROOT / "agents/build001/native-tools/espressif"
PYTHON_ENV = ROOT / "agents/build001/native-tools/python-env"
IDF_COMMIT = "b774170ff46c393eeb5e495ea37936038d3f4f4f"
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]*")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_record(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": sha(path)}


def checked_path(relative: str) -> Path:
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise SystemExit(f"unsafe manifest path: {relative}")
    result = (VDP / relative).resolve()
    if VDP.resolve() not in result.parents or not result.is_file():
        raise SystemExit(f"missing manifest input: {relative}")
    return result


def checked_dir(relative: str) -> Path:
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise SystemExit(f"unsafe manifest directory: {relative}")
    result = (VDP / relative).resolve()
    if VDP.resolve() not in result.parents or not result.is_dir():
        raise SystemExit(f"missing manifest directory: {relative}")
    return result


def cmake_quote(value: str) -> str:
    return '"' + value.replace("\\", "/").replace('"', '\\"') + '"'


def render_component(profile: dict, common: dict, generated: Path,
                     asset_overrides: dict[str, Path]) -> None:
    sources = [checked_path(item) for item in profile["sources"]]
    if len(sources) != len(set(sources)):
        raise SystemExit("duplicate selected source")
    forbidden = {checked_path(item) for item in profile["forbidden_sources"]}
    if forbidden.intersection(sources):
        raise SystemExit("selected source is also forbidden")
    assets = [asset_overrides.get(item, checked_path(item))
              for item in profile["embedded_text"]]
    include_dirs = [checked_dir(item) for item in common["include_dirs"]
                    if item != "video"]
    include_dirs.append(generated)
    options = ["-idirafter", str(VDP / "video"),
               # PlatformIO's hybrid application compile omitted -Wall and
               # -Wextra. Native IDF adds them; keep warnings visible without
               # converting inherited upstream diagnostics into build breaks.
               "-Wno-error=reorder", "-Wno-error=switch",
               "-Wno-error=parentheses", "-Wno-error=maybe-uninitialized"]
    if profile.get("force_stock_task_context"):
        options += ["-include",
                    str(VDP / "video/extender/port/stock_task_context.hpp")]
    if profile.get("force_vdp_architecture"):
        options += ["-include",
                    str(VDP / "video/extender/compat/p4_vdp_gl_architecture.hpp")]
    definitions = ["AGON_EXTENDER_NATIVE_BUILD=1", *profile["definitions"]]
    text = "idf_component_register(\n  SRCS\n"
    text += "".join(f"    {cmake_quote(str(path))}\n" for path in sources)
    text += "  INCLUDE_DIRS\n"
    text += "".join(f"    {cmake_quote(str(path))}\n" for path in include_dirs)
    requires = [*common.get("requires", []), *profile.get("requires", [])]
    if requires:
        text += "  REQUIRES\n"
        text += "".join(f"    {item}\n" for item in requires)
    if assets:
        text += "  EMBED_TXTFILES\n"
        text += "".join(f"    {cmake_quote(str(path))}\n" for path in assets)
    text += ")\n"
    text += "target_compile_options(${COMPONENT_LIB} PRIVATE\n"
    text += '  "$<$<COMPILE_LANGUAGE:CXX>:-std=gnu++17>"\n'
    text += "".join(f"  {cmake_quote(item)}\n" for item in options)
    text += ")\ntarget_compile_definitions(${COMPONENT_LIB} PRIVATE\n"
    text += "".join(f"  {item}\n" for item in definitions)
    text += ")\n"
    (generated / "CMakeLists.txt").write_text(text)
    dependencies = dict(common["dependencies"])
    dependencies.update(profile["dependencies"])
    manifest = "dependencies:\n  idf: \"==5.5.5\"\n"
    manifest += "".join(
        f"  {name}: \"=={version}\"\n" for name, version in dependencies.items()
    )
    (generated / "idf_component.yml").write_text(manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--build-id", default="UNVERSIONED-DO-NOT-DEPLOY")
    parser.add_argument("--mos", type=Path)
    parser.add_argument("--mos-sha256")
    parser.add_argument("--flash-agent", type=Path)
    parser.add_argument("--reset-url",
                        help="embed a machine-local HTTP(S) reset endpoint")
    args = parser.parse_args()
    if not SAFE_NAME.fullmatch(args.build_id):
        parser.error("build ID contains unsupported characters")
    output = args.output.resolve()
    if output.exists() or output.is_symlink():
        parser.error("output must be a fresh nonexisting path")
    document = json.loads(MANIFEST.read_text())
    try:
        profile = document["profiles"][args.profile]
    except KeyError:
        parser.error("unknown profile")
    payload_arguments = (args.mos, args.mos_sha256, args.flash_agent)
    if profile.get("mos_recovery_payload"):
        if not all(payload_arguments):
            parser.error("recovery profile requires --mos, --mos-sha256 and --flash-agent")
    elif any(payload_arguments):
        parser.error("recovery payload arguments require a recovery profile")
    if args.reset_url and args.profile != "p4-console":
        parser.error("--reset-url is supported only by p4-console")
    if args.reset_url and urlsplit(args.reset_url).scheme not in ("http", "https"):
        parser.error("reset URL must use HTTP(S)")
    if subprocess.check_output(["git", "-C", str(IDF), "rev-parse", "HEAD"],
                               text=True).strip() != IDF_COMMIT:
        raise SystemExit("wrong ESP-IDF checkout identity")
    output.mkdir(parents=True)
    project = output / "project"
    project.mkdir()
    shutil.copyfile(VDP / "native/CMakeLists.txt", project / "CMakeLists.txt")
    generated = project / "components/agon_vdp"
    generated.mkdir(parents=True)
    asset_overrides: dict[str, Path] = {}
    if args.reset_url:
        relative = "video/extender/web/index.html"
        page = generated / "embedded/index.html"
        page.parent.mkdir()
        source = checked_path(relative).read_text()
        marker = 'name="agon-reset-url" content=""'
        if source.count(marker) != 1:
            raise SystemExit("reset URL marker missing or ambiguous")
        page.write_text(source.replace(
            marker,
            'name="agon-reset-url" content="' +
            html.escape(args.reset_url, quote=True) + '"'))
        asset_overrides[relative] = page
    render_component(profile, document["common"], generated, asset_overrides)
    payload_artifacts = []
    if profile.get("mos_recovery_payload"):
        payload_header = generated / "generated/mos_recovery_payload.hpp"
        subprocess.run([
            sys.executable, str(ROOT / "scripts/prepare_mos_recovery.py"),
            "--mos", str(args.mos.resolve()),
            "--mos-sha256", args.mos_sha256,
            "--flash-agent", str(args.flash_agent.resolve()),
            "--output", str(payload_header),
        ], check=True)
        payload_artifacts = [payload_header, payload_header.with_suffix(".json")]
    header = (
        "// Generated by scripts/build_p4.py; do not edit.\n#pragma once\n"
        f'#define AGON_EXTENDER_SOURCE_IDENTITY "{args.profile}-native"\n'
        f'#define AGON_EXTENDER_BUILD_ID "{args.build_id}"\n'
        '#define AGON_EXTENDER_ARTIFACT_STATUS "experimental"\n'
    )
    if args.profile == "p4-port008-nonrelease-qualification":
        header += '#define AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY "PORT-008-D002"\n'
    (generated / "agon_extender_build_identity.hpp").write_text(header)
    source_config = checked_path(document["common"]["sdkconfig"])
    config = source_config.read_text().replace(
        'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions.csv"',
        f'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="{VDP / "partitions.csv"}"',
    )
    sdkconfig = output / "sdkconfig"
    sdkconfig.write_text(config)
    lock = output / "dependencies.lock"
    build = output / "build"
    env = os.environ.copy()
    env.update({
        "IDF_PATH": str(IDF), "IDF_TOOLS_PATH": str(TOOLS),
        "IDF_PYTHON_ENV_PATH": str(PYTHON_ENV),
        # Normally exported by ESP-IDF's activate.py. The wrapper constructs a
        # hermetic environment instead of sourcing a shell, and esp_hosted's
        # Kconfig expands this variable directly.
        "ESP_IDF_VERSION": "5.5",
    })
    tool_bins = [str(path) for path in TOOLS.glob("tools/**/bin") if path.is_dir()]
    env["PATH"] = os.pathsep.join(tool_bins + [str(PYTHON_ENV / "bin"), env["PATH"]])
    command = [str(PYTHON_ENV / "bin/python"), str(IDF / "tools/idf.py"),
               "-C", str(project), "-B", str(build),
               f"-DAGON_COMPONENT_DIR={generated}",
               f"-DAGON_DEPENDENCIES_LOCK={lock}",
               f"-DAGON_VDP_ROOT={VDP}",
               f"-DSDKCONFIG={sdkconfig}",
               f"-DAGON_DSP_LIFETIME_FIX={'ON' if profile.get('dsp_lifetime_fix') else 'OFF'}",
               "build"]
    with (output / "build.log").open("w") as log:
        completed = subprocess.run(command, env=env, stdout=log,
                                   stderr=subprocess.STDOUT)
    if completed.returncode:
        raise SystemExit(f"native build failed; inspect {output / 'build.log'}")
    validation = [sys.executable, str(ROOT / "scripts/validate_p4_build.py"),
                  "--profile", args.profile, "--output", str(output)]
    subprocess.run(validation, check=True)
    size_tool = next(TOOLS.glob("tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-size"))
    elf = build / "agon_extender.elf"
    size_result = subprocess.run([str(size_tool), "-A", str(elf)],
                                 check=True, text=True, capture_output=True)
    (output / "size-sections.txt").write_text(size_result.stdout)
    artifact_paths = [
        elf, build / "agon_extender.bin", build / "agon_extender.map",
        build / "bootloader/bootloader.bin",
        build / "partition_table/partition-table.bin",
        build / "ota_data_initial.bin", build / "flasher_args.json",
        build / "compile_commands.json", output / "validation.json",
        output / "size-sections.txt",
        *payload_artifacts,
    ]
    record = {
        "schema_version": 1, "profile": args.profile, "lcd": False,
        "build_id": args.build_id, "manifest_sha256": sha(MANIFEST),
        "idf_commit": IDF_COMMIT, "sdkconfig_sha256": sha(sdkconfig),
        "dependencies_lock_sha256": sha(lock),
        "source_commit": subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip(),
        "source_dirty": bool(subprocess.check_output(
            ["git", "-C", str(ROOT), "status", "--porcelain"], text=True
        ).strip()),
        "reset_url_configured": bool(args.reset_url),
        "reset_url_sha256": (hashlib.sha256(args.reset_url.encode()).hexdigest()
                             if args.reset_url else None),
        "artifacts": [artifact_record(path) for path in artifact_paths],
    }
    (output / "manifest.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"native P4 build PASS: {output}")


if __name__ == "__main__":
    main()
