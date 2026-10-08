#!/usr/bin/env python3
"""Freeze and build the standalone HDMI pattern; never flash or reset a board."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from esptool.bin_image import LoadFirmwareImage

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).resolve().parent
IDF = ROOT / "agents/build001/native-tools/esp-idf"
IDF_COMMIT = "b774170ff46c393eeb5e495ea37936038d3f4f4f"
TOOLS = ROOT / "agents/p4pc-demo/tools"
PYTHON_ENV = ROOT / "agents/p4pc-demo/python-env"
BRIDGE = ROOT / "vdp/components/esp_lcd_lt8912b"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(directory: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(directory), *args], text=True).strip()


def record(path: Path, base: Path) -> dict:
    return {"path": str(path.relative_to(base)), "bytes": path.stat().st_size,
            "sha256": digest(path)}


def write_manifest(output: Path, manifest: dict) -> None:
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def sources(directory: Path):
    for path in sorted(directory.rglob("*")):
        if any(part in {"__pycache__", ".git", "build", "managed_components"}
               for part in path.relative_to(directory).parts):
            continue
        if path.is_symlink():
            raise RuntimeError(f"Source symlink not admitted to frozen closure: {path}")
        if path.is_file() and path.suffix != ".pyc":
            yield path


def check_closure(project: Path, build: Path) -> dict:
    allowed = [directory.resolve() for directory in (project, IDF, build)]

    def accepted(path: Path) -> Path:
        path = path.resolve()
        if not any(path.is_relative_to(base) for base in allowed):
            raise RuntimeError(f"Compiled source escapes selected project/IDF/build: {path}")
        return path

    description = json.loads((build / "project_description.json").read_text())
    components = {}
    for name, info in description["build_component_info"].items():
        components[name] = str(accepted(Path(info["dir"])))
    units = []
    for command in json.loads((build / "compile_commands.json").read_text()):
        path = Path(command["file"])
        if not path.is_absolute():
            path = Path(command["directory"]) / path
        units.append(str(accepted(path)))
    return {"components": components, "compiled_source_count": len(units),
            "compiled_sources": units}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="New evidence directory; an existing directory is rejected")
    parser.add_argument("--inject-late-tag", type=int, default=0,
                        help="Negative control: delay one absolute strip tag;0 disables")
    args = parser.parse_args()
    if args.inject_late_tag < 0 or args.inject_late_tag > 10000:
        raise SystemExit("Fault tag must be0 (disabled) or1..10000 (outside preflight tags)")
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"Refusing to overwrite an existing build: {output}")
    if any(output.is_relative_to(path.resolve()) for path in (SOURCE, BRIDGE, IDF)):
        raise SystemExit("Output must not be nested inside a source/reference tree")
    for name in ("CMakeLists.txt", "main/CMakeLists.txt", "main/main.c", "pattern.c", "pattern.h"):
        if not (SOURCE / name).is_file():
            raise SystemExit(f"Missing standalone project source: {name}")
    if git(IDF, "rev-parse", "HEAD") != IDF_COMMIT:
        raise SystemExit("Expected pinned ESP-IDF 5.5.5")
    python = PYTHON_ENV / "bin/python"
    if not python.is_file() or not TOOLS.is_dir() or not BRIDGE.is_dir():
        raise SystemExit("The project-local ARM tools/Python or vendored HDMI bridge is missing")

    started = datetime.now(timezone.utc)
    stamp = started.strftime("%Y-%m-%d-%H-%M-%SZ")
    identity = json.loads((SOURCE / "identity.json").read_text())
    build_id = identity["artifact_id"] + "-" + identity["revision"] + "-b" + stamp
    project_version = identity["revision"] + "-b" + stamp
    assert len(project_version.encode()) < 32  # ESP-IDF application version field
    project, build = output / "project", output / "build"
    output.mkdir(parents=True)
    project.mkdir()
    inputs = {}
    for base, destination in ((SOURCE, project), (BRIDGE, project / "components/esp_lcd_lt8912b")):
        for source in sources(base):
            relative = source.relative_to(base)
            inputs[str(source.relative_to(ROOT))] = digest(source)
            if source == Path(__file__).resolve():
                continue  # Retained as a hashed input, not an IDF project source.
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            if digest(target) != inputs[str(source.relative_to(ROOT))]:
                raise RuntimeError(f"Source changed while freezing the project: {source}")
    if args.inject_late_tag:
        config = project / "main/strip_config.h"
        content = config.read_text()
        default = "#define STRIP_INJECT_LATE_TAG 0"
        if content.count(default) != 1:
            raise RuntimeError("Expected disabled fault injection in maintained source")
        config.write_text(content.replace(default,
                         f"#define STRIP_INJECT_LATE_TAG {args.inject_late_tag}"))
    (project / "main/build_identity.h").write_text(
        "#pragma once\n#define HDMI_TEST_BUILD_ID " + json.dumps(build_id) + "\n")
    (project / "version.txt").write_text(project_version + "\n")
    frozen = {str(path.relative_to(project)): digest(path) for path in sources(project)}
    manifest = {
        "schema_version": 1, "artifact_status": "experimental", "state": "prepared",
        "build_id": build_id, "project_version": project_version,
        "started_utc": started.isoformat(),
        "source_commit": git(ROOT, "rev-parse", "HEAD"),
        "source_dirty": git(ROOT, "status", "--porcelain=v1"),
        "idf_commit": IDF_COMMIT, "idf_dirty": git(IDF, "status", "--porcelain=v1"),
        "source_sha256": inputs, "frozen_source_sha256": frozen,
        "configuration": {"inject_late_tag": args.inject_late_tag},
        "commands": [],
    }
    write_manifest(output, manifest)
    env = os.environ.copy()
    env.update(IDF_PATH=str(IDF), IDF_TARGET="esp32p4", IDF_TOOLS_PATH=str(TOOLS),
               IDF_PYTHON_ENV_PATH=str(PYTHON_ENV), ESP_IDF_VERSION="5.5",
               ESP_ROM_ELF_DIR=str(TOOLS / "tools/esp-rom-elfs/20241011"))
    bins = [str(path) for path in sorted((TOOLS / "tools").glob("**/bin")) if path.is_dir()]
    env["PATH"] = os.pathsep.join([str(PYTHON_ENV / "bin"), *bins, env["PATH"]])
    prefix = [str(python), str(IDF / "tools/idf.py"), "-C", str(project), "-B", str(build)]
    elapsed_start = time.monotonic()
    try:
        with (output / "build.log").open("w") as log:
            for action in (["build"], ["merge-bin", "--output", "hdmi-timing.factory.bin"]):
                command = prefix + action
                manifest["commands"].append(command)
                manifest["state"] = "building"
                write_manifest(output, manifest)
                print(f"{build_id}: {' '.join(action)}", flush=True)
                log.write(json.dumps(command) + "\n")
                log.flush()
                subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        manifest["source_closure"] = check_closure(project, build)
        for name, expected in frozen.items():
            if digest(project / name) != expected:
                raise RuntimeError(f"Frozen source changed during build: {name}")
        flash_path = build / "flasher_args.json"
        flash = json.loads(flash_path.read_text())
        factory_path = build / "hdmi-timing.factory.bin"
        factory = factory_path.read_bytes()
        segments = []
        previous_end = 0
        for address, name in sorted(flash["flash_files"].items(), key=lambda item: int(item[0], 0)):
            offset = int(address, 0)
            path = (build / name).resolve()
            if not path.is_relative_to(build.resolve()) or not path.is_file():
                raise RuntimeError(f"Flash segment escapes or is missing from selected build: {name}")
            data = path.read_bytes()
            if offset < previous_end or factory[offset:offset + len(data)] != data:
                raise RuntimeError(f"Factory overlap/content mismatch at flash segment {address}: {name}")
            previous_end = offset + len(data)
            segments.append({"offset": offset, **record(path, output)})
        manifest["flash_segments"] = segments
        manifest["image_headers"] = {}
        for name in ("bootloader/bootloader.bin", "hdmi_timing.bin"):
            header = LoadFirmwareImage("esp32p4", str(build / name))
            manifest["image_headers"][name] = {
                "chip_id": header.chip_id, "min_rev_full": header.min_rev_full,
                "max_rev_full": header.max_rev_full,
            }
            if header.chip_id != 18 or not header.min_rev_full <= 103 <= header.max_rev_full:
                raise RuntimeError(f"Image is not compatible with the selected P4 silicon1.3: {name}")
        manifest["factory"] = {"offset": 0, **record(factory_path, output)}
        artifact_paths = [flash_path, build / "project_description.json", build / "compile_commands.json",
                          project / "sdkconfig", *sorted(build.glob("*.elf")), *sorted(build.glob("*.map"))]
        manifest["artifacts"] = [record(path, output) for path in artifact_paths if path.is_file()]
        manifest["state"] = "verified-build"
    except Exception as error:
        manifest["state"] = "failed"
        manifest["error"] = str(error)
        raise
    finally:
        manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["build_and_validation_seconds"] = round(time.monotonic() - elapsed_start, 3)
        write_manifest(output, manifest)
    print(f"Verified standalone build: {build_id}\nManifest: {output / 'manifest.json'}")


if __name__ == "__main__":
    main()
