#!/usr/bin/env python3
"""Capture the PORT-014 RTS/CTS visible text stages without changing board state.

Retains the accepted forward capture mechanics; the frozen historical forward
procedure stays under its original task. This script owns visible text verdicts.

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

PROCEDURE_ID = "uart-visible-text-probe-r01"
# Author-approved identity; physical capture still selects a frozen build.


def receiver_ready(data, build_id):
    text = re.sub(rb"\x1b\[[0-9;]*m", b"", data)
    if b"VISIBLE TEXT FAIL" in text or b"VISIBLE TEXT EVENT" in text:
        raise RuntimeError("visible text receiver failed before the reset cue")
    if b"VISIBLE TEXT START" in text or b"VISIBLE TEXT PASS" in text:
        raise RuntimeError("visible text exchange already started before reset cue")
    waits = re.findall(rb"VISIBLE TEXT WAIT received=(\d+) cts=(\d+) build=(\S+)\r?\n", text)
    for received, cts, build in waits:
        if received != b"0" or cts != b"1" or build.decode() != build_id:
            raise RuntimeError("receiver is not the selected empty, stopped-CTS peer")
    return bool(waits)


def verdict(data, build_id):
    text = re.sub(rb"\x1b\[[0-9;]*m", b"", data)
    if b"VISIBLE TEXT FAIL" in text or b"VISIBLE TEXT EVENT" in text:
        return False, "P4 reported a visible text test failure or UART error"
    if text.count(b"VISIBLE TEXT RECEIVER ") > 1:
        return False, "P4 restarted during capture"
    expected = [b"VISIBLE TEXT START", b"VISIBLE TEXT REQUEST hex=0C1F0202454D4F5320544F204544503A205541525420544558540D0A1700CA170080A6",
                b"VISIBLE TEXT PARSER reply=8001A6", b"VISIBLE TEXT SENT count=3"]
    prefixes = [b"VISIBLE TEXT START", b"VISIBLE TEXT REQUEST", b"VISIBLE TEXT PARSER", b"VISIBLE TEXT SENT"]
    last = -1
    for prefix, record in zip(prefixes, expected):
        full = record + b" build=" + build_id.encode()
        matches = list(re.finditer(re.escape(full) + rb"\r?\n", text))
        if len(matches) != 1 or text.count(prefix) != 1 or matches[0].start() <= last:
            return False, "missing, malformed, duplicate or out-of-order visible text stage"
        last = matches[0].start()
    passes = list(re.finditer(rb"VISIBLE TEXT PASS received=35 reply=3 build=" +
                             re.escape(build_id.encode()) + rb"\r?\n", text))
    if not passes or text.count(b"VISIBLE TEXT PASS") != len(passes) or passes[0].start() <= last:
        return False, "no exact final P4 visible text PASS after the required stages"
    if b"VISIBLE TEXT RECEIVER " in text[passes[0].start():]:
        return False, "P4 restarted after PASS"
    return True, "P4 visible text stages PASS; confirm Agon VDP TEXT PASS/prompt, browser text and exact waveform separately"


def capture_complete(first_pass_at, now, analyzer_finished):
    return first_pass_at is not None and now-first_pass_at >= 5 and analyzer_finished


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--port", type=Path, required=True)
    p.add_argument("--expected-serial", required=True)
    p.add_argument("--build-id", required=True)
    p.add_argument("--output-parent", type=Path, required=True)
    p.add_argument("--seconds", type=int, default=90)
    p.add_argument("--analyzer-complete", type=Path, required=True,
                   help="new-run marker written only when the combined analyzer process finishes")
    p.add_argument("--prompt-on-ready", action="store_true",
                   help="hide raw diagnostics; cue Agon reset only after a matching empty WAIT")
    args = p.parse_args()
    if PROCEDURE_ID == "UNVERSIONED-DO-NOT-DEPLOY":
        p.error("visible text procedure identity awaits Author approval")
    if not re.fullmatch(r"uart-visible-text-probe-r01-b\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}Z", args.build_id):
        p.error("select the approved frozen build; unversioned captures are not accepted")
    if not 10 <= args.seconds <= 180: p.error("capture duration must be 10–180 seconds")
    if args.port.parent != Path("/dev/serial/by-id"): p.error("use the verified stable by-id path")
    if args.analyzer_complete.exists(): p.error("acquisition marker must not preexist")
    device = args.port.resolve(strict=True)
    info = subprocess.check_output(["udevadm", "info", "--query=property", "--name", str(device)], text=True)
    props = dict(line.split("=", 1) for line in info.splitlines() if "=" in line)
    normalize = lambda s: s.replace(":", "").replace("-", "").lower()
    if normalize(props.get("ID_SERIAL_SHORT", "")) != normalize(args.expected_serial):
        p.error("USB serial identity mismatch")
    now = datetime.now(timezone.utc)
    folder = args.output_parent / ("PORT-014-" + now.strftime("%Y-%m-%d-%H-%M-%SZ"))
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
                          "Capturing through acquisition completion and five clean seconds after PASS.\n", flush=True)
                if first_pass_at is None and verdict(bytes(collected), args.build_id)[0]:
                    first_pass_at = time.monotonic()
                if capture_complete(first_pass_at, time.monotonic(), args.analyzer_complete.exists()):
                    break
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
    elif passed and not args.analyzer_complete.exists():
        passed, reason = False, "analyzer did not finish before the overall deadline"
    elif passed and observed_after_pass < 5:
        passed, reason = False, "less than five seconds observed after first PASS"
    record = {"run_id": folder.name, "started_at": now.isoformat(),
              "ended_at": datetime.now(timezone.utc).isoformat(), "build_id": args.build_id,
              "device": str(device), "usb_serial": props.get("ID_SERIAL_SHORT"),
              "maximum_capture_seconds": args.seconds,
              "analyzer_finished": args.analyzer_complete.exists(), "p4_text_pass": passed, "reason": reason,
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
