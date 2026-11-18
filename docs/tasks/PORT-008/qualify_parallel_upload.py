#!/usr/bin/env python3
"""PORT-008 candidate qualification. Each physical phase needs an open slot."""

import argparse
from contextlib import contextmanager, nullcontext
import fcntl
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import sys
from threading import Event


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import bench_process
from olimex_bench import Bench, LISTENER, PARALLEL_LISTENER, pinned, preflight, sd_path
from olimex_cli import Observer, rename_result
from passive_serial import open_passive_serial
from sdcard import RemoteError
from sdcard_staged import Client as StagedClient


LIVE_LISTENER = "/emos/sdserve.bin"
PHASES = {"install-p4": 650, "install-listener": 300, "stage": 300,
          "verify-scratch": 480, "run": 240, "restore-listener": 240,
          "restore-p4": 650, "handback": 90}
TWO_WAY_PHASES = {"prepare-emos": 360, "install-p4": 650, "install-emos": 420,
                  "install-listener": 300, "stage": 600, "verify-scratch": 720,
                  "run": 240, "restore-listener": 240, "restore-emos": 420,
                  "restore-p4": 650, "handback": 90}


def validate(packet):
    kit = packet["job"]
    preflight(kit)
    if ((kit["schema"], set(kit["firmware"])) not in
            ((2, {"p4"}), (3, {"p4", "emos"}))):
        raise ValueError("Qualification requires the matched PARLIO firmware changes")
    if not kit["fixture"]["inputs"] or kit["fixture"]["seconds"] > 30:
        raise ValueError("Qualification requires explicit scratch inputs and a bounded fixture")
    listener = packet["listener"]
    for key in ("candidate", "restore"):
        if not 0 < len(pinned(listener[key])) <= 0x8000:
            raise ValueError("Listener is outside the MOSlet size limit")
    if kit["preserve"][LIVE_LISTENER] != listener["restore"]["sha256"]:
        raise ValueError("Listener rollback differs from the bench pin")
    if listener["candidate"]["sha256"] == listener["restore"]["sha256"]:
        raise ValueError("Expected a distinct candidate listener")


def absent(client, path):
    try:
        client.stat_entry(path)
    except RemoteError as error:
        if error.status == 6 and error.detail in (b"\x04", b"\x05"):
            return
        raise
    raise RuntimeError(f"Provisioning path already exists: {path}")


def rename_listener(bench, commands):
    with open_passive_serial(bench.c["ports"][0], timeout=0.2) as reader:
        with (bench.out / "mainboard-serial.bin").open("xb") as transcript:
            observer = Observer(reader, transcript, bench.type_line)
            bench.type_line("mirror-on", "VDU 2")
            prompt = observer.witness()
            for number, (source, target) in enumerate(commands, start=1):
                command = f"RENAME {source} {target}"
                observer.exchange(f"rename-{number}", command,
                                  lambda data: rename_result(data, command, prompt, source, target), 15)
            observer.mirror_off(prompt)


def change_listener(bench, packet, install):
    root = bench.install_dir
    candidate = root + "/next.bin"
    previous = root + "/previous.bin"
    retained = root + "/candidate-retained.bin"
    files = packet["listener"]

    def prepare(client):
        if install:
            client.make_directory(root, parents=True)
            for path in (candidate, previous, retained):
                absent(client, path)
            # One-time listener bootstrap. The currently installed listener
            # uses the checksum-free UART service, and the canonical name is
            # protected until it returns to the CLI.
            client.upload(candidate, pinned(files["candidate"]), activate=True, fast=True)
        else:
            absent(client, retained)
            if client.stat_entry(previous)[0] != files["restore"]["bytes"]:
                raise RuntimeError("Preserved listener rollback is missing or has changed size")

    bench.listener("listener-preparation", LISTENER, prepare)
    paths = ((previous, candidate) if install else (retained, previous))
    rename_listener(bench, [(LIVE_LISTENER, paths[0]), (paths[1], LIVE_LISTENER)])
    selection = "candidate" if install else "restore"
    bench.kit["preserve"][LIVE_LISTENER] = files[selection]["sha256"]
    bench.cli()  # Read the replaced listener once as installation evidence.
    bench_process.record(bench.out / "listener-verified.json",
                         {"selection": selection, "sha256": files[selection]["sha256"]})


def resume_listener(bench, packet):
    # The failed phase already moved the production file away. The joined
    # inspection witnessed both the backup and staged candidate on the card.
    root = bench.install_dir
    previous = root + "/previous.bin"
    rename_listener(bench, [(root + "/next.bin", LIVE_LISTENER)])
    files = packet["listener"]
    bench.kit["preserve"][LIVE_LISTENER] = files["candidate"]["sha256"]

    def verify_backup(client):
        if sha256(client.download(previous)).hexdigest() != files["restore"]["sha256"]:
            raise RuntimeError("Preserved production listener differs from its pin")

    bench.listener("cli", LISTENER, verify_backup)
    bench_process.record(bench.out / "listener-verified.json",
                         {"selection": "candidate", "sha256": files["candidate"]["sha256"],
                          "restore_sha256": files["restore"]["sha256"]})


def compare_scratch(bench):
    both = bench.kit["schema"] == 3
    bench.start_listener("scratch", PARALLEL_LISTENER if both else LISTENER)
    for number, artifact in enumerate(bench.kit["fixture"]["inputs"]):
        path = sd_path(artifact["sd_path"], ("/test",))
        output = bench.out / f"scratch-{number:02d}.bin"
        client = StagedClient(bench.url, output.with_suffix(".json"), timeout=300 if both else 180)
        try:
            result = client.begin("get", path, destination=output, require_parallel=both)
            if output.read_bytes() != pinned(artifact["source"]):
                raise RuntimeError(f"Qualification scratch bytes differ: {path}")
            bench_process.record(output.with_suffix(".receipt.json"),
                                 {"target": path, "matched": True, "result": result})
        finally:
            client.close()
    bench.exit_staged_listener("scratch")


def prepare_emos(bench):
    payloads, results = bench.emos_install_inputs()

    def transfer(client):
        for parent in sorted({str(PurePosixPath(path).parent) for path in [*payloads, *results]}):
            client.make_directory(parent, parents=True)
        for path in [*payloads, *results]:
            absent(client, path)
        # Firmware bootstrap before the candidate carrier exists. These
        # inputs get independent ROM verification at the actual flash phases.
        for path, content in payloads.items():
            client.upload(path, content, activate=True, fast=True)

    bench.listener("emos-preparation", LISTENER, transfer)


@contextmanager
def capture_p4(bench):
    before = bench.keyboard()
    stop = Event()
    with (open_passive_serial(bench.c["ports"][1], timeout=0.2) as reader,
          (bench.out / "p4-passive.bin").open("xb") as transcript,
          ThreadPoolExecutor(max_workers=1) as executor):
        if bench.keyboard()["boot"] != before["boot"]:
            raise RuntimeError("Opening passive P4 capture changed input admission")

        def copy():
            while not stop.is_set():
                data = reader.read(1024)
                if data:
                    transcript.write(data)
                    transcript.flush()

        worker = executor.submit(copy)
        try:
            yield
        finally:
            stop.set()
            worker.result(timeout=3)


def perform(bench, packet, phase):
    if phase in ("stage", "verify-scratch", "run", "restore-listener"):
        bench.kit["preserve"][LIVE_LISTENER] = packet["listener"]["candidate"]["sha256"]
    both = bench.kit["schema"] == 3
    special = {"install-listener", "verify-scratch", "restore-listener", "prepare-emos", "resume-listener"}
    if phase not in special and not (both and phase == "stage"):
        bench.perform(phase)
        if phase == "run":
            if (bench.out / "result.txt").read_bytes() != b"Result file example\n":
                raise RuntimeError("Worked example differs from the expected 20 bytes")
        return
    with Path(bench.config["operation_lock"]).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        bench.lock = lock
        bench.validate_ports()
        observe = packet.get("capture_p4_usb") and phase in {"stage", "verify-scratch"}
        with capture_p4(bench) if observe else nullcontext():
            if phase == "verify-scratch":
                compare_scratch(bench)
            elif phase == "prepare-emos":
                prepare_emos(bench)
            elif phase == "stage":
                bench.stage(include_emos=False)
            elif phase == "resume-listener":
                resume_listener(bench, packet)
            else:
                change_listener(bench, packet, install=phase == "install-listener")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--operator")
    parser.add_argument("--resume-listener", action="store_true",
                        help="Resume a witnessed first listener rename without replaying it")
    parser.add_argument("phase")
    args = parser.parse_args()
    raw = args.packet.read_bytes()
    if sha256(raw).hexdigest() != args.sha256:
        raise ValueError("Qualification packet differs from its pin")
    packet = json.loads(raw)
    validate(packet)
    phases = TWO_WAY_PHASES if packet["job"]["schema"] == 3 else PHASES
    if args.resume_listener:
        if packet["job"]["schema"] != 3:
            parser.error("Listener recovery requires the two-way packet")
        phases = {("resume-listener" if name == "install-listener" else name): seconds
                  for name, seconds in phases.items()}
    if args.phase == "preflight":
        print("\n".join(phases))
        return 0
    phase = args.phase.removeprefix("worker-")
    if phase not in phases or not (args.config and args.out and args.operator):
        parser.error("Provide a physical phase, local config, evidence directory and slot operator")

    def argv(name):
        recovery = ["--resume-listener"] if (args.resume_listener and name in phases
                    and list(phases).index(name) >= list(phases).index("resume-listener")) else []
        return [sys.executable, str(Path(__file__).resolve()), "--packet", str(args.packet),
                "--sha256", args.sha256, "--config", str(args.config), "--out", str(args.out),
                "--operator", args.operator, *recovery, f"worker-{name}"]

    folder = args.out / phase
    if args.phase != phase:
        if bench_process.read(folder / "supervisor-started.json")["argv"] != argv(phase):
            raise RuntimeError("Worker is missing its supervisor binding")
        for previous in list(phases)[:list(phases).index(phase)]:
            bench_process.verify_child(args.out / previous, argv(previous))
        if phase == "resume-listener":
            bench_process.verify_child(args.out / "install-listener", argv("install-listener"),
                                       expected_returncode=1)
            bench_process.verify_child(args.out / "inspect-listener",
                                       [sys.executable, str(args.out / "inspect-listener.py"), "worker"])
            paths = bench_process.read(args.out / "inspect-listener/listings.json")
            root = "/extender/install/" + packet["job"]["namespace"]
            if (f"Directory: {root}" not in paths[root] or "Directory: /emos" not in paths["/emos"]
                    or "sdserve.bin" in " ".join(paths["/emos"]).lower().split()
                    or not {"next.bin", "previous.bin"} <= set(" ".join(paths[root]).lower().split())):
                raise RuntimeError("Inspection does not establish a completed first rename")
        perform(Bench(bench_process.read(args.config), packet["job"], folder), packet, phase)
        return 0
    return bench_process.run(argv(phase), folder, phases[phase], owner=args.operator,
                             lease=f"chat:{args.operator}", phase=phase,
                             next_action="Keep the slot and follow the bench stop procedure.")


if __name__ == "__main__":
    sys.exit(main())
