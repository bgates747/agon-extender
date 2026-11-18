#!/usr/bin/env python3
"""PORT-008 candidate qualification. Each physical phase needs an open slot."""

import argparse
import fcntl
from hashlib import sha256
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import bench_process
from olimex_bench import Bench, LISTENER, pinned, preflight, sd_path
from olimex_cli import Observer, command_result
from passive_serial import open_passive_serial
from sdcard import RemoteError
from sdcard_staged import Client as StagedClient


LIVE_LISTENER = "/emos/sdserve.bin"
PHASES = {"install-p4": 650, "install-listener": 300, "stage": 300,
          "verify-scratch": 480, "run": 240, "restore-listener": 240,
          "restore-p4": 650, "handback": 90}


def validate(packet):
    kit = packet["job"]
    preflight(kit)
    if kit["schema"] != 2 or set(kit["firmware"]) != {"p4"}:
        raise ValueError("Qualification requires a PARLIO job and only the P4 firmware change")
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
            for number, command in enumerate(commands, start=1):
                observer.exchange(f"rename-{number}", command,
                                  lambda data: command_result(data, command, prompt), 15)
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
    rename_listener(bench, [f"RENAME {LIVE_LISTENER} {paths[0]}",
                            f"RENAME {paths[1]} {LIVE_LISTENER}"])
    selection = "candidate" if install else "restore"
    bench.kit["preserve"][LIVE_LISTENER] = files[selection]["sha256"]
    bench.cli()  # Read the replaced listener once as installation evidence.
    bench_process.record(bench.out / "listener-verified.json",
                         {"selection": selection, "sha256": files[selection]["sha256"]})


def compare_scratch(bench):
    bench.start_listener("scratch", LISTENER)
    for number, artifact in enumerate(bench.kit["fixture"]["inputs"]):
        path = sd_path(artifact["sd_path"], ("/test",))
        output = bench.out / f"scratch-{number:02d}.bin"
        client = StagedClient(bench.url, output.with_suffix(".json"), timeout=180)
        try:
            result = client.begin("get", path, destination=output)
            if output.read_bytes() != pinned(artifact["source"]):
                raise RuntimeError(f"Qualification scratch bytes differ: {path}")
            bench_process.record(output.with_suffix(".receipt.json"),
                                 {"target": path, "matched": True, "result": result})
        finally:
            client.close()
    bench.exit_staged_listener("scratch")


def perform(bench, packet, phase):
    if phase in ("stage", "verify-scratch", "run", "restore-listener"):
        bench.kit["preserve"][LIVE_LISTENER] = packet["listener"]["candidate"]["sha256"]
    if phase not in ("install-listener", "verify-scratch", "restore-listener"):
        bench.perform(phase)
        if phase == "run":
            if (bench.out / "result.txt").read_bytes() != b"Result file example\n":
                raise RuntimeError("Worked example differs from the expected 20 bytes")
        return
    with Path(bench.config["operation_lock"]).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        bench.lock = lock
        bench.validate_ports()
        if phase == "verify-scratch":
            compare_scratch(bench)
        else:
            change_listener(bench, packet, install=phase == "install-listener")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--operator")
    parser.add_argument("phase")
    args = parser.parse_args()
    raw = args.packet.read_bytes()
    if sha256(raw).hexdigest() != args.sha256:
        raise ValueError("Qualification packet differs from its pin")
    packet = json.loads(raw)
    validate(packet)
    if args.phase == "preflight":
        print("\n".join(PHASES))
        return 0
    phase = args.phase.removeprefix("worker-")
    if phase not in PHASES or not (args.config and args.out and args.operator):
        parser.error("Provide a physical phase, local config, evidence directory and slot operator")

    def argv(name):
        return [sys.executable, str(Path(__file__).resolve()), "--packet", str(args.packet),
                "--sha256", args.sha256, "--config", str(args.config), "--out", str(args.out),
                "--operator", args.operator, f"worker-{name}"]

    folder = args.out / phase
    if args.phase != phase:
        if bench_process.read(folder / "supervisor-started.json")["argv"] != argv(phase):
            raise RuntimeError("Worker is missing its supervisor binding")
        for previous in list(PHASES)[:list(PHASES).index(phase)]:
            bench_process.verify_child(args.out / previous, argv(previous))
        perform(Bench(bench_process.read(args.config), packet["job"], folder), packet, phase)
        return 0
    return bench_process.run(argv(phase), folder, PHASES[phase], owner=args.operator,
                             lease=f"chat:{args.operator}", phase=phase,
                             next_action="Keep the slot and follow the bench stop procedure.")


if __name__ == "__main__":
    sys.exit(main())
