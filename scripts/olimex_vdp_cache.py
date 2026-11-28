#!/usr/bin/env python3
"""Provision the selected VDPlet recovery apps on the Olimex SD card."""

import argparse
import fcntl
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import sys

import bench_process
from olimex_bench import Bench, PRESERVED, ROOT, pinned
from olimex_vdp_ota import cache_images
from sdcard import Client, RemoteError


PHASE = "provision-vdp-cache"


def provision(target, images):
    target.verify_mos("cache-entry")
    with target.uart_listener("vdp-cache"):
        client = Client(target.url, target.out / "cache-metadata.json", timeout=12)
        present = {}
        try:
            client.connect(require_fast=True)
            client.make_directory("/extender/recovery/vdp", parents=True)
            for path, pin in images.items():
                try:
                    size, attributes = client.stat_entry(path)
                except RemoteError as error:
                    if error.status != 6 or error.detail not in (b"\x04", b"\x05"):
                        raise
                    present[path] = False
                else:
                    if size != pin["bytes"] or attributes & 0x10:
                        raise RuntimeError(f"Existing SD cache file differs in type or length: {path}")
                    present[path] = True
        finally:
            client.lock.close()

        for path, pin in images.items():
            label = PurePosixPath(path).stem
            receipt = {"path": path, "bytes": pin["bytes"], "expected_sha256": pin["sha256"]}
            if present[path]:
                receipt["evidence"] = "existing-file-metadata"
            else:
                reply = target.staged_uart(f"{label}-put", "put", path,
                                           source=Path(pin["path"]), activate=True)
                receipt.update(evidence="completed-upload", transfer=reply)
            bench_process.record(target.out / f"{label}-provisioned.json", receipt)
    target.handback()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--config-sha256", required=True)
    parser.add_argument("--lease-state", type=Path, required=True)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("mode", choices=("preflight", "provision", "worker"))
    args = parser.parse_args()
    config_bytes = args.config.read_bytes()
    if sha256(config_bytes).hexdigest() != args.config_sha256:
        raise ValueError("Commissioned bench config hash differs")
    config = json.loads(config_bytes)
    standard = bench_process.read(ROOT / "docs/olimex-firmware-standard.json")
    images = cache_images()
    for pin in images.values():
        pinned(pin)
    if args.mode == "preflight":
        print(json.dumps(images, indent=2))
        return 0

    def own_slot():
        if bench_process.read(args.lease_state)["active"] != args.operator:
            raise RuntimeError("The named operator does not own the Olimex slot")

    own_slot()
    argv = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:-1], "worker"]
    if args.mode == "provision":
        return bench_process.run(argv, args.out, 1400, owner=args.operator,
                                 phase=PHASE, lease=f"chat:{args.operator}",
                                 next_action="Keep the slot and follow the bench stop procedure.")
    supervisor = bench_process.read(args.out / "supervisor-started.json")
    if (supervisor["argv"] != argv or supervisor["phase"] != PHASE
            or supervisor["owner"] != args.operator or supervisor["lease"] != f"chat:{args.operator}"):
        raise RuntimeError("SD cache provisioning needs its joined supervisor")
    with Path(config["operation_lock"]).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        own_slot()
        inventory = bench_process.read(config["inventory"])
        if inventory.get("pending_operation") or inventory.get("ready_claim") is not True:
            raise RuntimeError("Reconcile the installed firmware inventory before changing the SD cache")
        preserve = dict(zip(PRESERVED, (inventory["components"]["startup_sha256"],
                                        standard["listener"]["sha256"]), strict=True))
        kit = {"namespace": PHASE, "transfer": "uart", "firmware": {}, "preserve": preserve}
        target = Bench(config, kit, args.out)
        target.lock = lock
        provision(target, images)
    return 0


if __name__ == "__main__":
    sys.exit(main())
