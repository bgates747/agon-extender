#!/usr/bin/env python3
"""Explicit Olimex operator phases. Run preflight offline and obtain custody first."""

import argparse
from contextlib import contextmanager
import fcntl
from hashlib import sha256
import json
from math import ceil
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
import olimex_vdp_ota
from olimex_cli import Observer, completion_markers
from olimex_flash import check_extent, flash_application, mainboard_programmer, mainboard_rom
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


def phases(kit, *, enter_cwd=False):
    components = [name for name in COMPONENTS if name in kit["firmware"]]
    invocation = list(fixture_runs(kit))
    if "human_start" in kit:
        invocation = ["preload"] if kit["human_start"] == "preload" else []
        if enter_cwd and kit["human_start"] == "stage-only":
            invocation = ["enter-cwd"]
    return (["stage"] + [f"install-{name}" for name in components] + invocation
            + [f"restore-{name}" for name in reversed(components)] + ["handback"])


def fixture_runs(kit):
    if "fixtures" in kit:
        return {f"run-{job['id']}": job for job in kit["fixtures"]}
    return {"run": kit["fixture"]}


def fixture_results(job):
    if "results" in job:
        return job["results"]
    return [job["sd_result"]]


def validate_targets(payloads, results):
    names = [path.lower() for path in (*payloads, *results)]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate fixture or result path")
    targets = {PurePosixPath(name) for name in names}
    if any(len(path) > 120 for path in results) or any(
            part.endswith(".") for path in targets for part in path.parts):
        raise ValueError("Fixture inputs or results contain an unsupported FAT path")
    if any(targets.intersection(p.parents) for p in targets):
        raise ValueError("A fixture file also names a required directory")


def fixture_inputs(job):
    payloads = {job["sd_program"]: job["agon"]}
    inputs = list(job.get("inputs", []))
    if "listener_handoff" in job:
        inputs.append(job["listener_handoff"])
    for item in inputs:
        path = sd_path(item["sd_path"], ("/test",))
        if path in payloads:
            raise ValueError(f"Duplicate fixture or result path: {path}")
        payloads[path] = item["source"]
    validate_targets(payloads, fixture_results(job))
    for path, spec in payloads.items():
        if len(path) > 112 or not 0 <= spec["bytes"] <= QUOTA:
            raise ValueError(f"Fixture exceeds the staged upload bounds: {path}")
    return payloads


def listener_batch(job):
    return f"RUN &{job['address']}\r\n{PARALLEL_LISTENER}\r\n".encode("ascii")


def validate_fixture(job, schema, *, named, manual=False):
    sd_path(job["sd_program"], ("/test",))
    if named:
        if "sd_result" in job or "expected_agon" in job or "p4_probe" in job:
            raise ValueError("Named fixtures use dynamic result files")
        if not isinstance(job["results"], list) or (not manual and not job["results"]):
            raise ValueError("Named fixtures require at least one result file")
        if any(PurePosixPath(path).name.lower() == "vdp-usb.bin" for path in job["results"]):
            raise ValueError("A result file uses the reserved UART transcript name")
        cwd = PurePosixPath(sd_path(job["cwd"], ("/test",)))
        if any(PurePosixPath(path).parent != cwd
               for path in [job["sd_program"], *job["results"]]):
            raise ValueError("The program and reports must be in the named fixture directory")
        if "uart_end" in job:
            end = job["uart_end"]
            if (not re.fullmatch(r"[ -~]{1,64}", end["prefix"])
                    or not re.fullmatch(r"[ -~]{1,120}", end["line"])
                    or not end["line"].startswith(end["prefix"])
                    or not 0 < end["seconds"] <= 120):
                raise ValueError("Invalid deferred UART terminator or time bound")
        if "listener_handoff" in job and "uart_end" not in job:
            raise ValueError("Listener handoff requires a native UART terminator")
    elif {"results", "cwd", "uart_end", "listener_handoff"} & job.keys():
        raise ValueError("Directory, deferred UART and dynamic results require named fixtures")
    results = fixture_results(job)
    for path in results:
        sd_path(path, ("/test",))
    if job["sd_program"] in results or not re.fullmatch(r"[0-9A-Fa-f]{6}", job["address"]):
        raise ValueError("Invalid fixture address or result path")
    if manual:
        if job["results"] or {"success", "failure", "seconds", "uart_end", "listener_handoff"} & job.keys():
            raise ValueError("Human-start jobs use the operator's chat verdict and an empty results list")
    else:
        if not 0 < job["seconds"] <= 1800:
            raise ValueError("Invalid fixture time bound")
        completion_markers(job["success"], job["failure"])
    if schema in (2, 3):
        inputs = fixture_inputs(job)
        if named and any(cwd not in PurePosixPath(path).parents for path in inputs):
            raise ValueError("Fixture inputs must be under the named fixture directory")
    else:
        if "inputs" in job:
            raise ValueError("Multiple fixture inputs require the parallel job schema")
        inputs = {job["sd_program"]: job["agon"]}
    batch_path = job.get("listener_handoff", {}).get("sd_path")
    for path, item in inputs.items():
        data = pinned(item)
        if path == batch_path and data != listener_batch(job):
            raise ValueError("The listener handoff batch must contain only the pinned RUN and listener commands")
    if "p4_probe" in job:
        pinned(job["p4_probe"])
    return [*inputs, *results]


def uart_transfer(kit):
    return kit.get("transfer") == "uart"


def uart_upload_seconds(size):
    # Conservative watchdog, based on the retained staged path's ~25 kB/s.
    return 60 + ceil(size / 8000)


def stage_seconds(kit):
    if not uart_transfer(kit):
        return 300
    files = [spec for job in fixture_runs(kit).values() for spec in fixture_inputs(job).values()]
    if ota := olimex_vdp_ota.spec_for(kit):
        files.extend(ota[f"{selection}_app"] for selection in ("candidate", "restore"))
    seconds = 300
    if emos := kit["firmware"].get("emos"):
        files.extend(emos[f"{selection}_write"] for selection in ("candidate", "restore"))
        # Two short generated MOS batches, each fits the first 8,000-byte band.
        seconds += 2 * uart_upload_seconds(1)
    return seconds + sum(uart_upload_seconds(spec["bytes"]) for spec in files)


def preflight(kit):
    schema = kit.get("schema", DEFAULT_SCHEMA)
    if schema not in (1, 2, 3) or set(kit["firmware"]) - set(COMPONENTS):
        raise ValueError("Unsupported bench job or component")
    named = "fixtures" in kit
    if named:
        jobs = kit["fixtures"]
        if ("fixture" in kit or schema != 3 or not isinstance(jobs, list) or not jobs
                or any(not re.fullmatch(r"[a-z][a-z0-9-]{0,23}", job["id"]) for job in jobs)
                or len(fixture_runs(kit)) != len(jobs)):
            raise ValueError("Expected uniquely named fixtures in a schema 3 job")
    else:
        jobs = [kit["fixture"]]
    manual = "human_start" in kit
    if manual and (kit["human_start"] not in ("stage-only", "preload") or not named or len(jobs) != 1):
        raise ValueError("Human start requires stage-only or preload and exactly one named fixture")
    targets = [path for job in jobs for path in validate_fixture(job, schema, named=named, manual=manual)]
    if "transfer" in kit and (not uart_transfer(kit) or not named
                              or any("listener_handoff" in job for job in jobs)):
        raise ValueError('The "uart" transfer option requires named schema-3 fixtures without listener handoff')
    if named:
        directories = [PurePosixPath(job["cwd"].lower()) for job in jobs]
        if len(set(directories)) != len(jobs) or any(
                set(directories).intersection(path.parents) for path in directories):
            raise ValueError("Named fixtures require separate working directories")
        validate_targets(targets, [])
    if set(kit["preserve"]) != set(PRESERVED):
        raise ValueError("Expected startup and foreground listener identity pins")
    if any(not re.fullmatch(r"[a-f0-9]{64}", digest) for digest in kit["preserve"].values()):
        raise ValueError("Startup and listener pins must be SHA-256 digests")
    if not re.fullmatch(r"[a-z0-9-]{1,36}", kit["namespace"]):
        raise ValueError("Invalid fixture namespace")
    ota = olimex_vdp_ota.spec_for(kit)
    if ota:
        if set(kit["firmware"]) != {"mainboard"} or not named or manual or not uart_transfer(kit):
            raise ValueError('Agon Flash requires an automated named schema-3 mainboard-only job with "transfer": "uart"')
        olimex_vdp_ota.validate(ota, pinned)
    for component, spec in kit["firmware"].items():
        if spec is ota:
            continue
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


def offboard_proof(kit, job_sha, option):
    spec = olimex_vdp_ota.spec_for(kit)
    if not uart_transfer(kit) or "fixtures" not in kit or (kit["firmware"] and spec is None):
        raise ValueError("Offboard staging requires a named UART job using production or Agon Flash")
    directory, manifest_sha, verification_sha = option
    paths = [Path(directory).resolve() / name for name in ("manifest.json", "verification.json")]
    documents = []
    for path, digest in zip(paths, (manifest_sha, verification_sha), strict=True):
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f"Offboard staging evidence changed: {path}")
        documents.append(json.loads(raw))
    manifest, verified = documents
    payloads = {path: pin for job in fixture_runs(kit).values()
                for path, pin in fixture_inputs(job).items()}
    if spec:
        for selection in ("candidate", "restore"):
            payloads[f"/extender/install/{kit['namespace']}/{selection}-vdp.bin"] = spec[f"{selection}_app"]
    pins = {path: {key: pin[key] for key in ("bytes", "sha256")} for path, pin in payloads.items()}
    reports = [path for job in fixture_runs(kit).values() for path in fixture_results(job)]
    if (manifest["job_sha256"] != job_sha or manifest["payloads"] != pins
            or manifest["expected_absent"] != reports or manifest["preserve"] != kit["preserve"]):
        raise ValueError("Offboard staging manifest differs from the commissioned files")
    preserved = list(kit["preserve"])
    if spec:
        preserved.append(olimex_vdp_ota.FLASH_PATH)
    if (verified["job_sha256"] != job_sha or verified["files_verified"] != len(pins)
            or verified["bytes_verified"] != sum(pin["bytes"] for pin in pins.values())
            or verified["expected_results_absent"] != reports or verified["writes_synced"] is not True
            or sorted(verified["preservation_verified"]) != sorted(preserved)):
        raise ValueError("Offboard staging receipt does not establish synced files and fresh reports")
    return {"manifest": str(paths[0]), "manifest_sha256": manifest_sha,
            "verification": str(paths[1]), "verification_sha256": verification_sha,
            "job_sha256": job_sha, "files": len(pins), "bytes": verified["bytes_verified"]}


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
        self.offboard = None

    def own(self):
        if self.lock is None or self.lock.closed:
            raise RuntimeError("The operator phase lock is not held")

    def get(self, route):
        with urlopen(self.url + route, timeout=3) as reply:
            return json.load(reply)

    def keyboard(self):
        actual = status(self.url)
        # The endpoint retains the previous session ID after cancellation.
        required = {"ready", "physical_neutral", "pending", "held", "session", "reason"}
        if (not required.issubset(actual) or not actual["ready"] or not actual["physical_neutral"]
                or actual["pending"] or actual["held"] or (actual["session"] and actual["reason"] != 1)):
            path = self.out / f"keyboard-refused-{time.time_ns()}.json"
            bench_process.record(path, actual)
            raise RuntimeError(f"Keyboard is not admitted and idle. Status saved in {path}")
        return actual

    def idle(self):
        service = self.get("/sd/status")
        if service["online"] or service.get("pending") or self.get("/sd/fast")["phase"] != 0:
            raise RuntimeError("A transfer or foreground listener is active")

    def ports_free(self, *ports):
        for port in ports or self.c["ports"]:
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
        if getattr(self, "offboard", None):
            raise RuntimeError("Offboard staging does not admit a P4 file listener")
        if uart_transfer(self.kit) and "--parallel" in command.split():
            raise RuntimeError("UART-only jobs cannot launch a parallel listener")
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

    def staged_uart(self, label, operation, remote, **paths):
        timeout = uart_upload_seconds(paths["source"].stat().st_size) if operation == "put" else 300
        staged = StagedClient(self.url, self.out / f"{label}.json", timeout=timeout)
        try:
            return staged.begin(operation, remote, require_uart=True, **paths)
        finally:
            staged.close()

    @contextmanager
    def uart_listener(self, label, command=LISTENER):
        self.start_listener(label, command)
        for number, (remote, expected) in enumerate(self.kit["preserve"].items(), start=1):
            name = f"preserve-{label}-{number:02d}"
            local = self.out / f"{name}.bin"
            self.staged_uart(name, "get", remote, destination=local)
            if sha256(local.read_bytes()).hexdigest() != expected:
                raise RuntimeError(f"Preserved bytes changed: {remote}")
        yield
        # A failed body retains the listener and transfer evidence for the
        # ordinary stop procedure. Successful staged jobs need a fresh EXIT.
        self.exit_staged_listener(label)

    def verify_mos(self, label="mos"):
        identity(self.reset_config)
        port = self.c["ports"][0]
        self.ports_free(port)
        olimex_vdp_ota.mos_witness(self, label)
        self.ports_free(port)

    def cli(self, label="cli"):
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", label):
            raise ValueError("Invalid CLI observation label")
        if getattr(self, "offboard", None):
            self.idle()
            self.verify_mos(label)
            self.idle()
        elif uart_transfer(self.kit):
            with self.uart_listener(label):
                pass
        else:
            self.listener(label, LISTENER, lambda client: None)

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
        schema = self.kit.get("schema", DEFAULT_SCHEMA)
        jobs = fixture_runs(self.kit).values()
        if schema in (2, 3):
            sources = {path: spec for job in jobs for path, spec in fixture_inputs(job).items()}
        else:
            job = self.kit["fixture"]
            sources = {job["sd_program"]: job["agon"]}
        payloads = {destination: pinned(spec) for destination, spec in sources.items()}
        expected_absent = []
        if include_emos and "emos" in self.kit["firmware"]:
            firmware_inputs, expected_absent = self.emos_install_inputs()
            payloads.update(firmware_inputs)

        if ota := olimex_vdp_ota.spec_for(self.kit):
            inventory = bench_process.read(self.config["inventory"])
            verified = olimex_vdp_ota.installed(inventory, ota, "restore", allow_padded=True)
            bench_process.record(self.out / "flash-entry.json", {
                "verification_receipt": verified["verification_receipt"],
                "companions": olimex_vdp_ota.companion_pins(inventory),
            })
            if not self.offboard:
                for selection in ("candidate", "restore"):
                    path = olimex_vdp_ota.staging_path(self, selection)
                    payloads[path] = pinned(ota[f"{selection}_app"])
        if getattr(self, "offboard", None):
            bench_process.record(self.out / "offboard-stage.json", self.offboard)
            return

        def existing(client, remote):
            try:
                return client.stat_entry(remote)
            except RemoteError as error:
                if error.status == 6 and error.detail in (b"\x04", b"\x05"):
                    return None
                raise

        if schema in (2, 3):
            results = [path for job in jobs for path in fixture_results(job)]
            stage = self.stage_uart if uart_transfer(self.kit) else self.stage_parallel
            stage(payloads, [*results, *expected_absent], existing)
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

    def stage_uart(self, payloads, result_paths, existing):
        with self.uart_listener("stage"):
            targets = [*payloads, *result_paths]
            client = Client(self.url, self.out / "sd-stage-metadata.json", timeout=12)
            try:
                client.connect(require_fast=True)
                for directory in sorted({str(PurePosixPath(path).parent) for path in targets}):
                    client.make_directory(directory, parents=True)
                for path in targets:
                    if existing(client, path) is not None:
                        raise RuntimeError(f"UART staging requires a fresh target: {path}")
            finally:
                client.lock.close()

            for number, (path, payload) in enumerate(payloads.items()):
                label = f"stage-file-{number:02d}"
                source = self.out / f"{label}.bin"
                with source.open("xb") as stream:
                    stream.write(payload)
                result = self.staged_uart(label, "put", path, source=source, activate=True)
                bench_process.record(self.out / f"{label}.receipt.json", {
                    "target": path, "payload_carrier": result["payload_carrier"], "activated": True,
                    "bytes": result["bytes"], "id": result["id"],
                    "source_sha256": sha256(payload).hexdigest(), "result": result,
                })

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

    def firmware(self, component, selection, *, retry=False, job_root=None):
        if component == "mainboard" and (ota := olimex_vdp_ota.spec_for(self.kit)):
            if retry:
                raise RuntimeError("The Agon Flash backend does not retry firmware writes")
            self.firmware_ota(ota, selection, job_root or self.out.parent)
            return
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

            command = f"EXEC {self.install_dir}/{selection}.txt"
            if uart_transfer(self.kit):
                with self.uart_listener("rom-readback", command):
                    self.staged_uart("sd-rom-readback", "get", f"{self.results_dir}/{selection}-rom.bin",
                                     destination=result)
                    if result.read_bytes() != image:
                        raise RuntimeError("Independent EMOS ROM readback differs")
            else:
                self.listener("rom-readback", command, read_rom)
        else:
            table = pinned(spec["partition_table"])
            if component == "p4":
                result = olimex_p4_app.replace(self, spec, image, table, before["boot"],
                                              begin, required_entry=required_entry)
            else:
                result = flash_application(
                    component, self.c["ports"][0],
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

    def firmware_ota(self, spec, selection, root):
        inventory = bench_process.read(self.config["inventory"])
        entry = bench_process.read(root / "stage" / "flash-entry.json")
        previous = "restore" if selection == "candidate" else "candidate"
        previous_receipt = (Path(entry["verification_receipt"]) if previous == "restore"
                            else root / "install-mainboard" / "independent-verification.json")
        olimex_vdp_ota.installed(inventory, spec, previous, receipt_path=previous_receipt,
                                 allow_padded=selection == "candidate")
        if entry["companions"] != olimex_vdp_ota.companion_pins(inventory):
            raise RuntimeError("The production P4 or EMOS identity changed after staging")
        app = spec[f"{selection}_app"]
        image = pinned(app)
        table = pinned(spec["partition_table"])
        slot = spec[f"{selection}_slot"]
        olimex_vdp_ota.stage_proof(self, root, selection, app)
        self.validate_ports()
        self.idle()
        bench_process.record(self.out / "inventory-before.json", inventory)

        def begin():
            if bench_process.read(self.config["inventory"]) != inventory:
                raise RuntimeError("Firmware inventory changed before FLASH confirmation")
            inventory["pending_operation"] = {
                "component": "native_vdp", "selection": selection, "operation": str(self.out),
                "write_sha256": app["sha256"], "method": "agon-flash-v1.9", "slot": slot,
                "recorded_epoch": time.time(),
            }
            inventory["ready_claim"] = False
            self.update_inventory(inventory)

        result, boot = olimex_vdp_ota.replace(self, spec, selection, image, table, begin)
        if bench_process.read(self.config["inventory"]) != inventory:
            raise RuntimeError("Firmware inventory changed during FLASH verification")
        receipt_path = self.out / "independent-verification.json"
        receipt = {
            **bench_process.read(self.out / "selected-image.json"),
            "component": "native_vdp", "selection": selection, "method": "agon-flash-v1.9",
            "verified_extent_sha256": app["sha256"], "verified_extent_bytes": app["bytes"],
            "readback": str(result.resolve()), "boot_cli_ready": True, "mos_boot": boot,
            "companions": entry["companions"], "verified_epoch": time.time(),
            "verification_receipt": str(receipt_path.resolve()),
            "status": "verified-standard" if selection == "restore" and slot == 0 else "verified-exception",
        }
        olimex_vdp_ota.require_image(receipt, spec, selection)
        bench_process.record(receipt_path, receipt)
        inventory["components"]["native_vdp_sha256"] = app["sha256"]
        inventory["native_vdp"] = dict(receipt, prior=inventory["native_vdp"])
        inventory["pending_operation"] = None
        inventory["recorded_epoch"] = time.time()
        inventory["source"] = "Olimex Agon Flash with independent selected-image and MOS verification"
        inventory["next_preparation"] = f"Mainboard verified on app{slot}. Confirm slot before any slot-specific job."
        self.update_inventory(inventory)

    def invoke(self, phase="run", *, defer_results=False):
        preload = phase == "preload"
        enter_cwd = phase == "enter-cwd"
        human_phase = {"preload": "preload", "enter-cwd": "stage-only"}.get(phase)
        if human_phase != self.kit.get("human_start"):
            raise ValueError("Smith owns fixture invocation for this job")
        job = self.kit["fixtures"][0] if human_phase else fixture_runs(self.kit)[phase]
        named = "fixtures" in self.kit
        if ota := olimex_vdp_ota.spec_for(self.kit):
            inventory = bench_process.read(self.config["inventory"])
            olimex_vdp_ota.installed(inventory, ota, "candidate", receipt_path=(
                self.out.parent / "install-mainboard" / "independent-verification.json"))
        handoff = job.get("listener_handoff")
        offboard = getattr(self, "offboard", None)
        leave_reports = bool(offboard or defer_results)
        if defer_results and (not named or human_phase or handoff):
            raise ValueError("Deferred results require a named automated fixture without listener handoff")
        output_dir = self.out / "results" if named else self.out
        if named:
            output_dir.mkdir()
        transcript_file = "vdp-usb.bin" if named else "mainboard-serial.bin"
        self.validate_ports()
        if not leave_reports:
            self.idle()
        self.keyboard()
        with open_passive_serial(self.c["ports"][0], timeout=0.2) as reader:
            with (output_dir / transcript_file).open("xb") as transcript:
                observer = Observer(reader, transcript, self.type_line)
                self.type_line("mirror-on", "VDU 2")
                prompt = observer.witness()
                if named:
                    if not prompt.startswith(b"/"):
                        raise RuntimeError("The Legacy prompt does not show the entry directory")
                    entry = prompt[:-2].decode("ascii")
                    if (not re.fullmatch(r"/[A-Za-z0-9_./-]*", entry)
                            or str(PurePosixPath(entry)) != entry
                            or ".." in PurePosixPath(entry).parts):
                        raise RuntimeError("The Legacy prompt cannot be used to restore its directory")
                    prompt = observer.change_directory("enter-cwd", job["cwd"], prompt)
                if enter_cwd:
                    observer.mirror_off(prompt)
                    bench_process.record(self.out / "enter-cwd.json", {
                        "cwd": job["cwd"], "prompt": prompt.decode("ascii"),
                        "entry_directory": entry,
                    })
                    return
                observer.quiet_load(f"LOAD {job['sd_program']} &{job['address']}", prompt)
                if preload:
                    observer.mirror_off(prompt)
                    bench_process.record(self.out / "preload.json", {
                        "sd_program": job["sd_program"], "address": job["address"],
                        "prompt": prompt.decode("ascii"), "entry_directory": entry,
                    })
                    return
                if handoff:
                    observer.mirror_off(prompt, "mirror-off-run")
                    self.idle()
                    status = observer.run_to_listener(handoff["sd_path"], job["seconds"], job["uart_end"],
                                                      lambda: self.get("/sd/status"))
                    bench_process.record(self.out / "run-witness.json", {
                        "listener": status, "uart_end": job["uart_end"]["line"],
                    })
                    self.collect_results(job, output_dir, named, listener_online=True)
                    self.type_line("mirror-resume", "VDU 2")
                    returned = observer.witness("post-run-witness")
                    if returned.lower() != prompt.lower():
                        raise RuntimeError("MOS returned to a different directory after the fixture")
                    prompt = returned
                else:
                    observer.run(f"RUN &{job['address']}", prompt, job["success"].encode(),
                                 job["failure"].encode(), job["seconds"], uart_end=job.get("uart_end"))
                if leave_reports:
                    returned = observer.witness("post-run-witness")
                    if returned.lower() != prompt.lower():
                        raise RuntimeError("MOS returned to a different directory after the fixture")
                    receipt = "offboard-results.json" if offboard else "deferred-results.json"
                    bench_process.record(self.out / receipt, {
                        "success_line": job["success"], "post_run_prompt": returned.decode("ascii"),
                        "reports": fixture_results(job),
                        "collection": "pending-physical-collection" if offboard else "pending-collection",
                    })
                if named:
                    prompt = observer.change_directory("restore-cwd", entry, prompt)
                observer.mirror_off(prompt)

        if not handoff and not leave_reports:
            self.collect_results(job, output_dir, named)

    def collect_results(self, job, output_dir, named, *, listener_online=False):
        result_path = self.out / "result.txt"
        def check_result():
            if result_path.read_bytes().decode("ascii").splitlines() != job["expected_agon"]:
                raise RuntimeError("Agon fixture result differs")

        if uart_transfer(self.kit):
            if not named or listener_online:
                raise RuntimeError("UART results need a fresh UART-only listener and named reports")

            with self.uart_listener("collect"):
                for number, path in enumerate(fixture_results(job), start=1):
                    channel = f"sd-collect-{number:02d}"
                    destination = output_dir / PurePosixPath(path).name
                    result = self.staged_uart(channel, "get", path, destination=destination)
                    bench_process.record(self.out / f"{channel}.receipt.json", {
                        **result, "target": path,
                    })
                    if not result["bytes"]:
                        raise RuntimeError(f"Fixture produced an empty report: {path}")
        elif self.kit.get("schema", DEFAULT_SCHEMA) == 3:
            if not listener_online:
                self.start_listener("collect", PARALLEL_LISTENER)
            for number, path in enumerate(fixture_results(job), start=1):
                channel = f"sd-collect-{number:02d}" if named else "sd-collect"
                destination = output_dir / PurePosixPath(path).name if named else result_path
                staged = StagedClient(self.url, self.out / f"{channel}.json")
                try:
                    receipt = staged.begin("get", path, destination=destination,
                                           require_parallel=True)
                    bench_process.record(self.out / f"{channel}.receipt.json", receipt)
                finally:
                    staged.close()
                if named and destination.stat().st_size == 0:
                    raise RuntimeError(f"Fixture produced an empty report: {path}")
            if not named:
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

    def handback(self, restores=None):
        if restores is None:
            restores = {c: self.out.parent / f"restore-{c}" for c in self.kit["firmware"]}
        self.verify_mos("handback-mos")
        self.idle()
        self.validate_ports()
        inventory = bench_process.read(self.config["inventory"])
        if inventory.get("pending_operation"):
            raise RuntimeError("Firmware is still pending reconciliation")
        ota = olimex_vdp_ota.spec_for(self.kit)
        for component, spec in self.kit["firmware"].items():
            if spec is ota:
                receipt = restores.get(component)
                olimex_vdp_ota.installed(inventory, ota, "restore", receipt_path=(
                    receipt / "independent-verification.json" if receipt is not None else None))
                continue
            role, hash_field = INVENTORY[component]
            expected = spec.get("restore_app", spec["restore_write"])["sha256"]
            if inventory["components"][hash_field] != expected:
                raise RuntimeError(f"Inventory differs from production for {role}")
            if component not in restores:
                continue
            receipt = bench_process.read(restores[component] / "independent-verification.json")
            if (receipt["sha256"] != expected or not receipt["boot_cli_ready"]
                    or receipt["verified_extent_sha256"] != spec["restore_write"]["sha256"]):
                raise RuntimeError(f"Missing verified production restore for {role}")
        bench_process.record(self.out / "handback.json", {
            "working_legacy_cli": True, "keyboard": self.keyboard(),
            "listener_offline": True, "staged_transfer_idle": True, "serial_handles_free": True,
            "production_restores": list(restores),
            **({"production_mainboard_slot": ota["restore_slot"]} if ota else {}),
        })
        if self.kit["firmware"]:
            inventory["ready_claim"] = True
            inventory["recorded_epoch"] = time.time()
            self.update_inventory(inventory)

    def recover(self, args, failed, owner, binding):
        root = self.out.parent
        history = recovery_history(args, self.kit, failed, owner, binding)
        inventory = bench_process.read(self.config["inventory"])
        if inventory.get("pending_operation"):
            raise RuntimeError("Unreconciled firmware operation. Inspect the inventory and original write evidence")
        changed, restores = [], {}
        for component in reversed(COMPONENTS):
            if component not in self.kit["firmware"]:
                continue
            spec = self.kit["firmware"][component]
            role, field = INVENTORY[component]
            operation = next((phase for phase in reversed(history)
                              if phase in (f"install-{component}", f"retry-{component}",
                                           f"restore-{component}")), None)
            selection = "restore" if operation in (None, f"restore-{component}") else "candidate"
            ota = spec is olimex_vdp_ota.spec_for(self.kit)
            suffix = "app" if ota else "write"
            extent = spec[f"{selection}_{suffix}"]
            digest = spec.get(f"{selection}_app", extent)["sha256"]
            if inventory["components"][field] != digest:
                raise RuntimeError(f"Inventory does not establish the expected {component} image")
            receipt_path = root / operation / "independent-verification.json" if operation else None
            if ota:
                olimex_vdp_ota.installed(inventory, spec, selection, receipt_path=receipt_path,
                                         allow_padded=operation is None)
            if receipt_path is None:
                continue
            receipt = bench_process.read(receipt_path)
            if (receipt["component"] != role or receipt["selection"] != selection
                    or receipt["sha256"] != digest or receipt["boot_cli_ready"] is not True
                    or receipt["verified_extent_sha256"] != extent["sha256"]
                    or receipt["verified_extent_bytes"] != extent["bytes"]
                    or Path(inventory[role]["verification_receipt"]).resolve() != receipt_path.resolve()):
                raise RuntimeError(f"Firmware evidence does not bind {component} to the original operation")
            if selection == "restore":
                restores[component] = receipt_path.parent
            elif ota or extent["sha256"] != spec["restore_write"]["sha256"]:
                changed.append(component)
        bench_process.record(self.out / "plan.json", {"failed": failed, "restore": changed,
                                                     "completed": history})
        for component in changed:
            folder = self.out / f"restore-{component}"
            folder.mkdir()
            restore = Bench(self.config, self.kit, folder)
            restore.lock = self.lock
            restore.offboard = getattr(self, "offboard", None)
            if component == "mainboard" and olimex_vdp_ota.spec_for(self.kit):
                restore.firmware(component, "restore", job_root=root)
            else:
                restore.firmware(component, "restore")
            restores[component] = folder
        self.handback(restores)

    def perform(self, phase, *, recovery=None, defer_results=False):
        path = Path(self.config["operation_lock"])
        with path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock = lock
            if recovery is not None:
                self.recover(*recovery)
            elif phase == "verify-mos":
                self.verify_mos()
            elif any(self.out.parent.glob("recover-after-*")):
                raise RuntimeError("Recovery has started in this evidence directory")
            elif phase == "stage":
                self.validate_ports()
                self.stage()
            elif phase in ("preload", "enter-cwd") or phase in fixture_runs(self.kit):
                if defer_results:
                    self.invoke(phase, defer_results=True)
                else:
                    self.invoke(phase)
            elif phase == "handback":
                self.handback()
            else:
                operation, component = phase.split("-", 1)
                selection = "restore" if operation == "restore" else "candidate"
                self.firmware(component, selection, retry=operation == "retry")


def child_argv(args, phase, *, defer_results=False):
    argv = [sys.executable, str(Path(__file__).resolve()), "--job", str(args.job),
            "--sha256", args.sha256, "--config", str(args.config), "--out", str(args.out)]
    if option := getattr(args, "offboard_stage", None):
        argv.extend(("--offboard-stage", *option))
    if defer_results:
        argv.append("--defer-results")
    return [*argv, f"worker-{phase}"]


def prior_argv(args, kit, phase, supervisor):
    argv = child_argv(args, phase)
    if phase.startswith("run-") and (job := fixture_runs(kit).get(phase)) and "listener_handoff" not in job:
        deferred = child_argv(args, phase, defer_results=True)
        if supervisor["argv"] == deferred:
            return deferred
    return argv


def runtime_preflight(kit, config):
    # reboot_pair uses the runner interpreter even for a mainboard-only job.
    if {"mainboard", "p4"}.intersection(kit["firmware"]):
        from esptool import __version__
        from esptool.reset import HardReset
        if __version__ != "5.1.0" or not callable(HardReset):
            raise RuntimeError(f"{sys.executable} needs stock esptool 5.1.0 for the paired restart")
    if olimex_vdp_ota.spec_for(kit):
        mainboard_rom()
    elif "mainboard" in kit["firmware"]:
        mainboard_programmer()


def recovery_history(args, kit, failed, owner, binding):
    order = phases(kit, enter_cwd=(args.out / "enter-cwd").is_dir())
    planned = failed.replace("retry-", "install-", 1) if failed.startswith("retry-") else failed
    completed = []
    expected = {f"recover-after-{failed}"}

    def verify(phase, *, fault=False):
        folder = args.out / phase
        supervisor = bench_process.read(folder / "supervisor-started.json")
        argv = prior_argv(args, kit, phase, supervisor)
        if (supervisor["owner"] != owner or supervisor["lease"] != f"chat:{owner}"
                or supervisor["phase"] != phase or supervisor["argv"] != argv
                or bench_process.read(folder / "operation-binding.json") != binding):
            raise RuntimeError(f"Original operator, packet or config differs for {phase}")
        code = 0
        if fault:
            blocked = bench_process.read(folder / "blocked.json")
            code = bench_process.read(folder / "child-terminal.json")["returncode"]
            if (type(code) is not int or code == 0 or blocked["phase"] != phase or blocked["owner"] != owner
                    or blocked["lease"] != supervisor["lease"]):
                raise RuntimeError(f"No matching first fault for {phase}")
        elif bench_process.read(folder / "complete.json")["state"] != "completed":
            raise RuntimeError(f"Missing successful completion for {phase}")
        bench_process.verify_child(folder, argv, expected_returncode=code, allow_interruption=fault)
        expected.add(phase)

    for prior in order[:order.index(planned)]:
        if prior in ("install-mainboard", "install-p4"):
            retry = prior.replace("install-", "retry-")
            if (args.out / retry).exists():
                verify(prior, fault=True)
                prior = retry
        verify(prior)
        completed.append(prior)
    if failed != planned:
        verify(planned, fault=True)
    verify(failed, fault=True)
    # A failed flash that reached an intent or a readback needs reconciliation.
    if failed.startswith(("install-", "retry-", "restore-")) and any(
            (args.out / failed / name).exists() for name in
            ("write-intent.json", "write-dispatched.json", "dispatch-flash.json",
             "write-verified.json", "independent-verification.json")):
        raise RuntimeError("The failed firmware phase has write evidence and needs reconciliation")
    known = set(order) | {"retry-mainboard", "retry-p4"}
    for folder in args.out.iterdir():
        if folder.name not in expected and (folder.name in known or folder.name.startswith("recover-after-")
                                             or (folder / "supervisor-started.json").is_file()):
            raise RuntimeError(f"Unexpected phase evidence: {folder.name}")
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--offboard-stage", nargs=3, metavar=("DIR", "MANIFEST_SHA256", "RECEIPT_SHA256"),
                        help="Use pinned physical SD staging evidence and retain reports on card")
    parser.add_argument("--defer-results", action="store_true",
                        help="For this named run, prove MOS return and leave the reports on card")
    parser.add_argument("--operator", help="The chat holding the open slot")
    parser.add_argument("phase")
    args = parser.parse_args()
    raw = args.job.read_bytes()
    if sha256(raw).hexdigest() != args.sha256:
        raise ValueError("Job manifest differs from the named hash")
    kit = json.loads(raw)
    phase = args.phase.removeprefix("worker-")
    order = [] if phase == "verify-mos" else preflight(kit)
    offboard = offboard_proof(kit, args.sha256, args.offboard_stage) if args.offboard_stage else None
    config = bench_process.read(args.config) if args.config else None
    if config is not None and phase != "verify-mos":
        runtime_preflight(kit, config)
    if args.phase == "preflight":
        print("\n".join(order))
        return 0
    if not args.config or not args.out:
        parser.error("Physical phases require --config and --out")
    job = fixture_runs(kit).get(phase) if args.defer_results else None
    if args.defer_results and (not phase.startswith("run-") or job is None
                               or "human_start" in kit or "listener_handoff" in job):
        parser.error("--defer-results applies to one named automated run without listener handoff")
    failed = phase.removeprefix("recover-after-") if phase.startswith("recover-after-") else None
    selected = failed or phase
    order = (["verify-mos"] if phase == "verify-mos" else
             phases(kit, enter_cwd=selected == "enter-cwd" or (args.out / "enter-cwd").is_dir()))
    retry_phase = selected in ("retry-mainboard", "retry-p4")
    ota = olimex_vdp_ota.spec_for(kit)
    if ota and retry_phase:
        parser.error("Agon Flash firmware writes cannot be retried by the runner")
    planned = selected.replace("retry-", "install-", 1) if retry_phase else selected
    if planned not in order:
        parser.error("The selected phase is absent from this job")
    if args.phase != phase:
        folder = args.out / phase
        supervisor = bench_process.read(folder / "supervisor-started.json")
        if supervisor["argv"] != child_argv(args, phase, defer_results=args.defer_results):
            raise RuntimeError("Worker is missing its supervisor binding")
        binding = {"cwd": str(Path.cwd()), "job_sha256": args.sha256, "config": config,
                   "reset_config_sha256": sha256(Path(config["reset_config"]).read_bytes()).hexdigest()}
        if offboard:
            binding["offboard_stage"] = offboard
        # Retain only the digest of the local binding in evidence.
        binding = {"sha256": sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()}
        bench_process.record(folder / "operation-binding.json", binding)
        bench = Bench(config, kit, folder)
        bench.offboard = offboard
        if failed:
            bench.perform(phase, recovery=(args, failed, supervisor["owner"], binding))
            return 0
        for prior in order[:order.index(planned)]:
            if not ota and prior in ("install-mainboard", "install-p4"):
                retry = prior.replace("install-", "retry-", 1)
                if (args.out / retry).exists():
                    bench_process.verify_child(args.out / prior, child_argv(args, prior),
                                               expected_returncode=1)
                    prior = retry
            argv = child_argv(args, prior)
            if ota or planned == "enter-cwd" or prior == "enter-cwd" or prior.startswith("run-"):
                previous = args.out / prior
                previous_supervisor = bench_process.read(previous / "supervisor-started.json")
                argv = prior_argv(args, kit, prior, previous_supervisor)
                if (previous_supervisor["owner"] != supervisor["owner"]
                        or previous_supervisor["lease"] != supervisor["lease"]
                        or previous_supervisor["phase"] != prior
                        or bench_process.read(previous / "operation-binding.json") != binding):
                    raise RuntimeError(f"Original operator, packet or config differs for {prior}")
            bench_process.verify_child(args.out / prior, argv)
        if retry_phase:
            bench_process.verify_child(args.out / planned, child_argv(args, planned),
                                       expected_returncode=1)
        bench.perform(phase, defer_results=args.defer_results)
        return 0
    if not args.operator:
        parser.error("Physical phases require --operator from the opened chat slot")
    print(f"Operator {args.operator} starting {phase} under its existing slot", flush=True)
    bounds = {"stage": 90 if offboard else stage_seconds(kit), "enter-cwd": 90,
              "install-mainboard": 550, "restore-mainboard": 550, "retry-mainboard": 550,
              "install-p4": 650, "restore-p4": 650, "retry-p4": 760, "handback": 90, "verify-mos": 90}
    if failed:
        bounds[phase] = 90 + sum(bounds.get(f"restore-{c}", 480) for c in kit["firmware"])
    job = None if phase == "verify-mos" else fixture_runs(kit).get(phase)
    seconds = (job["seconds"] + job.get("uart_end", {}).get("seconds", 0) + 210
               if job is not None else bounds.get(phase, 480))
    return bench_process.run(child_argv(args, phase, defer_results=args.defer_results), args.out / phase,
                             seconds, owner=args.operator,
                             lease=f"chat:{args.operator}", phase=phase,
                             next_action="Keep the slot and follow the bench stop procedure.")


if __name__ == "__main__":
    sys.exit(main())
