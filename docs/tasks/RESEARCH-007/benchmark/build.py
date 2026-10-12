#!/usr/bin/env python3
"""Prepare, build and package the standalone comparison; never access a device."""
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
import tarfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EXAMPLE = HERE.parent / "clut-example"
sys.path.insert(0, str(ROOT / "scripts"))
import build_p4 as native

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tools-path", type=Path, default=native.TOOLS)
    parser.add_argument("--python-env", type=Path, default=native.PYTHON_ENV)
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / "agents") or out.exists():
        parser.error("output must be a fresh path under ignored agents storage")
    baseline = json.loads((HERE / "baseline.json").read_text())
    metadata = json.loads((EXAMPLE / "backport.json").read_text())
    idf_commit = subprocess.check_output(["git", "-C", str(native.IDF), "rev-parse", "HEAD"], text=True).strip()
    if idf_commit != metadata["base_idf_commit"]:
        parser.error("SDK commit differs from pinned backport baseline")
    for entry in baseline["files"]:
        if sha(ROOT / entry["path"]) != entry["sha256"]:
            parser.error("CPU/partition baseline changed: " + entry["path"])
    for entry in metadata["files"]:
        if sha(native.IDF / entry["path"]) != entry["base_sha256"]:
            parser.error("SDK input changed: " + entry["path"])
    if subprocess.check_output(["git", "status", "--porcelain", "--", str(HERE), *[e["path"] for e in baseline["files"]], "scripts/build_p4.py"], cwd=ROOT, text=True).strip():
        parser.error("commit benchmark and selected inputs before identified builds")
    compiler = native.checked_tools(args.tools_path.resolve(), args.python_env.resolve())
    started = datetime.now(timezone.utc)
    build_id = "ppa-clut-benchmark-r01-b" + started.strftime("%Y-%m-%d-%H-%M-%SZ")
    project, build = out / "project", out / "build"
    project.mkdir(parents=True)
    inputs = [p for p in sorted(HERE.rglob("*")) if p.is_file() and "__pycache__" not in p.parts]
    inputs += [ROOT / e["path"] for e in baseline["files"]]
    inputs += [EXAMPLE / "backport.json", EXAMPLE / "clut-backport.patch", ROOT / "scripts/build_p4.py", ROOT / "scripts/p4_board.py"]
    sources = [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in inputs]
    with tarfile.open(out / "source.tar.gz", "w:gz") as archive:
        for p in inputs:
            archive.add(p, arcname=str(p.relative_to(ROOT)), recursive=False)
    for name in ["CMakeLists.txt", "sdkconfig.defaults", "partitions.csv", "main"]:
        src, dst = HERE / name, project / name
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
    headers = project / "main/extender/display"
    headers.mkdir(parents=True)
    for name in ["hdmi_geometry.hpp", "hdmi_timing.hpp"]:
        shutil.copy2(ROOT / "vdp/video/extender/display" / name, headers / name)
    derived = out / "derived-sdk"
    for entry in metadata["files"]:
        dst = derived / entry["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(native.IDF / entry["path"], dst)
    subprocess.run(["patch", "--batch", "--fuzz=0", "-p1", "-d", str(derived), "-i", str(EXAMPLE / "clut-backport.patch")], check=True, stdout=subprocess.DEVNULL)
    component = project / "components/esp_driver_ppa"
    shutil.copytree(native.IDF / "components/esp_driver_ppa", component, ignore=shutil.ignore_patterns("test_apps"))
    for entry in metadata["files"]:
        if sha(derived / entry["path"]) != entry["derived_sha256"]:
            raise RuntimeError("derived SDK hash mismatch")
        relative = entry["path"].removeprefix("components/")
        dst = component / relative.removeprefix("esp_driver_ppa/") if relative.startswith("esp_driver_ppa/") else component / "overlay/hal" / Path(relative).name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(derived / entry["path"], dst)
    with (component / "CMakeLists.txt").open("a") as f:
        f.write('\ntarget_include_directories(${COMPONENT_LIB} BEFORE PUBLIC "${CMAKE_CURRENT_LIST_DIR}/overlay")\n')
    with (project / "main/CMakeLists.txt").open("a") as f:
        f.write('\ntarget_include_directories(${COMPONENT_LIB} BEFORE PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../components/esp_driver_ppa/overlay")\n')
        f.write(f'target_compile_definitions(${{COMPONENT_LIB}} PRIVATE RESEARCH007_BUILD_ID="{build_id}")\n')
    env = os.environ.copy()
    env.update(IDF_PATH=str(native.IDF), IDF_TOOLS_PATH=str(args.tools_path.resolve()), IDF_PYTHON_ENV_PATH=str(args.python_env.resolve()), ESP_IDF_VERSION="5.5", IDF_TARGET="esp32p4")
    env["PATH"] = os.pathsep.join([str(args.python_env.resolve() / "bin"), *[str(p) for p in args.tools_path.resolve().glob("tools/**/bin")], env["PATH"]])
    rom_dirs = list(args.tools_path.resolve().glob("tools/esp-rom-elfs/*"))
    if len(rom_dirs) == 1:
        env["ESP_ROM_ELF_DIR"] = str(rom_dirs[0])
    idf = [str(args.python_env.resolve() / "bin/python"), str(native.IDF / "tools/idf.py"), "-C", str(project), "-B", str(build), f"-DSDKCONFIG={out / 'sdkconfig'}"]
    commands = [idf + ["reconfigure"], ["ninja", "-C", str(build), "-j2"], idf + ["merge-bin", "-o", str(out / "ppa-clut-benchmark.factory.bin")]]
    manifest = {"schema_version": 1, "build_id": build_id, "status": "experimental-uninstalled", "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "source_inputs": sources, "idf_commit": idf_commit, "compiler_sha256": sha(compiler), "upstream_clut_commit": metadata["upstream_clut_commit"], "commands": commands, "started_at": started.isoformat(), "hardware_execution": False, "flash_policy": "Write listed segments only; merged factory image contains FF-filled gaps over ordinary NVS and must not be flashed as one span on this bench."}
    begin = time.monotonic()
    result = 0
    with (out / "build.log").open("w") as log:
        for command in commands:
            result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
            if result:
                break
    manifest.update(exit_code=result, build_duration_s=round(time.monotonic()-begin, 3), finished_at=datetime.now(timezone.utc).isoformat())
    if result == 0:
        config = (out / "sdkconfig").read_text()
        for selection in ['CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ=360', 'CONFIG_SPIRAM_SPEED=200', 'CONFIG_CACHE_L2_CACHE_LINE_SIZE=64', 'CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y', 'CONFIG_PARTITION_TABLE_OFFSET=0x8000']:
            if selection not in config.splitlines():
                raise RuntimeError("actual configuration missing " + selection)
        args_json = json.loads((build / "flasher_args.json").read_text())
        factory = (out / "ppa-clut-benchmark.factory.bin").read_bytes()
        segments = []
        end = 0
        for offset, name in sorted(args_json["flash_files"].items(), key=lambda item: int(item[0], 0)):
            address = int(offset, 0)
            path = (build / name).resolve()
            if not path.is_relative_to(build) or address < end:
                raise RuntimeError("invalid or overlapping segment")
            data = path.read_bytes()
            if factory[address:address+len(data)] != data:
                raise RuntimeError("factory image segment mismatch")
            end = address + len(data)
            if end > 0x720000:
                raise RuntimeError("flash package overlaps unowned flash")
            # Existing ordinary NVS must never be part of this flash payload.
            if address < 0xF000 and end > 0x9000:
                raise RuntimeError("flash segment overlaps ordinary NVS")
            segments.append({"offset": offset, "path": str(path.relative_to(out)), "bytes": len(data), "sha256": sha(path)})
        manifest["flash_segments"] = segments
        for name in ["ppa_clut_benchmark.bin", "bootloader/bootloader.bin"]:
            header = (build / name).read_bytes()[:24]
            # ESP image header: chip18, full min/max revision in little-endian.
            chip = int.from_bytes(header[12:14], "little")
            low, high = int.from_bytes(header[15:17], "little"), int.from_bytes(header[17:19], "little")
            if header[0] != 0xE9 or chip != 18 or not low <= 103 <= high:
                raise RuntimeError("image does not admit the P4 v1.3 target")
            manifest.setdefault("image_headers", []).append({"file": name, "chip_id": chip, "min_revision": low, "max_revision": high})
    manifest["artifacts"] = [{"path": str(p.relative_to(out)), "bytes": p.stat().st_size, "sha256": sha(p)} for p in [out / "sdkconfig", out / "source.tar.gz", out / "ppa-clut-benchmark.factory.bin", build / "compile_commands.json", build / "ppa_clut_benchmark.elf", build / "ppa_clut_benchmark.map", build / "ppa_clut_benchmark.bin", build / "bootloader/bootloader.bin", build / "partition_table/partition-table.bin", build / "flasher_args.json"] if p.is_file()]
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    if result == 0:
        with tarfile.open(out / "flash-package.tar.gz", "w:gz") as archive:
            for p in [out / "manifest.json", out / "source.tar.gz", out / "sdkconfig", out / "ppa-clut-benchmark.factory.bin", *[out / e["path"] for e in manifest["flash_segments"]]]:
                archive.add(p, arcname=str(p.relative_to(out)), recursive=False)
    print(f"{build_id}: exit={result}; package/evidence={out}")
    return result

if __name__ == "__main__":
    raise SystemExit(main())
