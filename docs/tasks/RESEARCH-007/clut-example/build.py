#!/usr/bin/env python3
"""Build the isolated R07 CLUT example; no device/flash operations exist here."""
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import build_p4 as native


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--without-backport", action="store_true",
                        help="Build unmodified SDK as the expected API-gap negative control")
    parser.add_argument("--tools-path", type=Path, default=native.TOOLS)
    parser.add_argument("--python-env", type=Path, default=native.PYTHON_ENV)
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / "agents") or out.exists():
        parser.error("output must be a fresh path under ignored agents storage")
    metadata = json.loads((HERE / "backport.json").read_text())
    actual_idf = subprocess.check_output(
        ["git", "-C", str(native.IDF), "rev-parse", "HEAD"], text=True).strip()
    if actual_idf != metadata["base_idf_commit"]:
        parser.error("selected SDK commit does not match the backport baseline")
    for entry in metadata["files"]:
        if sha(native.IDF / entry["path"]) != entry["base_sha256"]:
            parser.error("selected SDK input hash changed: " + entry["path"])
    compiler = native.checked_tools(args.tools_path.resolve(), args.python_env.resolve())
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%SZ")
    build_id = "ppa-clut-example-r03-b" + stamp
    project = out / "project"
    project.mkdir(parents=True)
    for name in ["CMakeLists.txt", "sdkconfig.defaults", "main"]:
        src, dst = HERE / name, project / name
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
    with (project / "main/CMakeLists.txt").open("a") as f:
        f.write('\ntarget_compile_definitions(${COMPONENT_LIB} PRIVATE '
                f'RESEARCH007_BUILD_ID="{build_id}")\n')
    if not args.without_backport:
        # The selected SDK remains read-only. Generate only a component/header
        # override from hash-pinned inputs; CMake prefers project components.
        derived = out / "derived-sdk"
        for entry in metadata["files"]:
            dst = derived / entry["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(native.IDF / entry["path"], dst)
        subprocess.run(["patch", "--batch", "--fuzz=0", "-p1", "-d", str(derived),
                        "-i", str(HERE / "clut-backport.patch")], check=True,
                       stdout=subprocess.DEVNULL)
        for entry in metadata["files"]:
            if sha(derived / entry["path"]) != entry["derived_sha256"]:
                raise RuntimeError("derived SDK input mismatch: " + entry["path"])
        component = project / "components/esp_driver_ppa"
        shutil.copytree(native.IDF / "components/esp_driver_ppa", component,
                        ignore=shutil.ignore_patterns("test_apps"))
        for entry in metadata["files"]:
            relative = entry["path"].removeprefix("components/")
            if relative.startswith("esp_driver_ppa/"):
                shutil.copy2(derived / entry["path"], component / relative.removeprefix("esp_driver_ppa/"))
            else:
                dst = component / "overlay/hal" / Path(relative).name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(derived / entry["path"], dst)
        with (component / "CMakeLists.txt").open("a") as f:
            f.write('\n# R07-03 isolated header backport; no SDK tree mutation.\n'
                    'target_include_directories(${COMPONENT_LIB} BEFORE PUBLIC '
                    '"${CMAKE_CURRENT_LIST_DIR}/overlay")\n')
        # PUBLIC/BEFORE orders this component's own headers, but IDF can place
        # the stock HAL first for consumers. Pin the sample's include order too.
        with (project / "main/CMakeLists.txt").open("a") as f:
            f.write('\ntarget_include_directories(${COMPONENT_LIB} BEFORE PRIVATE '
                    '"${CMAKE_CURRENT_LIST_DIR}/../components/esp_driver_ppa/overlay")\n')

    env = os.environ.copy()
    env.update(IDF_PATH=str(native.IDF), IDF_TOOLS_PATH=str(args.tools_path.resolve()),
               IDF_PYTHON_ENV_PATH=str(args.python_env.resolve()), ESP_IDF_VERSION="5.5",
               IDF_TARGET="esp32p4")
    bins = [args.python_env.resolve() / "bin", *args.tools_path.resolve().glob("tools/**/bin")]
    env["PATH"] = os.pathsep.join([*(str(p) for p in bins), env["PATH"]])
    rom_dirs = list(args.tools_path.resolve().glob("tools/esp-rom-elfs/*"))
    if len(rom_dirs) == 1:
        env["ESP_ROM_ELF_DIR"] = str(rom_dirs[0])
    build = out / "build"
    commands = [[str(args.python_env.resolve() / "bin/python"), str(native.IDF / "tools/idf.py"),
                 "-C", str(project), "-B", str(build),
                 f"-DSDKCONFIG={out / 'sdkconfig'}", "reconfigure"],
                ["ninja", "-C", str(build), "-j2"]]
    source_inputs = [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)}
                     for p in sorted(HERE.rglob("*")) if p.is_file() and "__pycache__" not in p.parts]
    manifest = {
        "schema_version": 1, "build_id": build_id, "status": "experimental",
        "scope": "compile/link only; not deployed or physically tested",
        "variant": "stock-sdk-negative-control" if args.without_backport else "clut-backport",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "idf_commit": actual_idf, "compiler_sha256": sha(compiler),
        "upstream_clut_commit": metadata["upstream_clut_commit"], "source_inputs": source_inputs,
    }
    result = 0
    with (out / "build.log").open("w") as log:
        for command in commands:
            result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
            if result:
                break
    manifest["exit_code"] = result
    manifest["artifacts"] = [{"path": str(p.relative_to(out)), "bytes": p.stat().st_size,
                               "sha256": sha(p)}
                              for p in [out / "sdkconfig", build / "compile_commands.json",
                                        build / "ppa_clut_example.elf", build / "ppa_clut_example.bin"]
                              if p.is_file()]
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{build_id}: build exit={result}; evidence={out}")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
