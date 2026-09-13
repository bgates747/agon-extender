#!/usr/bin/env python3
"""Observe initial CLI handover, replace hello, and resume the finite boot batch.

Requires the already deployed bundle and one initial Escape/EXEC by the Author.
No keyboard injection, reset, firmware flash or remote shell. The only launch
trigger is the accepted SD EXIT operation returning to the existing MOS batch.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from sdcard import Client


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--handover-timeout", type=float, default=900)
    args = parser.parse_args()
    bundle, output = args.bundle.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    result = {"started_at": datetime.now(timezone.utc).isoformat(), "outcome": "in progress",
              "human_visual_audio_confirmation": "pending", "events": []}
    client = Client(args.url, output / "initial-state.json")

    def checkpoint(phase):
        result["phase"] = phase
        (output / "progress.json").write_text(json.dumps(result, indent=2) + "\n")
        print(phase, flush=True)

    def wait_new_service(previous, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status = client.status()
            if status["online"] and status["boot"] != previous:
                return status
            time.sleep(1)
        raise TimeoutError("No new service incarnation within the handover window")

    try:
        initial = client.status()
        if not initial["online"] or initial["pending"]:
            raise RuntimeError("Service must be online and idle before the handover")
        result["initial_status"] = initial
        checkpoint("Ready for Escape, then EXEC /extender/hello-start.txt at the physical MOS prompt")
        status = wait_new_service(initial["boot"], args.handover_timeout)
        client.lock.close()
        client = Client(args.url, output / "first-state.json")
        client.connect()
        first = client.download("/extender/hello-seen.txt")
        if first != b"stage=1\r\naudio_commands=pass\r\n":
            raise RuntimeError("Unexpected first execution/audio receipt: " + repr(first))
        if client.download("/autoexec.txt") != (bundle / "hello-boot.txt").read_bytes():
            raise RuntimeError("Installed startup differs from the prepared batch")
        if client.download("/extender/before-hello.txt") != (bundle / "autoexec-original.txt").read_bytes():
            raise RuntimeError("Startup rollback differs")
        if client.download("/extender/hello.bin") != (bundle / "build-1/hello.bin").read_bytes():
            raise RuntimeError("First executable differs")
        result["events"].append({"stage": 1, "receipt": first.decode(), "status": status})
        checkpoint("First execution and audio commands verified; replacing the executable over Ethernet")
        second = (bundle / "build-2/hello.bin").read_bytes()
        client.upload("/extender/hello.bin", second, True)
        if client.download("/extender/hello.bin.p17bak") != (bundle / "build-1/hello.bin").read_bytes():
            raise RuntimeError("Previous executable backup differs")
        result["second_sha256"] = hashlib.sha256(second).hexdigest()
        checkpoint("Second executable activated and read back; EXIT now resumes the boot batch")
        previous = client.state["boot"]
        client.rpc(11)
        status = wait_new_service(previous, 180)
        client.lock.close()
        client = Client(args.url, output / "second-state.json")
        client.connect()
        final = client.download("/extender/hello-seen.txt")
        if final != b"stage=2\r\naudio_commands=pass\r\n":
            raise RuntimeError("Unexpected second execution/audio receipt: " + repr(final))
        if client.download("/extender/hello.bin") != second:
            raise RuntimeError("Final executable readback differs")
        result["events"].append({"stage": 2, "receipt": final.decode(), "status": status})
        result["outcome"] = "pass"
        checkpoint("Both hardware execution receipts pass; service online, original startup and first binary retained")
    except Exception as error:
        result["outcome"] = "incomplete"
        result["error"] = repr(error)
        checkpoint("Stopped with files and client state preserved")
        raise
    finally:
        client.lock.close()
        result["ended_at"] = datetime.now(timezone.utc).isoformat()
        (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
