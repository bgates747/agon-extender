#!/usr/bin/env python3
"""Shared, non-authoritative helpers for commit-pinned hardware validation."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]


def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d-%H-%M-%SZ")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True
    ).strip()


def resolve_commit(root: Path, revision: str) -> str:
    return git(root, "rev-parse", "--verify", revision + "^{commit}")


def clean_snapshot(source: Path, commit: str, destination: Path) -> Path:
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"snapshot destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--quiet", "--shared", "--no-checkout",
         str(source.resolve()), str(destination)], check=True
    )
    subprocess.run(
        ["git", "-C", str(destination), "checkout", "--quiet", "--detach", commit],
        check=True,
    )
    if git(destination, "status", "--porcelain"):
        raise RuntimeError("new commit snapshot is unexpectedly dirty")
    return destination


def link_ignored(snapshot: Path, relative: str, source: Path) -> None:
    target = snapshot / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(source.resolve(), target_is_directory=True)
    with (snapshot / ".git/info/exclude").open("a") as stream:
        stream.write("\n/" + relative.rstrip("/") + "\n")


def load_config(path: Path) -> dict:
    document = json.loads(path.read_text())
    if document.get("schema") != 1:
        raise ValueError("hardware validation config must use schema 1")
    if not isinstance(document.get("extender_url"), str) or not document["extender_url"].startswith("http://"):
        raise ValueError("extender_url must be a local HTTP endpoint")
    if not isinstance(document.get("reset_url"), str) or not document["reset_url"].startswith("http://"):
        raise ValueError("reset_url must be a local HTTP endpoint")
    for key in ("reset_config", "emos_repository", "builder_repository", "fab_root"):
        if not isinstance(document.get(key), str) or not document[key]:
            raise ValueError(f"hardware validation config is missing {key}")
    p4 = document.get("p4")
    if not isinstance(p4, dict):
        raise ValueError("hardware validation config is missing p4")
    if (not isinstance(p4.get("ssh"), list) or not p4["ssh"] or
            p4["ssh"][0] != "ssh" or not all(isinstance(v, str) for v in p4["ssh"])):
        raise ValueError("p4.ssh must be a complete SSH argv array")
    for key in ("stable_port", "usb_serial", "esptool"):
        if not isinstance(p4.get(key), str) or not p4[key]:
            raise ValueError(f"hardware validation config is missing p4.{key}")
    return document


def wait_keyboard(url: str, *, old_boot: int | None = None,
                  timeout: float = 45) -> dict:
    from keyboard import Client
    journal = ROOT / "agents/hardware-validation" / ("status-" + str(time.time_ns()) + ".json")
    client = Client(url, journal)
    try:
        deadline = time.monotonic() + timeout
        last: object = "no response"
        while time.monotonic() < deadline:
            try:
                status = client.status()
                last = status
                if (status.get("ready") and status.get("physical_neutral") and
                        not status.get("held") and not status.get("pending") and
                        (old_boot is None or status.get("boot") != old_boot)):
                    return status
            except Exception as error:  # retain the last diagnostic at timeout
                last = repr(error)
            time.sleep(0.2)
        raise TimeoutError(f"keyboard readiness deadline exceeded: {last}")
    finally:
        client.lock.close()


def keyboard_status(url: str) -> dict:
    """Read status without requiring an admitted Extender keyboard."""
    from keyboard import Client
    journal = ROOT / "agents/hardware-validation" / ("status-" + str(time.time_ns()) + ".json")
    client = Client(url, journal)
    try:
        return client.status()
    finally:
        client.lock.close()


def type_line(url: str, journal: Path, line: str) -> dict:
    from keyboard import Client, text_events
    client = Client(url, journal)
    try:
        status = client.status()
        if not status.get("ready") or not status.get("physical_neutral"):
            raise RuntimeError("Extender keyboard is not admitted and neutral")
        client.open(status)
        try:
            client.send(text_events(line + "\n", status["locale"], status["caps"]))
        finally:
            if not client.state.get("pending"):
                client.cancel()
        return status
    finally:
        client.lock.close()


def wait_sd_service(url: str, state: Path, timeout: float = 60):
    from sdcard import Client
    deadline = time.monotonic() + timeout
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
        time.sleep(0.25)
    raise TimeoutError(f"SD service readiness deadline exceeded: {last}")


def run_logged(argv: list[str], log: Path, *, cwd: Path | None = None,
               env: dict[str, str] | None = None, timeout: float | None = None) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("x") as stream:
        stream.write(json.dumps(argv) + "\n")
        stream.flush()
        result = subprocess.run(argv, cwd=cwd, env=env, stdout=stream,
                                stderr=subprocess.STDOUT, timeout=timeout)
    if result.returncode:
        raise subprocess.CalledProcessError(result.returncode, argv)


def copy_tree_dependency(snapshot: Path, relative: str, source: Path) -> None:
    """Link a generated dependency tree and keep the source snapshot clean."""
    if not source.is_dir():
        raise FileNotFoundError(source)
    link_ignored(snapshot, relative, source)
