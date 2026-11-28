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
from olimex_vdp_ota import cache_images, cache_receipt, cache_receipts
from sdcard import Client, RemoteError


PHASE = "provision-vdp-cache"


def provision(target, images, receipts, *, verify_existing=None):
    recorded = {path: cache_receipt(path, pin, receipts) for path, pin in images.items()}
    if verify_existing is not None and (verify_existing not in images or recorded[verify_existing]):
        raise ValueError("Select an unrecorded recovery image for interrupted-deployment verification")
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
                    if recorded[path] or path == verify_existing:
                        raise RuntimeError(f"Expected SD recovery file is absent: {path}") from error
                    present[path] = False
                else:
                    if size != pin["bytes"] or attributes & 0x10:
                        raise RuntimeError(f"Existing SD cache file differs in type or length: {path}")
                    if not recorded[path] and path != verify_existing:
                        raise RuntimeError(f"Reconcile the missing initial verification receipt: {path}")
                    present[path] = True
        finally:
            client.lock.close()

        for path, pin in images.items():
            label = PurePosixPath(path).stem
            if recorded[path]:
                bench_process.record(target.out / f"{label}-present.json", {
                    "path": path, "bytes": pin["bytes"],
                    "published_receipt_sha256": recorded[path]["receipt_sha256"],
                })
                continue
            source = Path(pin["path"])
            if not present[path]:
                target.staged_uart(f"{label}-put", "put", path, source=source, activate=True)
            local = target.out / f"{label}-readback.bin"
            target.staged_uart(f"{label}-verify", "get", path, destination=local)
            if local.read_bytes() != pinned(pin):
                raise RuntimeError(f"Initial SD verification differs from the pinned image: {path}")
            bench_process.record(target.out / f"{label}-verified.json", {
                "path": path, "bytes": pin["bytes"], "sha256": pin["sha256"],
                "method": "uart-readback-byte-compare", "uploaded": not present[path],
            })
    target.handback()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--config-sha256", required=True)
    parser.add_argument("--lease-state", type=Path, required=True)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--verify-existing", metavar="SD_PATH",
                        help="Complete initial verification of one unrecorded file after interrupted deployment")
    parser.add_argument("mode", choices=("preflight", "provision", "worker"))
    args = parser.parse_args()
    config_bytes = args.config.read_bytes()
    if sha256(config_bytes).hexdigest() != args.config_sha256:
        raise ValueError("Commissioned bench config hash differs")
    config = json.loads(config_bytes)
    standard = bench_process.read(ROOT / "docs/olimex-firmware-standard.json")
    images = cache_images()
    receipts = cache_receipts()
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
        provision(target, images, receipts, verify_existing=args.verify_existing)
    return 0


if __name__ == "__main__":
    sys.exit(main())
