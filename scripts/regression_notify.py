#!/usr/bin/env python3
"""Use the accepted Legacy spoken cue and leave a regression verdict visible."""

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
        return json.load(response)


def send(url: str, journal: Path, events: list[tuple[int, int]]) -> None:
    client = KeyboardClient(url, journal)
    try:
        observed = client.status()
        client.open(observed)
        client.send(events)
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
        client = SdClient(url, journal)
        try:
            observed = client.status()
            last = observed
            if observed.get("online"):
                client.connect()
                client.rpc(11)
                return
        except Exception as error:
            last = repr(error)
        finally:
            client.lock.close()
        time.sleep(0.2)
    raise TimeoutError(f"attention listener did not become ready for exit: {last}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--suite-output", required=True, type=Path)
    parser.add_argument("--expected", required=True, choices=("success", "failure"))
    args = parser.parse_args()
    args.job.mkdir(parents=True, exist_ok=True)
    receipt = args.job / "notification.json"
    journal = args.job / "notification-keyboard.json"
    started = time.monotonic()
    label = "AUDIT-010 REGRESSION INFRASTRUCTURE FAILURE"
    try:
        summary_path = args.suite_output / "summary.json"
        summary = json.loads(summary_path.read_text()) if summary_path.is_file() else {}
        suite_status = summary.get("status", "missing-summary")
        if args.expected == "success" and suite_status == "success":
            label = "AUDIT-010 REGRESSION PASS"
        elif suite_status == "test-failure":
            label = "AUDIT-010 REGRESSION TEST FAILURE"
        elif suite_status == "timeout":
            label = "AUDIT-010 REGRESSION TIMEOUT"
        elif suite_status == "infrastructure-failure":
            label = "AUDIT-010 REGRESSION INFRASTRUCTURE FAILURE"
        else:
            label = "AUDIT-010 REGRESSION FAILURE"

        # Escape is bounded and harmless at an ordinary prompt. It gives a
        # failed foreground fixture one chance to return; this hook never resets.
        if args.expected == "failure":
            escape = key_usage("escape")
            send(args.url, journal, [(escape, 1), (escape, 0)])
        type_line(args.url, journal, "EMOS LEGACY")
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
