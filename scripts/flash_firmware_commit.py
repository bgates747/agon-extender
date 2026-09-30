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
                                 git, keyboard_status, link_ignored, load_config, resolve_commit,
                                 run_logged, sha256, type_line, utc_stamp, wait_keyboard,
                                 wait_sd_service)


def progress(message: str) -> None:
    print(f"[{utc_stamp()}] {message}", flush=True)


def build_emos(config: dict, commit: str, run: Path) -> tuple[Path, Path, dict]:
    progress(f"Preparing clean EMOS source and builder snapshots for {commit}")
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
    progress("Building EMOS and running its firmware checks; detailed output is in firmware-check.log")
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
    progress(f"Built {firmware.stat().st_size} bytes as {build_id}")
    return snapshot, firmware, manifest


def flash_emos(config: dict, commit: str, run: Path) -> dict:
    snapshot, firmware, manifest = build_emos(config, commit, run)
    url = config["extender_url"]
    reset_config = Path(config["reset_config"]).resolve(strict=True)
    build_id = manifest["build"]["build_id"]
    # A reset can very occasionally reach MOS before the P4 completes the
    # keyboard layout/poll admission exchange.  That leaves mainboard input
    # selected, so host automation cannot issue a retry through MOS.  A second
    # reset is safe here because no transfer or FLASH command has begun.
    status = keyboard_status(url)
    admission_error = None
    for attempt in range(2):
        progress(f"Resetting the Agon before staging (attempt {attempt + 1} of 2)")
        subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/reset_agon.py"),
                        "--config", str(reset_config)], check=True)
        try:
            progress("Waiting for EMOS boot and Extender keyboard admission")
            wait_keyboard(url, old_boot=status["boot"])
            admission_error = None
            break
        except TimeoutError as error:
            admission_error = error
            status = keyboard_status(url)
            if attempt == 0:
                print("Extender keyboard admission timed out; retrying one pre-flash reset",
                      file=sys.stderr)
    if admission_error is not None:
        raise admission_error
    progress("Preparing a clean Legacy prompt and starting the fast SD listener")
    type_line(url, run / "keyboard-clear.json", "VDU 12")
    type_line(url, run / "keyboard-legacy.json", "EMOS LEGACY")
    type_line(url, run / "keyboard-service.json", "EMOS sdserve --fast /")
    client = wait_sd_service(url, run / "sd-stage.json")
    # Every run needs fresh transaction and evidence names.  Commit-only names
    # collide with the transfer protocol's retained .p17bak file, while SAVE
    # refuses to replace an older ROM dump and prevents the following sdserve.
    target = "/extender/install/" + build_id + ".bin"
    rom_name = "/agents/extender/results/" + build_id + "-rom.bin"
    verify_batch = "/extender/install/" + build_id + ".verify.txt"
    verify_commands = (f"SAVE {rom_name} &0 &20000\r\n"
                       "EMOS sdserve --fast /\r\n").encode("ascii")
    try:
        for required in ("/extender/install", "/agents/extender/results"):
            _, attributes = client.stat_entry(required)
            if not attributes & 16:
                raise RuntimeError(f"required SD path is not a directory: {required}")
        progress(f"Uploading the {firmware.stat().st_size}-byte EMOS candidate")
        client.upload(target, firmware.read_bytes(), True, fast=True)
        progress("Independently downloading the staged candidate; this is expected to take several minutes")
        if client.download(target) != firmware.read_bytes():
            raise RuntimeError("fast firmware transfer failed independent readback")
        progress(f"Uploading the {len(verify_commands)}-byte post-flash verification batch")
        client.upload(verify_batch, verify_commands, True, fast=True)
        progress("Independently reading back the verification batch")
        if client.download(verify_batch) != verify_commands:
            raise RuntimeError("verification batch failed independent readback")
        progress("Stopping the staging listener before invoking FLASH")
        client.rpc(11)
    finally:
        client.lock.close()
    old_boot = wait_keyboard(url)["boot"]
    progress("Invoking FLASH mos; do not reset or interrupt the Agon")
    type_line(url, run / "keyboard-flash.json", f"FLASH mos {target} -f")
    progress("Waiting for the automatic reboot and fresh Extender keyboard admission")
    wait_keyboard(url, old_boot=old_boot, timeout=100)

    progress("Running the post-flash ROM-save batch and waiting for its SD listener")
    type_line(url, run / "keyboard-verify-batch.json", f"EXEC {verify_batch}")
    client = wait_sd_service(url, run / "sd-verify.json")
    try:
        progress("Downloading the complete 131,072-byte installed EMOS ROM; this is expected to take several minutes")
        rom = client.download(rom_name)
        progress("Stopping the verification listener")
        client.rpc(11)
    finally:
        client.lock.close()
    expected = firmware.read_bytes().ljust(131072, b"\xff")
    progress("Comparing every installed ROM byte with the candidate and erased padding")
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
    progress(f"Preparing a clean P4 source snapshot for {commit}")
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
    progress("Building the native P4 console image")
    subprocess.run(command, cwd=snapshot, check=True)
    manifest = json.loads((build / "manifest.json").read_text())
    if manifest["source_commit"] != commit or manifest["source_dirty"]:
        raise RuntimeError("P4 build manifest does not prove the requested clean commit")
    factory = build / "build/agon_extender.factory.bin"
    return snapshot, factory, manifest


def finish_p4_install(config: dict, receipt: dict, *, reset_agon: bool) -> dict:
    """Restore and verify the EMOS-to-P4 relationship after a verified P4 flash."""
    if (receipt.get("status") != "verified" or
            not receipt.get("write_verified") or
            not receipt.get("boot_identity_observed")):
        raise RuntimeError("refusing post-flash Agon reset before verified P4 write and boot")
    if not reset_agon:
        progress("Skipping the post-flash Agon reset and connectivity check by explicit request")
        receipt.update(agon_reset_performed=False,
                       agon_connection_verified=False,
                       workflow_completed_at=utc_stamp())
        return receipt

    url = config["extender_url"]
    progress("Waiting for the newly flashed P4 HTTP status endpoint")
    deadline = time.monotonic() + 60
    before = None
    last_error: object = "no response"
    while time.monotonic() < deadline:
        try:
            before = keyboard_status(url)
            break
        except Exception as error:
            last_error = repr(error)
            time.sleep(0.25)
    if before is None:
        raise TimeoutError(f"P4 status endpoint deadline exceeded: {last_error}")

    reset_config = Path(config["reset_config"]).resolve(strict=True)
    progress("Resetting the Agon through the bench Pi to establish a fresh EMOS-to-P4 session")
    subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/reset_agon.py"),
                    "--config", str(reset_config)], check=True)
    progress("Waiting for a new EMOS boot epoch and verified Extender keyboard connectivity")
    after = wait_keyboard(url, old_boot=before["boot"], timeout=60)
    receipt.update(
        agon_reset_performed=True,
        agon_connection_verified=True,
        agon_boot_before=before["boot"],
        agon_boot_after=after["boot"],
        keyboard_ready=after["ready"],
        workflow_completed_at=utc_stamp(),
    )
    progress("Post-flash Agon reset completed; EMOS and the P4 are connected")
    return receipt


def flash_p4(config: dict, commit: str, run: Path, *, reset_agon: bool = True) -> dict:
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
    progress("Creating the isolated P4 staging directory on the bench Pi")
    subprocess.run(ssh + ["mkdir -p " + remote], check=True)
    scp = ["scp", *ssh[1:-1], str(factory), str(local_config),
           str(ROOT / "scripts/p4_flash_remote.py"), ssh[-1] + ":" + remote + "/"]
    progress("Copying the P4 image and verified-device worker to the bench Pi")
    subprocess.run(scp, check=True)
    remote_command = (p4.get("python", "python3") + " " + remote +
                      "/p4_flash_remote.py --config " + remote + "/p4-remote.json")
    progress("Backing up, flashing, verifying, and boot-checking the exact P4 device")
    lines = []
    with (run / "remote-flash.log").open("x") as log:
        process = subprocess.Popen(ssh + [remote_command], text=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
            lines.append(line.rstrip("\n"))
        returncode = process.wait()
    if returncode:
        raise subprocess.CalledProcessError(returncode, remote_command)
    lines = [line for line in lines if line.startswith("{")]
    if not lines:
        raise RuntimeError("remote P4 worker returned no receipt")
    receipt = json.loads(lines[-1])
    receipt.update(component_snapshot=str(snapshot), remote_stage=remote)
    return finish_p4_install(config, receipt, reset_agon=reset_agon)


def print_success(receipt: dict, receipt_path: Path) -> None:
    target = receipt["target"].upper()
    print("", flush=True)
    print(f"{target} FLASH WORKFLOW SUCCEEDED", flush=True)
    print(f"Installed commit: {receipt['component_commit']}", flush=True)
    print(f"Installed build: {receipt['build_id']}", flush=True)
    if receipt["target"] == "p4":
        print("P4 flash verification: every required written region verified", flush=True)
        print("P4 boot verification: installed build identity observed", flush=True)
        if receipt.get("agon_connection_verified"):
            print("Agon reset: completed through the bench Pi", flush=True)
            print("EMOS-to-P4 connectivity: verified after the fresh Agon boot", flush=True)
        else:
            print("Agon reset and EMOS-to-P4 connectivity: SKIPPED BY --no-reset-agon",
                  flush=True)
    else:
        print("EMOS ROM verification: all 131,072 installed bytes verified", flush=True)
        print("EMOS reboot and Extender keyboard admission: verified", flush=True)
    print("Receipt: " + str(receipt_path), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=("p4", "emos"))
    parser.add_argument("--commit", required=True,
                        help="exact revision in the selected component repository")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "agents/hardware-validation.local.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--no-reset-agon", action="store_true",
        help="after a P4 flash, leave the Agon untouched and skip EMOS-to-P4 connectivity verification",
    )
    args = parser.parse_args()
    if args.no_reset_agon and args.target != "p4":
        parser.error("--no-reset-agon is valid only with --target p4")
    config = load_config(args.config.resolve(strict=True))
    repository = ROOT if args.target == "p4" else Path(config["emos_repository"])
    commit = resolve_commit(repository.resolve(strict=True), args.commit)
    run = (args.output or ROOT / "agents/hardware-validation" /
           ("flash-" + args.target + "-" + utc_stamp() + "-" + commit[:12])).resolve()
    if run.exists() or run.is_symlink():
        parser.error("output must be a fresh nonexisting path")
    run.mkdir(parents=True)
    atomic_json(run / "request.json", {"target": args.target, "commit": commit,
                                        "config": str(args.config.resolve()),
                                        "reset_agon_after_p4": not args.no_reset_agon})
    receipt = (flash_p4(config, commit, run, reset_agon=not args.no_reset_agon)
               if args.target == "p4" else flash_emos(config, commit, run))
    receipt["receipt_path"] = str(run / "flash-receipt.json")
    atomic_json(run / "flash-receipt.json", receipt)
    print_success(receipt, run / "flash-receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
