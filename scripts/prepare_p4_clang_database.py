#!/usr/bin/env python3
"""Create a validated Clang view of the canonical ESP GCC action database."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex


ROOT = Path(__file__).resolve().parents[1]
VDP = ROOT / "vdp"
PROFILE_PATH = VDP / "build/p4-profiles.json"
TOOLCHAIN = (ROOT / "agents/build001/native-tools/espressif/tools/"
             "riscv32-esp-elf/esp-14.2.0_20260121/riscv32-esp-elf")
GXX = TOOLCHAIN / "riscv32-esp-elf/include/c++/14.2.0"


def expand_response(arguments: list[str], directory: Path) -> list[str]:
    result: list[str] = []
    for argument in arguments:
        if argument.startswith("@"):
            response = Path(argument[1:].strip('"'))
            if not response.is_absolute():
                response = directory / response
            result.extend(shlex.split(response.read_text()))
        else:
            result.append(argument)
    return result


def translate(entry: dict, clang_root: Path) -> dict:
    directory = Path(entry["directory"])
    arguments = expand_response(shlex.split(entry["command"]), directory)
    is_cxx = Path(entry["file"]).suffix != ".c"
    translated = [str(clang_root / "bin" / ("clang++" if is_cxx else "clang"))]
    skip = {"-fstrict-volatile-bitfields", "-fno-tree-switch-conversion"}
    for argument in arguments[1:]:
        if argument in skip:
            continue
        if argument.startswith("-march="):
            argument = argument.replace("_xesppie", "")
        translated.append(argument)
    translated += ["--target=riscv32-esp-elf",
                   "-isystem", str(TOOLCHAIN / "riscv32-esp-elf/include")]
    if is_cxx:
        translated += ["-nostdinc++", "-isystem", str(GXX),
                       "-isystem", str(GXX / "riscv32-esp-elf"),
                       "-isystem", str(GXX / "backward")]
    return {"directory": entry["directory"], "file": entry["file"],
            "output": entry.get("output"), "arguments": translated}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--clang-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    profiles = json.loads(PROFILE_PATH.read_text())["profiles"]
    if args.profile not in profiles:
        parser.error("unknown profile")
    selected = {(VDP / item).resolve() for item in profiles[args.profile]["sources"]}
    database = json.loads(args.input.read_text())
    actual: dict[Path, list[dict]] = {}
    for entry in database:
        actual.setdefault(Path(entry["file"]).resolve(), []).append(entry)
    errors = [f"{path}: {len(actual.get(path, []))} actions"
              for path in sorted(selected) if len(actual.get(path, [])) != 1]
    if errors:
        raise SystemExit("invalid canonical database: " + "; ".join(errors))
    if not (args.clang_root / "bin/clang-tidy").is_file():
        raise SystemExit("clang root lacks bin/clang-tidy")
    if not GXX.is_dir():
        raise SystemExit("pinned Espressif C++ headers are absent")
    translated = [translate(actual[path][0], args.clang_root.resolve())
                  for path in sorted(selected)]
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "compile_commands.json").write_text(
        json.dumps(translated, indent=2) + "\n")
    report = {"schema_version": 1, "profile": args.profile,
              "canonical_actions": len(database),
              "selected_actions": len(translated),
              "removed_flags": ["-fstrict-volatile-bitfields",
                                  "-fno-tree-switch-conversion"],
              "translated_march_suffix": "_xesppie", "result": "PASS"}
    (args.output / "translation.json").write_text(
        json.dumps(report, indent=2) + "\n")
    print(f"Clang database view PASS: {len(translated)} selected actions")


if __name__ == "__main__":
    main()
