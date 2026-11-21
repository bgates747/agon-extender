#!/usr/bin/env python3
"""Supervise the commissioned BENCH-024 verified OTA round trip."""

import argparse
import fcntl
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import time

from ota_receipt import verify_candidate_boot, verify_selection, verify_write

ROOT = Path(__file__).resolve().parents[3]
CHECKOUT = ROOT.parent / "olimex-bench"
sys.path.insert(0, str(CHECKOUT / "scripts"))
import bench_process
from olimex_bench import (
    Bench, Observer, PARALLEL_LISTENER, RemoteError, open_passive_serial, pinned, status,
)
from olimex_flash import check_app0, check_extent, flash_application
from olimex_p4_app import reboot_pair

FLASH_PHASES = ("write-candidate", "select-candidate", "boot-candidate",
                "write-production", "select-production")
ORDER = ("bootstrap", "stage", *FLASH_PHASES, "boot-production", "verify-production")
BOUNDS = dict.fromkeys(ORDER, 420)
BOUNDS["bootstrap"] = 600
BOUNDS["stage"] = 480
BOUNDS["boot-candidate"] = 180
ADDRESS = "0B0000"
PRODUCTION_BANNER = "VDPlet Version 0.1.3-alpha"


def load_packet(job_path, expected_digest):
    raw = job_path.read_bytes()
    if sha256(raw).hexdigest() != expected_digest:
        raise ValueError("Job manifest hash differs")
    job = json.loads(raw)
    namespace = job["namespace"]
    if not re.fullmatch(r"b024-[0-9a-z]{6,16}", namespace):
        raise ValueError("Use one fresh bounded BENCH-024 namespace")
    if not re.fullmatch(r"[0-9a-f]{40}", job["runner"]):
        raise ValueError("Pin the full commissioned runner revision")
    executable = pinned(job["utility"])
    if not executable or len(executable) > 0x8000:
        raise ValueError("Agon Flash binary does not fit its pinned load layout")
    if not pinned(job["bootstrap_app0"]) or not pinned(job["receiver_manifest"]):
        raise ValueError("Missing sealed receiver input")
    for key in ("partition_table", "production_app0_extent"):
        pinned(job["usb_fallback"][key])
    legs = job["legs"]
    transactions = set()
    for name in ("candidate", "production"):
        spec = legs[name]
        transaction = spec["transaction"]
        if not re.fullmatch(r"[0-9a-f]{8}", transaction) or int(transaction, 16) == 0:
            raise ValueError(f"Invalid {name} transaction")
        transactions.add(transaction)
        if not re.fullmatch(r"[0-9a-f]{32}", spec["source_build"]):
            raise ValueError(f"Pin the {name} entry ELF build ID")
        image = pinned(spec["image"])
        if not image or len(image) > 0x140000:
            raise ValueError(f"Invalid size for {name} image on the stock app-slot layout")
    if len(transactions) != 2:
        raise ValueError("Each round-trip leg needs a fresh transaction")
    production = pinned(legs["production"]["image"])
    if job.get("physical_commissioning") == "approved":
        spec = job["firmware"]["mainboard"]
        bootstrap = pinned(job["bootstrap_app0"])
        padded = pinned(job["bootstrap_app0_extent"])
        check_extent("mainboard", spec, padded)
        if padded != bootstrap.ljust(len(padded), b"\xff"):
            raise ValueError("Bootstrap app and padded extent differ")
        if spec["partition_table"] != job["usb_fallback"]["partition_table"]:
            raise ValueError("Bootstrap and recovery partition tables differ")
    restore = pinned(job["usb_fallback"]["production_app0_extent"])
    if len(restore) < len(production) or restore != production.ljust(len(restore), b"\xff"):
        raise ValueError("USB fallback and OTA production return images differ")
    return job


class UpdateBench(Bench):
    def image(self, leg):
        return pinned(self.kit["legs"][leg]["image"])

    def transfer_inputs(self):
        directory = self.install_dir
        files = {
            f"{directory}/flash.bin": pinned(self.kit["utility"]),
            f"{directory}/candidate.bin": self.image("candidate"),
            f"{directory}/production.bin": self.image("production"),
        }
        for phase in FLASH_PHASES:
            files[f"{directory}/{phase}.txt"] = self.batch(phase)
        reserved = [f"{directory}/{name}.dat{suffix}"
                    for name in FLASH_PHASES for suffix in ("", ".log")]

        def absent(client, remote):
            try:
                return client.stat_entry(remote)
            except RemoteError as error:
                if error.status == 6 and error.detail in (b"\x04", b"\x05"):
                    return None
                raise

        self.validate_ports()
        self.stage_parallel(files, reserved, absent)

    def command(self, phase):
        if phase == "boot-candidate":
            return "vdp-status boot-candidate.dat"
        action, leg = phase.split("-")
        if action == "select":
            return f"vdp-activate write-{leg}.dat {phase}.dat"
        spec = self.kit["legs"][leg]
        slot = int(leg == "candidate")
        return (f"vdp-stage {leg}.bin {phase}.dat {spec['transaction']} {slot} "
                f"{spec['image']['bytes']} {spec['image']['sha256']}")

    def batch(self, phase):
        return f"RUN &{ADDRESS} {self.command(phase)}\r\n{PARALLEL_LISTENER}\r\n".encode("ascii")

    def run_flash(self, phase):
        self.validate_ports()
        self.idle()
        self.keyboard()
        directory = self.install_dir
        with open_passive_serial(self.c["ports"][0], timeout=0.2) as reader:
            with (self.out / "mainboard-serial.bin").open("xb") as transcript:
                observer = Observer(reader, transcript, self.type_line)
                self.type_line("mirror-on", "VDU 2")
                prompt = observer.witness()
                original = "/" if prompt == b"*" else prompt[:-2].decode("ascii")
                if (not re.fullmatch(r"/[A-Za-z0-9_./-]*", original)
                        or ".." in Path(original).parts):
                    raise ValueError("Cannot restore the original MOS directory")
                prompt = observer.change_directory("ota-cwd", directory, prompt)
                observer.quiet_load(f"LOAD flash.bin &{ADDRESS}", prompt)
                # The native receiver requires printer mirroring off for OTA.
                observer.mirror_off(prompt)
                self.type_line("run-flash", f"EXEC {directory}/{phase}.txt")
                deadline = time.monotonic() + 300
                while not self.get("/sd/status")["online"]:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Flash command did not return to its foreground listener")
                    time.sleep(0.2)

                results = self.out / "results"
                results.mkdir()
                name = f"{phase}.dat"
                self.collect_results({"results": [f"{directory}/{name}.log", f"{directory}/{name}"]},
                                     results, True, listener_online=True)
                self.type_line("mirror-resume", "VDU 2")
                returned = observer.witness("ota-return")
                if returned.lower() != prompt.lower():
                    raise RuntimeError("Agon Flash did not return to the original OTA directory")
                returned = observer.change_directory("return-cwd", original, returned)
                observer.mirror_off(returned, "mirror-off-final")
        return (results / name).read_bytes()


def saved_phase(root, phase, name):
    return (root / phase / "results" / name).read_bytes()


def write_proof(bench, leg, raw):
    spec = bench.kit["legs"][leg]
    return verify_write(raw, int(spec["transaction"], 16), int(leg == "production"),
                        spec["source_build"], bench.image(leg))


def write_phase(bench, leg, phase):
    before, after = write_proof(bench, leg, bench.run_flash(phase))
    if leg == "production":
        expected = bench_process.read(bench.out.parent / "boot-candidate" / "boot.json")
        if before.evidence() != expected:
            raise RuntimeError("Production write did not start on the verified boot of receiver B")
    return before, after


def select_phase(bench, leg, phase):
    name = f"write-{leg}.dat"
    raw = saved_phase(bench.out.parent, f"write-{leg}", name)
    _, verified = write_proof(bench, leg, raw)
    result = bench.run_flash(phase)
    return verify_selection(result, verified)


def candidate_boot(bench):
    root = bench.out.parent
    _, verified = write_proof(bench, "candidate",
                              saved_phase(root, "write-candidate", "write-candidate.dat"))
    _, selected = verify_selection(saved_phase(root, "select-candidate", "select-candidate.dat"),
                                   verified)
    old = bench.keyboard()["boot"]
    selected_receipt = bench_process.read(root / "select-candidate" / "vdplet.json")
    if old != selected_receipt["emos_boot"]:
        raise RuntimeError("Agon boot changed after candidate selection")
    reboot_pair(bench, old)
    bench.cli("candidate-boot-cli")
    return verify_candidate_boot(bench.run_flash("boot-candidate"),
                                 selected, bench.kit["legs"]["production"]["source_build"])


def bootstrap_entry(job, inventory):
    spec = job["firmware"]["mainboard"]
    if inventory["components"] != job["entry_components"]:
        raise RuntimeError("Installed components differ from the pinned bootstrap entry")
    if "production_entry" in job:
        restored = Path(job["production_entry"])
        start = bench_process.read(restored / "supervisor-started.json")
        proof = bench_process.verify_child(restored, start["argv"])
        receipt_path = restored / "independent-verification.json"
        receipt = bench_process.read(receipt_path)
        image = pinned(job["usb_fallback"]["production_app0_extent"])
        prod = job["legs"]["production"]["image"]
        if (inventory["pending_operation"]
                or inventory["components"]["native_vdp_sha256"] != prod["sha256"]
                or inventory["native_vdp"]["verification_receipt"] != str(receipt_path)
                or receipt["sha256"] != prod["sha256"]
                or not receipt["boot_cli_ready"]
                or (restored / "readback.bin").read_bytes() != image):
            raise RuntimeError("Bootstrap requires the verified production app0 entry")
        return proof

    attempted = Path(job["prior_interrupted_readback"])
    start = bench_process.read(attempted / "supervisor-started.json")
    proof = bench_process.verify_child(attempted, start["argv"], expected_returncode=1)
    dispatch = bench_process.read(attempted / "write-dispatched.json")
    log = (attempted / "programmer.log").read_text()
    if (dispatch != {"offset": int(spec["offset"], 0), "bytes": spec["write_bytes"]}
            or "Hash of data verified." not in log
            or "expected 0x1000 bytes but received 0xfd4 bytes" not in log
            or (attempted / "independent-verification.json").exists()):
        raise RuntimeError("Prior attempt does not establish the expected interrupted readback")
    table = pinned(spec["partition_table"])
    if (attempted / "partition-table.bin").read_bytes() != table:
        raise RuntimeError("Prior attempt did not establish the stock app-slot layout")
    check_app0((attempted / "ota-selector.bin").read_bytes())
    inventory = bench_process.read(bench.config["inventory"])
    pending = inventory["pending_operation"]
    if (not pending or pending["component"] != "native_vdp"
            or Path(pending["operation"]).resolve() != attempted.resolve()
            or pending["write_sha256"] != sha256((attempted / "write.bin").read_bytes()).hexdigest()):
        raise RuntimeError("Firmware inventory does not match the retained BENCH-023 stop")
    return proof


def bootstrap(bench):
    """Install receiver A in app0 using the commissioned programmer."""
    job = bench.kit
    spec = job["firmware"]["mainboard"]
    inventory = bench_process.read(bench.config["inventory"])
    proof = bootstrap_entry(job, inventory)
    bench_process.record(bench.out / "bootstrap-entry-proof.json", proof)
    bench_process.record(bench.out / "inventory-before.json", inventory)

    bench.validate_ports()
    bench.idle()
    if "production_entry" not in job:
        reboot_pair(bench, status(bench.url)["boot"])
    bench.cli("bootstrap-entry-cli")
    before = bench.keyboard()["boot"]
    image = pinned(job["bootstrap_app0_extent"])
    table = pinned(spec["partition_table"])

    def begin():
        inventory["pending_operation"] = {
            "component": "native_vdp", "selection": "candidate",
            "operation": str(bench.out), "write_sha256": job["bootstrap_app0_extent"]["sha256"],
            "recorded_epoch": time.time(),
        }
        inventory["ready_claim"] = False
        bench.update_inventory(inventory)

    if "programmer_51" in job:
        programmer = job["programmer_51"]
        pinned(programmer)
        (bench.out / "write.bin").write_bytes(image)
        (bench.out / "expected-partition-table.bin").write_bytes(table)
        begin()
        with (bench.out / "programmer.log").open("xb") as log:
            subprocess.run([sys.executable, "-u", programmer["path"], str(bench.c["ports"][0]),
                            bench.config["mainboard_mac"], str(bench.out)], stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=330)
        readback = bench.out / "readback.bin"
    else:
        readback = flash_application(
            "mainboard", bench.config["programmer"], bench.c["ports"][0],
            bench.config["mainboard_mac"], spec, image, table, bench.out, begin)
    if readback.read_bytes() != image:
        raise RuntimeError("Receiver A app0 readback differs")
    bench_process.record(bench.out / "write-verified.json", job["bootstrap_app0_extent"])
    restart_dir = bench.out / "post-write-boot"
    restart_dir.mkdir()
    restart_bench = UpdateBench(bench.config, job, restart_dir)
    restart_bench.lock = bench.lock
    reboot_pair(restart_bench, before)
    restart_bench.cli("bootstrap-cli")
    receipt = {
        "sha256": job["bootstrap_app0"]["sha256"],
        "verified_extent_sha256": sha256(image).hexdigest(),
        "verified_extent_bytes": len(image), "readback": str(readback), "boot_cli_ready": True,
        "verification_receipt": str(bench.out / "independent-verification.json"),
        "status": "verified-exception", "verified_epoch": time.time(),
    }
    bench_process.record(receipt["verification_receipt"], receipt)
    inventory["components"]["native_vdp_sha256"] = receipt["sha256"]
    inventory["native_vdp"] = dict(receipt, prior=inventory.get("native_vdp"))
    inventory["pending_operation"] = None
    inventory["recorded_epoch"] = time.time()
    bench.update_inventory(inventory)


def production_boot(bench):
    root = bench.out.parent
    _, written = write_proof(bench, "production",
                            saved_phase(root, "write-production", "write-production.dat"))
    _, selected = verify_selection(
        saved_phase(root, "select-production", "select-production.dat"), written)
    old = bench.keyboard()["boot"]
    receipt = bench_process.read(root / "select-production" / "vdplet.json")
    if old != receipt["emos_boot"]:
        raise RuntimeError("Agon boot changed after production selection")
    reboot_pair(bench, old)
    bench.cli("production-boot-cli")
    new = bench.keyboard()["boot"]
    if new == old:
        raise RuntimeError("Production restart did not produce a fresh MOS boot")
    bench_process.record(bench.out / "production-boot.json",
                         {"selected": selected.evidence(), "old_boot": old, "boot": new})


def verify_production(bench):
    root = bench.out.parent
    observed = bench_process.read(root / "production-banner.json")
    boot = bench_process.read(root / "boot-production" / "production-boot.json")
    if observed["banner"] != PRODUCTION_BANNER or observed["boot"] != boot["boot"]:
        raise RuntimeError("Production banner does not match this restart")
    bench.validate_ports()
    bench.cli("production-final-cli")
    bench.idle()
    bench.ports_free()
    keyboard = bench.keyboard()
    if keyboard["boot"] != boot["boot"]:
        raise RuntimeError("MOS boot changed after the production witness")
    image = bench.kit["legs"]["production"]["image"]
    if boot["selected"]["target"] != 0 or boot["selected"]["digest"] != image["sha256"]:
        raise RuntimeError("The verified production image and app0 selector are required")
    receipt = {"boot": boot, "observation": observed, "sha256": image["sha256"],
               "verified_extent_bytes": image["bytes"], "boot_cli_ready": True,
               "listener_offline": True, "staged_transfer_idle": True, "serial_handles_free": True,
               "status": "verified-standard", "verified_epoch": time.time(),
               "verification_receipt": str(bench.out / "production-verified.json")}
    bench_process.record(receipt["verification_receipt"], receipt)
    inventory = bench_process.read(bench.config["inventory"])
    pending = inventory.get("pending_operation")
    if (not pending or pending["selection"] != "ota-round-trip"
            or pending["operation"] != str(root)):
        raise RuntimeError("The active inventory operation differs from this round trip")
    inventory["components"]["native_vdp_sha256"] = image["sha256"]
    inventory["native_vdp"] = dict(receipt, prior=inventory.get("native_vdp"))
    inventory["pending_operation"] = None
    inventory["ready_claim"] = True
    inventory["recorded_epoch"] = time.time()
    bench.update_inventory(inventory)


def perform(bench, phase):
    if phase == "bootstrap":
        bootstrap(bench)
        return
    if phase == "stage":
        bench.transfer_inputs()
        return
    if phase == "boot-candidate":
        bench_process.record(bench.out / "boot.json", candidate_boot(bench).evidence())
        return
    if phase == "boot-production":
        production_boot(bench)
        return
    if phase == "verify-production":
        verify_production(bench)
        return
    action, leg = phase.split("-")
    before_boot = bench.keyboard()["boot"]
    if action == "write":
        if leg == "candidate":
            inventory = bench_process.read(bench.config["inventory"])
            if (inventory.get("pending_operation")
                    or inventory["components"]["native_vdp_sha256"]
                    != bench.kit["bootstrap_app0"]["sha256"]):
                raise RuntimeError("Inventory does not bind the verified bootstrap app")
            bench_process.record(bench.out / "inventory-before.json", inventory)
            inventory["pending_operation"] = {
                "component": "native_vdp", "selection": "ota-round-trip",
                "operation": str(bench.out.parent), "recorded_epoch": time.time(),
            }
            inventory["ready_claim"] = False
            bench.update_inventory(inventory)
        before, after = write_phase(bench, leg, phase)
    else:
        before, after = select_phase(bench, leg, phase)
    if bench.keyboard()["boot"] != before_boot:
        raise RuntimeError("Agon boot changed before the OTA result was collected")
    bench_process.record(bench.out / "vdplet.json",
                         {"before": before.evidence(), "after": after.evidence(),
                          "emos_boot": before_boot})


def worker_argv(args, phase):
    return [sys.executable, str(Path(__file__).resolve()), "--worker",
            "--job", str(args.job.resolve()), "--sha256", args.sha256,
            "--config", str(args.config.resolve()), "--config-sha256", args.config_sha256,
            "--out", str(args.out.resolve()), "--operator", args.operator, phase]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--config-sha256")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--operator")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("phase", choices=("preflight", *ORDER))
    args = parser.parse_args()
    job = load_packet(args.job, args.sha256)
    if args.phase == "preflight":
        if job.get("physical_commissioning") != "approved":
            print("Offline manifest and artifact pins match. Physical commissioning is pending.")
            return 0
    if job.get("physical_commissioning") != "approved":
        parser.error("Physical commissioning is pending")
    if not (args.config and args.config_sha256 and args.out and args.operator):
        parser.error("A commissioned phase requires config, its SHA-256, evidence root and operator")
    raw_config = args.config.read_bytes()
    if sha256(raw_config).hexdigest() != args.config_sha256:
        raise ValueError("Operator config hash differs")
    config = json.loads(raw_config)
    if (config["reset_config"] != job["reset_config"]["path"]
            or not pinned(job["reset_config"])):
        raise ValueError("Operator reset config differs")
    # The first physical packet will pin the specific commissioned runner.
    actual = subprocess.check_output(["git", "-C", str(CHECKOUT), "rev-parse", "HEAD"], text=True)
    if actual.strip() != job["runner"]:
        raise RuntimeError("Runner checkout differs from the job")
    subprocess.run(["git", "-C", str(CHECKOUT), "diff", "--exit-code", "HEAD", "--", "scripts"], check=True)
    if args.phase == "preflight":
        if "programmer_51" in job:
            pinned(job["programmer_51"])
            subprocess.run([sys.executable, "-B", job["programmer_51"]["path"], "--offline"],
                           check=True)
        else:
            programmer_python = Path(config["programmer"]).with_name("python")
            subprocess.run([str(programmer_python), "-c",
                            "import esptool; assert esptool.__version__.startswith('4.12.')"],
                           check=True)
        bootstrap_entry(job, bench_process.read(config["inventory"]))
        print("Commissioned packet, programmer, and joined predecessor match.")
        return 0
    fifo = bench_process.read(ROOT / "agents/olimex-scheduling/rehearsal-r02-fifo.json")
    if fifo.get("temporary_operator", fifo["active"]) != args.operator:
        raise RuntimeError("The named operator does not have sole custody")

    phase_dir = args.out / args.phase
    selected = worker_argv(args, args.phase)
    if not args.worker:
        return bench_process.run(selected, phase_dir, BOUNDS[args.phase], owner=args.operator,
                                 lease=f"chat:{args.operator}", phase=args.phase,
                                 next_action="Keep the slot and follow the Olimex stop rule.")
    # Bind predecessor receipts to the original argument vector and input pins.
    current = bench_process.read(phase_dir / "supervisor-started.json")
    if current["argv"] != selected or current["owner"] != args.operator:
        raise RuntimeError("Worker invocation differs from the supervisor")
    for previous in ORDER[:ORDER.index(args.phase)]:
        bench_process.verify_child(args.out / previous, worker_argv(args, previous))
    bench = UpdateBench(config, job, phase_dir)
    with Path(bench.config["operation_lock"]).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        bench.lock = lock
        perform(bench, args.phase)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
