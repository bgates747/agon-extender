#!/usr/bin/env python3
"""Run the complete physical suite against verified installed P4 and EMOS."""

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
sys.path.insert(0, str(ROOT / "qualification"))
sys.path.insert(0, str(ROOT / "scripts"))
from hardware_validation import (atomic_json, clean_snapshot, load_config,
                                 resolve_commit, sha256,
                                 type_line, utc_stamp, wait_keyboard, wait_sd_service)
from video import capture as capture_video


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
        if case.get("receipt_target") not in ("emos", "p4"):
            raise ValueError(f"{case_id}: invalid receipt_target")
        if not isinstance(case.get("required_checks"), int) or case["required_checks"] < 1:
            raise ValueError(f"{case_id}: invalid required_checks")
        if case.get("acceptance_required") is not True:
            raise ValueError(f"{case_id}: every canonical hardware case must be acceptance-required")
        if not isinstance(case.get("timeout_seconds"), int) or case["timeout_seconds"] < 1:
            raise ValueError(f"{case_id}: positive integer timeout required")
    if len(ids) != len(set(ids)):
        raise ValueError("repair case ids must be unique")
    preceding_ids = set()
    for case in document["cases"]:
        case_id = case["id"]
        dependencies = case.get("depends_on", [])
        if (not isinstance(dependencies, list) or
                len(dependencies) != len(set(dependencies)) or
                any(item not in preceding_ids for item in dependencies)):
            raise ValueError(f"{case_id}: depends_on must name unique preceding cases")
        preceding_ids.add(case_id)


def unmet_dependencies(case: dict, results_by_id: dict) -> list[str]:
    return [dependency for dependency in case.get("depends_on", [])
            if results_by_id.get(dependency, {}).get("status") != "pass"]


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


def wait_screen(url: str, predicate, description: str, output: Path,
                timeout: float = 45) -> str:
    """Request fresh captures until an observable screen condition is true."""
    output.mkdir(parents=True, exist_ok=False)
    deadline = time.monotonic() + timeout
    attempt = 0
    last = "no capture"
    while time.monotonic() < deadline:
        attempt += 1
        remaining = max(1.0, deadline - time.monotonic())
        last = capture_text(url, timeout=min(remaining, 15))
        (output / f"screen-{attempt:02d}.txt").write_text(last)
        if predicate(last):
            return last
        time.sleep(0.25)
    raise TimeoutError(f"screen did not {description}; last capture was saved")


def run_p4_smoke(config: dict, receipt: dict, output: Path) -> dict:
    """Exercise the installed P4, EMOS wire, browser assets and reset bridge."""
    output.mkdir(parents=True, exist_ok=False)
    url = config["extender_url"]
    reset = [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/reset_agon.py"),
             "--config", str(Path(config["reset_config"]).resolve(strict=True))]
    started = time.monotonic()
    cleanup_error = None
    checks = []

    def passed(check_id: str, **evidence) -> None:
        checks.append({"id": check_id, "status": "pass", **evidence})
        atomic_json(output / "checks.json", checks)
        announce("PASS " + check_id)

    try:
        announce("RUN p4-web-assets")
        with urlopen(url.rstrip("/") + "/", timeout=5) as response:
            page = response.read().decode("utf-8")
        if "<title>Agon Extender</title>" not in page:
            raise RuntimeError("installed browser asset has the wrong product title")
        if f'name="agon-reset-url" content="{config["reset_url"]}"' not in page:
            raise RuntimeError("installed browser asset does not contain the configured reset bridge")
        passed("p4-web-assets")

        announce("RUN agon-reset-and-keyboard-readmission")
        bridge_reset(config, url, output)
        passed("agon-reset-and-keyboard-readmission")
        announce("RUN legacy-screen-capture")
        legacy_text = capture_text(url)
        (output / "screen-legacy-before.txt").write_text(legacy_text)
        passed("legacy-screen-capture", bytes=len(legacy_text.encode()))
        marker = "P4QUAL" + uuid.uuid4().hex[:8].upper()
        announce("RUN excom-mode-handoff")
        type_line(url, output / "keyboard-excom.json", "EMOS EXCOM")
        excom_text = wait_screen(
            url, lambda text: text != legacy_text,
            "change after EMOS EXCOM", output / "excom-transition")
        (output / "screen-excom-before-clear.txt").write_text(excom_text)
        passed("excom-mode-handoff")
        announce("RUN excom-clear")
        type_line(url, output / "keyboard-clear.json", "VDU 12")
        # A complete fresh capture is also a parser-progress barrier. The clear
        # can legitimately leave an already blank screen byte-for-byte equal.
        cleared_text = capture_text(url)
        (output / "screen-after-clear.txt").write_text(cleared_text)
        passed("excom-clear")
        announce("RUN excom-keyboard-and-text-render")
        type_line(url, output / "keyboard-marker.json", "ECHO " + marker)
        display = read_json(url, "/display/status")
        if (not display.get("available") or display.get("width", 0) < 1 or
                display.get("height", 0) < 1 or display.get("colors", 0) < 2):
            raise RuntimeError(f"installed P4 reports an invalid display: {display}")
        text = wait_screen(
            url, lambda captured: marker in captured,
            "contain the injected marker", output / "marker-transition")
        (output / "screen.txt").write_text(text)
        passed("excom-keyboard-and-text-render", marker=marker)
        announce("RUN display-status-contract")
        passed("display-status-contract", mode=display["mode"], width=display["width"],
               height=display["height"], colors=display["colors"])

        announce("RUN websocket-video-frames")
        video = capture_video(url, output / "video", 3)
        if any((item["width"], item["height"]) !=
               (display["width"], display["height"]) for item in video):
            raise RuntimeError("video frames disagree with display status geometry")
        passed("websocket-video-frames", frames=video)

        announce("RUN legacy-mode-handoff")
        type_line(url, output / "keyboard-legacy.json", "EMOS LEGACY")
        # Completing a capture requested after the handoff gives EMOS/P4 time
        # to consume the mode command before keyboard input is routed to Legacy.
        legacy_handoff = capture_text(url)
        (output / "screen-after-legacy-handoff.txt").write_text(legacy_handoff)
        passed("legacy-mode-handoff")
        announce("RUN mainboard-sd-service")
        type_line(url, output / "keyboard-sd.json", "EMOS sdserve --fast /")
        client = wait_sd_service(url, output / "sd.json")
        passed("mainboard-sd-service")
        target = "/extender/.qualification-" + uuid.uuid4().hex + ".bin"
        payload = (receipt["component_commit"] + "\n" + receipt["artifact_sha256"] + "\n").encode()
        try:
            announce("RUN mainboard-sd-round-trip")
            client.upload(target, payload, True, fast=True)
            if client.download(target) != payload:
                raise RuntimeError("installed P4/EMOS SD round trip changed bytes")
            client.rpc(11)
            passed("mainboard-sd-round-trip", bytes=len(payload))
        finally:
            client.lock.close()

        # The production listener predates directory capability 0x20, so its
        # wire protocol cannot remove even a single file. Use MOS's independent
        # file command, then restart the listener to verify absence remotely.
        announce("RUN mainboard-sd-cleanup")
        type_line(url, output / "keyboard-delete.json", "DELETE " + target)
        delete_barrier = capture_text(url)
        (output / "screen-after-delete.txt").write_text(delete_barrier)
        type_line(url, output / "keyboard-cleanup-sd.json", "EMOS sdserve --fast /")
        cleanup = wait_sd_service(url, output / "sd-cleanup.json")
        try:
            from sdcard import RemoteError
            try:
                cleanup.download(target)
            except RemoteError as error:
                if error.status != 6:
                    raise
            else:
                raise RuntimeError("MOS DELETE left the temporary qualification file present")
            cleanup.rpc(11)
            passed("mainboard-sd-cleanup")
        finally:
            cleanup.lock.close()
        announce("RUN final-startup-recovery")
        final = reset_and_wait(reset, url)
        if not final.get("ready") or not final.get("physical_neutral"):
            raise RuntimeError("final reset did not restore admitted neutral input")
        passed("final-startup-recovery")
        return {
            "id": "installed-p4-integrated-smoke", "component": "integrated",
            "status": "pass", "duration_seconds": time.monotonic() - started,
            "flashed_commit": receipt["component_commit"],
            "flashed_artifact_sha256": receipt["artifact_sha256"],
            "browser_reset": True, "keyboard": True, "excom": True,
            "display_status": display, "screen_marker": marker,
            "sd_round_trip_bytes": len(payload), "sd_cleanup_verified": True,
            "startup_restored": True, "checks": checks,
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
    checks = []

    def passed(check_id: str, **evidence) -> None:
        checks.append({"id": check_id, "status": "pass", **evidence})
        atomic_json(output / "checks.json", checks)
        announce("PASS " + check_id)

    announce("RUN emos-receipt-and-fixture-source")
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
    passed("emos-receipt-and-fixture-source", fixture_sha256=binary_hash)
    url = config["extender_url"]
    reset = [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/reset_agon.py"),
             "--config", str(Path(config["reset_config"]).resolve(strict=True))]

    # Start from the reviewed default startup, then use the service only long
    # enough to stage the one-shot startup and fixture.
    announce("RUN emos-fixture-staging")
    announce("Resetting the Agon and waiting for Extender keyboard admission before staging")
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
        announce("Fixture transfer verified; staging the one-shot startup file")
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
        passed("emos-fixture-staging")
    finally:
        if not staged and original_startup:
            try:
                client.upload("/autoexec.txt", original_startup, True, fast=True)
            except Exception:
                pass
        client.lock.close()

    announce("RUN emos-raw-sector-write-read-restore")
    started = time.monotonic()
    before_test_boot = wait_keyboard(url)["boot"]
    announce("Resetting the Agon to run the one-shot raw-sector fixture")
    subprocess.run(reset, check=True)
    try:
        announce("Waiting up to 120 seconds for the fixture result listener; no output is expected during execution")
        client = wait_sd_service(url, output / "sd-result.json", timeout=120)
    except TimeoutError:
        # The fixture disarms its one-shot startup before raw access. One reset
        # therefore enters its recovery service rather than replaying the test.
        announce("The first result listener did not appear; waiting for fixture boot completion before guarded recovery")
        wait_keyboard(url, old_boot=before_test_boot)
        recovery_boot = wait_keyboard(url)["boot"]
        announce("Resetting the Agon once to enter the disarmed recovery startup")
        subprocess.run(reset, check=True)
        wait_keyboard(url, old_boot=recovery_boot)
        announce("Waiting up to 60 seconds for the recovery result listener")
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
        announce("Restoring and independently verifying the original startup file")
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
    announce("Resetting the Agon and verifying ordinary startup after result collection")
    reset_and_wait(reset, url)
    if result_error:
        raise RuntimeError(f"RP04 result collection failed after startup restoration: {result_error}")
    parsed = parse_result(result_data)
    if parsed["status"] == "pass":
        passed("emos-raw-sector-write-read-restore", sector=int(parsed["sector"]),
               before_crc32=parsed["before_crc32"], pattern_crc32=parsed["pattern_crc32"])
    announce("RUN emos-startup-restoration")
    passed("emos-startup-restoration")
    record = {
        "id": "a10-rp04-raw-sd-write", "component": "emos",
        "status": ("infrastructure-error" if parsed["status"] == "infrastructure-error"
                   else "pass" if parsed["status"] == "pass" else "test-failure"),
        "duration_seconds": time.monotonic() - started,
        "flashed_commit": receipt["component_commit"],
        "flashed_artifact_sha256": receipt["artifact_sha256"],
        "fixture_sha256": binary_hash, "oracle": parsed,
        "startup_restored": True, "checks": checks,
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
    parser.add_argument("--flash-receipt", required=True, action="append", type=Path,
                        help="verified receipt; repeat once each for P4 and EMOS")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "agents/hardware-validation.local.json")
    parser.add_argument("--repair-manifest", type=Path,
                        default=ROOT / "qualification/manifests/hardware.json")
    parser.add_argument("--case", action="append",
                        help="targeted diagnostic only; default runs the full paired-component suite")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = load_config(args.config.resolve(strict=True))
    receipts = {}
    receipt_paths = {}
    for path in args.flash_receipt:
        resolved = path.resolve(strict=True)
        receipt = json.loads(resolved.read_text())
        if receipt.get("schema") != 1 or receipt.get("status") != "verified":
            parser.error(f"{path}: not a verified schema-1 installation")
        target = receipt.get("target")
        if target not in ("p4", "emos") or target in receipts:
            parser.error(f"duplicate or unsupported flash-receipt target: {target}")
        receipts[target] = receipt
        receipt_paths[target] = str(resolved)
    manifest = json.loads(args.repair_manifest.resolve(strict=True).read_text())
    validate_repair_manifest(manifest)
    selected = [case for case in manifest["cases"]
                if case["receipt_target"] in receipts]
    if args.case:
        wanted = set(args.case)
        selected = [case for case in selected if case["id"] in wanted]
        missing = wanted - {case["id"] for case in selected}
        if missing:
            parser.error(f"unknown or wrong-component repair cases: {sorted(missing)}")
    if not args.case and set(receipts) != {"p4", "emos"}:
        parser.error("full qualification requires verified P4 and EMOS flash receipts")
    if not selected:
        parser.error("firmware acceptance requires at least one applicable installed-hardware case")
    run = (args.output or ROOT / "agents/hardware-validation" /
           ("qualification-" + utc_stamp() + "-" +
            "-".join(receipts[key]["component_commit"][:8] for key in sorted(receipts)))).resolve()
    if run.exists() or run.is_symlink():
        parser.error("output must be a fresh nonexisting path")
    run.mkdir(parents=True)
    started_at = utc_stamp()
    atomic_json(run / "request.json", {
        "flash_receipts": receipt_paths,
        "hardware_cases": [case["id"] for case in selected],
    })
    started = time.monotonic()
    announce(f"FULL INSTALLED-SYSTEM QUALIFICATION START — {len(selected)} hardware case(s)")

    physical = []
    results_by_id = {}
    for case in selected:
        blocked_by = unmet_dependencies(case, results_by_id)
        if blocked_by:
            record = {
                "id": case["id"], "applies_to": case["applies_to"],
                "status": "blocked", "blocked_by": blocked_by,
                "error": "prerequisite physical case did not pass",
            }
            physical.append(record)
            results_by_id[case["id"]] = record
            atomic_json(run / (case["id"] + ".json"), record)
            announce("BLOCKED " + case["id"] + " — prerequisite: " + ", ".join(blocked_by))
            continue
        announce("RUN " + case["id"])
        try:
            receipt = receipts[case["receipt_target"]]
            if case["driver"] == "installed-p4-smoke":
                record = run_p4_smoke(config, receipt, run / case["id"])
            elif case["driver"] == "fwbug008-physical":
                record = run_fwbug008(config, receipt, run / case["id"])
            else:
                raise RuntimeError("unreachable physical driver")
        except BaseException as error:
            record = {"id": case["id"], "applies_to": case["applies_to"],
                      "status": "infrastructure-error", "error": repr(error)}
            checks_path = run / case["id"] / "checks.json"
            if checks_path.is_file():
                record["checks"] = json.loads(checks_path.read_text())
        if (record["status"] == "pass" and
                len(record.get("checks", ())) != case["required_checks"]):
            record["status"] = "infrastructure-error"
            record["error"] = (f"case reported {len(record.get('checks', ()))} checks; "
                               f"manifest requires {case['required_checks']}")
        physical.append(record)
        results_by_id[case["id"]] = record
        atomic_json(run / (case["id"] + ".json"), record)
        announce(record["status"].upper() + " " + case["id"])

    success = all(item["status"] == "pass" for item in physical)
    infrastructure_failed = any(item["status"] == "infrastructure-error"
                                for item in physical)
    status = ("success" if success else
              "infrastructure-failure" if infrastructure_failed else "test-failure")
    summary = {
        "schema": 1, "status": status, "started_at": started_at,
        "duration_seconds": time.monotonic() - started,
        "flashed": {target: {key: receipt.get(key) for key in
                    ("target", "component_commit", "build_id", "artifact_sha256")}
                    for target, receipt in receipts.items()},
        "physical_cases": physical,
        "counts": {
            "pass": sum(item["status"] == "pass" for item in physical),
            "test-failure": sum(item["status"] == "test-failure" for item in physical),
            "infrastructure-error": sum(item["status"] == "infrastructure-error" for item in physical),
            "blocked": sum(item["status"] == "blocked" for item in physical),
        },
        "check_counts": {
            "pass": sum(len(item.get("checks", ())) for item in physical),
            "required": sum(case["required_checks"] for case in selected),
        },
    }
    atomic_json(run / "summary.json", summary)
    detail = next((item["id"] for item in physical if item["status"] != "pass"),
                  "installed-hardware")
    summary["notification"] = notify(config, run, success, detail)
    atomic_json(run / "summary.json", summary)
    announce("FIRMWARE QUALIFICATION " + status.upper())
    print("Summary: " + str(run / "summary.json"))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
