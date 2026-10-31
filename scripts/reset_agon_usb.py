#!/usr/bin/env python3
"""One explicit Agon reset through a commissioned USB RTS/Q4 actuator.

This uses the Agon Light2 shared eZ80 RESET / mainboard VDP EN circuit, not
P4 USB. Configuration owns the stable adapter endpoint and exact udev identity.
Joined DTR/RTS release is required: separate transitions can pulse this circuit.
There is no command injection, firmware write, retry or application replay.
"""
import argparse
import fcntl
import json
from pathlib import Path
import signal
import struct
import subprocess
import termios
import time

from passive_serial import open_passive_serial
from reset_agon import status, wait_boot


MASK = termios.TIOCM_DTR | termios.TIOCM_RTS


def identity(config):
    port = Path(config["stable_port"])
    if port.parent != Path("/dev/serial/by-id"):
        raise ValueError("reset requires a stable /dev/serial/by-id endpoint")
    resolved = port.resolve(strict=True)
    properties = dict(line.split("=", 1) for line in subprocess.check_output(
        ["udevadm", "info", "--query=property", "--name", str(resolved)],
        text=True).splitlines() if "=" in line)
    expected = config["udev"]
    if (not isinstance(expected, dict) or
            not {"ID_VENDOR_ID", "ID_MODEL_ID", "ID_PATH"} <= expected.keys() or
            any(not value or properties.get(key) != value for key, value in expected.items())):
        raise ValueError("Agon reset adapter identity differs; port was not opened")
    return port


def pulse(config):
    port = identity(config)

    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)

    # A bridge timeout sends TERM. Release in finally on that path as well as
    # ordinary failure; SIGKILL/power failure cannot provide software cleanup.
    signals = (signal.SIGTERM, signal.SIGHUP)
    previous = {item: signal.signal(item, interrupted) for item in signals}
    try:
        with open_passive_serial(port, timeout=0.2) as handle:
            def controls():
                return struct.unpack("I", fcntl.ioctl(
                    handle.fd, termios.TIOCMGET, struct.pack("I", 0)))[0] & MASK

            try:
                if controls() != 0:
                    raise RuntimeError("Agon reset controls are not initially neutral")
                fcntl.ioctl(handle.fd, termios.TIOCMBIS,
                            struct.pack("I", termios.TIOCM_RTS))
                if controls() != termios.TIOCM_RTS:
                    raise RuntimeError("Agon reset assertion was not observed")
                time.sleep(0.1)
            finally:
                fcntl.ioctl(handle.fd, termios.TIOCMBIC, struct.pack("I", MASK))
                if controls() != 0:
                    raise RuntimeError("Agon USB reset controls failed to release")
    finally:
        for item, handler in previous.items():
            signal.signal(item, handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--verify-url")
    parser.add_argument("--verify-timeout", type=float, default=60)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    before = status(args.verify_url) if args.verify_url else None
    pulse(config)
    if before is None:
        print("PULSE-ONLY COMPLETE — USB RTS released; caller owns boot/CLI verification.")
    else:
        after = wait_boot(args.verify_url, before["boot"], args.verify_timeout)
        print(f"AGON RESET VERIFIED — fresh admitted boot {after['boot']}; CLI execution needs a separate check.")


if __name__ == "__main__":
    main()
