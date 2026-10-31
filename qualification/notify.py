#!/usr/bin/env python3
"""Use the accepted Legacy spoken cue and leave a qualification verdict visible."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from keyboard import Client as KeyboardClient, key_usage, text_events  # noqa: E402
from sdcard import Client as SdClient  # noqa: E402
EXPECTED_BOOT = None


def save(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def status(url: str) -> dict:
    with urlopen(url.rstrip("/") + "/keyboard/status", timeout=5) as response:
        value = json.load(response)
    if EXPECTED_BOOT is not None and value.get("boot") != EXPECTED_BOOT:
        raise RuntimeError("Agon reset before notification; no input authorized in the new epoch")
    return value


def send(url: str, journal: Path, events: list[tuple[int, int]]) -> None:
    client = KeyboardClient(url, journal)
    try:
        observed = client.status()
        if EXPECTED_BOOT is not None and observed.get("boot") != EXPECTED_BOOT:
            raise RuntimeError("Agon reset before notification event dispatch")
        client.open(observed)
        # Same conservative CLI pacing as hardware_validation.type_line; a
        # P4 event-drain receipt does not prove MOS consumed a whole text line.
        for offset in range(0, len(events), 2):
            client.send(events[offset:offset + 2])
        client.cancel()
    finally:
        client.lock.close()


def type_line(url: str, journal: Path, value: str) -> None:
    observed = status(url)
    send(url, journal, text_events(value + "\n", observed["locale"], observed["caps"]))


def exit_attention_service(url: str, journal: Path, timeout: float = 15) -> None:
    deadline = time.monotonic() + timeout
    last: object = "no response"
    while time.monotonic() < deadline:
        if EXPECTED_BOOT is not None:
            status(url)
        client = SdClient(url, journal)
        try:
            observed = client.status()
            last = observed
            if observed.get("online"):
                client.connect(require_fast=True)
                client.rpc(11)
                return
        except Exception as error:
            last = repr(error)
        finally:
            client.lock.close()
        time.sleep(0.2)
    raise TimeoutError(f"attention listener did not become ready for exit: {last}")


def main() -> int:
    global EXPECTED_BOOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--suite-output", required=True, type=Path)
    parser.add_argument("--expected", required=True, choices=("success", "failure"))
    parser.add_argument("--expected-boot", type=int,
                        help="block all input if the qualification epoch changed")
    args = parser.parse_args()
    EXPECTED_BOOT = args.expected_boot
    args.job.mkdir(parents=True, exist_ok=True)
    receipt = args.job / "notification.json"
    journal = args.job / "notification-keyboard.json"
    started = time.monotonic()
    label = "Firmware qualification infrastructure failure"
    try:
        summary_path = args.suite_output / "summary.json"
        summary = json.loads(summary_path.read_text()) if summary_path.is_file() else {}
        suite_status = summary.get("status", "missing-summary")
        if args.expected == "success" and suite_status == "success":
            label = ("Diagnostic checks passed; full suite pending" if summary.get("full_suite") is False else
                     "Qualification automated checks passed; visual review pending")
        elif suite_status == "test-failure":
            label = "Firmware qualification test failure"
        elif suite_status == "timeout":
            label = "Firmware qualification timeout"
        elif suite_status == "infrastructure-failure":
            label = "Firmware qualification infrastructure failure"
        else:
            label = "Firmware qualification failure"

        # The caller must prove a safe CLI before notification. Do not try to
        # escape an unknown foreground or recover a workload as an alert hook.
        type_line(args.url, journal, "EMOS LEGACY --keep-display")
        type_line(args.url, journal, "EXEC /extender/attention.txt")
        # The retained player has no completion endpoint. Preserve its proven
        # bounded playback allowance, then restore the durable verdict last.
        time.sleep(15)
        exit_attention_service(args.url, args.job / "notification-sd.json")
        type_line(args.url, journal, "ECHO " + label)
        final = status(args.url)
        if not final.get("ready") or not final.get("physical_neutral") or final.get("pending"):
            raise RuntimeError("terminal keyboard receipt is not ready and neutral")
        save(receipt, {"status": "success", "label": label,
                       "suite_status": suite_status,
                       "duration_seconds": time.monotonic() - started,
                       "attention_listener_exited": True,
                       "proof": "accepted keyboard event stream acknowledged; human hearing and Legacy pixels remain operator observations",
                       "keyboard": final})
        return 0
    except BaseException as error:
        save(receipt, {"status": "failure", "label": label,
                       "duration_seconds": time.monotonic() - started,
                       "error": repr(error)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
