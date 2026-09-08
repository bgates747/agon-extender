#!/usr/bin/env python3
"""Capture the PORT-011 RTS/CTS flow stages without changing board state.

Retains the accepted forward capture mechanics; the frozen historical forward
procedure stays under its original task. This script owns flow-control verdicts.

Use the bench's existing esptool virtual environment (pyserial included).
Device/account values are command-line inputs from HARDWARE.local.md, not
tracked defaults. Capture output contains private device metadata; keep local.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

PROCEDURE_ID = "uart-flow-probe-r01"
# Author-approved identity; physical capture still selects a frozen build.


def receiver_ready(data, build_id):
    text = re.sub(rb"\x1b\[[0-9;]*m", b"", data)
    if b"UART FLOW FAIL" in text or b"UART FLOW EVENT" in text:
        raise RuntimeError("flow receiver failed before the reset cue")
    if b"UART FLOW FORWARD RELEASE" in text or b"UART FLOW PASS" in text:
        raise RuntimeError("flow exchange already started before reset cue")
    waits = re.findall(rb"UART FLOW WAIT received=(\d+) cts=(\d+) build=(\S+)\r?\n", text)
    for received, cts, build in waits:
        if received != b"0" or cts != b"1" or build.decode() != build_id:
            raise RuntimeError("receiver is not the selected empty, stopped-CTS peer")
    return bool(waits)


def verdict(data, build_id):
    text = re.sub(rb"\x1b\[[0-9;]*m", b"", data)
    if b"UART FLOW FAIL" in text or b"UART FLOW EVENT" in text:
        return False, "P4 reported a flow-test failure or UART error"
    if text.count(b"UART FLOW RECEIVER ") > 1:
        return False, "P4 restarted during capture"
    expected = [
        b"UART FLOW FORWARD RELEASE min_hold_ms=1000",
        b"UART FLOW REQUEST count=6 hex=464C4F570D0A",
        b"UART FLOW ACK QUEUED cts=stop",
        b"UART FLOW ACK SENT count=9 hex=464C4F5741434B0D0A",
        b"UART FLOW BLOCKED QUEUED cts=stop",
        b"UART FLOW BLOCKED TIMEOUT cancelled=1",
    ]
    prefixes = [b"UART FLOW FORWARD RELEASE", b"UART FLOW REQUEST", b"UART FLOW ACK QUEUED",
                b"UART FLOW ACK SENT", b"UART FLOW BLOCKED QUEUED", b"UART FLOW BLOCKED TIMEOUT"]
    last = -1
    for prefix, record in zip(prefixes, expected):
        full = record + b" build=" + build_id.encode()
        matches = list(re.finditer(re.escape(full) + rb"\r?\n", text))
        if len(matches) != 1 or text.count(prefix) != 1 or matches[0].start() <= last:
            return False, "missing, malformed, duplicate or out-of-order flow stage"
        last = matches[0].start()
    passes = list(re.finditer(rb"UART FLOW PASS received=6 ack=9 blocked=1 cancelled=1 build=" +
                             re.escape(build_id.encode()) + rb"\r?\n", text))
    if not passes or text.count(b"UART FLOW PASS") != len(passes) or passes[0].start() <= last:
        return False, "no exact final P4 flow PASS after the required stages"
    if b"UART FLOW RECEIVER " in text[passes[0].start():]:
        return False, "P4 restarted after PASS"
    return True, "P4 flow stages PASS; confirm Agon UART FLOW PASS/prompt and analyzer pause evidence separately"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=Path, required=True)
    p.add_argument("--expected-serial", required=True)
    p.add_argument("--build-id", required=True)
    p.add_argument("--output-parent", type=Path, required=True)
    p.add_argument("--seconds", type=int, default=90)
    p.add_argument("--prompt-on-ready", action="store_true",
                   help="hide raw diagnostics; cue Agon reset only after a matching empty WAIT")
    args = p.parse_args()
    if PROCEDURE_ID == "UNVERSIONED-DO-NOT-DEPLOY":
        p.error("flow-control procedure identity awaits Author approval")
    if not re.fullmatch(r"uart-flow-probe-r\d+-b\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}Z", args.build_id):
        p.error("select the approved frozen build; unversioned captures are not accepted")
    if not 10 <= args.seconds <= 180: p.error("capture duration must be 10–180 seconds")
    if args.port.parent != Path("/dev/serial/by-id"): p.error("use the verified stable by-id path")
    device = args.port.resolve(strict=True)
    info = subprocess.check_output(["udevadm", "info", "--query=property", "--name", str(device)], text=True)
    props = dict(line.split("=", 1) for line in info.splitlines() if "=" in line)
    normalize = lambda s: s.replace(":", "").replace("-", "").lower()
    if normalize(props.get("ID_SERIAL_SHORT", "")) != normalize(args.expected_serial):
        p.error("USB serial identity mismatch")
    now = datetime.now(timezone.utc)
    folder = args.output_parent / ("PORT-011-" + now.strftime("%Y-%m-%d-%H-%M-%SZ"))
    folder.mkdir(parents=True, exist_ok=False)
    import serial
    port = serial.Serial(port=None, baudrate=115200, timeout=1)
    port.dtr = False
    port.rts = False
    port.port = str(args.port)
    port.open()
    collected = bytearray()
    first_pass_at = None
    capture_error = None
    ready_at = None
    try:
        if args.port.resolve(strict=True) != device: raise RuntimeError("device changed during open")
        deadline = time.monotonic() + (15 if args.prompt_on_ready else args.seconds)
        with (folder / "serial.log").open("wb") as log:
            while time.monotonic() < deadline:
                data = port.read(4096)
                if not data: continue
                log.write(data); log.flush(); collected.extend(data)
                if not args.prompt_on_ready:
                    print(data.decode("utf-8", errors="replace"), end="", flush=True)
                if len(collected) > 2_000_000: raise RuntimeError("unexpected diagnostic volume")
                if args.prompt_on_ready and ready_at is None and receiver_ready(bytes(collected), args.build_id):
                    ready_at = time.monotonic()
                    deadline = ready_at + args.seconds
                    print("\n========================================\n"
                          "           RESET AGON NOW\n"
                          "  Press and release its reset button.\n"
                          "========================================\n"
                          f"Capturing for {args.seconds} seconds. Leave both boards powered.\n", flush=True)
                if first_pass_at is None and verdict(bytes(collected), args.build_id)[0]:
                    first_pass_at = time.monotonic()
    except Exception as exc:
        capture_error = str(exc)
    finally:
        port.close()
    passed, reason = verdict(bytes(collected), args.build_id)
    observed_after_pass = 0 if first_pass_at is None else time.monotonic() - first_pass_at
    if args.prompt_on_ready and ready_at is None and not capture_error:
        capture_error = "no matching empty receiver WAIT within 15 seconds; do not reset Agon"
    if capture_error:
        passed, reason = False, "capture interrupted: " + capture_error
    elif passed and observed_after_pass < 5:
        passed, reason = False, "less than five seconds observed after first PASS"
    record = {"run_id": folder.name, "started_at": now.isoformat(),
              "ended_at": datetime.now(timezone.utc).isoformat(), "build_id": args.build_id,
              "device": str(device), "usb_serial": props.get("ID_SERIAL_SHORT"),
              "capture_seconds": args.seconds, "p4_flow_pass": passed, "reason": reason,
              "seconds_observed_after_first_pass": observed_after_pass,
              "procedure_identity": PROCEDURE_ID,
              "operator_trigger": "powered Agon reset button" if args.prompt_on_ready else "externally coordinated",
              "reset_cue_issued": ready_at is not None,
              "serial_sha256": hashlib.sha256(collected).hexdigest()}
    (folder / "capture-result.json").write_text(json.dumps(record, indent=2) + "\n")
    print("\n" + ("PASS: " if passed else "FAIL: ") + reason + "\nEvidence: " + str(folder))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
