#!/usr/bin/env python3
"""Sequential, receipt-driven rendering qualification; never launches on boot.

The local plan supplies reviewed mode setup, installation, fixture and display
adapters. Adapters own bench admission and must return a validation receipt;
process exit alone is not a test pass. No shell, retry, reset or implicit resume.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import time

MODES = (0, 3, 8, 20, 136)
CASES = ("bitmap-light", "bitmap-heavy", "partial-scroll", "software-static",
         "software-scroll", "nurples-software", "hardware-static", "nurples-hardware")


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".new")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_plan(plan):
    if plan.get("schema") != 1 or plan.get("ready") is not True:
        raise ValueError("Plan must be explicitly qualified ready; preparation is not execution")
    renderers = plan["renderers"]
    if len(renderers) != 2 or set(renderers) != {"rgb888", "indexed"}:
        raise ValueError("Require the selected indexed and most modern RGB888 pair")
    expected = {(r, m, c, n) for r in renderers for m in MODES for c in CASES for n in range(1, 4)}
    actual = [(j["renderer"], j["mode"], j["case"], j["repeat"]) for j in plan["jobs"]]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("Require exactly 240 unique mode/case/repeat/renderer jobs")
    ids = [j["id"] for j in plan["jobs"]]
    if len(ids) != len(set(ids)) or any(not s or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in s) for s in ids):
        raise ValueError("Unsafe or duplicate job ID")
    for key in ("success", "errors"):
        if not plan["notification"][key]:
            raise ValueError("Both persistent display notification adapters are required")
    for job in plan["jobs"]:
        if job.get("qualified_geometry") is not True or not job.get("command"):
            raise ValueError("Every workload requires per-mode geometry qualification")
    for path, digest in plan["inputs"].items():
        if sha(path) != digest:
            raise ValueError("Changed adapter, firmware or fixture: " + path)


def execute(argv, log, cwd):
    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
        raise ValueError("Adapter commands must be argument lists")
    with log.open("xb") as output:
        return subprocess.run(argv, cwd=cwd, stdout=output, stderr=subprocess.STDOUT).returncode


def run(plan, output, invoke=execute):
    validate_plan(plan)
    output.mkdir(parents=True, exist_ok=False)
    output = output.resolve()
    save(output / "plan.json", plan)
    summary = {"started_utc": utc(), "state": "running", "planned": len(plan["jobs"]),
               "passed": 0, "failed": 0, "jobs": []}
    start = time.monotonic()
    save(output / "summary.json", summary)
    completed = False
    try:
        for job in plan["jobs"]:
            # A fresh destination and absent receipt prevent stale-pass reuse.
            folder = output / job["id"]
            folder.mkdir()
            receipt = folder / "receipt.json"
            row = {"id": job["id"], "started_utc": utc(), "state": "running"}
            summary["jobs"].append(row)
            save(output / "summary.json", summary)
            tick = time.monotonic()
            argv = [a.replace("{receipt}", str(receipt)).replace("{evidence}", str(folder)) for a in job["command"]]
            rc = invoke(argv, folder / "adapter.log", plan["cwd"])
            result = json.loads(receipt.read_text()) if receipt.exists() else {}
            binding = {k: job[k] for k in ("id", "renderer", "mode", "case", "repeat")}
            if any(result.get(k) != v for k, v in binding.items()):
                raise RuntimeError("Missing or mismatched completion receipt: " + job["id"])
            if result.get("bench_idle") is not True:
                raise RuntimeError("No confirmed CLI/listener handback; no further input")
            valid = result.get("validated") is True and rc == 0
            if not valid and result.get("safe_to_continue") is not True:
                raise RuntimeError("Failure has no confirmed recovery boundary")
            row.update(state="passed" if valid else "failed", ended_utc=utc(),
                       duration_seconds=time.monotonic() - tick, returncode=rc,
                       receipt_sha256=sha(receipt))
            summary["passed" if valid else "failed"] += 1
            save(output / "summary.json", summary)
        completed = True
        summary["state"] = "complete_with_errors" if summary["failed"] else "success"
        save(output / "summary.json", summary)
        # Only the admitted display adapter may put the final cue on Extender.
        key = "errors" if summary["failed"] else "success"
        rc = invoke(plan["notification"][key], output / "notification.log", plan["cwd"])
        summary["notification_returncode"] = rc
        if rc:
            summary["state"] = "notification_failed"
    except BaseException as error:
        summary.update(state="incomplete", error=str(error))
        # Unknown application state forbids speculative error-screen input.
        raise
    finally:
        summary.update(ended_utc=utc(), duration_seconds=time.monotonic() - start,
                       all_jobs_finished=completed)
        save(output / "summary.json", summary)
    return 0 if summary["state"] == "success" else 1


def banner(success):
    """MOS VDU command file, no mode switch, load/run, reset or boot hook."""
    message = "ALL TESTS COMPLETE SUCCESS" if success else "TESTS COMPLETE WITH ERRORS"
    # Stock physical colours: green=2, red=1, white=7. Full coloured screen
    # and repeated white text remain legible even in the 40-column mode.
    lines = ["VDU 17 " + str(128 + (2 if success else 1)), "VDU 12", "VDU 17 7"]
    for y in (3, 5, 7, 9, 11):
        lines.append("VDU 31 2 " + str(y))
        data = message.encode("ascii")
        for offset in range(0, len(data), 16):
            lines.append("VDU " + " ".join(str(b) for b in data[offset:offset + 16]))
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-banners", type=Path)
    args = parser.parse_args()
    if args.write_banners:
        args.write_banners.mkdir(parents=True, exist_ok=False)
        for name, success in (("success.txt", True), ("errors.txt", False)):
            (args.write_banners / name).write_bytes(banner(success))
        return 0
    if not args.plan:
        parser.error("--plan is required")
    plan = json.loads(args.plan.read_text())
    validate_plan(plan)
    if args.check:
        print("PASS: 240 jobs, per-mode readiness and pinned inputs")
        return 0
    if not args.output:
        parser.error("--output is required")
    return run(plan, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
