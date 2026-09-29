#!/usr/bin/env python3
"""Pi-side exact-device P4 flash worker; invoked only by flash_firmware_commit.py."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized(value: str) -> str:
    return re.sub(r"[:-]", "", value).lower()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    root = args.config.resolve().parent
    image = root / config["image"]
    if sha(image) != config["image_sha256"]:
        raise RuntimeError("staged factory image hash mismatch")
    stable = Path(config["stable_port"])
    resolved = stable.resolve(strict=True)
    properties = dict(
        line.split("=", 1) for line in subprocess.check_output(
            ["udevadm", "info", "--query=property", "--name", str(resolved)],
            text=True,
        ).splitlines() if "=" in line
    )
    if normalized(properties.get("ID_SERIAL_SHORT", "")) != normalized(config["usb_serial"]):
        raise RuntimeError("stable path resolved to the wrong USB serial")
    if not os.access(stable, os.R_OK | os.W_OK):
        raise RuntimeError("stable P4 serial path is not readable and writable")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d-%H-%M-%SZ")
    evidence = root / ("deploy-" + stamp)
    evidence.mkdir()
    esptool = config["esptool"]
    base = [esptool, "--chip", "esp32p4", "--port", str(stable), "--baud", "460800"]

    def run(label: str, tail: list[str]) -> None:
        argv = base + tail
        (evidence / (label + "-command.json")).write_text(json.dumps({
            "device": {"stable": str(stable), "resolved": str(resolved),
                       "usb_serial": properties["ID_SERIAL_SHORT"]},
            "argv": argv,
        }, indent=2) + "\n")
        with (evidence / (label + ".log")).open("x") as log:
            completed = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT)
        if completed.returncode:
            raise subprocess.CalledProcessError(completed.returncode, argv)

    backup = evidence / "preflash-16MiB.bin"
    run("readback", ["--before", "usb_reset", "--after", "no_reset",
                     "read_flash", "0x0", hex(int(config["flash_bytes"])), str(backup)])
    run("write", ["--before", "no_reset", "--after", "no_reset", "write_flash",
                  "--flash_mode", "keep", "--flash_freq", "keep",
                  "--flash_size", "keep", "0x0", str(image)])
    run("verify", ["--before", "no_reset", "--after", "hard_reset",
                   "verify_flash", "0x0", str(image)])

    deadline = time.monotonic() + 30
    while not stable.exists() and time.monotonic() < deadline:
        time.sleep(0.2)
    stable.resolve(strict=True)
    import serial
    port = serial.Serial(port=None, baudrate=115200, timeout=1)
    port.dtr = False
    port.rts = False
    port.port = str(stable)
    port.open()
    boot = bytearray()
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            boot.extend(port.read(4096))
    finally:
        port.close()
    (evidence / "boot.log").write_bytes(boot)
    expected = config["build_id"].encode()
    if expected not in boot or b"USB HOST READY:" not in boot:
        raise RuntimeError("flashed build identity or USB host readiness was not observed")
    faults = (b"Guru Meditation", b"abort()", b"USB FAIL", b"USB HOST FAULT")
    if any(item in boot for item in faults):
        raise RuntimeError("P4 boot log contains a fatal marker")
    receipt = {
        "schema": 1, "status": "verified", "target": "p4",
        "component_commit": config["component_commit"],
        "build_id": config["build_id"],
        "artifact_sha256": config["image_sha256"],
        "backup": {"path": str(backup), "bytes": backup.stat().st_size,
                   "sha256": sha(backup)},
        "write_verified": True, "boot_identity_observed": True,
        "evidence": str(evidence), "completed_at": stamp,
    }
    (evidence / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

