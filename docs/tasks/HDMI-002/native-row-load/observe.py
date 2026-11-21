"""Observe one explicitly commissioned Olimex window. Requests are read-only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from threading import Event
from urllib.request import urlopen


def utc():
    return datetime.now(timezone.utc).isoformat()


def record(file, **values):
    file.write(json.dumps(dict(utc=utc(), host_ns=time.monotonic_ns(), **values)) + "\n")
    file.flush()


def fetch(base, path, output):
    begin = time.monotonic_ns()
    try:
        with urlopen(base + path, timeout=2) as response:
            raw = response.read(16385)
            if len(raw) > 16384:
                raise ValueError("Oversize metadata")
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError("Expected metadata object")
        record(output, path=path, start_ns=begin, body_bytes=len(raw), data=value)
        return value
    except (OSError, ValueError) as error:
        record(output, path=path, start_ns=begin, error=str(error))
        return {}


@contextmanager
def capture_serial(directory, port, open_passive_serial):
    # Keep reading even when an HTTP call times out. Otherwise the kernel can
    # overrun its serial input buffer during the failure we most need to see.
    stopped = Event()
    with open_passive_serial(port, timeout=0.1) as reader, \
         (directory / "p4-serial.bin").open("xb") as raw, \
         (directory / "p4-serial-index.jsonl").open("x") as index:
        def drain():
            while True:
                closing = stopped.is_set()
                data = reader.read(max(1, min(8192, reader.in_waiting)))
                if data:
                    offset = raw.tell()
                    raw.write(data)
                    raw.flush()
                    record(index, serial_offset=offset, serial_length=len(data))
                if closing:
                    break
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(drain)
            try:
                yield future
            finally:
                stopped.set()
                future.result()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--arm", choices=("legacy", "full-frame", "native"), required=True)
    parser.add_argument("--seconds", type=int, required=True)
    parser.add_argument("--hz", type=int, choices=(0, 1, 4), required=True)
    parser.add_argument("--output", type=Path, required=True, help="Fresh window directory")
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error("Use a positive window duration")
    binding = json.loads(args.binding.read_bytes())
    config_bytes = Path(binding["config"]["path"]).read_bytes()
    if sha256(config_bytes).hexdigest() != binding["config"]["sha256"]:
        parser.error("Configuration differs from packet")
    config = json.loads(config_bytes)
    revision = subprocess.check_output(["git", "-C", binding["runner_checkout"],
                                        "rev-parse", "HEAD"], text=True).strip()
    if revision != binding["runner_revision"]:
        parser.error("Runner checkout differs from packet")
    job = binding["arms"][args.arm]["job"]
    if sha256(Path(job["path"]).read_bytes()).hexdigest() != job["sha256"]:
        parser.error("Job differs from packet")
    sys.path.insert(0, str(Path(binding["runner_checkout"]) / "scripts"))
    from passive_serial import open_passive_serial

    args.output.mkdir(parents=True, exist_ok=False)
    base = config["url"].rstrip("/")
    other = "/display/scanout" if args.arm == "native" else "/display/status"
    # The same two GETs per period are sent on all arms. Legacy's P4 status
    # measures service traffic only. MOS drives the mainboard display there.
    with (args.output / "observations.jsonl").open("x") as log, \
         capture_serial(args.output, config["p4"]["port"], open_passive_serial) as serial:
        start = time.monotonic()
        end = start + args.seconds
        record(log, event="start", arm=args.arm, hz=args.hz, seconds=args.seconds,
               job_sha256=job["sha256"])
        previous_fault = None
        next_sample = start
        while True:
            now = time.monotonic()
            if now >= next_sample or now >= end:
                fetch(base, "/display/status", log)
                observed = fetch(base, other, log)
                if args.arm == "native":
                    # Previous epochs can first report a fault after the next
                    # mode starts. Bracket every window with the saved register.
                    key = (observed.get("epoch"), observed.get("fault"))
                    if key != previous_fault or now >= end:
                        fetch(base, "/display/scanout?last_fault=1", log)
                        if observed.get("fault"):
                            print(f"P4 scanout fault {key[1]}, epoch {key[0]}. Preserve the trial.",
                                  file=sys.stderr, flush=True)
                        previous_fault = key
                next_sample = time.monotonic() + 1 / args.hz if args.hz else end
            if serial.done():
                serial.result()  # propagate a disconnected serial reader
            if now >= end:
                break
            time.sleep(min(0.02, max(0, end - time.monotonic())))
        record(log, event="end", elapsed_s=time.monotonic() - start)


if __name__ == "__main__":
    main()
