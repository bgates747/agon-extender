#!/usr/bin/env python3
"""Explicit Olimex operator phases. Run preflight offline and obtain custody first."""

import argparse
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import sys
import time
from urllib.request import urlopen

import bench_process
import olimex_p4_app
from olimex_cli import Observer
from olimex_flash import check_extent, flash_application
from passive_serial import open_passive_serial
from reset_agon import status, wait_boot
from reset_agon_usb import identity
from sdcard import Client, RemoteError
from sdcard_staged import Client as StagedClient, QUOTA


ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ("mainboard", "p4", "emos")
INVENTORY = {
    "mainboard": ("native_vdp", "native_vdp_sha256"),
    "p4": ("p4", "p4_app_sha256"),
    "emos": ("emos", "emos_rom_sha256"),
}
PRESERVED = ("/autoexec.txt", "/emos/sdserve.bin")
LISTENER = "EMOS sdserve --fast /"
PARALLEL_LISTENER = "EMOS sdserve --fast --parallel /"
DEFAULT_SCHEMA = 3


def pinned(specification):
    data = Path(specification["path"]).read_bytes()
    verify_pin(data, specification)
    return data


def verify_pin(data, specification):
    if (len(data) != specification["bytes"]
            or sha256(data).hexdigest() != specification["sha256"]):
        raise ValueError(f"Pin mismatch for {specification['path']}")


def sd_path(path, roots):
    if (not re.fullmatch(r"/[A-Za-z0-9_./-]+", path)
            or str(PurePosixPath(path)) != path
            or ".." in PurePosixPath(path).parts
            or not any(path.startswith(root + "/") for root in roots)):
        raise ValueError(f"Invalid bench SD path: {path!r}")
    return path


def phases(kit):
    components = [name for name in COMPONENTS if name in kit["firmware"]]
    return (["stage"] + [f"install-{name}" for name in components] + ["run"]
            + [f"restore-{name}" for name in reversed(components)] + ["handback"])


def fixture_inputs(job):
    payloads = {job["sd_program"]: job["agon"]}
    names = {job["sd_program"].lower(), job["sd_result"].lower()}
    if len(names) != 2:
        raise ValueError("Fixture program and result name the same FAT path")
    for item in job.get("inputs", []):
        path = sd_path(item["sd_path"], ("/test",))
        if path.lower() in names:
            raise ValueError(f"Duplicate fixture or result path: {path}")
        names.add(path.lower())
        payloads[path] = item["source"]
    targets = {PurePosixPath(name) for name in names}
    if len(job["sd_result"]) > 120 or any(part.endswith(".") for path in targets for part in path.parts):
        raise ValueError("Fixture inputs or result contain an unsupported FAT path")
    if any(targets.intersection(p.parents) for p in targets):
        raise ValueError("A fixture file also names a required directory")
    for path, spec in payloads.items():
        if len(path) > 112 or not 0 <= spec["bytes"] <= QUOTA:
            raise ValueError(f"Fixture exceeds the staged upload bounds: {path}")
    return payloads


def preflight(kit):
    schema = kit.get("schema", DEFAULT_SCHEMA)
    if schema not in (1, 2, 3) or set(kit["firmware"]) - set(COMPONENTS):
        raise ValueError("Unsupported bench job or component")
    job = kit["fixture"]
    sd_path(job["sd_program"], ("/test",))
    sd_path(job["sd_result"], ("/test",))
    if (job["sd_program"] == job["sd_result"] or
            not re.fullmatch(r"[0-9A-Fa-f]{6}", job["address"])):
        raise ValueError("Invalid fixture address or result path")
    if not 0 < job["seconds"] <= 1800:
        raise ValueError("Invalid fixture time bound")
    for name in ("success", "failure"):
        if not re.fullmatch(r"[ -~]+", job[name]):
            raise ValueError(f"Missing ASCII completion marker: {name}")
    if job["success"].startswith(job["failure"]):
        raise ValueError("Fixture success matches its failure prefix")
    if set(kit["preserve"]) != set(PRESERVED):
        raise ValueError("Expected startup and foreground listener identity pins")
    if any(not re.fullmatch(r"[a-f0-9]{64}", digest) for digest in kit["preserve"].values()):
        raise ValueError("Startup and listener pins must be SHA-256 digests")
    if schema in (2, 3):
        for item in fixture_inputs(job).values():
            pinned(item)
    else:
        if "inputs" in job:
            raise ValueError("Multiple fixture inputs require the parallel job schema")
        pinned(job["agon"])
    if "p4_probe" in job:
        pinned(job["p4_probe"])
    if not re.fullmatch(r"[a-z0-9-]{1,36}", kit["namespace"]):
        raise ValueError("Invalid fixture namespace")
    for component, spec in kit["firmware"].items():
        for selection in ("candidate", "restore"):
            image = pinned(spec[f"{selection}_write"])
            if component == "emos":
                if len(image) != 0x20000:
                    raise ValueError("EMOS requires a complete 128 KiB ROM")
            else:
                check_extent(component, spec, image)
                app = pinned(spec[f"{selection}_app"])
                if not image.startswith(app) or any(byte != 255 for byte in image[len(app):]):
                    raise ValueError("Application image and padded write extent differ")
        if component != "emos":
            pinned(spec["partition_table"])
    return phases(kit)


class Bench:
    def __init__(self, config, kit, out):
        self.config = config
        self.kit = kit
        self.out = out
        self.url = config["url"].rstrip("/")
        self.reset_config = bench_process.read(config["reset_config"])
        self.c = {"ports": [self.reset_config["stable_port"], config["p4"]["port"]]}
        self.install_dir = "/extender/install/" + kit["namespace"]
        self.results_dir = "/agents/extender/" + kit["namespace"]
        self.lock = None

    def own(self):
        if self.lock is None or self.lock.closed:
            raise RuntimeError("The operator phase lock is not held")

    def get(self, route):
        with urlopen(self.url + route, timeout=3) as reply:
            return json.load(reply)

    def keyboard(self):
        actual = status(self.url)
        # The endpoint retains the previous session ID after cancellation.
        closed = not actual["session"] or actual["reason"] == 1
        if not (actual["ready"] and actual["physical_neutral"]
                and not actual["pending"] and not actual["held"] and closed):
            raise RuntimeError("Keyboard is not admitted and idle")
        return actual

    def idle(self):
        service = self.get("/sd/status")
        if service["online"] or service.get("pending") or self.get("/sd/fast")["phase"] != 0:
            raise RuntimeError("A transfer or foreground listener is active")

    def ports_free(self):
        for port in self.c["ports"]:
            Path(port).resolve(strict=True)
            check = subprocess.run(["fuser", port], capture_output=True, text=True, timeout=5)
            if check.returncode != 1 or check.stderr:
                raise RuntimeError(f"Serial port is occupied or could not be checked: {port}")

    def validate_ports(self):
        identity(self.reset_config)
        port = Path(self.config["p4"]["port"])
        if port.parent != Path("/dev/serial/by-id"):
            raise ValueError("P4 needs a stable serial endpoint")
        report = subprocess.check_output(
            ["udevadm", "info", "--query=property", "--name", str(port.resolve(strict=True))],
            text=True, timeout=5)
        if "ID_SERIAL_SHORT=" + self.config["p4"]["serial"] not in report.splitlines():
            raise RuntimeError("P4 USB identity differs from commissioning")
        self.ports_free()

    def type_line(self, label, command):
        self.own()
        self.keyboard()
        bench_process.record(self.out / f"dispatch-{label}.json",
                             {"command": command, "epoch": time.time()})
        subprocess.run([sys.executable, str(ROOT / "scripts/keyboard.py"),
                        "--url", self.url, "--state", str(self.out / f"keys-{label}.json"),
                        "type", command, "--enter"], check=True, timeout=42)

    def start_listener(self, label, command):
        self.idle()
        self.type_line(label, command)
        deadline = time.monotonic() + 25
        while not self.get("/sd/status")["online"]:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Foreground listener did not start during {label}")
            time.sleep(0.2)

    def listener(self, label, command, operation):
        self.start_listener(label, command)
        client = Client(self.url, self.out / f"sd-{label}.json", timeout=12)
        try:
            client.connect(require_fast=True)
            for remote, expected in self.kit["preserve"].items():
                data = client.download(remote)
                if sha256(data).hexdigest() != expected:
                    raise RuntimeError(f"Preserved bytes changed: {remote}")
            operation(client)
            client.rpc(11)
            self.idle()
            self.keyboard()
        finally:
            client.lock.close()

    def cli(self):
        self.listener("cli", LISTENER, lambda client: None)

    def emos_install_inputs(self):
        payloads, results = {}, []
        for selection in ("candidate", "restore"):
            payloads[f"{self.install_dir}/{selection}.bin"] = pinned(
                self.kit["firmware"]["emos"][f"{selection}_write"])
            rom = f"{self.results_dir}/{selection}-rom.bin"
            results.append(rom)
            payloads[f"{self.install_dir}/{selection}.txt"] = (
                f"SAVE {rom} &0 &20000\r\n{LISTENER}\r\n").encode("ascii")
        return payloads, results

    def stage(self, *, include_emos=True):
        job = self.kit["fixture"]
        schema = self.kit.get("schema", DEFAULT_SCHEMA)
        sources = (fixture_inputs(job) if schema in (2, 3) else
                   {job["sd_program"]: job["agon"]})
        payloads = {destination: pinned(spec) for destination, spec in sources.items()}
        expected_absent = []
        if include_emos and "emos" in self.kit["firmware"]:
            firmware_inputs, expected_absent = self.emos_install_inputs()
            payloads.update(firmware_inputs)

        def existing(client, remote):
            try:
                return client.stat_entry(remote)
            except RemoteError as error:
                if error.status == 6 and error.detail in (b"\x04", b"\x05"):
                    return None
                raise

        if schema in (2, 3):
            self.stage_parallel(payloads, [job["sd_result"], *expected_absent], existing)
            return

        def transfer(client):
            directories = {str(PurePosixPath(remote).parent) for remote in payloads}
            directories.add(str(PurePosixPath(job["sd_result"]).parent))
            directories.update(str(PurePosixPath(path).parent) for path in expected_absent)
            for remote in sorted(directories):
                client.make_directory(remote, parents=True)
            for remote in expected_absent:
                if existing(client, remote) is not None:
                    raise RuntimeError(f"ROM evidence path already exists: {remote}")
            present = set()
            for remote, payload in payloads.items():
                if existing(client, remote) is not None:
                    if client.download(remote) != payload:
                        raise RuntimeError(f"Staging conflict at {remote}")
                    present.add(remote)
            if existing(client, job["sd_result"]) is not None:
                prior = client.download(job["sd_result"])
                with (self.out / "prior-result.txt").open("xb") as saved:
                    saved.write(prior)
                    saved.flush()
                    os.fsync(saved.fileno())
                client.remove(job["sd_result"])
            for remote, payload in payloads.items():
                if remote not in present:
                    client.upload(remote, payload, activate=True, fast=True)
                if client.download(remote) != payload:
                    raise RuntimeError(f"Independent SD readback differs: {remote}")
                print(f"Verified {remote} {sha256(payload).hexdigest()}", flush=True)

        self.listener("stage", LISTENER, transfer)

    def stage_parallel(self, payloads, result_paths, existing):
        capabilities = self.get("/sd/fast")
        both = self.kit.get("schema", DEFAULT_SCHEMA) == 3
        if capabilities.get("parallel_required_supported") is not True:
            raise RuntimeError("P4 does not support required parallel uploads")
        if both and capabilities.get("parallel_get_required_supported") is not True:
            raise RuntimeError("P4 does not support required parallel downloads")
        self.start_listener("stage", PARALLEL_LISTENER)
        targets = [*payloads, *result_paths]
        client = Client(self.url, self.out / "sd-stage-metadata.json", timeout=12)
        try:
            client.connect(require_fast=True)
            hello = client.rpc(1)
            required = 0x180 if both else 0x80
            if len(hello) != 8 or struct.unpack_from("<H", hello, 6)[0] & required != required:
                raise RuntimeError("The foreground listener lacks the required parallel capabilities")
            for directory in sorted({str(PurePosixPath(path).parent) for path in targets}):
                client.make_directory(directory, parents=True)
            for path in targets:
                if existing(client, path) is not None:
                    raise RuntimeError(f"Parallel staging requires a fresh target: {path}")
        finally:
            client.lock.close()

        for number, (path, payload) in enumerate(payloads.items()):
            prefix = self.out / f"stage-file-{number:02d}"
            source = prefix.with_suffix(".bin")
            with source.open("xb") as stream:
                stream.write(payload)
            staged = StagedClient(self.url, prefix.with_suffix(".json"))
            try:
                result = staged.begin("put", path, source=source, activate=True,
                                      require_parallel=True)
                bench_process.record(prefix.with_suffix(".receipt.json"),
                                     {"target": path, "result": result})
            finally:
                staged.close()

        self.exit_staged_listener("stage")

    def exit_staged_listener(self, label):
        # A staged job establishes its own listener session. Never issue EXIT
        # from the direct client used before staging.
        client = Client(self.url, self.out / f"sd-{label}-exit.json", timeout=12)
        try:
            client.connect(require_fast=True)
            client.rpc(11)
            self.idle()
            self.keyboard()
        finally:
            client.lock.close()

    def update_inventory(self, inventory):
        target = Path(self.config["inventory"])
        temporary = target.with_name(f".{target.name}.{time.time_ns()}.tmp")
        bench_process.record(temporary, inventory)
        temporary.replace(target)

    def firmware(self, component, selection, *, retry=False):
        self.validate_ports()
        self.idle()
        before = self.keyboard()
        spec = self.kit["firmware"][component]
        image = pinned(spec[f"{selection}_write"])
        original = spec.get(f"{selection}_app", spec[f"{selection}_write"])
        role, hash_field = INVENTORY[component]
        inventory = bench_process.read(self.config["inventory"])
        pending = inventory.get("pending_operation")
        required_entry = None
        if retry:
            original_attempt = self.out.parent / f"install-{component}"
            if (not pending or pending["component"] != role or
                    pending["selection"] != "candidate" or
                    Path(pending["operation"]).resolve() != original_attempt.resolve() or
                    pending["write_sha256"] != sha256(image).hexdigest()):
                raise RuntimeError(f"The firmware record does not bind the original {component} failure")
            required_entry = pinned(spec["restore_write"])
        elif pending:
            raise RuntimeError("A prior firmware action requires reconciliation")
        bench_process.record(self.out / "inventory-before.json", inventory)

        def begin():
            inventory["pending_operation"] = {
                "component": role, "selection": selection, "operation": str(self.out),
                "write_sha256": sha256(image).hexdigest(), "recorded_epoch": time.time(),
            }
            inventory["ready_claim"] = False
            self.update_inventory(inventory)

        if component == "emos":
            begin()
            self.type_line("flash", f"FLASH mos {self.install_dir}/{selection}.bin -f")
            wait_boot(self.url, before["boot"], 100)
            result = self.out / "readback.bin"

            def read_rom(client):
                result.write_bytes(client.download(f"{self.results_dir}/{selection}-rom.bin"))
                if result.read_bytes() != image:
                    raise RuntimeError("Independent EMOS ROM readback differs")

            self.listener("rom-readback", f"EXEC {self.install_dir}/{selection}.txt", read_rom)
        else:
            table = pinned(spec["partition_table"])
            if component == "p4":
                result = olimex_p4_app.replace(self, spec, image, table, before["boot"],
                                              begin, required_entry=required_entry)
            else:
                result = flash_application(
                    component, self.config["programmer"], self.c["ports"][0],
                    self.config["mainboard_mac"], spec, image, table, self.out, begin,
                    required_entry=required_entry)
                if result.read_bytes() != image:
                    raise RuntimeError("Independent mainboard application readback differs")
                bench_process.record(self.out / "write-verified.json", {
                    "bytes": len(image), "write_sha256": sha256(image).hexdigest(),
                })
                olimex_p4_app.reboot_pair(self, before["boot"])
            self.cli()

        receipt = {
            "component": role, "selection": selection, "sha256": original["sha256"],
            "verified_extent_sha256": sha256(image).hexdigest(),
            "verified_extent_bytes": len(image), "bytes": original["bytes"],
            "readback": str(result), "boot_cli_ready": True, "verified_epoch": time.time(),
            "status": "verified-standard" if selection == "restore" else "verified-exception",
        }
        receipt["verification_receipt"] = str(self.out / "independent-verification.json")
        bench_process.record(receipt["verification_receipt"], receipt)
        inventory["components"][hash_field] = original["sha256"]
        inventory[role] = dict(receipt, prior=inventory.get(role))
        inventory["pending_operation"] = None
        inventory["recorded_epoch"] = time.time()
        inventory["source"] = "Olimex operator verified write and CLI"
        self.update_inventory(inventory)

    def invoke(self):
        self.validate_ports()
        self.idle()
        self.keyboard()
        job = self.kit["fixture"]
        with open_passive_serial(self.c["ports"][0], timeout=0.2) as reader:
            with (self.out / "mainboard-serial.bin").open("xb") as transcript:
                observer = Observer(reader, transcript, self.type_line)
                self.type_line("mirror-on", "VDU 2")
                prompt = observer.witness()
                observer.quiet_load(f"LOAD {job['sd_program']} &{job['address']}", prompt)
                observer.run(f"RUN &{job['address']}", prompt, job["success"].encode(),
                             job["failure"].encode(), job["seconds"])
                observer.mirror_off(prompt)

        result_path = self.out / "result.txt"
        def check_result():
            if result_path.read_bytes().decode("ascii").splitlines() != job["expected_agon"]:
                raise RuntimeError("Agon fixture result differs")

        if self.kit.get("schema", DEFAULT_SCHEMA) == 3:
            self.start_listener("collect", PARALLEL_LISTENER)
            staged = StagedClient(self.url, self.out / "sd-collect.json")
            try:
                receipt = staged.begin("get", job["sd_result"], destination=result_path,
                                       require_parallel=True)
                bench_process.record(self.out / "sd-collect.receipt.json", receipt)
            finally:
                staged.close()
            check_result()
            self.exit_staged_listener("collect")
        else:
            def collect(client):
                result_path.write_bytes(client.download(job["sd_result"]))
                check_result()

            self.listener("collect", LISTENER, collect)
        if "p4_probe" in job:
            probe = self.out / "p4-probe.py"
            probe.write_bytes(pinned(job["p4_probe"]))
            with (self.out / "p4-result.txt").open("xb") as log:
                subprocess.run([sys.executable, str(probe), self.url], stdout=log,
                               stderr=subprocess.STDOUT, check=True, timeout=20)
            if (self.out / "p4-result.txt").read_text().splitlines() != job["expected_p4"]:
                raise RuntimeError("P4 fixture result differs")

    def handback(self):
        if self.kit.get("schema", DEFAULT_SCHEMA) == 3:
            self.start_listener("handback", PARALLEL_LISTENER)
            self.exit_staged_listener("handback")
        else:
            self.cli()
        self.validate_ports()
        inventory = bench_process.read(self.config["inventory"])
        if inventory.get("pending_operation"):
            raise RuntimeError("Firmware is still pending reconciliation")
        for component, spec in self.kit["firmware"].items():
            role, hash_field = INVENTORY[component]
            expected = spec.get("restore_app", spec["restore_write"])["sha256"]
            receipt = bench_process.read(self.out.parent / f"restore-{component}"
                                         / "independent-verification.json")
            if (receipt["sha256"] != expected or not receipt["boot_cli_ready"]
                    or inventory["components"][hash_field] != expected):
                raise RuntimeError(f"Missing verified production restore for {role}")
        bench_process.record(self.out / "handback.json", {
            "working_legacy_cli": True, "keyboard": self.keyboard(),
            "listener_offline": True, "staged_transfer_idle": True, "serial_handles_free": True,
            "production_restores": list(self.kit["firmware"]),
        })
        if self.kit["firmware"]:
            inventory["ready_claim"] = True
            inventory["recorded_epoch"] = time.time()
            self.update_inventory(inventory)

    def perform(self, phase):
        path = Path(self.config["operation_lock"])
        with path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock = lock
            if phase == "stage":
                self.validate_ports()
                self.stage()
            elif phase == "run":
                self.invoke()
            elif phase == "handback":
                self.handback()
            else:
                operation, component = phase.split("-", 1)
                selection = "restore" if operation == "restore" else "candidate"
                self.firmware(component, selection, retry=operation == "retry")


def child_argv(args, phase):
    return [sys.executable, str(Path(__file__).resolve()), "--job", str(args.job),
            "--sha256", args.sha256, "--config", str(args.config),
            "--out", str(args.out), f"worker-{phase}"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--operator", help="The chat holding the open slot")
    parser.add_argument("phase")
    args = parser.parse_args()
    raw = args.job.read_bytes()
    if sha256(raw).hexdigest() != args.sha256:
        raise ValueError("Job manifest differs from the named hash")
    kit = json.loads(raw)
    order = preflight(kit)
    if args.phase == "preflight":
        print("\n".join(order))
        return 0
    if not args.config or not args.out:
        parser.error("Physical phases require --config and --out")
    phase = args.phase.removeprefix("worker-")
    retry_phase = phase in ("retry-mainboard", "retry-p4")
    planned = phase.replace("retry-", "install-", 1) if retry_phase else phase
    if planned not in order:
        parser.error("The selected phase is absent from this job")
    if args.phase != phase:
        folder = args.out / phase
        supervisor = bench_process.read(folder / "supervisor-started.json")
        if supervisor["argv"] != child_argv(args, phase):
            raise RuntimeError("Worker is missing its supervisor binding")
        for prior in order[:order.index(planned)]:
            if prior in ("install-mainboard", "install-p4"):
                retry = prior.replace("install-", "retry-", 1)
                if (args.out / retry).exists():
                    bench_process.verify_child(args.out / prior, child_argv(args, prior),
                                               expected_returncode=1)
                    prior = retry
            bench_process.verify_child(args.out / prior, child_argv(args, prior))
        if retry_phase:
            bench_process.verify_child(args.out / planned, child_argv(args, planned),
                                       expected_returncode=1)
        Bench(bench_process.read(args.config), kit, folder).perform(phase)
        return 0
    if not args.operator:
        parser.error("Physical phases require --operator from the opened chat slot")
    print(f"Operator {args.operator} starting {phase} under its existing slot", flush=True)
    bounds = {"stage": 300, "run": kit["fixture"]["seconds"] + 210,
              "install-mainboard": 550, "restore-mainboard": 550, "retry-mainboard": 550,
              "install-p4": 650, "restore-p4": 650, "retry-p4": 760, "handback": 90}
    return bench_process.run(child_argv(args, phase), args.out / phase,
                             bounds.get(phase, 480), owner=args.operator,
                             lease=f"chat:{args.operator}", phase=phase,
                             next_action="Keep the slot and follow the bench stop procedure.")


if __name__ == "__main__":
    sys.exit(main())
