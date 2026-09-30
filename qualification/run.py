#!/usr/bin/env python3
"""Run the canonical offline closure and installed-hardware qualification cases."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hardware_validation import (atomic_json, clean_snapshot, copy_tree_dependency,
                                 link_ignored, load_config, resolve_commit, sha256,
                                 type_line, utc_stamp, wait_keyboard, wait_sd_service)


def announce(message: str) -> None:
    print(f"[{utc_stamp()}] {message}", flush=True)


def validate_repair_manifest(document: dict) -> None:
    if document.get("schema") != 1 or not isinstance(document.get("cases"), list):
        raise ValueError("repair manifest must use schema 1")
    ids = []
    for case in document["cases"]:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("repair case requires a nonempty id")
        ids.append(case_id)
        applies = case.get("applies_to")
        if (not isinstance(applies, list) or not applies or
                any(item not in ("emos", "p4") for item in applies) or
                len(applies) != len(set(applies))):
            raise ValueError(f"{case_id}: invalid applies_to")
        if case.get("driver") not in ("fwbug008-physical", "installed-p4-smoke"):
            raise ValueError(f"{case_id}: unknown physical driver")
        if case.get("acceptance_required") is not True:
            raise ValueError(f"{case_id}: every canonical hardware case must be acceptance-required")
        if not isinstance(case.get("timeout_seconds"), int) or case["timeout_seconds"] < 1:
            raise ValueError(f"{case_id}: positive integer timeout required")
    if len(ids) != len(set(ids)):
        raise ValueError("repair case ids must be unique")


def prepare_extender_snapshot(commit: str, run: Path) -> Path:
    snapshot = clean_snapshot(ROOT, commit, run / "source-extender")
    copy_tree_dependency(snapshot, "agents/build001/native-tools",
                         ROOT / "agents/build001/native-tools")
    copy_tree_dependency(snapshot, "vdp/managed_components", ROOT / "vdp/managed_components")
    link_ignored(snapshot, ".venv", ROOT / ".venv")
    return snapshot


def run_retained_suite(extender: Path, emos: Path, output: Path) -> dict:
    command = [str(ROOT / ".venv/bin/python"), str(ROOT / "qualification/offline.py"),
               "--output", str(output), "--source-root", str(extender),
               "--manifest", str(ROOT / "qualification/manifests/offline.json"),
               "--python", str(extender / ".venv/bin/python"),
               "--idf-root", str(extender / "agents/build001/native-tools/esp-idf"),
               "--emos-root", str(emos)]
    completed = subprocess.run(command, cwd=extender)
    summary = json.loads((output / "summary.json").read_text())
    summary["command_exit_code"] = completed.returncode
    return summary


def require_directory(client, path: str) -> None:
    _, attributes = client.stat_entry(path)
    if not attributes & 16:
        raise RuntimeError(f"required SD path is not a directory: {path}")


def close_retained_backup(client, path: str, evidence: Path) -> None:
    from sdcard import path_payload
    flags = client.rpc(10, b"\0" + path_payload(path))[0]
    if flags & 8:
        evidence.write_bytes(client.download(path + ".p17bak"))
        if flags != 9:
            raise RuntimeError(f"{path}: unsafe transfer-recovery state 0x{flags:02x}")
        remaining = client.rpc(10, b"\3" + path_payload(path))
        if remaining != b"\x01":
            raise RuntimeError(f"{path}: retained-backup close returned {remaining.hex()}")


def parse_result(data: bytes) -> dict[str, str]:
    result = {}
    for raw in data.decode("ascii").splitlines():
        if "=" not in raw:
            raise ValueError("malformed physical result line")
        key, value = raw.split("=", 1)
        if not key or key in result:
            raise ValueError("malformed or duplicate physical result key")
        result[key] = value
    required = {"schema", "case", "status", "sector", "test_rc", "restore_rc",
                "restore_verify_rc", "before_crc32", "pattern_crc32",
                "observed_crc32", "restored_crc32", "detail",
                "first_partition_lba", "write_attempted"}
    if set(result) != required or result["schema"] != "1":
        raise ValueError("physical result has the wrong schema")
    return result


def reset_and_wait(reset: list[str], url: str) -> dict:
    before = wait_keyboard(url)
    subprocess.run(reset, check=True)
    return wait_keyboard(url, old_boot=before["boot"])


def read_json(url: str, path: str, timeout: float = 5) -> dict:
    with urlopen(url.rstrip("/") + path, timeout=timeout) as response:
        return json.load(response)


def bridge_reset(config: dict, url: str, output: Path) -> dict:
    before = wait_keyboard(url)
    request = Request(
        config["reset_url"], method="POST",
        headers={"Content-Type": "application/json", "X-Agon-Reset": "1",
                 "Origin": url.rstrip("/")},
        data=json.dumps({"id": str(uuid.uuid4())}).encode("ascii"),
    )
    with urlopen(request, timeout=10) as response:
        result = json.load(response)
    if result.get("pulse") != "released":
        raise RuntimeError(f"browser reset bridge did not confirm release: {result}")
    after = wait_keyboard(url, old_boot=before["boot"], timeout=60)
    atomic_json(output / "browser-reset.json", {
        "status": "pass", "old_boot": before["boot"], "new_boot": after["boot"],
        "pulse": result["pulse"], "keyboard_ready": after["ready"],
    })
    return after


def capture_text(url: str, timeout: float = 30) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(url.rstrip("/") + "/screen/text", timeout=5) as response:
                if response.status == 200:
                    return response.read().decode("utf-8", "replace")
        except Exception as error:
            if getattr(error, "code", None) not in (202, 409):
                raise
        time.sleep(0.2)
    raise TimeoutError("live P4 screen-text capture did not complete")


def run_p4_smoke(config: dict, receipt: dict, output: Path) -> dict:
    """Exercise the installed P4, EMOS wire, browser assets and reset bridge."""
    output.mkdir(parents=True, exist_ok=False)
    url = config["extender_url"]
    reset = [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/reset_agon.py"),
             "--config", str(Path(config["reset_config"]).resolve(strict=True))]
    started = time.monotonic()
    cleanup_error = None
    try:
        with urlopen(url.rstrip("/") + "/", timeout=5) as response:
            page = response.read().decode("utf-8")
        if "<title>Agon Extender</title>" not in page:
            raise RuntimeError("installed browser asset has the wrong product title")
        if f'name="agon-reset-url" content="{config["reset_url"]}"' not in page:
            raise RuntimeError("installed browser asset does not contain the configured reset bridge")

        bridge_reset(config, url, output)
        marker = "P4QUAL" + uuid.uuid4().hex[:8].upper()
        type_line(url, output / "keyboard-excom.json", "EMOS EXCOM")
        type_line(url, output / "keyboard-clear.json", "VDU 12")
        type_line(url, output / "keyboard-marker.json", "ECHO " + marker)
        display = read_json(url, "/display/status")
        if (not display.get("available") or display.get("width", 0) < 1 or
                display.get("height", 0) < 1 or display.get("colors", 0) < 2):
            raise RuntimeError(f"installed P4 reports an invalid display: {display}")
        text = capture_text(url)
        (output / "screen.txt").write_text(text)
        if marker not in text:
            raise RuntimeError("installed P4 screen capture did not contain injected marker")

        type_line(url, output / "keyboard-legacy.json", "EMOS LEGACY")
        type_line(url, output / "keyboard-sd.json", "EMOS sdserve --fast /")
        client = wait_sd_service(url, output / "sd.json")
        target = "/extender/qualification/live-" + uuid.uuid4().hex + ".bin"
        payload = (receipt["component_commit"] + "\n" + receipt["artifact_sha256"] + "\n").encode()
        try:
            client.make_directory("/extender/qualification", parents=True)
            client.upload(target, payload, True, fast=True)
            if client.download(target) != payload:
                raise RuntimeError("installed P4/EMOS SD round trip changed bytes")
            client.remove(target)
            client.rpc(11)
        finally:
            client.lock.close()
        final = reset_and_wait(reset, url)
        if not final.get("ready") or not final.get("physical_neutral"):
            raise RuntimeError("final reset did not restore admitted neutral input")
        return {
            "id": "installed-p4-integrated-smoke", "component": "integrated",
            "status": "pass", "duration_seconds": time.monotonic() - started,
            "flashed_commit": receipt["component_commit"],
            "flashed_artifact_sha256": receipt["artifact_sha256"],
            "browser_reset": True, "keyboard": True, "excom": True,
            "display_status": display, "screen_marker": marker,
            "sd_round_trip_bytes": len(payload), "startup_restored": True,
        }
    except BaseException:
        try:
            reset_and_wait(reset, url)
        except BaseException as error:
            cleanup_error = repr(error)
        if cleanup_error:
            raise RuntimeError("P4 smoke failed and final startup recovery failed: " + cleanup_error)
        raise


def run_fwbug008(config: dict, receipt: dict, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    receipt_source = Path(receipt["component_snapshot"]).resolve(strict=True)
    if resolve_commit(receipt_source, "HEAD") != receipt["component_commit"]:
        raise RuntimeError("EMOS snapshot no longer matches the flashed commit")
    if subprocess.check_output(["git", "-C", str(receipt_source), "status", "--porcelain"],
                               text=True).strip():
        raise RuntimeError("EMOS snapshot must be clean before fixture build")
    source = clean_snapshot(receipt_source, receipt["component_commit"],
                            output / "source-emos-fixture")
    fixture = source / "projects/fwbug008-physical"
    if not fixture.is_dir():
        raise RuntimeError("flashed EMOS commit does not contain the RP04 physical fixture")
    toolchain = Path(config["builder_repository"]).resolve() / "toolchains/agondev"
    build_log = output / "fixture-build.log"
    with build_log.open("x") as log:
        completed = subprocess.run(
            ["make", "clean", "all", f"AGONDEV_TOOLCHAIN={toolchain}"],
            cwd=fixture, stdout=log, stderr=subprocess.STDOUT,
        )
    if completed.returncode:
        raise RuntimeError("RP04 physical fixture failed to build")
    binary = fixture / "bin/FWBUG008.bin"
    binary_hash = sha256(binary)
    url = config["extender_url"]
    reset = [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/reset_agon.py"),
             "--config", str(Path(config["reset_config"]).resolve(strict=True))]

    # Start from the reviewed default startup, then use the service only long
    # enough to stage the one-shot startup and fixture.
    reset_and_wait(reset, url)
    type_line(url, output / "keyboard-clear.json", "VDU 12")
    type_line(url, output / "keyboard-legacy.json", "EMOS LEGACY")
    type_line(url, output / "keyboard-stage-service.json", "EMOS sdserve --fast /")
    client = wait_sd_service(url, output / "sd-stage.json")
    original_startup = b""
    staged = False
    try:
        original_startup = client.download("/autoexec.txt")
        for directory in ("/extender/fixtures", "/agents/extender/results"):
            require_directory(client, directory)
        target = "/extender/fixtures/FWBUG008.bin"
        close_retained_backup(client, target, output / "prior-fixture-backup.bin")
        client.upload(target, binary.read_bytes(), True, fast=True)
        if client.download(target) != binary.read_bytes():
            raise RuntimeError("RP04 fixture fast transfer failed independent readback")
        close_retained_backup(client, target, output / "replaced-fixture-backup.bin")
        close_retained_backup(client, "/autoexec.txt",
                              output / "prior-autoexec-backup.txt")
        startup = (b"SET KEYBOARD 1\r\nEMOS KEYINPUT extender\r\nVDU 22 3\r\n"
                   b"IFTHERE /agents/extender/results/a10-rp04.txt Then "
                   b"DELETE /agents/extender/results/a10-rp04.txt\r\n"
                   b"LOAD /extender/fixtures/FWBUG008.bin\r\nRUN\r\n"
                   b"EMOS sdserve --fast /\r\n")
        client.upload("/autoexec.txt", startup, True, fast=True)
        if client.download("/autoexec.txt") != startup:
            raise RuntimeError("one-shot startup failed independent readback")
        close_retained_backup(client, "/autoexec.txt", output / "original-autoexec.txt")
        staged = True
        client.rpc(11)
    finally:
        if not staged and original_startup:
            try:
                client.upload("/autoexec.txt", original_startup, True, fast=True)
            except Exception:
                pass
        client.lock.close()

    started = time.monotonic()
    before_test_boot = wait_keyboard(url)["boot"]
    subprocess.run(reset, check=True)
    try:
        client = wait_sd_service(url, output / "sd-result.json", timeout=120)
    except TimeoutError:
        # The fixture disarms its one-shot startup before raw access. One reset
        # therefore enters its recovery service rather than replaying the test.
        wait_keyboard(url, old_boot=before_test_boot)
        recovery_boot = wait_keyboard(url)["boot"]
        subprocess.run(reset, check=True)
        wait_keyboard(url, old_boot=recovery_boot)
        client = wait_sd_service(url, output / "sd-result-recovery.json", timeout=60)
    result_data = b""
    result_error = None
    cleanup_error = None
    try:
        result_data = client.download("/agents/extender/results/a10-rp04.txt")
        (output / "physical-result.txt").write_bytes(result_data)
    except BaseException as error:
        result_error = error
    try:
        client.upload("/autoexec.txt", original_startup, True, fast=True)
        if client.download("/autoexec.txt") != original_startup:
            raise RuntimeError("original startup restoration failed independent readback")
        close_retained_backup(client, "/autoexec.txt", output / "recovery-autoexec.txt")
        client.rpc(11)
    except BaseException as error:
        cleanup_error = error
    finally:
        client.lock.close()
    if cleanup_error:
        raise RuntimeError(f"RP04 collection/startup restoration failed: {cleanup_error}")
    reset_and_wait(reset, url)
    if result_error:
        raise RuntimeError(f"RP04 result collection failed after startup restoration: {result_error}")
    parsed = parse_result(result_data)
    record = {
        "id": "a10-rp04-raw-sd-write", "component": "emos",
        "status": ("infrastructure-error" if parsed["status"] == "infrastructure-error"
                   else "pass" if parsed["status"] == "pass" else "test-failure"),
        "duration_seconds": time.monotonic() - started,
        "flashed_commit": receipt["component_commit"],
        "flashed_artifact_sha256": receipt["artifact_sha256"],
        "fixture_sha256": binary_hash, "oracle": parsed,
        "startup_restored": True,
    }
    if parsed["write_attempted"] == "1" and (
            parsed["restore_rc"] != "0" or parsed["restore_verify_rc"] != "0" or
            parsed["before_crc32"] != parsed["restored_crc32"]):
        record["status"] = "infrastructure-error"
        record["critical"] = "raw sector restoration was not independently verified"
    return record


def notify(config: dict, run: Path, success: bool, detail: str) -> dict:
    command = [str(ROOT / ".venv/bin/python"), str(ROOT / "qualification/notify.py"),
               "--url", config["extender_url"], "--job", str(run / "notification"),
               "--suite-output", str(run), "--expected", "success" if success else "failure"]
    completed = subprocess.run(command)
    # The alert player runs first; leave the durable detailed failure last.
    if not success:
        try:
            type_line(config["extender_url"], run / "failure-screen.json",
                      "ECHO FIRMWARE QUALIFICATION FAILED - " + detail[:40])
        except Exception as error:
            return {"status": "failure", "exit_code": completed.returncode,
                    "screen_error": repr(error)}
    return {"status": "success" if completed.returncode == 0 else "failure",
            "exit_code": completed.returncode}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flash-receipt", required=True, type=Path)
    parser.add_argument("--extender-commit", required=True)
    parser.add_argument("--emos-commit",
                        help="required for a P4 receipt; EMOS commit paired with the retained suite")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "agents/hardware-validation.local.json")
    parser.add_argument("--repair-manifest", type=Path,
                        default=ROOT / "qualification/manifests/hardware.json")
    parser.add_argument("--case", action="append", help="run selected repair case; default all for the flashed component")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = load_config(args.config.resolve(strict=True))
    receipt = json.loads(args.flash_receipt.resolve(strict=True).read_text())
    if receipt.get("schema") != 1 or receipt.get("status") != "verified":
        parser.error("flash receipt is not a verified schema-1 installation")
    if receipt.get("target") not in ("p4", "emos"):
        parser.error("flash receipt has an unsupported target")
    if receipt["target"] == "p4" and not args.emos_commit:
        parser.error("--emos-commit is required when validating a P4 flash receipt")
    manifest = json.loads(args.repair_manifest.resolve(strict=True).read_text())
    validate_repair_manifest(manifest)
    selected = [case for case in manifest["cases"]
                if receipt["target"] in case["applies_to"]]
    if args.case:
        wanted = set(args.case)
        selected = [case for case in selected if case["id"] in wanted]
        missing = wanted - {case["id"] for case in selected}
        if missing:
            parser.error(f"unknown or wrong-component repair cases: {sorted(missing)}")
    if not selected:
        parser.error("firmware acceptance requires at least one applicable installed-hardware case")
    extender_commit = resolve_commit(ROOT, args.extender_commit)
    run = (args.output or ROOT / "agents/hardware-validation" /
           ("qualification-" + utc_stamp() + "-" + extender_commit[:12])).resolve()
    if run.exists() or run.is_symlink():
        parser.error("output must be a fresh nonexisting path")
    run.mkdir(parents=True)
    started_at = utc_stamp()
    atomic_json(run / "request.json", {
        "flash_receipt": str(args.flash_receipt.resolve()),
        "extender_commit": extender_commit,
        "emos_commit": args.emos_commit or receipt.get("component_commit"),
        "hardware_cases": [case["id"] for case in selected],
    })
    started = time.monotonic()
    announce(f"FIRMWARE QUALIFICATION START — offline suite plus {len(selected)} installed-hardware case(s)")
    extender = prepare_extender_snapshot(extender_commit, run)
    if receipt["target"] == "emos":
        emos = Path(receipt["component_snapshot"]).resolve(strict=True)
    else:
        emos_source = Path(config["emos_repository"]).resolve(strict=True)
        emos_commit = resolve_commit(emos_source, args.emos_commit)
        emos = clean_snapshot(emos_source, emos_commit, run / "source-emos")
    announce("RUN canonical offline qualification prerequisite")
    retained = run_retained_suite(extender, emos, run / "retained-suite")
    announce("RETAINED " + retained["status"].upper())

    physical = []
    for case in selected:
        announce("RUN " + case["id"])
        try:
            if case["driver"] == "installed-p4-smoke":
                record = run_p4_smoke(config, receipt, run / case["id"])
            elif case["driver"] == "fwbug008-physical":
                record = run_fwbug008(config, receipt, run / case["id"])
            else:
                raise RuntimeError("unreachable physical driver")
        except BaseException as error:
            record = {"id": case["id"], "applies_to": case["applies_to"],
                      "status": "infrastructure-error", "error": repr(error)}
        physical.append(record)
        atomic_json(run / (case["id"] + ".json"), record)
        announce(record["status"].upper() + " " + case["id"])

    success = retained["status"] == "success" and all(
        item["status"] == "pass" for item in physical
    )
    infrastructure_failed = (retained["status"] == "infrastructure-failure" or
                             any(item["status"] == "infrastructure-error"
                                 for item in physical))
    status = ("success" if success else
              "infrastructure-failure" if infrastructure_failed else "test-failure")
    summary = {
        "schema": 1, "status": status, "started_at": started_at,
        "duration_seconds": time.monotonic() - started,
        "flashed": {key: receipt.get(key) for key in
                    ("target", "component_commit", "build_id", "artifact_sha256")},
        "extender_commit": extender_commit,
        "emos_commit": resolve_commit(emos, "HEAD"),
        "retained_suite": retained, "physical_cases": physical,
        "counts": {
            "pass": sum(item["status"] == "pass" for item in physical),
            "test-failure": sum(item["status"] == "test-failure" for item in physical),
            "infrastructure-error": sum(item["status"] == "infrastructure-error" for item in physical),
        },
    }
    atomic_json(run / "summary.json", summary)
    detail = next((item["id"] for item in physical if item["status"] != "pass"),
                  "retained-suite")
    summary["notification"] = notify(config, run, success, detail)
    atomic_json(run / "summary.json", summary)
    announce("FIRMWARE QUALIFICATION " + status.upper())
    print("Summary: " + str(run / "summary.json"))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
