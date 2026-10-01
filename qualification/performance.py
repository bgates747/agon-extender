#!/usr/bin/env python3
"""Measure installed P4 application cadence and video delivery on real hardware.

The suite never flashes firmware.  It builds commit-pinned, finite fixtures,
stages them through the admitted EMOS SD service, and selects each video mode
from a one-shot /autoexec.txt before the fixture starts.  The original startup
file is restored byte-for-byte on success and whenever an active SD service
makes failure recovery safe.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import uuid


ROOT = Path(__file__).resolve().parents[1]
NURPLES_COMMIT = "0c741d5e2021927adfa440f45b8e04b950114889"
NURPLES_ASSETS = {
    "/test/nurples/game.agnb": 367168,
    "/test/nurples/ui.agnb": 246844,
    "/test/nurples/fonts/Lat38-VGA8_8x8.font": 2048,
}
MODES = {0: (640, 480), 8: (320, 240), 20: (512, 384)}
PERFORMANCE_UPDATES = 1800

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "qualification"))
sys.path.append(str(ROOT / "tests/performance"))
from analyze import summarize
from hardware_validation import (atomic_json, clean_snapshot, load_config,
                                 resolve_commit, sha256, type_line, utc_stamp,
                                 wait_sd_service)
from run import (close_retained_backup, read_json, require_extender_startup,
                 reset_and_wait, restore_startup,
                 try_restore_startup_from_active_service)
from video import VideoSession


def announce(message: str) -> None:
    print(f"[{utc_stamp()}] {message}", flush=True)


def wait_result_service(url: str, state: Path, case_id: str,
                        timeout: float = 240):
    """Wait at low polling rate and make a long slowed fixture visible."""
    from sdcard import Client
    started = time.monotonic()
    deadline = started + timeout
    next_notice = started + 15
    last: object = "no response"
    while time.monotonic() < deadline:
        client = Client(url, state)
        keep = False
        try:
            current = client.status()
            last = current
            if current.get("online"):
                client.connect()
                keep = True
                return client
        except Exception as error:
            last = repr(error)
        finally:
            if not keep:
                client.lock.close()
        now = time.monotonic()
        if now >= next_notice:
            announce(f"{case_id} still running — {now - started:.0f} seconds elapsed")
            next_notice += 15
        time.sleep(1)
    raise TimeoutError(f"{case_id} result listener deadline exceeded: {last}")


def phase_count(document: dict, name: str) -> int:
    return next(item["count"] for item in document["phases"]
                if item["name"] == name)


def summarize_video(records: list[dict], start: float, stop: float,
                    geometry: tuple[int, int], request_cap_hz: int) -> dict:
    selected = [item for item in records
                if start <= item["received_monotonic"] <= stop and
                (item["width"], item["height"]) == geometry]
    if len(selected) < 2:
        raise RuntimeError(f"only {len(selected)} matching video frames were received")
    elapsed = selected[-1]["received_monotonic"] - selected[0]["received_monotonic"]
    if elapsed <= 0:
        raise RuntimeError("matching video frames have no positive elapsed time")
    sequence_span = (selected[-1]["sequence"] - selected[0]["sequence"]) & 0xFFFFFFFF
    return {
        "consumer": "direct WebSocket frame requests",
        "request_cap_hz": request_cap_hz,
        "matching_frames": len(selected),
        "measurement_seconds": elapsed,
        "delivered_frames_per_second": (len(selected) - 1) / elapsed,
        "source_sequence_per_second": sequence_span / elapsed,
        "first_sequence": selected[0]["sequence"],
        "last_sequence": selected[-1]["sequence"],
        "width": geometry[0], "height": geometry[1],
    }


def validate_receipts(paths: list[Path]) -> tuple[dict, dict]:
    receipts = {}
    locations = {}
    for path in paths:
        resolved = path.resolve(strict=True)
        receipt = json.loads(resolved.read_text())
        target = receipt.get("target")
        if (receipt.get("schema") != 1 or receipt.get("status") != "verified" or
                target not in ("p4", "emos") or target in receipts):
            raise ValueError(f"{path}: expected one verified schema-1 receipt per target")
        receipts[target] = receipt
        locations[target] = str(resolved)
    if set(receipts) != {"p4", "emos"}:
        raise ValueError("performance qualification requires verified P4 and EMOS receipts")
    return receipts, locations


def build_startup(case: dict, fixture: str, result: str,
                  raw_start: int | None = None, raw_size: int | None = None) -> bytes:
    lines = [
        "SET KEYBOARD 1",
        "EMOS KEYINPUT extender",
        "EMOS EXCOM",
        f"VDU 22 {case['mode']}",
    ]
    if case["workdir"]:
        lines.append("CD " + case["workdir"])
    lines += ["LOAD " + fixture]
    if case["kind"] == "empty":
        lines.append("RUN . " + result)
    else:
        if raw_start is None or raw_size is None:
            raise ValueError("Nurples startup requires its exact raw timing range")
        lines += ["RUN", f"SAVE {result} &{raw_start:X} &{raw_size:X}"]
    lines += ["EMOS LEGACY --keep-display", "EMOS sdserve --fast /"]
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


class VideoObserver:
    """Continuously request frames from one controlled video consumer."""

    def __init__(self, url: str, request_cap_hz: int):
        self.url = url
        self.request_cap_hz = request_cap_hz
        self.records: list[dict] = []
        self.error: BaseException | None = None
        self.ready = threading.Event()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._run, name="performance-video",
                                       daemon=True)

    def _run(self) -> None:
        try:
            with VideoSession(self.url) as session:
                self.ready.set()
                next_request = time.monotonic()
                while not self.stop.is_set():
                    delay = next_request - time.monotonic()
                    if delay > 0:
                        self.stop.wait(delay)
                    if self.stop.is_set():
                        break
                    frame = session.next_frame()
                    frame["received_monotonic"] = time.monotonic()
                    self.records.append(frame)
                    next_request = max(next_request + 1 / self.request_cap_hz,
                                       frame["received_monotonic"])
        except BaseException as error:
            self.error = error
            self.ready.set()

    def start(self) -> None:
        self.thread.start()
        if not self.ready.wait(15):
            raise TimeoutError("controlled video observer did not connect")
        if self.error is not None:
            raise RuntimeError("controlled video observer failed to connect") from self.error

    def finish(self, start: float, stop: float, geometry: tuple[int, int]) -> dict:
        self.stop.set()
        self.thread.join(35)
        if self.thread.is_alive():
            raise TimeoutError("controlled video observer did not close")
        if self.error is not None:
            raise RuntimeError("controlled video observer failed") from self.error
        return summarize_video(self.records, start, stop, geometry,
                               self.request_cap_hz)


def parse_nurples(raw: bytes, symbols: Path, destination: Path) -> dict:
    syms = {match.group(1): int(match.group(2), 16) for match in re.finditer(
        r"^(\w+) \$([0-9a-fA-F]+)", symbols.read_text(), re.M)}
    size = syms["gt_data_end"] - syms["gt_data"]
    expected_size = 8 + PERFORMANCE_UPDATES * 12
    if size != expected_size or len(raw) != size or raw[:8] != b"GT1PRT!!":
        raise ValueError("Nurples raw timing block does not match its exact symbols")
    records = [[int.from_bytes(raw[8 + index * 12 + offset:
                                  11 + index * 12 + offset], "little")
                for offset in (0, 3, 6, 9)] for index in range(PERFORMANCE_UPDATES)]
    if not all(0 < active <= total <= 65535 for active, total, _, _ in records):
        raise ValueError("Nurples contains incomplete or invalid PRT rows")
    rows = []
    run_ticks = (records[-1][3] - records[0][2]) & 0xFFFFFF
    for index, (active, total, started, stopped) in enumerate(records):
        rows.append({
            "source": 255, "frame": index,
            "active_prt": active, "logic_prt": 0, "submit_prt": active,
            "pacing_prt": total - active, "total_prt": total,
            "overflow": int(total == 65535),
            "mos_ticks": (stopped - started) & 0xFFFFFF,
            "run_ticks": run_ticks, "submitted_us": 0,
            "completed_us": 0, "drain_us": 0,
        })
    with destination.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    return summarize(destination, expected_updates=PERFORMANCE_UPDATES)


def build_fixtures(nurples_source: Path, run: Path) -> dict:
    commit = resolve_commit(nurples_source, NURPLES_COMMIT)
    source = clean_snapshot(nurples_source, commit, run / "source-nurples")
    build = run / "build"
    build.mkdir()
    announce("Building the fixed no-marker empty-frame control")
    subprocess.run([
        sys.executable, str(ROOT / "tests/performance/builders/controls.py"),
        "--output", str(build / "controls"), "--no-markers",
        "--frames", str(PERFORMANCE_UPDATES),
    ], check=True)
    announce("Building deterministic 120-update Nurples from its pinned source")
    subprocess.run([
        sys.executable, str(ROOT / "tests/performance/builders/nurples.py"),
        "--source", str(source), "--output", str(build / "nurples"),
        "--no-markers", "--frames", str(PERFORMANCE_UPDATES),
    ], check=True)
    empty = build / "controls/empty/bin/empty.bin"
    nurples = build / "nurples/ntiming0.bin"
    symbols = build / "nurples/asm/nurples.symbols"
    if not all(path.is_file() for path in (empty, nurples, symbols)):
        raise RuntimeError("performance fixture build did not produce all artifacts")
    return {"empty": empty, "nurples": nurples, "symbols": symbols,
            "nurples_commit": commit}


def cases() -> list[dict]:
    result = []
    for mode in (0, 8, 20):
        for video_hz in (None, 60):
            result.append({"id": f"mode{mode}-empty-{'video60' if video_hz else 'no-video'}",
                           "kind": "empty", "mode": mode, "video_hz": video_hz,
                           "workdir": None})
    for video_hz in (None, 30, 60):
        result.append({"id": f"mode20-nurples-{'video' + str(video_hz) if video_hz else 'no-video'}",
                       "kind": "nurples", "mode": 20, "video_hz": video_hz,
                       "workdir": "/test/nurples"})
    return result


def run_case(config: dict, case: dict, client, fixture_path: str,
             result_path: str, output: Path,
             symbols: Path, raw_start: int | None, raw_size: int | None,
             reset: list[str]) -> tuple[dict, object]:
    output.mkdir(parents=True, exist_ok=False)
    url = config["extender_url"]
    next_client = None
    observer = None
    try:
        payload = build_startup(case, fixture_path, result_path, raw_start, raw_size)
        (output / "autoexec.txt").write_bytes(payload)
        client.upload("/autoexec.txt", payload, True, fast=True)
        if client.download("/autoexec.txt") != payload:
            raise RuntimeError("one-shot startup failed independent readback")
        close_retained_backup(client, "/autoexec.txt", output / "prior-autoexec.txt")
        geometry = MODES[case["mode"]]
        observer = VideoObserver(url, case["video_hz"]) if case["video_hz"] else None
        if observer:
            announce(f"Opening one controlled {case['video_hz']}-Hz video consumer before stopping the staging listener")
            observer.start()
        client.rpc(11)
        client.lock.close()

        before = read_json(url, "/diagnostics/video-timing")
        announce(f"Pulsing Agon reset; {case['id']} then runs unattended for "
                 f"{PERFORMANCE_UPDATES} updates (30 nominal seconds)")
        started = time.monotonic()
        subprocess.run(reset, check=True)
        announce("Waiting for fixture completion and its result listener; "
                 "slowed cases can exceed 30 wall-clock seconds")
        next_client = wait_result_service(
            url, output / "sd-result.json", case["id"], timeout=240)
        finished = time.monotonic()
        video = observer.finish(started, finished, geometry) if observer else None
        after = read_json(url, "/diagnostics/video-timing")
        display = read_json(url, "/display/status")
        if (display.get("mode"), display.get("width"), display.get("height")) != (
                case["mode"], geometry[0], geometry[1]):
            raise RuntimeError(f"fixture ended with unexpected display status: {display}")

        data = next_client.download(result_path)
        (output / ("raw.bin" if case["kind"] == "nurples" else "device.csv")).write_bytes(data)
        if case["kind"] == "nurples":
            timing = parse_nurples(data, symbols, output / "combined.csv")
        else:
            (output / "combined.csv").write_bytes(data)
            timing = summarize(output / "combined.csv",
                               expected_updates=PERFORMANCE_UPDATES)
        if not case["video_hz"]:
            deltas = {name: phase_count(after, name) - phase_count(before, name)
                      for name in ("snapshot", "socket_send")}
            if any(deltas.values()):
                raise RuntimeError(
                    "video work occurred during a no-video case; close every browser consumer: " +
                    repr(deltas))
        else:
            deltas = None
        record = {
            "id": case["id"], "status": "pass", "mode": case["mode"],
            "geometry": list(geometry), "workload": case["kind"],
            "video_consumer": bool(case["video_hz"]),
            "video_request_cap_hz": case["video_hz"],
            "host_fixture_seconds": finished - started,
            "application": timing, "video": video, "no_video_phase_deltas": deltas,
            "display": display,
        }
        atomic_json(output / "summary.json", record)
        return record, next_client
    except BaseException:
        if observer is not None:
            observer.stop.set()
            observer.thread.join(35)
        # Leave an established result listener online for the caller's exact
        # startup recovery, but release this process's state-file lock.
        if next_client is not None:
            next_client.lock.close()
        else:
            client.lock.close()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flash-receipt", required=True, action="append", type=Path,
                        help="verified receipt; repeat once each for P4 and EMOS")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "agents/hardware-validation.local.json")
    parser.add_argument("--nurples-source", type=Path,
                        default=ROOT.parent / "nurples-repair")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        receipts, receipt_paths = validate_receipts(args.flash_receipt)
    except ValueError as error:
        parser.error(str(error))
    config = load_config(args.config.resolve(strict=True))
    nurples_source = args.nurples_source.resolve(strict=True)
    token = uuid.uuid4().hex[:8]
    run = (args.output or ROOT / "agents/hardware-validation" /
           ("performance-" + utc_stamp() + "-" + token)).resolve()
    if run.exists() or run.is_symlink():
        parser.error("output must be a fresh nonexisting path")
    run.mkdir(parents=True)
    atomic_json(run / "request.json", {
        "flash_receipts": receipt_paths, "nurples_source": str(nurples_source),
        "nurples_commit": NURPLES_COMMIT, "updates_per_case": PERFORMANCE_UPDATES,
        "nominal_seconds_per_case": PERFORMANCE_UPDATES / 60,
        "cases": [item["id"] for item in cases()],
    })
    artifacts = build_fixtures(nurples_source, run)
    reset = [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/reset_agon.py"),
             "--config", str(Path(config["reset_config"]).resolve(strict=True))]
    url = config["extender_url"]
    announce("Resetting the Agon and verifying Extender keyboard admission before staging")
    reset_and_wait(reset, url)
    type_line(url, run / "keyboard-legacy.json", "EMOS LEGACY")
    type_line(url, run / "keyboard-service.json", "EMOS sdserve --fast /")
    client = wait_sd_service(url, run / "sd-stage.json")
    original = b""
    results = []
    failure: BaseException | None = None
    startup_restored = False
    try:
        original = client.download("/autoexec.txt")
        require_extender_startup(original)
        for asset, expected_size in NURPLES_ASSETS.items():
            size, attributes = client.stat_entry(asset)
            if attributes & 16 or size != expected_size:
                raise RuntimeError(f"required isolated Nurples asset is wrong: {asset}")
        remote = {
            "empty": f"/extender/fixtures/perf-{token}-empty.bin",
            "nurples": f"/extender/fixtures/perf-{token}-nurples.bin",
        }
        for name in ("empty", "nurples"):
            announce(f"Staging and independently verifying the {name} fixture")
            close_retained_backup(client, remote[name], run / f"old-{name}-backup.bin")
            data = artifacts[name].read_bytes()
            client.upload(remote[name], data, True, fast=True)
            if client.download(remote[name]) != data:
                raise RuntimeError(f"{name} fixture independent readback failed")
            close_retained_backup(client, remote[name], run / f"replaced-{name}-backup.bin")

        syms = {match.group(1): int(match.group(2), 16) for match in re.finditer(
            r"^(\w+) \$([0-9a-fA-F]+)", artifacts["symbols"].read_text(), re.M)}
        raw_start = syms["gt_data"]
        raw_size = syms["gt_data_end"] - raw_start
        for case in cases():
            announce("RUN " + case["id"])
            suffix = case["id"].replace("-", "")
            result_path = (f"/agents/extender/results/p{token}-{suffix}." +
                           ("raw" if case["kind"] == "nurples" else "csv"))
            active_client = client
            client = None
            record, client = run_case(
                config, case, active_client, remote[case["kind"]], result_path,
                run / case["id"], artifacts["symbols"],
                raw_start if case["kind"] == "nurples" else None,
                raw_size if case["kind"] == "nurples" else None, reset)
            results.append(record)
            app_fps = record["application"]["updates_per_second"]
            message = f"PASS {case['id']} — application {app_fps:.2f} updates/s"
            if record["video"]:
                message += (f", delivered video "
                            f"{record['video']['delivered_frames_per_second']:.2f} frames/s")
            announce(message)
        announce("Restoring and independently verifying the exact pre-suite startup")
        restore_startup(client, original, run, "final-autoexec-backup.txt")
        startup_restored = True
        client.lock.close()
        client = None
        reset_and_wait(reset, url)
    except BaseException as error:
        failure = error
        if client is not None:
            try:
                if original:
                    announce("Failure occurred with an active listener; restoring the exact startup")
                    restore_startup(client, original, run, "failure-autoexec-backup.txt")
                    startup_restored = True
            except BaseException as cleanup_error:
                failure = RuntimeError(
                    f"performance case failed and exact startup restoration also failed: "
                    f"case={error!r}; restoration={cleanup_error!r}")
            finally:
                client.lock.close()
                client = None
        elif original:
            restored, detail = try_restore_startup_from_active_service(url, original, run)
            startup_restored = restored
            announce("Failure startup recovery: " + detail)
            if not restored:
                announce("Agon was not reset because fixture foreground safety is unknown")

    summary = {
        "schema": 1, "status": "success" if failure is None else "infrastructure-failure",
        "flashed": {target: {key: receipt.get(key) for key in
                    ("target", "component_commit", "build_id", "artifact_sha256")}
                    for target, receipt in receipts.items()},
        "fixtures": {"nurples_source_commit": artifacts["nurples_commit"],
                     "empty_sha256": sha256(artifacts["empty"]),
                     "nurples_sha256": sha256(artifacts["nurples"])},
        "cases": results, "startup_restored": startup_restored,
    }
    if failure is not None:
        summary["error"] = repr(failure)
    atomic_json(run / "summary.json", summary)
    print("\nPERFORMANCE QUALIFICATION " + summary["status"].upper().replace("-", " "))
    print("Summary: " + str(run / "summary.json"))
    if results:
        print("\ncase                                  app updates/s   delivered video fps")
        for record in results:
            delivered = (f"{record['video']['delivered_frames_per_second']:.2f}"
                         if record["video"] else "none")
            print(f"{record['id']:<37}"
                  f"{record['application']['updates_per_second']:>12.2f}   {delivered:>19}")
    if failure is not None:
        raise failure
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
