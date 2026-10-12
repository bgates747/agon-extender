#!/usr/bin/env python3
"""Host bounds/correctness check; optional actual P4 assembly/disassembly check."""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p4-toolchain",type=Path,help="Directory containing riscv32-esp-elf-gcc/objdump")
    parser.add_argument("--p4-config",type=Path,help="Reviewed generated directory containing sdkconfig.h")
    parser.add_argument("--object-output",type=Path,help="Retain actual P4 object/disassembly under an ignored output directory")
    args=parser.parse_args()
    if bool(args.p4_toolchain)!=bool(args.p4_config):
        parser.error("Supply both P4 toolchain and generated config")
    with tempfile.TemporaryDirectory(prefix="scroll-copy-") as directory:
        work=Path(directory)
        for enabled in (False,True):
            binary=work/("check-enabled" if enabled else "check-default")
            subprocess.run([
                "g++","-std=c++17","-O2","-g","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-fno-omit-frame-pointer",
                *(["-DAGON_EXTENDER_SCROLL_FAST=1"] if enabled else []),
                "-I"+str(ROOT/"vdp/video"),str(Path(__file__).with_suffix(".cpp")),
                "-o",str(binary)],check=True)
            subprocess.run([str(binary)],check=True,timeout=30)
        if args.p4_toolchain:
            output=args.object_output.resolve() if args.object_output else work
            output.mkdir(parents=True,exist_ok=True)
            obj=output/"scroll_copy_pie.o"
            cc=args.p4_toolchain.resolve()/"riscv32-esp-elf-gcc"
            dump=args.p4_toolchain.resolve()/"riscv32-esp-elf-objdump"
            subprocess.run([
                str(cc),"-mabi=ilp32f","-march=rv32imafc_zicsr_zifencei_xesppie",
                "-DESP_PLATFORM","-DAGON_EXTENDER_SCROLL_FAST=1",
                "-I"+str(args.p4_config.resolve()),"-c",
                str(ROOT/"vdp/video/extender/display/scroll_copy_pie.S"),"-o",str(obj)],check=True)
            disassembly=subprocess.run([str(dump),"-dr",str(obj)],check=True,text=True,capture_output=True).stdout
            for instruction in ("esp.vld.128.ip","esp.vst.128.ip","esp.src.q","esp.movx.w.sar.bytes"):
                assert instruction in disassembly,instruction
            assert "cfg" not in disassembly
            (output/"scroll_copy_pie.disassembly.txt").write_text(disassembly)
            print(disassembly)
            print("PASS: actual RV32/XEspPIE object assembled; task-context and hardware output remain physical qualification gates")


if __name__=="__main__":
    main()
