#!/usr/bin/env python3
"""Run the complete physical suite against verified installed P4 and EMOS."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
RP04_COMPLETION_TIMEOUT = 20
sys.path.insert(0, str(ROOT / "qualification"))
sys.path.insert(0, str(ROOT / "scripts"))
from hardware_validation import (atomic_json, load_config,
                                 keyboard_status, sha256,
                                 type_line as hardware_type_line, utc_stamp, wait_keyboard, wait_sd_service)
from video import VideoSession
from installation import load_receipt
from lifecycle import Session, UnsafeForeground, require_normal_startup, verify_fixtures, stage_new_file

ACTIVE_SESSION = None


def type_line(url: str, journal: Path, line: str) -> dict:
    if ACTIVE_SESSION is not None:
        value = ACTIVE_SESSION.command(journal, line)
        if line.upper().startswith("EMOS LEGACY"):
            ACTIVE_SESSION.route = "legacy"
        elif line.upper().startswith("EMOS EXCOM"):
            ACTIVE_SESSION.route = "excom"
        return value
    return hardware_type_line(url, journal, line)


def select_mode(url: str, journal: Path, mode: int, width: int, height: int, colors: int) -> dict:
    if ACTIVE_SESSION is not None:
        return ACTIVE_SESSION.select_extender_mode(
            dict(mode=mode, width=width, height=height, colors=colors))
    before = read_json(url, "/display/status")
    if (before.get("mode"), before.get("width"), before.get("height")) == (mode, width, height):
        return before
    type_line(url, journal, f"VDU 22 {mode}")
    result = wait_display(url, mode, width, height)
    time.sleep(1.0)
    return result


class UnsafeMainboardState(RuntimeError):
    """The runner must not inject input or reset while resolving this failure."""


def announce(message: str) -> None:
    print(f"[{utc_stamp()}] {message}", flush=True)


def validate_repair_manifest(document: dict) -> None:
    if document.get("schema") != 1 or not isinstance(document.get("cases"), list):
        raise ValueError("repair manifest must use schema 1")
    profiles = document.get("output_profiles", {})
    if set(profiles) != {"browser-video", "native-hdmi"}:
        raise ValueError("explicit browser-video and native-hdmi coverage required")
    for name, profile in profiles.items():
        manual = profile.get("manual_cases")
        if (not profile.get("automated_output_oracle") or not isinstance(manual, list) or
                not manual or len(manual) != len(set(manual)) or
                any(not isinstance(item, str) or not item for item in manual)):
            raise ValueError(f"{name}: automated oracle and distinct manual cases required")
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
        if case.get("driver") not in ("fwbug008-physical", "installed-p4-smoke",
                                      "rp06-mode-transaction"):
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


def notification_blockers(results: list[dict]) -> list[str]:
    return [item["id"] for item in results if item.get("foreground_unsafe")]


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


def unchanged_startup(client, original: bytes, output: Path) -> None:
    if client.download("/autoexec.txt") != original:
        raise UnsafeMainboardState("startup changed; runner will not repair it or reset")
    atomic_json(output / "startup-preservation.json", {
        "status": "unchanged", "sha256": hashlib.sha256(original).hexdigest(),
        "independent_readback": True, "writes": 0})


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
                "first_partition_lba", "write_attempted", "token"}
    if set(result) != required or result["schema"] != "1":
        raise ValueError("physical result has the wrong schema")
    return result


def require_extender_startup(data: bytes) -> None:
    require_normal_startup(data)



def read_json(url: str, path: str, timeout: float = 5) -> dict:
    with urlopen(url.rstrip("/") + path, timeout=timeout) as response:
        return json.load(response)


def bridge_reset(config: dict, url: str, output: Path) -> dict:
    if ACTIVE_SESSION is not None:
        ACTIVE_SESSION.verify_startup()
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
    if ACTIVE_SESSION is not None:
        ACTIVE_SESSION.after_reset(after)
    atomic_json(output / "browser-reset.json", {
        "status": "pass", "old_boot": before["boot"], "new_boot": after["boot"],
        "pulse": result["pulse"], "keyboard_ready": after["ready"],
    })
    return after


def capture_text(url: str, timeout: float = 30) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ACTIVE_SESSION is not None:
            ACTIVE_SESSION.check_boot()
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


def marker_followed_by_prompt(text: str, marker: str) -> bool:
    """Accept only a run-specific marker followed by a visible MOS prompt."""
    visible = [line.rstrip("?").rstrip() for line in text.splitlines()]
    try:
        marker_line = visible.index(marker)
    except ValueError:
        return False
    return any(line.endswith(" *") for line in visible[marker_line + 1:])


def wait_display(url: str, mode: int, width: int, height: int,
                 timeout: float = 30) -> dict:
    deadline = time.monotonic() + timeout
    last = {}
    while time.monotonic() < deadline:
        last = read_json(url, "/display/status")
        if (last.get("available") and last.get("mode") == mode and
                last.get("width") == width and last.get("height") == height):
            return last
        time.sleep(0.2)
    raise TimeoutError(
        f"display did not commit mode {mode} at {width}x{height}: {last}")


def wait_video_geometry(session: VideoSession, output: Path, label: str,
                        width: int, height: int, timeout: float = 30) -> dict:
    deadline = time.monotonic() + timeout
    attempt = 0
    last = {}
    while time.monotonic() < deadline:
        attempt += 1
        last = session.frame(output / f"{label}-{attempt:02d}.evf")
        if (last["width"], last["height"]) == (width, height):
            return last
        time.sleep(0.2)
    raise TimeoutError(
        f"browser video did not publish {width}x{height} for {label}: {last}")


HDMI_FAULTS = ("faults", "underruns", "invalid_blocks", "sequence_errors",
               "cache_errors", "overlap", "first_fault", "first_error")


def hdmi_sample(value: dict) -> dict:
    rolling = value.get("rolling", {})
    if (value.get("output") != "hdmi" or value.get("frame_clock") != "dma-frame-complete" or
            not value.get("available") or min(value.get("output_width", 0), value.get("output_height", 0)) < 1 or
            type(rolling.get("frames")) is not int or
            any(type(rolling.get(key)) is not int or rolling[key] != 0 for key in HDMI_FAULTS)):
        raise RuntimeError(f"HDMI carrier or DMA fault contract failed: {value}")
    return value


def hdmi_progress(url: str, output: Path, timeout: float = 5) -> dict:
    """Observe real DMA progress; this is not a physical pixel/colour oracle."""
    before = hdmi_sample(read_json(url, "/display/status"))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ACTIVE_SESSION is not None:
            ACTIVE_SESSION.check_boot()
        after = hdmi_sample(read_json(url, "/display/status"))
        for key in ("mode", "width", "height", "colors", "output_width", "output_height"):
            if after[key] != before[key]:
                raise RuntimeError("HDMI geometry changed during the progress observation")
        delta = (after["rolling"]["frames"] - before["rolling"]["frames"]) & 0xffffffff
        if 0 < delta < 0x80000000:
            record = {"before": before, "after": after, "dma_frames_advanced": delta,
                      "scope": "committed geometry, DMA progress and zero fault counters; visual review separate"}
            atomic_json(output, record)
            return record
        if delta >= 0x80000000:
            raise RuntimeError("HDMI frame counter restarted or moved backwards")
        time.sleep(0.1)
    raise TimeoutError("HDMI DMA frame-complete counter did not advance")


def output_profile(config: dict) -> str:
    value = config.get("output_profile")
    if value not in ("browser-video", "native-hdmi"):
        raise ValueError("select output_profile explicitly: browser-video or native-hdmi")
    return value


def run_p4_smoke(config: dict, receipt: dict, output: Path) -> dict:
    """Exercise the installed P4, EMOS wire, browser assets and reset bridge."""
    if ACTIVE_SESSION is None:
        raise ValueError("installed-pair smoke requires its coordinated CLI session")
    output.mkdir(parents=True, exist_ok=False)
    url = config["extender_url"]
    started = time.monotonic()
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
        type_line(url, output / "keyboard-excom.json", "EMOS EXCOM --keep-display")
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

        if output_profile(config) == "native-hdmi":
            passed("hdmi-dma-progress", evidence=hdmi_progress(url, output / "hdmi-progress.json"))
        else:
            announce("RUN websocket-video-frames")
            video_dir = output / "video"
            video_dir.mkdir()
            video = []
            with VideoSession(url) as session:
                for index in range(3):
                    video.append(wait_video_geometry(
                        session, video_dir, f"frame-{index + 1}", display["width"], display["height"]))
            if len({item["sequence"] for item in video}) != len(video):
                raise RuntimeError("video endpoint returned a stale frame generation")
            passed("websocket-video-frames", frames=video)

        announce("RUN legacy-mode-handoff")
        type_line(url, output / "keyboard-legacy.json", "EMOS LEGACY --keep-display")
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
        ACTIVE_SESSION.owned_paths.append(target)
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

        # The listener lacks directory operations. Queue MOS cleanup and its
        # following listener together; key delivery is not FAT completion.
        announce("RUN mainboard-sd-cleanup")
        ACTIVE_SESSION.cleanup([target])
        passed("mainboard-sd-cleanup")
        announce("RUN final-startup-recovery")
        final = bridge_reset(config, url, output / "final-reset")
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
            "startup_unchanged": True, "checks": checks,
        }
    except BaseException:
        raise


def run_rp06_mode_transaction(config: dict, receipt: dict, output: Path) -> dict:
    """Exercise common 8/20 commits and the declared output profile oracles."""
    output.mkdir(parents=True, exist_ok=False)
    url = config["extender_url"]
    checks = []
    started = time.monotonic()

    def passed(check_id: str, **evidence) -> None:
        checks.append({"id": check_id, "status": "pass", **evidence})
        atomic_json(output / "checks.json", checks)
        announce("PASS " + check_id)

    def switch(mode: int, width: int, height: int, label: str) -> dict:
        announce(f"Switching the P4 display to mode {mode} ({width}x{height}) for {label}")
        return select_mode(url, output / f"keyboard-{label}.json", mode, width, height, 64)

    try:
        announce("Resetting the Agon and entering ExCom for RP06 mode qualification")
        bridge_reset(config, url, output / "initial-reset")
        legacy_text = capture_text(url)
        type_line(url, output / "keyboard-excom.json", "EMOS EXCOM --keep-display")
        wait_screen(url, lambda text: text != legacy_text,
                    "change after EMOS EXCOM", output / "excom-transition")

        for mode, width, height, label in (
                (8, 320, 240, "browser-absent-mode8"),
                (20, 512, 384, "browser-absent-mode20"),
                (8, 320, 240, "browser-absent-return-mode8")):
            display = switch(mode, width, height, label)
            evidence = {"display": display}
            if output_profile(config) == "native-hdmi":
                evidence["progress"] = hdmi_progress(url, output / f"{label}-dma.json")
            passed("rp06-" + label, **evidence)

        if output_profile(config) == "native-hdmi":
            # Explicit native replacement for the unavailable browser observer:
            # include full-carrier mode96 and fresh rendered text at every edge.
            for mode, width, height, label in (
                    (96, 848, 480, "wide96"), (20, 512, 384, "standard20"),
                    (96, 848, 480, "return-wide96")):
                display = switch(mode, width, height, label)
                marker = "HDMI" + uuid.uuid4().hex[:8].upper()
                type_line(url, output / f"marker-{label}.json", "ECHO " + marker)
                wait_screen(url, lambda text: marker_followed_by_prompt(text, marker),
                            "render the fresh mode marker and following prompt", output / label)
                progress = hdmi_progress(url, output / f"{label}-dma.json")
                passed("rp06-hdmi-" + label, display=display, progress=progress)
        else:
            video_dir = output / "browser-present-video"
            video_dir.mkdir()
            announce("Opening one retained browser-video connection for mode transitions")
            with VideoSession(url) as video:
                frame8 = wait_video_geometry(video, video_dir, "mode8-before", 320, 240)
                passed("rp06-browser-present-mode8", frame=frame8)
                active20 = switch(20, 512, 384, "browser-present-mode20")
                frame20 = wait_video_geometry(video, video_dir, "mode20", 512, 384)
                passed("rp06-browser-present-mode20", display=active20, frame=frame20)
                active8 = switch(8, 320, 240, "browser-present-return-mode8")
                final_frame = wait_video_geometry(video, video_dir, "mode8-after", 320, 240)
                passed("rp06-browser-present-return-mode8", display=active8, frame=final_frame)

        announce("Resetting the Agon and verifying ordinary startup after RP06 transitions")
        final = bridge_reset(config, url, output / "final-reset")
        if not final.get("ready") or not final.get("physical_neutral"):
            raise RuntimeError("RP06 final reset did not restore admitted neutral input")
        passed("rp06-final-startup-recovery")
        return {
            "id": "a10-rp06-mode-transaction", "component": "p4",
            "status": "pass", "duration_seconds": time.monotonic() - started,
            "flashed_commit": receipt["component_commit"],
            "flashed_artifact_sha256": receipt["artifact_sha256"],
            "checks": checks, "startup_unchanged": True,
        }
    except BaseException:
        raise


def run_fwbug008(config: dict, receipt: dict, output: Path) -> dict:
    """Invoke the separately pinned raw-SD app explicitly, never through reset."""
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    checks = []

    def passed(check_id: str, **evidence) -> None:
        checks.append({"id": check_id, "status": "pass", **evidence})
        atomic_json(output / "checks.json", checks)
        announce("PASS " + check_id)

    fixture = config["_fixtures"]["fixtures"]["raw_sd"]
    binary = Path(fixture["binary"])
    if sha256(binary) != fixture["sha256"] or b"/autoexec.txt" in binary.read_bytes():
        raise RuntimeError("raw-SD fixture changed or writes startup")
    passed("emos-receipt-and-fixture-source", fixture_sha256=fixture["sha256"],
           source_files=fixture["source_files"], firmware_source=receipt.get("source"))
    url = config["extender_url"]
    completion_token = uuid.uuid4().hex[:16].upper()
    completion_marker = "A10-RP04 COMPLETE " + completion_token
    target = "/extender/.raw-sd-" + completion_token + ".bin"
    launch_script = "/extender/.raw-sd-" + completion_token + ".txt"
    atomic_json(output / "completion-contract.json", {
        "schema": 1, "token": completion_token, "completion_marker": completion_marker,
        "launch": "explicit CLI RUN; never boot/reset",
        "meaning": "COMPLETE plus a later prompt proves the app returned; result separately proves restoration",
    })
    type_line(url, output / "keyboard-legacy.json", "EMOS LEGACY --keep-display")
    type_line(url, output / "keyboard-stage-service.json", "EMOS sdserve --fast /")
    client = wait_sd_service(url, output / "sd-stage.json", require_fast=True)
    try:
        original_startup = client.download("/autoexec.txt")
        require_extender_startup(original_startup)
        for directory in ("/extender", "/agents/extender/results"):
            require_directory(client, directory)
        # Preserve the maintained fixture's preceding evidence before it writes
        # this owned result name. Per-run tokens reject stale results.
        from sdcard import RemoteError
        try:
            (output / "previous-physical-result.txt").write_bytes(
                client.download("/agents/extender/results/a10-rp04.txt"))
        except RemoteError as error:
            if error.status != 6:
                raise
        stage_new_file(client, target, binary.read_bytes())
        stage_new_file(client, launch_script,
                       (f"LOAD {target}\r\nRUN . {completion_token}\r\n").encode("ascii"))
        if ACTIVE_SESSION:
            ACTIVE_SESSION.owned_paths.extend((target, launch_script))
        client.rpc(11)
    finally:
        client.lock.close()
    passed("emos-fixture-staging")
    type_line(url, output / "keyboard-excom.json", "EMOS EXCOM --keep-display")
    # This is an EMOS SD API test, with resolution-independent output. Native
    # mode20 fits its token/prompt and belongs to the declared HDMI profile.
    # R02 exposed a real mode3 clear/scanout fault before raw I/O; preserve that
    # limitation separately rather than making this API fixture exercise an
    # additional, unqualified 640x240 double-scan presentation. No timing/fault
    # guard or sector oracle is relaxed. Browser output retains its mode3 path.
    raw_mode = (20, 512, 384, 64) if output_profile(config) == "native-hdmi" else (3, 640, 240, 64)
    select_mode(url, output / "keyboard-mode.json", *raw_mode)
    type_line(url, output / "keyboard-clear.json", "VDU 12")
    # The marker is printed by the fixture after every raw operation has ended.
    # Do not use an ECHO/prompt before RUN as proof of post-RUN handback.
    # MOS orders LOAD completion before RUN. Keyboard delivery cannot prove a
    # preceding file load returned; early RUN characters can otherwise be lost.
    type_line(url, output / "keyboard-run.json", "EXEC " + launch_script)
    try:
        text = wait_screen(
            url, lambda text: marker_followed_by_prompt(text, completion_marker),
            "show the per-run completion token followed by a MOS prompt",
            output / "completion-transition", timeout=RP04_COMPLETION_TIMEOUT)
        (output / "completion-screen.txt").write_text(text)
    except BaseException as error:
        if ACTIVE_SESSION:
            ACTIVE_SESSION.unsafe = True
        raise UnsafeMainboardState(
            "RP04 gave no safe-completion handoff; no further input was sent and Agon was not reset"
        ) from error
    passed("emos-fixture-completion-handoff", token=completion_token)

    announce("Fixture returned to MOS; starting the host-owned result listener")
    type_line(url, output / "keyboard-result-legacy.json", "EMOS LEGACY --keep-display")
    type_line(url, output / "keyboard-result-service.json", "EMOS sdserve --fast /")
    try:
        client = wait_sd_service(url, output / "sd-result.json", timeout=RP04_COMPLETION_TIMEOUT,
                                 require_fast=True)
    except BaseException as error:
        if ACTIVE_SESSION:
            ACTIVE_SESSION.unsafe = True
        raise UnsafeMainboardState("RP04 result service handback is uncertain; no reset attempted") from error
    try:
        data = client.download("/agents/extender/results/a10-rp04.txt")
        (output / "physical-result.txt").write_bytes(data)
        unchanged_startup(client, original_startup, output)
        client.rpc(11)
    finally:
        client.lock.close()
    parsed = parse_result(data)
    if parsed["token"] != completion_token:
        raise RuntimeError("RP04 result token does not match the invocation")
    restored = parsed["write_attempted"] == "0" or (
        parsed["restore_rc"] == "0" and parsed["restore_verify_rc"] == "0" and
        parsed["before_crc32"] == parsed["restored_crc32"])
    if not restored:
        if ACTIVE_SESSION:
            ACTIVE_SESSION.unsafe = True
        raise UnsafeMainboardState("raw sector restoration was not independently verified")
    if parsed["status"] == "pass":
        if (parsed["sector"] != "2" or parsed["write_attempted"] != "1" or
                int(parsed["first_partition_lba"]) <= 2 or parsed["test_rc"] != "0" or
                parsed["pattern_crc32"] != parsed["observed_crc32"]):
            raise RuntimeError("raw-SD pass result contradicts its test oracles")
        passed("emos-raw-sector-write-read-restore", oracle=parsed)
    passed("emos-startup-unchanged")
    return {"id": "a10-rp04-raw-sd-write", "component": "emos",
            "status": "pass" if parsed["status"] == "pass" else "test-failure",
            "duration_seconds": time.monotonic() - started,
            "flashed_commit": receipt["component_commit"],
            "flashed_artifact_sha256": receipt["artifact_sha256"],
            "fixture_sha256": fixture["sha256"], "oracle": parsed,
            "startup_unchanged": True, "checks": checks}


def notify(config: dict, run: Path, success: bool, detail: str) -> dict:
    command = [str(ROOT / ".venv/bin/python"), str(ROOT / "qualification/notify.py"),
               "--url", config["extender_url"], "--job", str(run / "notification"),
               "--suite-output", str(run), "--expected", "success" if success else "failure"]
    if ACTIVE_SESSION is not None:
        ACTIVE_SESSION.check_boot()
        command += ["--expected-boot", str(ACTIVE_SESSION.boot)]
    completed = subprocess.run(command)
    # The alert player runs first; leave the durable detailed failure last.
    if not success:
        try:
            type_line(config["extender_url"], run / "failure-screen.json",
                      "ECHO Firmware qualification failed - " + detail[:40])
        except Exception as error:
            return {"status": "failure", "exit_code": completed.returncode,
                    "screen_error": repr(error)}
    return {"status": "success" if completed.returncode == 0 else "failure",
            "exit_code": completed.returncode}


def main() -> int:
    global ACTIVE_SESSION
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
    parser.add_argument("--fixtures", required=True, type=Path,
                        help="offline-built fixtures.json from qualification/build_fixtures.py")
    parser.add_argument("--check-only", action="store_true",
                        help="validate retained bytes, fixtures and plan offline; never contact boards")
    parser.add_argument("--bench-ready", action="store_true",
                        help="operator confirms exclusive bench, Legacy idle CLI, exact installed pair and commissioned reset")
    args = parser.parse_args()
    config = load_config(args.config.resolve(strict=True))
    receipts = {}
    receipt_paths = {}
    for path in args.flash_receipt:
        resolved = path.resolve(strict=True)
        receipt = load_receipt(resolved)
        target = receipt.get("target")
        if target not in ("p4", "emos") or target in receipts:
            parser.error(f"duplicate or unsupported flash-receipt target: {target}")
        receipts[target] = receipt
        receipt_paths[target] = str(resolved)
    manifest = json.loads(args.repair_manifest.resolve(strict=True).read_text())
    validate_repair_manifest(manifest)
    profile = output_profile(config)
    fixtures = verify_fixtures(args.fixtures.resolve(strict=True))
    config["_fixtures"] = fixtures
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
    if args.check_only:
        print(json.dumps({"status": "offline-preparation-verified", "hardware_contacted": False,
                          "profile": profile, "cases": [c["id"] for c in selected],
                          "required_automated_checks": sum(c["required_checks"] for c in selected),
                          "manual_cases": manifest["output_profiles"][profile]["manual_cases"],
                          "installed_pair_freshly_verified": False,
                          "hardware_ready": False,
                          "remaining": ["exclusive bench and verified idle CLI", "current paired identities",
                                        "commissioned reset and fixture deployment", "physical execution and Author review"]}, indent=2))
        return 0
    if not args.bench_ready:
        parser.error("hardware execution requires --bench-ready after exclusive bench/CLI/identity/reset preflight")
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
        "output_profile": profile, "fixtures": str(args.fixtures.resolve()),
        "operator_preflight_confirmed": True,
    })
    started = time.monotonic()
    announce(f"{'Targeted diagnostic' if args.case else 'Complete installed-pair qualification'} start — {len(selected)} hardware case(s)")

    preparation_started = time.monotonic()
    try:
        session = Session(config, run, fixtures)
        ACTIVE_SESSION = session
        session.prepare()
        if "emos" in receipts:
            announce("Verifying the complete current EMOS ROM before physical cases")
            session.verify_emos_rom(receipts["emos"])
    except BaseException as error:
        atomic_json(run / "summary.json", {"status": "preparation-failure", "error": repr(error),
                    "hardware_cases_invoked": False, "started_at": started_at, "ended_at": utc_stamp(),
                    "duration_seconds": time.monotonic() - started,
                    "notification": "not sent; foreground requires reconciliation"})
        ACTIVE_SESSION = None
        return 1
    preparation_seconds = time.monotonic() - preparation_started
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
        case_started = time.monotonic()
        case_started_at = utc_stamp()
        try:
            receipt = receipts[case["receipt_target"]]
            if case["driver"] == "installed-p4-smoke":
                record = run_p4_smoke(config, receipt, run / case["id"])
            elif case["driver"] == "rp06-mode-transaction":
                record = run_rp06_mode_transaction(config, receipt, run / case["id"])
            elif case["driver"] == "fwbug008-physical":
                record = run_fwbug008(config, receipt, run / case["id"])
            else:
                raise RuntimeError("unreachable physical driver")
        except BaseException as error:
            record = {"id": case["id"], "applies_to": case["applies_to"],
                      "status": "infrastructure-error", "error": repr(error)}
            # A failed physical driver may leave uncertain command/service
            # ownership. No dependent test, reset or notification can assume CLI.
            record["foreground_unsafe"] = True
            session.unsafe = True
            checks_path = run / case["id"] / "checks.json"
            if checks_path.is_file():
                record["checks"] = json.loads(checks_path.read_text())
        if (record["status"] == "pass" and
                len(record.get("checks", ())) != case["required_checks"]):
            record["status"] = "infrastructure-error"
            record["error"] = (f"case reported {len(record.get('checks', ()))} checks; "
                               f"manifest requires {case['required_checks']}")
        physical.append(record)
        record.update(started_at=case_started_at, ended_at=utc_stamp(),
                      total_case_seconds=time.monotonic() - case_started)
        results_by_id[case["id"]] = record
        atomic_json(run / (case["id"] + ".json"), record)
        announce(record["status"].upper() + " " + case["id"])

    restoration_started = time.monotonic()
    restoration = {"status": "blocked", "reason": "unsafe foreground"}
    if not session.unsafe:
        try:
            session.restore()
            restoration = {"status": "verified"}
        except BaseException as error:
            restoration = {"status": "failed", "error": repr(error)}
            session.unsafe = True
    restoration["duration_seconds"] = time.monotonic() - restoration_started
    success = all(item["status"] == "pass" for item in physical) and restoration["status"] == "verified"
    infrastructure_failed = (restoration["status"] != "verified" or
                             any(item["status"] == "infrastructure-error" for item in physical))
    status = ("success" if success else
              "infrastructure-failure" if infrastructure_failed else "test-failure")
    summary = {
        "output_profile": profile, "full_suite": not bool(args.case),
        "qualification_state": "awaiting-author-review" if success and not args.case else "not-qualified",
        "manual_cases_required": manifest["output_profiles"][profile]["manual_cases"],
        "restoration": restoration,
        "preparation_seconds": preparation_seconds,
        "clock": "host monotonic seconds; operational timing, not independently calibrated",
        "schema": 1, "status": status, "started_at": started_at,
        "duration_seconds": time.monotonic() - started,
        "flashed": {target: {key: receipt.get(key) for key in
                    ("target", "component_commit", "build_id", "artifact_sha256",
                     "installed_readback_sha256", "source", "verification_scope")}
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
    blockers = notification_blockers(physical)
    if session.unsafe and not blockers:
        blockers = ["lifecycle-restoration"]
    if blockers:
        summary["notification"] = {
            "status": "skipped", "reason": "unsafe-mainboard-foreground",
            "blocked_by": blockers,
            "detail": "No reset or keyboard input was sent after ambiguous fixture completion",
        }
        announce("NOTIFICATION SKIPPED — unsafe mainboard foreground: " +
                 ", ".join(blockers))
    else:
        notification_started = time.monotonic()
        summary["notification"] = notify(config, run, success, detail)
        summary["notification"]["duration_seconds"] = time.monotonic() - notification_started
        if summary["notification"]["status"] != "success":
            summary["status"] = "infrastructure-failure"
            summary["qualification_state"] = "not-qualified"
            success = False
        # Verify without changing modes or clearing the terminal spoken cue.
        # A player that changes entry modes fails qualification, not a silent
        # post-notification mode repair.
        try:
            session.verify_entry()
            session.cleanup()
            type_line(config["extender_url"], run / "terminal-verdict.json",
                      "ECHO Qualification " + ("automated checks passed; visual review pending" if success else "failed"))
        except BaseException as error:
            summary["notification"]["restoration_error"] = repr(error)
            summary["status"] = "infrastructure-failure"
            summary["qualification_state"] = "not-qualified"
            success = False
    summary["total_duration_seconds"] = time.monotonic() - started
    summary["ended_at"] = utc_stamp()
    atomic_json(run / "summary.json", summary)
    ACTIVE_SESSION = None
    announce("Firmware automated qualification " + summary["status"])
    print("Summary: " + str(run / "summary.json"))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
