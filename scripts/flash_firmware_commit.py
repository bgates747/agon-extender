#!/usr/bin/env python3
"""Build, install, and independently verify P4 or EMOS at one exact commit."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hardware_validation import (atomic_json, clean_snapshot, copy_tree_dependency,
                                 git, link_ignored, load_config, resolve_commit,
                                 run_logged, sha256, type_line, utc_stamp, wait_keyboard,
                                 wait_sd_service)


def build_emos(config: dict, commit: str, run: Path) -> tuple[Path, Path, dict]:
    run = run.resolve()
    source = Path(config["emos_repository"]).resolve(strict=True)
    snapshot = clean_snapshot(source, commit, run / "source-emos")
    builder_source = Path(config["builder_repository"]).resolve(strict=True)
    builder_commit = resolve_commit(builder_source, "HEAD")
    builder = clean_snapshot(builder_source, builder_commit, run / "source-builder")
    for relative in (".venv", "toolchains"):
        link_ignored(builder, relative, builder_source / relative)
    worktree = builder / "projects/mos-port/worktree"
    run_logged(
        [str(builder / ".venv/bin/python"),
         str(builder / "scripts/prepare_mos_worktree.py"),
         "--upstream", str(snapshot), "--destination", str(worktree)],
        run / "prepare.log", cwd=builder,
    )
    output = run / "build"
    output.mkdir()
    build_id = "hwval-emos-" + commit[:12] + "-" + utc_stamp()
    environment = dict(os.environ, EMOS_BUILD_ID=build_id)
    make = ["make", f"PYTHON={ROOT / '.venv/bin/python'}",
            f"MOS_AGONDEV_ROOT={builder}", f"MOS_WORKTREE={worktree}",
            f"AGONDEV_TOOLCHAIN={builder / 'toolchains/agondev'}",
            f"MOS_AGONDEV_PYTHON={builder / '.venv/bin/python'}",
            f"EMOS_BUILD_ID={build_id}", "firmware-check"]
    run_logged(make, run / "firmware-check.log", cwd=snapshot, env=environment)
    source_firmware = builder / "projects/mos-port/bin/MOS.bin"
    firmware = output / (build_id + ".bin")
    shutil.copyfile(source_firmware, firmware)
    record = {"filename": firmware.name, "role": "firmware",
              "size_bytes": firmware.stat().st_size, "sha256": sha256(firmware)}
    manifest = {
        "schema_version": 1,
        "build": {"artifact_id": "agon-emos", "build_id": build_id,
                  "status": "candidate"},
        "provenance": {"commit": commit, "dirty": False,
                       "builder_commit": builder_commit, "builder_dirty": False},
        "outputs": [record],
    }
    atomic_json(output / "build-manifest.json", manifest)
    if git(snapshot, "status", "--porcelain"):
        raise RuntimeError("EMOS source snapshot changed during its firmware build")
    if git(builder, "status", "--porcelain"):
        raise RuntimeError("MOS builder snapshot changed outside ignored build outputs")
    return snapshot, firmware, manifest


def flash_emos(config: dict, commit: str, run: Path) -> dict:
    snapshot, firmware, manifest = build_emos(config, commit, run)
    url = config["extender_url"]
    reset_config = Path(config["reset_config"]).resolve(strict=True)
    subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/reset_agon.py"),
                    "--config", str(reset_config)], check=True)
    ready = wait_keyboard(url)
    type_line(url, run / "keyboard-clear.json", "VDU 12")
    type_line(url, run / "keyboard-legacy.json", "EMOS LEGACY")
    type_line(url, run / "keyboard-service.json", "EMOS sdserve --fast /")
    client = wait_sd_service(url, run / "sd-stage.json")
    target = "/extender/install/hwval-" + commit[:12] + ".bin"
    try:
        client.make_directory("/extender", parents=True)
        client.make_directory("/extender/install", parents=True)
        client.make_directory("/agents", parents=True)
        client.make_directory("/agents/extender", parents=True)
        client.make_directory("/agents/extender/results", parents=True)
        client.upload(target, firmware.read_bytes(), True, fast=True)
        if client.download(target) != firmware.read_bytes():
            raise RuntimeError("fast firmware transfer failed independent readback")
        client.rpc(11)
    finally:
        client.lock.close()
    old_boot = ready["boot"]
    type_line(url, run / "keyboard-flash.json", f"FLASH mos {target} -f")
    wait_keyboard(url, old_boot=old_boot, timeout=100)

    rom_name = "/agents/extender/results/hwval-rom-" + commit[:12] + ".bin"
    type_line(url, run / "keyboard-save.json", f"SAVE {rom_name} &0 &20000")
    type_line(url, run / "keyboard-verify-service.json", "EMOS sdserve --fast /")
    client = wait_sd_service(url, run / "sd-verify.json")
    try:
        rom = client.download(rom_name)
        client.rpc(11)
    finally:
        client.lock.close()
    expected = firmware.read_bytes().ljust(131072, b"\xff")
    if rom != expected:
        raise RuntimeError("full 128 KiB EMOS ROM does not match the candidate plus erased padding")
    rom_path = run / "installed-rom.bin"
    rom_path.write_bytes(rom)
    return {
        "schema": 1, "status": "verified", "target": "emos",
        "component_commit": commit, "component_snapshot": str(snapshot),
        "build_id": manifest["build"]["build_id"],
        "artifact": str(firmware), "artifact_sha256": sha256(firmware),
        "installed_rom_sha256": sha256(rom_path), "installed_rom_bytes": len(rom),
        "automatic_reboot_observed": True, "full_rom_verified": True,
        "evidence": str(run), "completed_at": utc_stamp(),
    }


def build_p4(config: dict, commit: str, run: Path) -> tuple[Path, Path, dict]:
    run = run.resolve()
    snapshot = clean_snapshot(ROOT, commit, run / "source-extender")
    copy_tree_dependency(snapshot, "agents/build001/native-tools",
                         ROOT / "agents/build001/native-tools")
    copy_tree_dependency(snapshot, "vdp/managed_components", ROOT / "vdp/managed_components")
    link_ignored(snapshot, ".venv", ROOT / ".venv")
    build = run / "build"
    build_id = "hwval-p4-" + commit[:12] + "-" + utc_stamp()
    command = [str(ROOT / ".venv/bin/python"), str(snapshot / "scripts/build_p4.py"),
               "--profile", "p4-console", "--output", str(build),
               "--build-id", build_id]
    if config.get("reset_url"):
        command.extend(("--reset-url", config["reset_url"]))
    subprocess.run(command, cwd=snapshot, check=True)
    manifest = json.loads((build / "manifest.json").read_text())
    if manifest["source_commit"] != commit or manifest["source_dirty"]:
        raise RuntimeError("P4 build manifest does not prove the requested clean commit")
    factory = build / "build/agon_extender.factory.bin"
    return snapshot, factory, manifest


def flash_p4(config: dict, commit: str, run: Path) -> dict:
    snapshot, factory, manifest = build_p4(config, commit, run)
    p4 = config["p4"]
    remote = p4.get("stage_root", "/home/smith/agon-bench/agon-extender/hardware-validation")
    remote = remote.rstrip("/") + "/" + manifest["build_id"]
    remote_config = {
        "image": factory.name, "image_sha256": sha256(factory),
        "build_id": manifest["build_id"], "component_commit": commit,
        "stable_port": p4["stable_port"], "usb_serial": p4["usb_serial"],
        "esptool": p4["esptool"], "flash_bytes": int(p4.get("flash_bytes", 16777216)),
    }
    local_config = run / "p4-remote.json"
    atomic_json(local_config, remote_config)
    ssh = p4["ssh"]
    subprocess.run(ssh + ["mkdir -p " + remote], check=True)
    scp = ["scp", *ssh[1:-1], str(factory), str(local_config),
           str(ROOT / "scripts/p4_flash_remote.py"), ssh[-1] + ":" + remote + "/"]
    subprocess.run(scp, check=True)
    remote_command = (p4.get("python", "python3") + " " + remote +
                      "/p4_flash_remote.py --config " + remote + "/p4-remote.json")
    completed = subprocess.run(ssh + [remote_command], text=True, capture_output=True)
    (run / "remote-flash.log").write_text(completed.stdout + completed.stderr)
    if completed.returncode:
        raise subprocess.CalledProcessError(completed.returncode, remote_command)
    lines = [line for line in completed.stdout.splitlines() if line.startswith("{")]
    if not lines:
        raise RuntimeError("remote P4 worker returned no receipt")
    receipt = json.loads(lines[-1])
    receipt.update(component_snapshot=str(snapshot), remote_stage=remote)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=("p4", "emos"))
    parser.add_argument("--commit", required=True,
                        help="exact revision in the selected component repository")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "agents/hardware-validation.local.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = load_config(args.config.resolve(strict=True))
    repository = ROOT if args.target == "p4" else Path(config["emos_repository"])
    commit = resolve_commit(repository.resolve(strict=True), args.commit)
    run = (args.output or ROOT / "agents/hardware-validation" /
           ("flash-" + args.target + "-" + utc_stamp() + "-" + commit[:12])).resolve()
    if run.exists() or run.is_symlink():
        parser.error("output must be a fresh nonexisting path")
    run.mkdir(parents=True)
    atomic_json(run / "request.json", {"target": args.target, "commit": commit,
                                        "config": str(args.config.resolve())})
    receipt = flash_p4(config, commit, run) if args.target == "p4" else flash_emos(config, commit, run)
    receipt["receipt_path"] = str(run / "flash-receipt.json")
    atomic_json(run / "flash-receipt.json", receipt)
    print("FLASH VERIFIED")
    print("Receipt: " + str(run / "flash-receipt.json"))
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
