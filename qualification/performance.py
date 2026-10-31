#!/usr/bin/env python3
"""Retained cadence analysis/build helpers; physical entry points are disabled.

The historical coordinator launched fixtures through rewritten startup. It must
be migrated to the current test-appliance lifecycle before any hardware reuse.
Canonical release qualification is qualification/run.py; performance is separate.
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
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
NURPLES_COMMIT = "0c741d5e2021927adfa440f45b8e04b950114889"
NURPLES_ASSETS = {
    "/test/nurples/game.agnb": 367168,
    "/test/nurples/ui.agnb": 246844,
    "/test/nurples/fonts/Lat38-VGA8_8x8.font": 2048,
}
MODES = {0: (640, 480), 8: (320, 240), 20: (512, 384)}
PERFORMANCE_SECONDS = 30
PERFORMANCE_TICKS = PERFORMANCE_SECONDS * 120
PERFORMANCE_CAPACITY = 2400

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "qualification"))
sys.path.append(str(ROOT / "tests/performance"))
from analyze import summarize
from hardware_validation import (atomic_json, clean_snapshot, load_config,
                                 resolve_commit, sha256, type_line, utc_stamp,
                                 wait_sd_service)
from run import read_json
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
                client.connect(require_fast=True)
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


def video_timing_capability(url: str) -> tuple[bool, dict | None]:
    """Treat the diagnostic counter endpoint as optional build instrumentation."""
    try:
        return True, read_json(url, "/diagnostics/video-timing")
    except HTTPError as error:
        if error.code == 404:
            return False, None
        raise


def summarize_video(records: list[dict], start: float, stop: float,
                    geometry: tuple[int, int], request_cap_hz: int,
                    *, stop_inclusive: bool = True) -> dict:
    selected = [item for item in records
                if start <= item["received_monotonic"] and
                (item["received_monotonic"] <= stop if stop_inclusive else
                 item["received_monotonic"] < stop) and
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


def white_boundary(records: list[dict], geometry: tuple[int, int],
                   not_before: float) -> float:
    """Return the first received all-white frame for this geometry."""
    expected = {
        pixel_format: hashlib.sha256(
            bytes([63 if pixel_format == 2 else 255]) *
            geometry[0] * geometry[1] * (1 if pixel_format == 2 else 3)
        ).hexdigest()
        for pixel_format in (1, 2)
    }
    marker = next((item for item in records
                   if item["received_monotonic"] >= not_before and
                   (item["width"], item["height"]) == geometry and
                   item["sha256"] == expected.get(item["format"])), None)
    if marker is None:
        raise RuntimeError("post-measurement white video boundary was not observed")
    return marker["received_monotonic"]


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
        boundary = white_boundary(
            self.records, geometry, start + PERFORMANCE_SECONDS)
        window_start = boundary - PERFORMANCE_SECONDS
        if window_start < start:
            raise RuntimeError("video boundary arrived before a complete 30-second window")
        result = summarize_video(self.records, window_start, boundary, geometry,
                                 self.request_cap_hz, stop_inclusive=False)
        result["window_alignment"] = (
            "30 wall seconds ending at the first post-measurement white boundary; "
            "loading and result cleanup excluded")
        result["boundary_received_monotonic"] = boundary
        return result


def parse_nurples(raw: bytes, symbols: Path, destination: Path) -> dict:
    syms = {match.group(1): int(match.group(2), 16) for match in re.finditer(
        r"^(\w+) \$([0-9a-fA-F]+)", symbols.read_text(), re.M)}
    size = syms["gt_data_end"] - syms["gt_data"]
    expected_size = 11 + PERFORMANCE_CAPACITY * 12
    if size != expected_size or len(raw) != size or raw[:8] != b"GTPRN2!!":
        raise ValueError("Nurples raw timing block does not match its exact symbols")
    count = int.from_bytes(raw[8:11], "little")
    if not 1 <= count <= PERFORMANCE_CAPACITY:
        raise ValueError("Nurples raw timing count is outside its retained capacity")
    records = [[int.from_bytes(raw[11 + index * 12 + offset:
                                  14 + index * 12 + offset], "little")
                for offset in (0, 3, 6, 9)] for index in range(count)]
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
    summary = summarize(destination, expected_updates=None)
    summary["mos_run_ticks"] = run_ticks
    summary["measured_wall_seconds_nominal"] = run_ticks / 120
    if not PERFORMANCE_TICKS - 10 <= run_ticks <= PERFORMANCE_TICKS + 240:
        raise ValueError(f"Nurples did not retain the requested 30-second window: {run_ticks} ticks")
    return summary


def parse_pacing(raw: bytes, destination: Path) -> dict:
    if len(raw) < 20 or raw[:8] != b"GTPRT2!!":
        raise ValueError("empty-control compact timing block has the wrong identity or size")
    frames = int.from_bytes(raw[8:10], "little")
    run_ticks = int.from_bytes(raw[10:13], "little")
    if (not 1 <= frames <= PERFORMANCE_CAPACITY or
            len(raw) != 13 + frames * 7 or not run_ticks):
        raise ValueError("empty-control compact timing header is incomplete")
    rows = []
    for index in range(frames):
        at = 13 + index * 7
        active = int.from_bytes(raw[at:at + 2], "little")
        total = int.from_bytes(raw[at + 2:at + 4], "little")
        mos_ticks = int.from_bytes(raw[at + 4:at + 7], "little")
        if not 0 <= active <= total <= 65535:
            raise ValueError("empty-control compact timing row is invalid")
        rows.append({
            "source": 255, "frame": index,
            "active_prt": active, "logic_prt": 0, "submit_prt": active,
            "pacing_prt": total - active, "total_prt": total,
            "overflow": int(total == 65535), "mos_ticks": mos_ticks,
            "run_ticks": run_ticks, "submitted_us": 0,
            "completed_us": 0, "drain_us": 0,
        })
    with destination.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    summary = summarize(destination, expected_updates=None)
    summary["mos_run_ticks"] = run_ticks
    summary["measured_wall_seconds_nominal"] = run_ticks / 120
    if not PERFORMANCE_TICKS - 10 <= run_ticks <= PERFORMANCE_TICKS + 240:
        raise ValueError(f"empty control did not retain the requested 30-second window: {run_ticks} ticks")
    return summary


def build_fixtures(nurples_source: Path, run: Path) -> dict:
    commit = resolve_commit(nurples_source, NURPLES_COMMIT)
    source = clean_snapshot(nurples_source, commit, run / "source-nurples")
    build = run / "build"
    build.mkdir()
    announce("Building the fixed no-marker empty-frame control")
    subprocess.run([
        sys.executable, str(ROOT / "tests/performance/builders/controls.py"),
        "--output", str(build / "controls"), "--no-markers", "--compact-empty",
        "--frames", str(PERFORMANCE_CAPACITY),
        "--duration-ticks", str(PERFORMANCE_TICKS),
    ], check=True)
    announce("Building deterministic 30-wall-second Nurples from its pinned source")
    subprocess.run([
        sys.executable, str(ROOT / "tests/performance/builders/nurples.py"),
        "--source", str(source), "--output", str(build / "nurples"),
        "--no-markers", "--frames", str(PERFORMANCE_CAPACITY),
        "--duration-ticks", str(PERFORMANCE_TICKS),
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
             reset: list[str], video_timing_available: bool) -> tuple[dict, object]:
    raise RuntimeError("Physical cadence runner disabled: migrate startup/CLI lifecycle before reuse")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    parser.error("physical cadence execution disabled; use qualification/run.py for release qualification")


if __name__ == "__main__":
    raise SystemExit(main())
