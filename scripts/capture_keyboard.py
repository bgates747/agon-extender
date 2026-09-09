#!/usr/bin/env python3
"""Capture the PORT-005 RTS/CTS keyboard stages without changing board state.

Retains the accepted forward capture mechanics; the frozen historical forward
procedure stays under its original task. This script owns the controlled keyboard verdicts.

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

PROCEDURE_ID = "uart-keyboard-probe-r01"
# Author-approved identity; physical capture still selects a frozen build.


def records(data):
    text = re.sub(rb"\x1b\[[0-9;]*m", b"", data)
    return re.findall(rb"KEYBOARD [^\r\n]*", text)


def receiver_ready(data, build_id):
    seen = records(data)
    wanted = b"KEYBOARD WAIT cts=1 build=" + build_id.encode()
    header = b"KEYBOARD SENDER " + build_id.encode() + b" (candidate)"
    if any(line not in (wanted, header) for line in seen):
        raise RuntimeError("sender is not the selected idle peer; do not reset Agon")
    return wanted in seen


def verdict(data, build_id):
    seen = records(data)
    suffix = b" build=" + build_id.encode()
    stages = []
    headers = 0
    for line in seen:
        if line.startswith(b"KEYBOARD SENDER ") and not line.startswith(b"KEYBOARD SENDER PASS "):
            headers += 1
            if stages or headers > 1 or line != b"KEYBOARD SENDER " + build_id.encode() + b" (candidate)":
                return False, "P4 restarted or reported a different sender identity"
        elif line in (b"KEYBOARD WAIT cts=0" + suffix, b"KEYBOARD WAIT cts=1" + suffix):
            continue
        else:
            stages.append(line)
    polls = [line for line in stages if line.startswith(b"KEYBOARD POLL ")]
    if len(polls) != 1:
        return False, "missing or duplicate readiness poll"
    match = re.fullmatch(rb"KEYBOARD POLL token=(\d+)" + re.escape(suffix), polls[0])
    if match is None or not 0 <= int(match[1]) <= 255:
        return False, "invalid poll token or build identity"
    expected = [b"KEYBOARD START cycle=1" + suffix, b"KEYBOARD LOCALE 1" + suffix, polls[0]]
    expected += [b"KEYBOARD EVENT " + str(i).encode() + b" SENT" + suffix for i in range(1,13)]
    expected += [b"KEYBOARD SENDER PASS events=12 key_bytes=72" + suffix]
    if stages != expected:
        return False, "missing, malformed, duplicate or out-of-order keyboard stages"
    return True, "P4 sent twelve key events; confirm Agon PASS, prompt and waveform separately"


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
        p.error("keyboard procedure identity awaits Author approval")
    if not re.fullmatch(r"uart-keyboard-probe-r01-b\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}Z", args.build_id):
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
    folder = args.output_parent / ("PORT-005-" + now.strftime("%Y-%m-%d-%H-%M-%SZ"))
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
        passed, reason = False, "less than five seconds observed after the final keyboard event"
    record = {"run_id": folder.name, "started_at": now.isoformat(),
              "ended_at": datetime.now(timezone.utc).isoformat(), "build_id": args.build_id,
              "device": str(device), "usb_serial": props.get("ID_SERIAL_SHORT"),
              "maximum_capture_seconds": args.seconds,
              "analyzer_finished": args.analyzer_complete.exists(), "p4_keyboard_pass": passed, "reason": reason,
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
