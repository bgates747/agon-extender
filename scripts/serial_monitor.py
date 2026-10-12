#!/usr/bin/env python3
"""Bounded passive USB serial capture using joined DTR/RTS updates.

The caller owns bench/device selection and functional qualification. This tool
never resets, flashes, injects keys, writes serial bytes, reconnects or retries.
"""
import argparse
import signal
import time
from pathlib import Path

from passive_serial import open_passive_serial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=30)
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--ready-file", type=Path)
    parser.add_argument("--stop-file", type=Path)
    args = parser.parse_args()
    if not 0 < args.seconds <= 7200:
        parser.error("--seconds must be greater than zero and at most 7200")
    if args.port.parent != Path("/dev/serial/by-id"):
        parser.error("select the verified stable /dev/serial/by-id endpoint")
    args.port.resolve(strict=True)
    for marker in (args.ready_file, args.stop_file):
        if marker and marker.exists():
            parser.error(f"marker already exists: {marker}")
    stopped = False

    def stop(*_):
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    with args.output.open("xb") as output:
        with open_passive_serial(args.port, baudrate=args.baud) as handle:
            if args.ready_file:
                args.ready_file.touch(exist_ok=False)
            print("Passive capture opened; DTR/RTS updated together.", flush=True)
            deadline = time.monotonic() + args.seconds
            while not stopped and time.monotonic() < deadline:
                if args.stop_file and args.stop_file.exists():
                    break
                data = handle.read(8192)
                if data:
                    output.write(data)
                    output.flush()
    print("Passive capture closed.", flush=True)


if __name__ == "__main__":
    main()
