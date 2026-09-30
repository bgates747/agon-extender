#!/usr/bin/env python3
"""Run the maintained host regression closure with durable per-case evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "qualification/manifests/offline.json"
DEFAULT_IDF = ROOT / "agents/build001/native-tools/esp-idf"
DEFAULT_EMOS = ROOT / "agents/audit010/emos-baseline"
LOCK = ROOT / "agents/qualification-offline.lock"


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def announce(message: str) -> None:
    print(f"[{utc()}] {message}", flush=True)


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def append_event(path: Path, kind: str, **fields: object) -> None:
    record = {"at": utc(), "event": kind, **fields}
    with path.open("a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def git_identity(path: Path) -> dict[str, object]:
    return {
        "path": str(path.resolve()),
        "commit": subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
        ).strip(),
        "branch": subprocess.check_output(
            ["git", "-C", str(path), "branch", "--show-current"], text=True
        ).strip(),
        "dirty": bool(subprocess.check_output(
            ["git", "-C", str(path), "status", "--porcelain"], text=True
        ).strip()),
    }


def validate_manifest(document: dict) -> None:
    if document.get("schema") != 1 or not isinstance(document.get("cases"), list):
        raise ValueError("unsupported regression manifest")
    ids = [case.get("id") for case in document["cases"]]
    if any(not isinstance(case_id, str) or not case_id for case_id in ids):
        raise ValueError("each case needs a nonempty string id")
    if len(ids) != len(set(ids)):
        raise ValueError("regression case ids must be unique")
    known = set(ids)
    for case in document["cases"]:
        if case.get("phase") not in {"host", "browser", "build"}:
            raise ValueError(f"{case['id']}: unsupported phase")
        if (not isinstance(case.get("argv"), list) or not case["argv"] or
                not all(isinstance(item, str) and item for item in case["argv"])):
            raise ValueError(f"{case['id']}: argv must be a nonempty string array")
        timeout = case.get("timeout_seconds")
        if not isinstance(timeout, int) or timeout < 1:
            raise ValueError(f"{case['id']}: positive integer timeout required")
        dependencies = case.get("depends_on", [])
        if (not isinstance(dependencies, list) or
                any(item not in known or item == case["id"] for item in dependencies)):
            raise ValueError(f"{case['id']}: invalid dependency")


def expand(case: dict, output: Path, python: Path, idf_root: Path,
           source_root: Path = ROOT) -> list[str]:
    values = {
        "{root}": str(source_root),
        "{output}": str(output),
        "{python}": str(python),
        "{idf_root}": str(idf_root),
    }
    expanded = []
    for item in case["argv"]:
        for token, value in values.items():
            item = item.replace(token, value)
        if "{" in item or "}" in item:
            raise ValueError(f"{case['id']}: unknown placeholder in {item!r}")
        expanded.append(item)
    return expanded


def unchanged(expected: dict[str, dict[str, object]]) -> tuple[bool, dict]:
    actual = {name: git_identity(Path(record["path"]))
              for name, record in expected.items()}
    stable = all(actual[name]["commit"] == record["commit"] and
                 not actual[name]["dirty"] for name, record in expected.items())
    return stable, actual


def run(args: argparse.Namespace) -> int:
    output = args.output.resolve()
    source_root = args.source_root.resolve()
    if output.exists() or output.is_symlink():
        raise ValueError("output must be a fresh nonexisting path")
    manifest = json.loads(args.manifest.read_text())
    validate_manifest(manifest)
    selected = manifest["cases"]
    if args.phase:
        selected = [case for case in selected if case["phase"] in args.phase]
    if args.case:
        wanted = set(args.case)
        selected = [case for case in selected if case["id"] in wanted]
        missing = wanted - {case["id"] for case in selected}
        if missing:
            raise ValueError(f"unknown or phase-filtered cases: {sorted(missing)}")
    if not selected:
        raise ValueError("no cases selected")

    output.mkdir(parents=True)
    events = output / "events.jsonl"
    started = time.monotonic()
    preparation_started = started
    state = {"status": "preparing", "started_at": utc(),
             "manifest": str(args.manifest.resolve()), "cases": []}
    atomic_json(output / "progress.json", state)
    append_event(events, "suite-start", selected_cases=[case["id"] for case in selected])
    announce(f"SUITE START — {len(selected)} cases")

    repositories = {
        "extender": git_identity(source_root),
        "emos": git_identity(args.emos_root.resolve()),
    }
    dirty = [name for name, record in repositories.items() if record["dirty"]]
    if dirty:
        raise RuntimeError(f"clean frozen checkouts required: {', '.join(dirty)} is dirty")
    python = args.python.absolute()
    if not python.is_file():
        raise RuntimeError(f"project Python is missing: {python}")
    if not args.idf_root.is_dir():
        raise RuntimeError(f"pinned ESP-IDF checkout is missing: {args.idf_root}")
    provenance = {
        "recorded_at": utc(), "repositories": repositories,
        "python": str(python),
        "python_version": subprocess.check_output(
            [str(python), "--version"], text=True, stderr=subprocess.STDOUT
        ).strip(),
        "idf_root": str(args.idf_root.resolve()),
        "manifest_sha256": subprocess.check_output(
            ["sha256sum", str(args.manifest)], text=True
        ).split()[0],
    }
    atomic_json(output / "provenance.json", provenance)
    preparation_seconds = time.monotonic() - preparation_started
    append_event(events, "preparation-complete", duration_seconds=preparation_seconds)
    announce(f"PREPARATION PASS — {preparation_seconds:.2f} s")

    results: dict[str, dict] = {}
    phases: dict[str, float] = {}
    state.update(status="running", phase=selected[0]["phase"],
                 preparation_seconds=preparation_seconds)
    atomic_json(output / "progress.json", state)
    current_phase = None
    phase_started = None
    for case in selected:
        if case["phase"] != current_phase:
            if current_phase is not None and phase_started is not None:
                phases[current_phase] = time.monotonic() - phase_started
                append_event(events, "phase-end", phase=current_phase,
                             duration_seconds=phases[current_phase])
            current_phase = case["phase"]
            phase_started = time.monotonic()
            state["phase"] = current_phase
            append_event(events, "phase-start", phase=current_phase)
            announce(f"PHASE {current_phase}")

        blocked_by = [item for item in case.get("depends_on", [])
                      if results.get(item, {}).get("status") != "pass"]
        record = {"id": case["id"], "phase": case["phase"],
                  "started_at": utc()}
        if blocked_by:
            record.update(status="blocked", blocked_by=blocked_by,
                          ended_at=utc(), duration_seconds=0.0)
            results[case["id"]] = record
            state["cases"].append(record)
            append_event(events, "case-blocked", case=case["id"], blocked_by=blocked_by)
            announce(f"BLOCKED {case['id']} — dependency: {', '.join(blocked_by)}")
            atomic_json(output / "progress.json", state)
            continue

        stable, actual = unchanged(repositories)
        if not stable:
            record.update(status="infrastructure-error",
                          error="source closure changed during the run",
                          repositories=actual, ended_at=utc(), duration_seconds=0.0)
            results[case["id"]] = record
            state["cases"].append(record)
            append_event(events, "case-error", case=case["id"], error=record["error"])
            atomic_json(output / "progress.json", state)
            break

        argv = expand(case, output, python, args.idf_root.resolve(),
                      source_root)
        log_path = output / "cases" / (case["id"] + ".log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        record.update(status="running", argv=argv, log=str(log_path))
        state["active_case"] = case["id"]
        atomic_json(output / "progress.json", state)
        append_event(events, "case-start", case=case["id"], phase=case["phase"])
        announce(f"RUN {case['id']}")
        case_started = time.monotonic()
        try:
            with log_path.open("xb") as log:
                environment = dict(os.environ, AGON_EMOS_ROOT=str(args.emos_root.resolve()))
                completed = subprocess.run(argv, cwd=source_root, stdin=subprocess.DEVNULL,
                                           stdout=log, stderr=subprocess.STDOUT,
                                           timeout=case["timeout_seconds"], env=environment)
            status = "pass" if completed.returncode == 0 else "test-failure"
            record.update(status=status, exit_code=completed.returncode)
        except subprocess.TimeoutExpired:
            record.update(status="timeout", exit_code=None,
                          error=f"exceeded {case['timeout_seconds']} seconds")
        except (OSError, ValueError) as error:
            record.update(status="infrastructure-error", exit_code=None,
                          error=repr(error))
        record.update(ended_at=utc(), duration_seconds=time.monotonic() - case_started)
        results[case["id"]] = record
        state["cases"].append(record)
        state.pop("active_case", None)
        atomic_json(output / "progress.json", state)
        append_event(events, "case-end", case=case["id"], status=record["status"],
                     duration_seconds=record["duration_seconds"])
        announce(f"{record['status'].upper()} {case['id']} — {record['duration_seconds']:.2f} s")

    if current_phase is not None and phase_started is not None:
        phases[current_phase] = time.monotonic() - phase_started
        append_event(events, "phase-end", phase=current_phase,
                     duration_seconds=phases[current_phase])

    stable, final_repositories = unchanged(repositories)
    counts = {name: sum(item["status"] == name for item in results.values())
              for name in ("pass", "test-failure", "infrastructure-error", "timeout", "blocked")}
    terminal = "success"
    if not stable or counts["infrastructure-error"]:
        terminal = "infrastructure-failure"
    elif counts["timeout"]:
        terminal = "timeout"
    elif counts["test-failure"] or counts["blocked"]:
        terminal = "test-failure"
    summary = {
        "status": terminal, "started_at": state["started_at"], "ended_at": utc(),
        "duration_seconds": time.monotonic() - started,
        "preparation_seconds": preparation_seconds,
        "fixture_runtime_seconds": sum(item["duration_seconds"] for item in results.values()),
        "retrieval_seconds": 0.0,
        "phase_seconds": phases, "counts": counts,
        "source_closure_unchanged": stable,
        "initial_repositories": repositories,
        "final_repositories": final_repositories,
        "cases": list(results.values()),
        "limits": [
            "Host-only suite: no flash, reset, SD transfer, foreground application, or physical observation.",
            "Mainboard phase display is intentionally omitted because the host suite does not own the foreground; progress.json and events.jsonl are the durable channel.",
            "Performance and manually observed loaded-asset mode-switch cases are outside this concurrent run."
        ]
    }
    atomic_json(output / "summary.json", summary)
    state.update(status=terminal, ended_at=summary["ended_at"], counts=counts)
    state.pop("active_case", None)
    atomic_json(output / "progress.json", state)
    append_event(events, "suite-end", status=terminal,
                 duration_seconds=summary["duration_seconds"], counts=counts)
    announce(f"SUITE {terminal.upper()} — {summary['duration_seconds']:.2f} s — {counts}")
    print(json.dumps({"status": terminal, "counts": counts,
                      "summary": str(output / "summary.json")}, sort_keys=True))
    return 0 if terminal == "success" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--source-root", type=Path, default=ROOT,
                        help="clean checkout containing the pinned Extender commit")
    parser.add_argument("--python", type=Path, default=ROOT / ".venv/bin/python")
    parser.add_argument("--idf-root", type=Path, default=DEFAULT_IDF)
    parser.add_argument("--emos-root", type=Path, default=DEFAULT_EMOS)
    parser.add_argument("--phase", action="append", choices=("host", "browser", "build"))
    parser.add_argument("--case", action="append")
    args = parser.parse_args()
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("another regression suite owns the exclusive lock")
        try:
            return run(args)
        except BaseException as error:
            output = args.output.resolve()
            if output.is_dir():
                failure = {"status": "infrastructure-failure", "ended_at": utc(),
                           "error": repr(error), "traceback": traceback.format_exc()}
                atomic_json(output / "summary.json", failure)
                atomic_json(output / "progress.json", failure)
                append_event(output / "events.jsonl", "suite-end",
                             status="infrastructure-failure", error=repr(error))
            print(f"regression suite infrastructure failure: {error}", file=sys.stderr)
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
