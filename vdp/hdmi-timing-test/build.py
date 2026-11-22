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
import sys
import time
from esptool.bin_image import LoadFirmwareImage
from timings import TIMINGS, selected, header as timing_header

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


def verify_probe_build(project: Path, build: Path, tools_dir: Path, manifest: dict, probe: str) -> dict:
    config = json.loads((build / "config/sdkconfig.json").read_text())
    for key, expected in {"ESP32P4_REV_MIN_FULL": 100, "ESP32P4_REV_MAX_FULL": 199,
                          "ESP_CONSOLE_USB_SERIAL_JTAG": True, "ESP_DEFAULT_CPU_FREQ_MHZ": 360,
                          "PARTITION_TABLE_CUSTOM": True, "PARTITION_TABLE_OFFSET": 0x8000}.items():
        if config.get(key) != expected:
            raise RuntimeError(f"Unexpected {key} in {probe} probe configuration: {config.get(key)}")
    units = [Path(name) for name in manifest["source_closure"]["compiled_sources"]]
    derivatives = []
    for name in ("esp_lcd_panel_dpi.c", "dw_gdma.c"):
        expected_unit = build / probe / name
        if [unit for unit in units if unit.name == name] != [expected_unit]:
            raise RuntimeError(f"Expected exactly one derived compilation of {name}")
        derivatives.append(record(expected_unit, build))
    actions = json.loads((build / "compile_commands.json").read_text())
    main_command, = (entry["command"] for entry in actions
                     if Path(entry["file"]).resolve() == project / "main/main.c")
    if f"-DAGON_HDMI_{probe.upper()}_PROBE=1" not in main_command.split():
        raise RuntimeError(f"Standalone entry point compiled without the {probe} probe")
    compiler = Path(json.loads((build / "project_description.json").read_text())["c_compiler"]).resolve()
    candidates = [p.resolve() for p in tools_dir.glob("tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-gcc")]
    if candidates != [compiler]:
        raise RuntimeError(f"Unexpected {probe} probe compiler: {compiler}")
    return {"derivatives": derivatives, "compiler": str(compiler), "compiler_sha256": digest(compiler)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="New evidence directory; an existing directory is rejected")
    parser.add_argument("--timing", choices=TIMINGS, default="848x480")
    parser.add_argument("--ppa-scale-320", action="store_true",
                        help="Bilinear 2x320x240 pattern, centered in the 848x480 carrier")
    probes = parser.add_mutually_exclusive_group()
    probes.add_argument("--pair-probe", action="store_true",
                        help="USB-commanded standalone 848x480 two-row interrupt experiment")
    probes.add_argument("--mode0-pattern", type=Path, metavar="M000.VDU",
                        help="Build the one-frame mode 0 row probe from the pinned packed preview")
    parser.add_argument("--tools-path", type=Path, default=TOOLS,
                        help="Host-native ESP-IDF tool directory")
    parser.add_argument("--python-env", type=Path, default=PYTHON_ENV,
                        help="Host-native ESP-IDF Python environment")
    args = parser.parse_args()
    if args.ppa_scale_320 and args.timing != "848x480":
        parser.error("--ppa-scale-320 requires the proven 848x480 carrier")
    probe = "mode0" if args.mode0_pattern else "pair" if args.pair_probe else None
    if probe and (args.ppa_scale_320 or args.timing != "848x480"):
        parser.error("The USB probes require native 848x480 output")
    timing = selected(args.timing)
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
    tools_dir = args.tools_path.resolve()
    python_env = args.python_env.resolve()
    python = python_env / "bin/python"
    if not python.is_file() or not tools_dir.is_dir() or not BRIDGE.is_dir():
        raise SystemExit("The project-local ARM tools/Python or vendored HDMI bridge is missing")

    started = datetime.now(timezone.utc)
    stamp = started.strftime("%Y-%m-%d-%H-%M-%SZ")
    identity = json.loads((SOURCE / "identity.json").read_text())
    if args.pair_probe:
        identity = {"artifact_id": "hdmi-pair-irq", "revision": "r02"}
    elif args.mode0_pattern:
        identity = {"artifact_id": "hdmi-mode0-row", "revision": "r01"}
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
    if probe:
        # IDF resolves component requirements in a separate CMake script
        # that does not inherit the project's cache variables.
        (project / f"{probe}-probe.enabled").touch()
        partitions = ROOT / "vdp/partitions.csv"
        inputs[str(partitions.relative_to(ROOT))] = digest(partitions)
        shutil.copyfile(partitions, project / "partitions.csv")
        if digest(project / "partitions.csv") != inputs["vdp/partitions.csv"]:
            raise RuntimeError("Partition map changed during source freeze")
    if args.mode0_pattern:
        artwork = json.loads(subprocess.check_output([
            sys.executable, str(project / "mode0/prepare_pattern.py"), "--packed",
            str(args.mode0_pattern.resolve()), "--output", str(project / "mode0/mode0_rgba2222.bin"),
        ], text=True))
    (project / "main/build_identity.h").write_text(
        "#pragma once\n#define HDMI_TEST_BUILD_ID " + json.dumps(build_id) + "\n")
    (project / "version.txt").write_text(project_version + "\n")
    (project / "main/timing_config.h").write_text(timing_header(timing) +
        f"\n#define TEST_PPA_SCALE_320 {int(args.ppa_scale_320)}\n")
    frozen = {str(path.relative_to(project)): digest(path) for path in sources(project)}
    manifest = {
        "schema_version": 1, "artifact_status": "experimental", "state": "prepared",
        "build_id": build_id, "project_version": project_version,
        "started_utc": started.isoformat(), "timing": timing,
        "presentation": ({"source": [320, 240], "scale": [2, 2],
                          "offset": [104, 0], "method": "ppa-srm-bilinear",
                          "scope": "static-before-scanout; no sprite qualification"}
                         if args.ppa_scale_320 else {"method": "native-unscaled"}),
        "source_commit": git(ROOT, "rev-parse", "HEAD"),
        "source_dirty": git(ROOT, "status", "--porcelain=v1"),
        "idf_commit": IDF_COMMIT, "idf_dirty": git(IDF, "status", "--porcelain=v1"),
        "source_sha256": inputs, "frozen_source_sha256": frozen,
        "commands": [],
    }
    write_manifest(output, manifest)
    env = os.environ.copy()
    env.update(IDF_PATH=str(IDF), IDF_TARGET="esp32p4", IDF_TOOLS_PATH=str(tools_dir),
               IDF_PYTHON_ENV_PATH=str(python_env), ESP_IDF_VERSION="5.5",
               ESP_ROM_ELF_DIR=str(tools_dir / "tools/esp-rom-elfs/20241011"))
    bins = [str(path) for path in sorted((tools_dir / "tools").glob("**/bin")) if path.is_dir()]
    # Tool installations on the Pi can symlink the versioned compiler tree.
    # Recursive globs do not traverse that symlink on our supported Python.
    compilers = list(tools_dir.glob("tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-gcc"))
    if len(compilers) != 1:
        raise RuntimeError(f"Expected one RISC-V compiler under {tools_dir}")
    env["PATH"] = os.pathsep.join([str(python_env / "bin"), str(compilers[0].parent), *bins, env["PATH"]])
    prefix = [str(python), str(IDF / "tools/idf.py"), "-C", str(project), "-B", str(build)]
    actions = [["build"]]
    if probe:
        prefix.extend(["-D", f"AGON_HDMI_{probe.upper()}_PROBE=ON"])
        if args.mode0_pattern:
            manifest["presentation"] = {"method": "mode0-same-row-irq", "source": [640, 480],
                                        "offset": [104, 0], "slots": 1, "frame_limit": 1,
                                        "invocation": "usb-console", "artwork": artwork}
        else:
            manifest["presentation"] = {"method": "reference-card-then-direct-pair-irq", "pair_rows": 2,
                                        "slots": 2, "frame_limit": 300, "invocation": "usb-console"}
    else:
        actions.append(["merge-bin", "--output", "hdmi-timing.factory.bin"])
    elapsed_start = time.monotonic()
    try:
        with (output / "build.log").open("w") as log:
            for action in actions:
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
        factory = None if probe else factory_path.read_bytes()
        segments = []
        previous_end = 0
        for address, name in sorted(flash["flash_files"].items(), key=lambda item: int(item[0], 0)):
            offset = int(address, 0)
            path = (build / name).resolve()
            if not path.is_relative_to(build.resolve()) or not path.is_file():
                raise RuntimeError(f"Flash segment escapes or is missing from selected build: {name}")
            data = path.read_bytes()
            if offset < previous_end or (factory is not None and factory[offset:offset + len(data)] != data):
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
            if probe and (not header.append_digest or header.stored_digest != header.calc_digest):
                raise RuntimeError(f"ESP image SHA-256 trailer mismatch: {name}")
        if probe:
            manifest[f"{probe}_toolchain"] = verify_probe_build(project, build, tools_dir, manifest, probe)
            app = flash["app"]
            if (int(app["offset"], 0), app["file"]) != (0x20000, "hdmi_timing.bin"):
                raise RuntimeError(f"Unexpected probe app target: {app}")
            app_path = build / app["file"]
            if not 0 < app_path.stat().st_size <= 0x700000:
                raise RuntimeError("Probe image does not fit the selected OTA partition")
            manifest["app_only"] = {"offset": 0x20000, **record(app_path, output)}
        else:
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
