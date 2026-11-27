"""Opt-in, attempt-bound reports for the Olimex runner."""

from contextlib import contextmanager
from hashlib import file_digest, sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import subprocess
import sys
import tempfile
import time

import bench_process as process
from sdcard import Client, RemoteError
from sdcard_staged import Client as StagedClient, QUOTA


FIRMWARE = {"native_vdp_sha256", "p4_app_sha256", "emos_rom_sha256"}
TOKEN = r"[0-9a-f]{16}"
NAME = r"[A-Za-z0-9_-]{1,8}(?:\.[A-Za-z0-9_-]{1,3})?"
PREFIX = b"OLXR1 "
STATUS = re.compile(
    rf"OLXR1 ({TOKEN}) ({NAME}) ([0-9]{{1,8}}) ([0-9]{{1,8}}) (saved|open|write|short|close) ([0-9]{{1,3}}) ([0-9]{{1,3}})"
)


def validate(kit, pinned):
    cfg = kit["report_lifecycle"]
    if (set(cfg) != {"project", "fixture", "mode", "firmware"}
            or kit.get("schema", 3) != 3 or "fixtures" not in kit
            or "human_start" in kit or kit["firmware"]):
        raise ValueError("Report lifecycle requires a named, production-only automated schema 3 job")
    if cfg["mode"] not in ("token-v1", "legacy"):
        raise ValueError("Unknown report lifecycle mode")
    if (set(cfg["firmware"]) != FIRMWARE or any(
            not re.fullmatch(r"[a-f0-9]{64}", value) for value in cfg["firmware"].values())):
        raise ValueError("Report lifecycle requires the three installed firmware pins")
    if any(not re.fullmatch(r"[a-z][a-z0-9-]{0,23}", cfg[key]) for key in ("project", "fixture")):
        raise ValueError("Invalid report workspace identity")
    for arm in kit["fixtures"]:
        if arm["cwd"] != f"/test/{cfg['project']}/{cfg['fixture']}/{arm['id']}":
            raise ValueError("Report workspace must match project, fixture and arm")
        if {"uart_end", "listener_handoff"} & arm.keys():
            raise ValueError("Report lifecycle requires command-correlated mirrored RUN output")
        if any(not re.fullmatch(NAME, PurePosixPath(path).name) for path in arm["results"]):
            raise ValueError("Lifecycle reports require unambiguous 8.3 output names")
        pinned(arm["report_validator"])


def publish(path, value):
    """Publish a complete immutable record, including across a killed writer."""
    path = Path(path)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=".report-") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
        os.link(stream.name, path)
    sync_directory(path.parent)


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def digest(path):
    with Path(path).open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def run_digest(path, count):
    with path.open("rb") as stream:
        data = stream.read(count)
    if len(data) != count:
        raise RuntimeError("Original RUN transcript is truncated")
    return sha256(data).hexdigest()


def lease(path, owner):
    with Path(path).open("rb") as stream:
        data = stream.read()
        opened = os.fstat(stream.fileno())
    current = Path(path).stat()
    stamp = [current.st_dev, current.st_ino, current.st_mtime_ns, current.st_ctime_ns]
    if (stamp != [opened.st_dev, opened.st_ino, opened.st_mtime_ns, opened.st_ctime_ns]
            or json.loads(data)["active"] != owner):
        raise RuntimeError("Olimex scheduler custody differs from the operator")
    return {"owner": owner, "file": stamp, "sha256": sha256(data).hexdigest()}


def stat_file(client, path):
    try:
        return client.stat_entry(path)
    except RemoteError as error:
        if error.status == 6 and error.detail in (b"\x04", b"\x05"):
            return None
        raise


def report_status(lines, token, name):
    entries = []
    for line in lines:
        if not line.startswith("OLXR1 "):
            continue
        fields = line.split()
        if len(fields) >= 3 and fields[2].lower() == name.lower():
            match = STATUS.fullmatch(line)
            entries.append(match.groups() if match else None)
    if len(entries) != 1 or entries[0] is None or entries[0][:2] != (token, name):
        return None
    _, _, expected, actual, stage, error, close = entries[0]
    return {"expected": int(expected), "actual": int(actual), "stage": stage,
            "error": int(error), "close_error": int(close)}


def validate_report(mode, attempt, witness, remote, archive, validator):
    name = PurePosixPath(remote).name
    status = report_status(witness["output"], attempt["token"], name) if mode == "token-v1" else None
    saved = "unreported"
    if mode == "token-v1":
        if status is None:
            return {"saved": "unknown", "owned": False, "accepted": False,
                    "reason": "Missing, ambiguous or mismatched serial report status"}
        with archive.open("rb") as stream:
            header = stream.read(len(PREFIX) + len(attempt["token"]) + 1)
        if header != PREFIX + attempt["token"].encode("ascii") + b"\n":
            return {"saved": "unknown", "owned": False, "accepted": False,
                    "reason": "Report header does not identify this attempt", "serial": status}
        if (status["stage"] != "saved" or status["error"] or status["close_error"]
                or status["actual"] != status["expected"]
                or status["actual"] != archive.stat().st_size):
            return {"saved": "failed", "owned": False, "accepted": False,
                    "reason": "Write, close or report length was not confirmed", "serial": status}
        saved = "confirmed"
    elif witness["outcome"] != "passed":
        return {"saved": saved, "owned": False, "accepted": False,
                "reason": "Legacy report needs a single witnessed successful invocation"}
    verdict = validator(archive)
    return {"saved": saved, "owned": True, **verdict, "serial": status}


class Lifecycle:
    def __init__(self, bench, owner, binding, *, agon_boot):
        self.bench = bench
        self.owner = owner
        self.binding = binding
        self.config = bench.kit["report_lifecycle"]
        self.agon_boot = agon_boot

    def custody(self):
        return lease(self.bench.config["report_lease_state"], self.owner)

    def baseline(self):
        inventory = process.read(self.bench.config["inventory"])
        if inventory.get("pending_operation"):
            raise RuntimeError("Firmware has an unresolved operation")
        result = {}
        for key, role in (("native_vdp_sha256", "native_vdp"), ("p4_app_sha256", "p4"),
                          ("emos_rom_sha256", "emos")):
            expected = self.config["firmware"][key]
            entry = inventory[role]
            receipt = Path(entry["verification_receipt"])
            data = receipt.read_bytes()
            proof = json.loads(data)
            if (inventory["components"][key] != expected or entry["sha256"] != expected
                    or proof["sha256"] != expected or not proof["boot_cli_ready"]
                    or entry["status"] != "verified-standard"):
                raise RuntimeError(f"Installed {role} differs from the verified report baseline")
            result[key] = {"image": expected, "receipt": str(receipt), "sha256": sha256(data).hexdigest()}
        return result

    def fence(self):
        return {"lease": self.custody(), "firmware": self.baseline(),
                "agon_boot": self.agon_boot(), "p4_boot": self.bench.get("/sd/fast")["boot"]}

    @contextmanager
    def metadata(self, label):
        client = Client(self.bench.url, self.bench.out / f"report-{label}.json", timeout=12)
        try:
            client.connect(require_fast=True)
            yield client
        finally:
            client.lock.close()

    def prepare(self, phase, job, stage):
        if self.binding != stage["binding"]:
            raise RuntimeError("Staging used a different job or configuration")
        before = self.fence()
        if any(before[key] != stage["fence"][key] for key in ("lease", "firmware", "p4_boot")):
            raise RuntimeError("Staging custody or baseline changed")
        self.bench.start_listener("report-fresh", "EMOS sdserve --fast --parallel /")
        collisions = []
        with self.metadata("fresh") as client:
            for path in job["results"]:
                metadata = stat_file(client, path)
                if metadata is not None:
                    collisions.append({"path": path, "bytes": metadata[0], "attributes": metadata[1]})
        if collisions:
            publish(self.bench.out / "report-collision.json", {"retained": collisions})
        self.bench.exit_staged_listener("report-fresh")
        if collisions:
            raise RuntimeError(f"Outstanding SD report: {collisions[0]['path']}; launch blocked")
        if self.fence() != before:
            raise RuntimeError("Custody or boot changed while establishing report freshness")
        attempt = {"token": secrets.token_hex(8), "phase": phase, "mode": self.config["mode"],
                   "binding": self.binding, "fence": before, "fixture": job["agon"]["sha256"],
                   "program": job["sd_program"], "paths": job["results"], "fresh_epoch": time.time()}
        publish(self.bench.out / "report-attempt.json", attempt)
        return attempt

    def download(self, journal, remote, archive):
        client = StagedClient(self.bench.url, journal)
        try:
            known = client.state.get("job") or client.state.get("last")
            if known and (known.get("remote") != remote or known.get("destination") != str(archive.absolute())
                          or known.get("operation") != "get" or not known.get("require_parallel")):
                raise RuntimeError("Retained transfer belongs to a different report")
            if client.state.get("job"):
                receipt = client.resume()
            elif known:
                if not known.get("delivered"):
                    raise RuntimeError("Missing completed staged transfer proof")
                receipt = known["result"]
            else:
                receipt = client.begin("get", remote, destination=archive, require_parallel=True)
        finally:
            client.close()
        length = archive.stat().st_size
        if not 0 <= length <= QUOTA or receipt["size"] != length or receipt["bytes"] != length:
            raise RuntimeError("Collected bytes differ from the transfer receipt")
        if receipt["payload_carrier"] != ("parlio" if length else "empty-control"):
            raise RuntimeError("Unexpected report carrier")
        return receipt

    def run_validator(self, job, remote, archive, witness, attempt):
        spec = job["report_validator"]
        path = Path(spec["path"]).resolve()
        if path.stat().st_size != spec["bytes"] or digest(path) != spec["sha256"]:
            raise RuntimeError("Pinned host validator changed")
        result = subprocess.run(
            [sys.executable, str(path), str(archive), str(witness), remote, attempt["token"]],
            capture_output=True, timeout=20, check=True)
        verdict = json.loads(result.stdout)
        if (set(verdict) != {"accepted", "reason"} or type(verdict["accepted"]) is not bool
                or not isinstance(verdict["reason"], str) or not verdict["reason"].strip()):
            raise RuntimeError("Invalid host validator verdict")
        return verdict

    def collect(self, origin, job, attempt, witness):
        current = self.fence()
        if any(current[key] != attempt["fence"][key] for key in ("lease", "firmware")):
            raise RuntimeError("Report custody or verified firmware changed")
        if current != attempt["fence"] and attempt["mode"] == "legacy":
            raise RuntimeError("Legacy report continuity changed; retain the SD copy")
        if attempt["binding"] != self.binding or attempt["paths"] != job["results"]:
            raise RuntimeError("Original attempt binding differs")
        transcript = origin / "results/vdp-usb.bin"
        if run_digest(transcript, witness["transcript_bytes"]) != witness["transcript_sha256"]:
            raise RuntimeError("Original transcript differs")
        entries = [origin / f"report-{index:02d}" for index in range(len(job["results"]))]
        if all((entry / "cleaned.json").is_file() for entry in entries):
            online = self.bench.get("/sd/status")["online"]
            if not online:
                return self.finish(entries)
        listener = self.bench.get("/sd/status")
        if listener["online"]:
            prior = {row["boot"] for file in origin.glob("report-listener-*.json")
                     for row in [process.read(file)] if row["fence"] == current}
            if listener["boot"] not in prior:
                raise RuntimeError("An unbound listener is active; keep its state")
        else:
            self.bench.start_listener("report-collect", "EMOS sdserve --fast --parallel /")
            listener = self.bench.get("/sd/status")
        publish(origin / f"report-listener-{self.bench.out.name}.json",
                {"boot": listener["boot"], "fence": current})
        for index, (remote, entry) in enumerate(zip(job["results"], entries, strict=True)):
            self.collect_one(origin, job, attempt, witness, remote, entry, index)
        self.bench.exit_staged_listener("report-collect")
        return self.finish(entries)

    @staticmethod
    def finish(entries):
        return all((entry / "cleaned.json").is_file()
                   and process.read(entry / "validation.json")["accepted"] for entry in entries)

    def collect_one(self, origin, job, attempt, witness, remote, entry, index):
        entry.mkdir(exist_ok=True)
        sync_directory(origin)
        archive = entry / PurePosixPath(remote).name
        evidence = entry / "archive.json"
        if not evidence.exists():
            source = entry / "source.json"
            if not source.exists():
                with self.metadata(f"source-{index:02d}") as client:
                    metadata = stat_file(client, remote)
                if metadata is None or metadata[1] & 16 or metadata[0] > QUOTA:
                    publish(self.bench.out / f"report-unavailable-{index:02d}.json",
                            {"path": remote, "metadata": metadata,
                             "reason": "Missing, non-file or oversized SD report"})
                    print(f"{attempt['token']} {remote}: report unavailable; no removal", flush=True)
                    return
                publish(source, {"path": remote, "bytes": metadata[0]})
            selected = process.read(source)
            if selected["path"] != remote:
                raise RuntimeError("Initial report metadata belongs to a different path")
            receipt = self.download(entry / "transfer.json", remote, archive)
            if archive.stat().st_size != selected["bytes"]:
                raise RuntimeError("Report size changed during transfer")
            publish(evidence, {"path": remote, "attempt": attempt["token"], "bytes": selected["bytes"],
                               "sha256": digest(archive), "transfer": receipt,
                               "witness": witness["transcript_sha256"]})
        record = process.read(evidence)
        if (record["path"] != remote or record["attempt"] != attempt["token"]
                or record["witness"] != witness["transcript_sha256"]
                or record["bytes"] != archive.stat().st_size or record["sha256"] != digest(archive)):
            raise RuntimeError("Archived report or its evidence changed")
        validation = entry / "validation.json"
        if not validation.exists():
            verdict = validate_report(
                attempt["mode"], attempt, witness, remote, archive,
                lambda file: self.run_validator(job, remote, file, origin / "report-run.json", attempt))
            publish(validation, verdict)
        verdict = process.read(validation)
        if verdict["owned"] and not (entry / "cleaned.json").exists():
            sync_directory(entry)
            self.cleanup(entry, remote, record, attempt, index)
        print(f"{attempt['token']} {remote} -> {archive}: saved={verdict['saved']} "
              f"collected=yes validation={verdict['reason']} "
              f"cleaned={'yes' if (entry / 'cleaned.json').exists() else 'retained'}", flush=True)

    def cleanup(self, entry, remote, record, attempt, index):
        intent = entry / "delete-intent.json"
        cleaned = entry / "cleaned.json"
        expected = {"path": remote, "attempt": attempt["token"], "archive": record["sha256"]}
        if self.fence() != attempt["fence"]:
            return  # A reset may permit archival but cannot prove continuing SD ownership.
        with self.metadata(f"cleanup-stat-{index:02d}") as client:
            metadata = stat_file(client, remote)
        if intent.exists():
            if process.read(intent) != expected:
                raise RuntimeError("Delete intent differs from the archived report")
            if metadata is None:
                publish(cleaned, {"result": "confirmed-absent", **expected})
                return
            if metadata[1] & 16 or metadata[0] != record["bytes"]:
                raise RuntimeError("SD report changed after interrupted cleanup; retained")
            observed = self.bench.out / f"report-reconcile-{index:02d}.bin"
            self.download(observed.with_suffix(".json"), remote, observed)
            if digest(observed) != record["sha256"]:
                raise RuntimeError("SD report differs from the archived bytes; retained")
        else:
            if metadata is None or metadata[1] & 16 or metadata[0] != record["bytes"]:
                raise RuntimeError("SD report changed before cleanup; retained")
            publish(intent, expected)
        if self.fence() != attempt["fence"]:
            raise RuntimeError("Custody or boot changed before exact report removal")
        with self.metadata(f"cleanup-remove-{index:02d}") as client:
            client.remove_file(remote)
        publish(cleaned, {"result": "removed", **expected})
