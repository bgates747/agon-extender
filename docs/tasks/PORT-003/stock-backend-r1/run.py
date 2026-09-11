#!/usr/bin/env python3
"""Build an isolated host executable and nondeployable P4 relocatable closure.

No PlatformIO/CMake invocation, device access, worker startup or firmware image.
Use the project's Python venv. Local compiler arguments remain in ignored output.
"""
import argparse
import datetime as dt
import json
import shlex
import subprocess
from pathlib import Path

from verify_source import ROOT, HERE, CONTROLLERS, sha, verify

IDENTITY = "stock-backend-binding-r01"
EXPECTED_OBSERVATIONS = {
    "FAIL VGA2 unaligned partial viewport vertical scroll -3; outside preserved",
    "FAIL VGA2 unaligned partial viewport vertical scroll +3; outside preserved",
}


def stamp():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d-%H-%M-%SZ")


def call(argv, cwd, log, expected=(0,)):
    with log.open("w") as stream:
        result = subprocess.run(argv, cwd=cwd, stdout=stream, stderr=stream, timeout=120)
    if result.returncode not in expected:
        raise RuntimeError(f"{log.name}: exit {result.returncode}; see {log}")
    return result.returncode


def target_args():
    database = ROOT / "vdp/compile_commands.json"
    entry = next(e for e in json.loads(database.read_text()) if e["file"].endswith("/p4_display_controller.cpp"))
    args = entry.get("arguments") or shlex.split(entry["command"])
    compiler = ROOT / "vdp/.pio/packages/toolchain-riscv32-esp/bin/riscv32-esp-elf-g++"
    filtered, skip = [str(compiler)], False
    for arg in args[1:]:
        if skip:
            skip = False
            continue
        if arg in ("-o", "-MF", "-MT", "-MQ"):
            skip = True
            continue
        if arg in ("-c", "-MMD", "-MD", "-MP") or arg.endswith("/p4_display_controller.cpp"):
            continue
        if arg.endswith("p4_vdp_gl_architecture.hpp"):
            arg = str(HERE / "task_context.hpp")
        filtered.append(arg)
    assert str(HERE / "task_context.hpp") in filtered, "missing strict task-context boundary"
    filtered += ["-DAGON_EXTENDER_STOCK_ROWS_PROOF", "-fdiagnostics-color=never",
                 "-I" + str(ROOT / "vdp/.pio/build/p4-console/config")]
    return filtered, Path(entry["directory"]), sha(database.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT / "agents/stock-backend-r1")
    args = parser.parse_args()
    build = IDENTITY + "-b" + stamp()
    out = args.output_root.resolve() / build
    out.mkdir(parents=True, exist_ok=False)
    result = {"identity": IDENTITY, "build": build, "run": "PORT-003-" + stamp(),
              "status": "experimental", "scope": "host rows and P4 relocatable link; no hardware execution",
              "source_checkpoint": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "worktree": "modified source; see source hashes", "source_verification": verify()}
    (out / "source.patch").write_bytes(subprocess.check_output(["git", "diff", "--binary"], cwd=ROOT))
    gl = ROOT / "vdp/vendor/vdp-gl/src"
    sources = [gl / f"dispdrivers/{s}controller.cpp" for s in CONTROLLERS]
    sources += [gl / (s + ".cpp") for s in ("canvas", "displaycontroller", "codepages", "fabfonts")]
    sources += [ROOT / "vdp/video/extender/port/stock_render_utils.cpp", HERE / "native_rows.cpp"]
    host = ["g++", "-std=c++17", "-O1", "-g", "-ffunction-sections", "-fdata-sections",
            "-DFABGL_EMULATED", "-DAGON_EXTENDER_STOCK_ROWS_PROOF", "-I" + str(HERE / "compat"),
            "-I" + str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat"), "-I" + str(gl),
            "-include", str(HERE / "compat/host_preinclude.hpp")]
    target, target_cwd, database_hash = target_args()
    result["compile_database_sha256"] = database_hash
    (out / "local-commands.json").write_text(json.dumps({"host": host, "target": target,
        "target_directory": str(target_cwd)}, indent=2) + "\n")
    result["compilers"] = {name: subprocess.check_output([cmd[0], "--version"], text=True).splitlines()[0]
                           for name, cmd in (("host", host), ("target", target))}
    dependency_files = set()
    for kind, flags, cwd in (("host", host, ROOT), ("target", target, target_cwd)):
        objects = []
        for source in sources:
            obj = out / f"{kind}-{source.stem}.o"
            dep = obj.with_suffix(".d")
            call(flags + ["-MMD", "-MF", str(dep), "-c", str(source), "-o", str(obj)],
                 cwd, obj.with_suffix(".log"))
            objects.append(str(obj))
            for file in shlex.split(dep.read_text().replace("\\\n", " ").split(":", 1)[1]):
                dependency_files.add((cwd / file).resolve())
        if kind == "host":
            binary = out / "native-rows"
            call([host[0], "-Wl,--gc-sections", *objects, "-o", str(binary)], ROOT, out / "host-link.log")
            code = call([str(binary)], ROOT, out / "native-rows.log", expected=(0, 1))
            lines = (out / "native-rows.log").read_text().splitlines()
            failures = {line for line in lines if line.startswith("FAIL ")}
            assert code == 1 and failures == EXPECTED_OBSERVATIONS, "unexpected native-row comparison result"
            result["native_comparison"] = {"exit_code": code, "passed": sum(l.startswith("PASS ") for l in lines),
                "failed_logical_expectations": sorted(failures), "summary": lines[-1],
                "disposition": "preserved upstream narrow swapRows behavior; no bug fix"}
            result["host_executable_sha256"] = sha(binary.read_bytes())
        else:
            # Pull only referenced official Espressif DSP members. This is a
            # relocatable closure, not a bootable ELF or a fabricated SDK runtime.
            dsp = ROOT / "vdp/.pio/build/p4-console/esp-idf/espressif__esp-dsp/libespressif__esp-dsp.a"
            binary = out / "stock-rows-p4.o"
            call([target[0], "-r", "-nostdlib", *objects, str(dsp), "-o", str(binary)],
                 ROOT, out / "target-link.log")
            nm = str(Path(target[0]).with_name("riscv32-esp-elf-nm"))
            undefined = subprocess.check_output([nm, "-uC", str(binary)], text=True)
            (out / "target-undefined.txt").write_text(undefined)
            assert "fabgl::" not in undefined and "dspm::" not in undefined, "unresolved renderer symbol"
            for forbidden in ("GPIOStream", "esp_intr_alloc", "xthal_", "xTaskCreate", "i2s", "spi_flash_cache"):
                assert forbidden not in undefined, "unexpected physical/ISR dependency: " + forbidden
            result["target_link"] = {"translation_units": len(sources), "format": "RISC-V ELF relocatable; not flashable",
                "sha256": sha(binary.read_bytes()), "dsp_archive_sha256": sha(dsp.read_bytes()),
                "remaining_dependencies": undefined.splitlines()}
            call([str(Path(target[0]).with_name("riscv32-esp-elf-objdump")), "-drC", str(binary)],
                 ROOT, out / "target-disassembly.txt")
        print(kind + " build/comparison complete", flush=True)
    # Keep exact include closure locally, and project-owned dependency hashes in
    # the shareable result. Compiler-generated files/SDK paths stay machine-local.
    local_dependencies = {str(p): sha(p.read_bytes()) for p in sorted(dependency_files) if p.is_file()}
    (out / "local-dependencies.json").write_text(json.dumps(local_dependencies, indent=2) + "\n")
    result["project_dependencies"] = {str(p.relative_to(ROOT)): local_dependencies[str(p)]
        for p in sorted(dependency_files) if str(p) in local_dependencies and p.is_relative_to(ROOT)
        and ".pio" not in p.parts}
    result["proof_files"] = {str(p.relative_to(ROOT)): sha(p.read_bytes())
        for p in sorted(HERE.rglob("*")) if p.is_file() and p.suffix in (".cpp", ".hpp", ".h", ".py", ".json")
        and p.name != "results.json"}
    (out / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["native_comparison"]["summary"])
    print("R1 evidence ready; two upstream discrepancies retained.")
    print(out)


if __name__ == "__main__":
    main()
