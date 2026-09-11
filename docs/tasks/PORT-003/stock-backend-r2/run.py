#!/usr/bin/env python3
"""Exercise original scanline bodies, then compile/link them for P4.

Quiescent host execution and a nonbootable P4 relocatable closure only. Reuse
the accepted R1 compiler binding without modifying that frozen fixture.
"""
import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R1 = HERE.parent / "stock-backend-r1"
sys.path.insert(0, str(R1))
from verify_source import ROOT, CONTROLLERS, sha, verify
# This file is __main__ when invoked, so 'run' resolves to the frozen R1 helper.
from run import call, stamp, target_args

IDENTITY = "stock-backend-binding-r02"


def verify_scanlines():
    ledger = json.loads((HERE / "scanline-spans.json").read_text())
    selected = (ROOT / "vdp/video/extender/display/stock_scanline.cpp").read_bytes()
    for span in ledger["bodies"]:
        source = subprocess.check_output([
            "git", "show", ledger["body_source_checkpoint"] + ":" + span["source"]], cwd=ROOT)
        offset = sum(len(line) for line in source.splitlines(keepends=True)[:span["start_line"] - 1])
        body = source[offset:offset + span["bytes"]]
        assert sha(body) == span["sha256"], span
        assert body in selected and body in (ROOT / span["source"]).read_bytes(), span
    return ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT / "agents/stock-backend-r2")
    args = parser.parse_args()
    build = IDENTITY + "-b" + stamp()
    out = args.output_root.resolve() / build
    out.mkdir(parents=True, exist_ok=False)
    result = {"identity": IDENTITY, "build": build, "run": "PORT-003-" + stamp(),
              "status": "experimental", "scope": "quiescent scanline execution; no concurrency or hardware claim",
              "source_checkpoint": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "worktree": "modified; exact sources in dependency/proof hashes and local source copy",
              "source_verification": verify(), "scanline_verification": verify_scanlines()}
    (out / "source.patch").write_bytes(subprocess.check_output(["git", "diff", "--binary"], cwd=ROOT))
    gl = ROOT / "vdp/vendor/vdp-gl/src"
    sources = [gl / f"dispdrivers/{s}controller.cpp" for s in CONTROLLERS]
    sources += [gl / (s + ".cpp") for s in ("canvas", "displaycontroller", "codepages", "fabfonts")]
    sources += [ROOT / "vdp/video/extender/port/stock_render_utils.cpp",
                ROOT / "vdp/video/extender/display/stock_scanline.cpp", HERE / "scanline_tests.cpp"]
    host = ["g++", "-std=c++17", "-O1", "-g", "-ffunction-sections", "-fdata-sections",
            "-DFABGL_EMULATED", "-DAGON_EXTENDER_STOCK_ROWS_PROOF", "-I" + str(R1 / "compat"),
            "-I" + str(ROOT / "docs/tasks/PORT-003/phase-b/tests/compat"), "-I" + str(gl),
            "-include", str(R1 / "compat/host_preinclude.hpp"), "-I" + str(ROOT / "vdp/video")]
    target, target_cwd, database_hash = target_args()
    result["compile_database_sha256"] = database_hash
    result["compilers"] = {name: subprocess.check_output([flags[0], "--version"], text=True).splitlines()[0]
                           for name, flags in (("host", host), ("target", target))}
    (out / "local-commands.json").write_text(json.dumps({"host": host, "target": target,
        "target_directory": str(target_cwd)}, indent=2) + "\n")
    dependencies = set()
    for kind, flags, cwd in (("host", host, ROOT), ("target", target, target_cwd)):
        objects = []
        for source in sources:
            obj = out / f"{kind}-{source.stem}.o"
            dep = obj.with_suffix(".d")
            call(flags + ["-MMD", "-MF", str(dep), "-c", str(source), "-o", str(obj)], cwd, obj.with_suffix(".log"))
            objects.append(str(obj))
            for file in shlex.split(dep.read_text().replace("\\\n", " ").split(":", 1)[1]):
                dependencies.add((cwd / file).resolve())
        if kind == "host":
            binary = out / "scanline-tests"
            call([host[0], "-Wl,--gc-sections", *objects, "-o", str(binary)], ROOT, out / "host-link.log")
            call([str(binary)], ROOT, out / "scanline-tests.log")
            lines = (out / "scanline-tests.log").read_text().splitlines()
            assert lines[-1] == "Stock scanline comparisons: 42 checks, 0 failures", lines[-1]
            result["scanline_comparison"] = {"passed": 42, "failed": 0, "checks": lines[:-1], "summary": lines[-1]}
            result["host_executable_sha256"] = sha(binary.read_bytes())
        else:
            dsp = ROOT / "vdp/.pio/build/p4-console/esp-idf/espressif__esp-dsp/libespressif__esp-dsp.a"
            binary = out / "stock-scanlines-p4.o"
            call([target[0], "-r", "-nostdlib", *objects, str(dsp), "-o", str(binary)], ROOT, out / "target-link.log")
            nm = str(Path(target[0]).with_name("riscv32-esp-elf-nm"))
            undefined = subprocess.check_output([nm, "-uC", str(binary)], text=True)
            (out / "target-undefined.txt").write_text(undefined)
            for forbidden in ("fabgl::", "dspm::", "GPIOStream", "esp_intr_alloc", "xthal_", "xTaskCreate", "i2s", "spi_flash_cache"):
                assert forbidden not in undefined, "unexpected dependency: " + forbidden
            result["target_link"] = {"translation_units": len(sources), "format": "RISC-V ELF relocatable; not flashable",
                "sha256": sha(binary.read_bytes()), "dsp_archive_sha256": sha(dsp.read_bytes()),
                "remaining_dependencies": undefined.splitlines()}
        print(kind + " build/comparison complete", flush=True)
    local = {str(p): sha(p.read_bytes()) for p in sorted(dependencies) if p.is_file()}
    (out / "local-dependencies.json").write_text(json.dumps(local, indent=2) + "\n")
    result["project_dependencies"] = {str(p.relative_to(ROOT)): local[str(p)]
        for p in sorted(dependencies) if str(p) in local and p.is_relative_to(ROOT) and ".pio" not in p.parts}
    result["proof_files"] = {str(p.relative_to(ROOT)): sha(p.read_bytes())
        for p in sorted(HERE.iterdir()) if p.suffix in (".cpp", ".json", ".py") and p.name != "results.json"}
    # Include untracked new source bytes: git diff by itself omits them.
    for relative in result["project_dependencies"].keys() | result["proof_files"].keys():
        saved = out / "source" / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes((ROOT / relative).read_bytes())
    (out / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["scanline_comparison"]["summary"])
    print(out)


if __name__ == "__main__":
    main()
