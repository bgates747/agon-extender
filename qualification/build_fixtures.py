#!/usr/bin/env python3
"""Build stopped qualification applications in a fresh local output directory."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hardware_validation import atomic_json, sha256, utc_stamp, resolve_commit


def build(emos: Path, toolchain: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    sources = {
        "qstate": ROOT / "tests/fixtures/qualification-state",
        "raw_sd": emos / "projects/fwbug008-physical",
    }
    result = {"schema": 1, "status": "built-offline", "created_at": utc_stamp(),
              "fixture_contract": "explicit-cli-no-startup-write", "fixtures": {}}
    for name, source in sources.items():
        work = output / name
        work.mkdir()
        shutil.copytree(source / "src", work / "src")
        shutil.copy2(source / "Makefile", work / "Makefile")
        if name == "qstate":
            shutil.copy2(ROOT / "tests/fixtures/controller/mos_io.asm", work / "src/mos_io.asm")
        inputs = {str(p.relative_to(work)): sha256(p) for p in sorted(work.rglob("*")) if p.is_file()}
        # The old EMOS fixture wrote a recovery startup from inside the app.
        # Refuse to build that frozen snapshot even if the host runner is fixed.
        if any(b"/autoexec.txt" in p.read_bytes() for p in (work / "src").rglob("*") if p.is_file()):
            raise ValueError("obsolete startup-writing qualification fixture")
        with (output / (name + "-build.log")).open("x") as log:
            subprocess.run(["make", "all", f"AGONDEV_TOOLCHAIN={toolchain.resolve()}"],
                           cwd=work, stdout=log, stderr=subprocess.STDOUT, check=True)
        binary = work / "bin" / ("QSTATE.bin" if name == "qstate" else "FWBUG008.bin")
        if b"/autoexec.txt" in binary.read_bytes():
            raise ValueError("startup path present in qualification application")
        result["fixtures"][name] = {"binary": str(binary.resolve()), "sha256": sha256(binary),
                                    "source_files": inputs,
                                    "owner_commit": resolve_commit(emos if name == "raw_sd" else ROOT, "HEAD"),
                                    "source_state": "exact copied inputs; commit alone may have local preparation changes"}
    atomic_json(output / "fixtures.json", result)
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--emos-source", required=True, type=Path)
    p.add_argument("--toolchain", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    build(a.emos_source.resolve(strict=True), a.toolchain.resolve(strict=True), a.output.resolve())
    print("Qualification applications built offline; nothing deployed or invoked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
