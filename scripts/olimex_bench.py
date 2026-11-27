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
import olimex_reports as reports
from olimex_cli import Observer, completion_markers
from olimex_flash import check_extent, flash_application, mainboard_programmer
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
    if "report_lifecycle" in kit:
        reports.validate(kit, pinned)
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
    reports = None
    reuse_stage = None

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

    def cli(self, label="cli"):
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", label):
            raise ValueError("Invalid CLI observation label")
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

        def existing(client, remote):
            try:
                return client.stat_entry(remote)
            except RemoteError as error:
                if error.status == 6 and error.detail in (b"\x04", b"\x05"):
                    return None
                raise

        if schema in (2, 3):
            results = [path for job in jobs for path in fixture_results(job)]
            self.stage_parallel(payloads, [*results, *expected_absent], existing)
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
                if self.reuse_stage is None:
                    client.make_directory(directory, parents=True)
            for path in targets:
                remote = existing(client, path)
                if self.reuse_stage is not None and path in payloads:
                    if remote is None or remote[1] & 16 or remote[0] != len(payloads[path]):
                        raise RuntimeError(f"Previously staged file is missing or differs in size: {path}")
                elif remote is not None:
                    raise RuntimeError(f"Parallel staging requires a fresh target: {path}")
        finally:
            client.lock.close()

        uploads = payloads.items() if self.reuse_stage is None else ()
        for number, (path, payload) in enumerate(uploads):
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

    def invoke(self, phase="run"):
        preload = phase == "preload"
        enter_cwd = phase == "enter-cwd"
        human_phase = {"preload": "preload", "enter-cwd": "stage-only"}.get(phase)
        if human_phase != self.kit.get("human_start"):
            raise ValueError("Smith owns fixture invocation for this job")
        job = self.kit["fixtures"][0] if human_phase else fixture_runs(self.kit)[phase]
        named = "fixtures" in self.kit
        handoff = job.get("listener_handoff")
        output_dir = self.out / "results" if named else self.out
        if named:
            output_dir.mkdir()
        transcript_file = "vdp-usb.bin" if named else "mainboard-serial.bin"
        self.validate_ports()
        self.idle()
        self.keyboard()
        attempt = None
        if self.reports:
            stage = bench_process.read(self.out.parent / "stage/report-stage.json")
            attempt = self.reports.prepare(phase, job, stage)
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
                elif attempt:
                    if self.reports.fence() != attempt["fence"]:
                        raise RuntimeError("Custody or boot changed before RUN")
                    argument = " " + attempt["token"] if attempt["mode"] == "token-v1" else ""
                    command = f"RUN &{job['address']}{argument}"
                    witness = observer.run_report(command, prompt, job["success"], job["failure"], job["seconds"])
                    transcript.flush()
                    os.fsync(transcript.fileno())
                    path = output_dir / transcript_file
                    witness.update(transcript_bytes=path.stat().st_size, transcript_sha256=reports.digest(path),
                                   token=attempt["token"], command=command, prompt=prompt.decode("ascii"))
                    reports.publish(self.out / "report-run.json", witness)
                else:
                    observer.run(f"RUN &{job['address']}", prompt, job["success"].encode(),
                                 job["failure"].encode(), job["seconds"], uart_end=job.get("uart_end"))
                if named:
                    prompt = observer.change_directory("restore-cwd", entry, prompt)
                observer.mirror_off(prompt)

        if attempt:
            self.finish_reports(self.out, job, attempt, witness)
        elif not handoff:
            self.collect_results(job, output_dir, named)

    def finish_reports(self, origin, job, attempt, witness):
        valid = self.reports.collect(origin, job, attempt, witness)
        if witness["outcome"] != "passed" or not valid:
            raise RuntimeError("Fixture or report failed; see the attempt and per-report receipts")

    def collect_results(self, job, output_dir, named, *, listener_online=False):
        result_path = self.out / "result.txt"
        def check_result():
            if result_path.read_bytes().decode("ascii").splitlines() != job["expected_agon"]:
                raise RuntimeError("Agon fixture result differs")

        if self.kit.get("schema", DEFAULT_SCHEMA) == 3:
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
            extent = spec[f"{selection}_write"]
            digest = spec.get(f"{selection}_app", extent)["sha256"]
            if inventory["components"][field] != digest:
                raise RuntimeError(f"Inventory does not establish the expected {component} image")
            if operation is None:
                continue
            receipt_path = root / operation / "independent-verification.json"
            receipt = bench_process.read(receipt_path)
            if (receipt["component"] != role or receipt["selection"] != selection
                    or receipt["sha256"] != digest or receipt["boot_cli_ready"] is not True
                    or receipt["verified_extent_sha256"] != extent["sha256"]
                    or receipt["verified_extent_bytes"] != extent["bytes"]
                    or Path(inventory[role]["verification_receipt"]).resolve() != receipt_path.resolve()):
                raise RuntimeError(f"Firmware evidence does not bind {component} to the original operation")
            if selection == "restore":
                restores[component] = receipt_path.parent
            elif extent["sha256"] != spec["restore_write"]["sha256"]:
                changed.append(component)
        bench_process.record(self.out / "plan.json", {"failed": failed, "restore": changed,
                                                     "completed": history})
        for component in changed:
            folder = self.out / f"restore-{component}"
            folder.mkdir()
            restore = Bench(self.config, self.kit, folder)
            restore.lock = self.lock
            restore.firmware(component, "restore")
            restores[component] = folder
        self.handback(restores)

    def perform(self, phase, *, recovery=None, resume_reports=None):
        path = Path(self.config["operation_lock"])
        with path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock = lock
            if self.reports:
                self.reports.custody()
            if resume_reports is not None:
                origin, job, attempt, witness = resume_reports
                self.validate_ports()
                self.finish_reports(origin, job, attempt, witness)
            elif recovery is not None:
                self.recover(*recovery)
            elif any(self.out.parent.glob("recover-after-*")):
                raise RuntimeError("Recovery has started in this evidence directory")
            elif phase == "stage":
                self.validate_ports()
                if self.reports:
                    fence = self.reports.fence()
                    if self.reuse_stage and fence != self.reuse_stage["fence"]:
                        raise RuntimeError("Stage reuse requires uninterrupted custody, firmware and boots")
                self.stage()
                if self.reports:
                    if self.reports.fence() != fence:
                        raise RuntimeError("Custody or boot changed during staging")
                    reports.publish(self.out / "report-stage.json", {
                        "binding": self.reports.binding, "fence": fence,
                        "reused_from": self.reuse_stage["source"] if self.reuse_stage else None,
                    })
            elif phase in ("preload", "enter-cwd") or phase in fixture_runs(self.kit):
                self.invoke(phase)
            elif phase == "handback":
                self.handback()
            else:
                operation, component = phase.split("-", 1)
                selection = "restore" if operation == "restore" else "candidate"
                self.firmware(component, selection, retry=operation == "retry")


def child_argv(args, phase):
    argv = [sys.executable, str(Path(__file__).resolve()), "--job", str(args.job),
            "--sha256", args.sha256, "--config", str(args.config),
            "--out", str(args.out)]
    if getattr(args, "reuse_stage", None):
        argv += ["--reuse-stage", str(args.reuse_stage)]
    return [*argv, f"worker-{phase}"]


def runtime_preflight(kit, config):
    # reboot_pair uses the runner interpreter even for a mainboard-only job.
    if {"mainboard", "p4"}.intersection(kit["firmware"]):
        from esptool import __version__
        from esptool.reset import HardReset
        if __version__ != "5.1.0" or not callable(HardReset):
            raise RuntimeError(f"{sys.executable} needs stock esptool 5.1.0 for the paired restart")
    if "mainboard" in kit["firmware"]:
        mainboard_programmer()
    if "report_lifecycle" in kit and not Path(config["report_lease_state"]).is_absolute():
        raise ValueError("Report lifecycle requires the absolute scheduler state path")


def verify_bound_phase(args, phase, owner, binding, *, code=None):
    folder = args.out / phase
    argv = child_argv(args, phase)
    supervisor = bench_process.read(folder / "supervisor-started.json")
    if (supervisor["owner"] != owner or supervisor["lease"] != f"chat:{owner}"
            or supervisor["phase"] != phase or supervisor["argv"] != argv
            or bench_process.read(folder / "operation-binding.json") != binding):
        raise RuntimeError(f"Original operator, packet or config differs for {phase}")
    result = bench_process.read(folder / "child-terminal.json")["returncode"]
    if code is not None and result != code:
        raise RuntimeError(f"Unexpected exit for {phase}: {result}")
    if result:
        failure = bench_process.read(folder / "blocked.json")
        if (failure["owner"], failure["lease"], failure["phase"]) != (owner, f"chat:{owner}", phase):
            raise RuntimeError(f"Unbound failure receipt for {phase}")
    elif bench_process.read(folder / "complete.json")["state"] != "completed":
        raise RuntimeError(f"Missing successful completion for {phase}")
    bench_process.verify_child(folder, argv, expected_returncode=result, allow_interruption=bool(result))
    return result


def report_resume_names(args, run):
    name = re.compile(rf"resume-{re.escape(run)}-[0-9]{{2}}")
    names = sorted(path.name for path in args.out.iterdir() if name.fullmatch(path.name))
    if names != [f"resume-{run}-{index:02d}" for index in range(1, len(names) + 1)]:
        raise RuntimeError(f"Unexpected or out-of-order report resume for {run}")
    return names


def verify_report_run(args, run, owner, binding, *, successful):
    code = verify_bound_phase(args, run, owner, binding)
    resumes = report_resume_names(args, run)
    for name in resumes:
        if code == 0:
            raise RuntimeError(f"Unexpected report resume after completion: {name}")
        code = verify_bound_phase(args, name, owner, binding)
    if successful and code:
        raise RuntimeError(f"No completed report collection for {run}")
    return resumes


def report_resume(args, phase, run, order, kit, owner, binding):
    if any((args.out / later).exists() for later in order[order.index(run) + 1:]):
        raise RuntimeError("A successor phase already started")
    if any(args.out.glob("recover-after-*")):
        raise RuntimeError("Bench recovery has already started")
    if verify_bound_phase(args, run, owner, binding) == 0:
        raise RuntimeError("The original report phase already completed")
    resumes = report_resume_names(args, run)
    if not resumes or resumes[-1] != phase:
        raise RuntimeError("Use the next numbered report resume")
    for prior in resumes[:-1]:
        if verify_bound_phase(args, prior, owner, binding) == 0:
            raise RuntimeError("The report collection already completed")
    origin = args.out / run
    attempt = bench_process.read(origin / "report-attempt.json")
    witness = bench_process.read(origin / "report-run.json")
    job = fixture_runs(kit)[run]
    mode = kit["report_lifecycle"]["mode"]
    argument = f" {attempt['token']}" if mode == "token-v1" else ""
    command = f"RUN &{job['address']}{argument}"
    if (attempt["phase"] != run or attempt["mode"] != mode or attempt["binding"] != binding
            or attempt["program"] != job["sd_program"] or attempt["fixture"] != job["agon"]["sha256"]
            or not re.fullmatch(reports.TOKEN, attempt["token"]) or witness["token"] != attempt["token"]
            or witness["command"] != command or witness["outcome"] not in ("passed", "failed")
            or bench_process.read(origin / "dispatch-run.json")["command"] != command):
        raise RuntimeError("The original RUN and report attempt do not agree")
    return origin, job, attempt, witness


def stage_reuse(args, kit, owner, binding):
    source = args.reuse_stage
    if (source.resolve() == args.out.resolve() or not source.is_absolute()
            or not (source / "stage/report-stage.json").is_file()):
        raise ValueError("Reuse requires the absolute evidence root of an earlier stage")
    original = argparse.Namespace(**vars(args))
    original.out, original.reuse_stage = source, None
    verify_bound_phase(original, "stage", owner, binding, code=0)
    stage = bench_process.read(source / "stage/report-stage.json")
    if stage["binding"] != binding or stage["reused_from"] is not None:
        raise RuntimeError("Reuse must refer to the original matching upload receipts")
    payloads = {path: item for job in fixture_runs(kit).values() for path, item in fixture_inputs(job).items()}
    for number, (path, item) in enumerate(payloads.items()):
        prefix = source / f"stage/stage-file-{number:02d}"
        receipt = bench_process.read(prefix.with_suffix(".receipt.json"))
        if (receipt["target"] != path or receipt["result"]["size"] != item["bytes"]
                or receipt["result"]["bytes"] != item["bytes"] or receipt["result"]["error"] != 0
                or reports.digest(prefix.with_suffix(".bin")) != item["sha256"]):
            raise RuntimeError(f"No matching completed upload and host input for {path}")
    return {"source": str(source), "fence": stage["fence"]}


def recovery_history(args, kit, failed, owner, binding):
    order = phases(kit, enter_cwd=(args.out / "enter-cwd").is_dir())
    planned = failed.replace("retry-", "install-", 1) if failed.startswith("retry-") else failed
    completed = []
    expected = {f"recover-after-{failed}"}

    def verify(phase, *, fault=False):
        folder = args.out / phase
        argv = child_argv(args, phase)
        supervisor = bench_process.read(folder / "supervisor-started.json")
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
        if "report_lifecycle" in kit and prior in fixture_runs(kit):
            expected.update(verify_report_run(args, prior, owner, binding, successful=True))
            expected.add(prior)
            completed.append(prior)
            continue
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
    if "report_lifecycle" in kit and failed in fixture_runs(kit):
        expected.update(verify_report_run(args, failed, owner, binding, successful=False))
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
    parser.add_argument("--operator", help="The chat holding the open slot")
    parser.add_argument("--reuse-stage", type=Path, help="Original upload evidence root for a lifecycle job")
    parser.add_argument("phase")
    args = parser.parse_args()
    raw = args.job.read_bytes()
    if sha256(raw).hexdigest() != args.sha256:
        raise ValueError("Job manifest differs from the named hash")
    kit = json.loads(raw)
    order = preflight(kit)
    config = bench_process.read(args.config) if args.config else None
    if config is not None:
        runtime_preflight(kit, config)
    if args.phase == "preflight":
        print("\n".join(order))
        return 0
    if not args.config or not args.out:
        parser.error("Physical phases require --config and --out")
    phase = args.phase.removeprefix("worker-")
    failed = phase.removeprefix("recover-after-") if phase.startswith("recover-after-") else None
    managed = "report_lifecycle" in kit
    resume = re.fullmatch(r"resume-(run-[a-z][a-z0-9-]{0,23})-([0-9]{2})", phase) if managed else None
    if args.reuse_stage and not managed:
        parser.error("Stage reuse requires opt-in report lifecycle")
    selected = failed or phase
    order = phases(kit, enter_cwd=selected == "enter-cwd" or (args.out / "enter-cwd").is_dir())
    retry_phase = selected in ("retry-mainboard", "retry-p4")
    planned = resume[1] if resume else selected.replace("retry-", "install-", 1) if retry_phase else selected
    if planned not in order:
        parser.error("The selected phase is absent from this job")
    if args.phase != phase:
        folder = args.out / phase
        supervisor = bench_process.read(folder / "supervisor-started.json")
        if supervisor["argv"] != child_argv(args, phase):
            raise RuntimeError("Worker is missing its supervisor binding")
        binding = {"cwd": str(Path.cwd()), "job_sha256": args.sha256, "config": config,
                   "reset_config_sha256": sha256(Path(config["reset_config"]).read_bytes()).hexdigest()}
        # Retain only the digest of the local binding in evidence.
        binding = {"sha256": sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()}
        bench_process.record(folder / "operation-binding.json", binding)
        bench = Bench(config, kit, folder)
        owner = supervisor["owner"]
        if managed:
            if supervisor["lease"] != f"chat:{owner}" or supervisor["phase"] != phase:
                raise RuntimeError("Report phase lacks its original operator binding")
            bench.reports = reports.Lifecycle(bench, owner, binding, agon_boot=lambda: status(bench.url)["boot"])
            bench.reports.custody()
            if resume:
                record = report_resume(args, phase, planned, order, kit, owner, binding)
                bench.perform(phase, resume_reports=record)
                return 0
            if args.reuse_stage and phase == "stage":
                bench.reuse_stage = stage_reuse(args, kit, owner, binding)
        if failed:
            bench.perform(phase, recovery=(args, failed, owner, binding))
            return 0
        for prior in order[:order.index(planned)]:
            if managed and prior in fixture_runs(kit):
                verify_report_run(args, prior, owner, binding, successful=True)
                continue
            if managed and prior == "stage":
                verify_bound_phase(args, prior, owner, binding, code=0)
                continue
            if prior in ("install-mainboard", "install-p4"):
                retry = prior.replace("install-", "retry-", 1)
                if (args.out / retry).exists():
                    bench_process.verify_child(args.out / prior, child_argv(args, prior),
                                               expected_returncode=1)
                    prior = retry
            if planned == "enter-cwd" or prior == "enter-cwd":
                previous = args.out / prior
                previous_supervisor = bench_process.read(previous / "supervisor-started.json")
                if (previous_supervisor["owner"] != supervisor["owner"]
                        or previous_supervisor["lease"] != supervisor["lease"]
                        or previous_supervisor["phase"] != prior
                        or bench_process.read(previous / "operation-binding.json") != binding):
                    raise RuntimeError(f"Original operator, packet or config differs for {prior}")
            bench_process.verify_child(args.out / prior, child_argv(args, prior))
        if retry_phase:
            bench_process.verify_child(args.out / planned, child_argv(args, planned),
                                       expected_returncode=1)
        bench.perform(phase)
        return 0
    if not args.operator:
        parser.error("Physical phases require --operator from the opened chat slot")
    if resume and phase != f"resume-{planned}-{len(report_resume_names(args, planned)) + 1:02d}":
        parser.error("Use the next numbered report resume")
    print(f"Operator {args.operator} starting {phase} under its existing slot", flush=True)
    bounds = {"stage": 300, "enter-cwd": 90,
              "install-mainboard": 550, "restore-mainboard": 550, "retry-mainboard": 550,
              "install-p4": 650, "restore-p4": 650, "retry-p4": 760, "handback": 90}
    if failed:
        bounds[phase] = 90 + sum(bounds.get(f"restore-{c}", 480) for c in kit["firmware"])
    job = fixture_runs(kit).get(phase)
    seconds = (job["seconds"] + job.get("uart_end", {}).get("seconds", 0) + 210
               if job is not None else bounds.get(phase, 480))
    if managed and (job is not None or resume):
        count = len(fixture_runs(kit)[planned]["results"])
        seconds = (job["seconds"] if job is not None else 0) + 150 + count * 690
    return bench_process.run(child_argv(args, phase), args.out / phase,
                             seconds, owner=args.operator,
                             lease=f"chat:{args.operator}", phase=phase,
                             next_action="Keep the slot and follow the bench stop procedure.")


if __name__ == "__main__":
    sys.exit(main())
