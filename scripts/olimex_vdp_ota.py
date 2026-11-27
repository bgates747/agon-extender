"""Ordinary Agon Flash staging, invocation and independent mainboard readback."""

from hashlib import sha256
from pathlib import Path
import struct
import subprocess
import sys
import time
import zlib

from bench_process import read, record
from olimex_cli import Observer, returned_output
from olimex_flash import LAYOUTS, mainboard_rom
from olimex_p4_app import reboot_pair
from passive_serial import open_passive_serial
from reset_agon import wait_boot
from reset_agon_usb import pulse


FLASH_PATH = "/mos/flash.bin"
FLASH_BYTES = 15624
FLASH_SHA = "480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57"
FLASH_BANNER = b"Agon firmware update utility v1.9"
FLASH_PROMPT = b"Flash firmware (y/n)?"
REBOOT_NOTICE = b"Rebooting in 3...2...1...0!"
SELECTOR, APP0, CAPACITY = LAYOUTS["mainboard"]
SLOTS = {0: APP0, 1: APP0 + CAPACITY}
COMPANIONS = {"p4": "p4_app_sha256", "emos": "emos_rom_sha256"}


def spec_for(kit):
    spec = kit.get("firmware", {}).get("mainboard")
    return spec if spec and spec.get("method") == "agon-flash" else None


def staging_path(target, selection):
    return f"{target.install_dir}/{selection}-vdp.bin"


def validate(spec, pinned):
    fields = {"method", "candidate_app", "restore_app", "partition_table",
              "candidate_slot", "restore_slot"}
    if set(spec) != fields or any(type(spec[name]) is not int for name in ("candidate_slot", "restore_slot")):
        raise ValueError("Agon Flash requires raw apps, a partition-table pin and explicit integer OTA slots")
    if {spec["candidate_slot"], spec["restore_slot"]} != set(SLOTS):
        raise ValueError("Agon Flash requires distinct candidate and restore OTA slots")
    table = pinned(spec["partition_table"])
    if len(table) != 0xC00:
        raise ValueError("Agon Flash needs the classic ESP32 partition table")
    entries = []
    for pos in range(0, len(table), 32):
        magic, typ, subtype, address, length, _, flags = struct.unpack_from("<HBBII16sI", table, pos)
        if magic != 0x50AA:
            if magic not in (0xEBEB, 0xFFFF):
                raise ValueError("Unrecognized classic ESP32 partition entry")
            break
        entries.append((typ, subtype, address, length, flags))
    apps = [entry for entry in entries if entry[0] == 0]
    expected = [(0, 0x10 + slot, address, CAPACITY, 0) for slot, address in SLOTS.items()]
    selectors = [entry for entry in entries if entry[:2] == (1, 0)]
    if sorted(apps) != expected or selectors != [(1, 0, SELECTOR, 0x2000, 0)]:
        raise ValueError("Partition table differs from the commissioned two-slot OTA layout")
    for selection in ("candidate", "restore"):
        image = pinned(spec[f"{selection}_app"])
        if not 0 < len(image) <= CAPACITY or image[0] != 0xE9:
            raise ValueError(f"Agon Flash {selection} app does not fit its OTA slot")


def selected_slot(selector):
    if len(selector) != 0x2000:
        raise RuntimeError("Short OTA selector read")
    if selector == b"\xff" * len(selector):
        return 0
    entries = []
    for offset in (0, 0x1000):
        row = selector[offset:offset + 32]
        sequence, state, checksum = struct.unpack("<I20xII", row)
        if (sequence not in (0, 0xFFFFFFFF) and state not in (3, 4)
                and checksum == zlib.crc32(row[:4], 0xFFFFFFFF)):
            entries.append((sequence, state))
    if not entries or len({sequence for sequence, _ in entries}) != len(entries):
        raise RuntimeError("Ambiguous OTA selector")
    sequence, state = max(entries)
    if state not in (2, 0xFFFFFFFF):
        raise RuntimeError("Unconfirmed OTA selector")
    return (sequence - 1) % 2


def require_image(verification, spec, selection, *, allow_padded=False):
    app = spec[f"{selection}_app"]
    slot = spec[f"{selection}_slot"]
    if (verification.get("component") != "native_vdp" or verification.get("slot") != slot
            or verification.get("address") != hex(SLOTS[slot])
            or verification.get("sha256") != app["sha256"] or verification.get("bytes") != app["bytes"]
            or verification.get("boot_cli_ready") is not True):
        raise RuntimeError(f"Independent proof does not establish {selection} image on app{slot}")
    extent = verification.get("verified_extent_bytes")
    digest = verification.get("verified_extent_sha256")
    if extent == app["bytes"] and digest == app["sha256"]:
        return
    if allow_padded and selection == "restore" and type(extent) is int and app["bytes"] < extent <= CAPACITY:
        path = Path(verification["readback"])
        if path.stat().st_size == extent:
            data = path.read_bytes()
            if (sha256(data).hexdigest() == digest and
                    sha256(data[:app["bytes"]]).hexdigest() == app["sha256"] and
                    data[app["bytes"]:] == b"\xff" * (extent - app["bytes"])):
                return
    raise RuntimeError(f"Independent extent proof differs for {selection} image on app{slot}")


def installed(inventory, spec, selection, *, receipt_path=None, allow_padded=False):
    if inventory.get("pending_operation"):
        raise RuntimeError("A prior firmware action requires reconciliation")
    entry = inventory["native_vdp"]
    require_image(entry, spec, selection, allow_padded=allow_padded)
    path = Path(entry["verification_receipt"]).resolve(strict=True)
    if receipt_path is not None and path != receipt_path.resolve():
        raise RuntimeError("Installed image belongs to a different firmware operation")
    verification = read(path)
    require_image(verification, spec, selection, allow_padded=allow_padded)
    fields = ("sha256", "slot", "verified_extent_bytes", "verified_extent_sha256", "readback")
    if (inventory["components"]["native_vdp_sha256"] != entry["sha256"]
            or Path(verification["verification_receipt"]).resolve() != path
            or any(verification.get(key) != entry.get(key) for key in fields)):
        raise RuntimeError("Selected image evidence disagrees with firmware inventory")
    for role, field in COMPANIONS.items():
        companion = inventory[role]
        proof = read(companion["verification_receipt"])
        if (companion["sha256"] != inventory["components"][field]
                or proof["sha256"] != companion["sha256"] or proof["boot_cli_ready"] is not True):
            raise RuntimeError(f"Bench companion {role} lacks matching verification")
    return verification


def companion_pins(inventory):
    return {field: inventory["components"][field] for field in COMPANIONS.values()}


def stage_proof(target, root, selection, app):
    if getattr(target, "offboard", None):
        if read(root / "stage" / "offboard-stage.json") != target.offboard:
            raise RuntimeError("Offboard staging proof differs from the admitted job")
        return
    path = staging_path(target, selection)
    receipts = [file for file in (root / "stage").glob("stage-file-*.receipt.json")
                if read(file)["target"] == path]
    if len(receipts) != 1:
        raise RuntimeError(f"No unique completed FLASH staging receipt for {path}")
    receipt = receipts[0]
    result = read(receipt)
    payload = receipt.with_name(receipt.name.removesuffix(".receipt.json") + ".bin")
    if (result["bytes"] != app["bytes"] or result["activated"] is not True
            or result["payload_carrier"] != "uart" or result["source_sha256"] != app["sha256"]
            or sha256(payload.read_bytes()).hexdigest() != app["sha256"]):
        raise RuntimeError(f"FLASH staging evidence differs from the pinned image for {path}")


def check_updater(target):
    with target.uart_listener("installed-updater"):
        local = target.out / "installed-flash.bin"
        transfer = target.staged_uart("sd-installed-flash", "get", FLASH_PATH, destination=local)
        image = local.read_bytes()
        if len(image) != FLASH_BYTES or sha256(image).hexdigest() != FLASH_SHA:
            raise RuntimeError("Installed /mos/flash.bin differs from published Agon Flash v1.9")
        record(target.out / "updater.json", {"path": FLASH_PATH, "bytes": FLASH_BYTES,
                                            "sha256": FLASH_SHA, "payload_carrier": transfer["payload_carrier"]})


def invoke_flash(target, selection, app, begin):
    before = target.keyboard()
    path = staging_path(target, selection)
    with open_passive_serial(target.c["ports"][0], timeout=0.2) as reader:
        with (target.out / "vdp-usb.bin").open("xb") as capture:
            observer = Observer(reader, capture, target.type_line)
            target.type_line("mirror-on", "VDU 2")
            prompt = observer.witness("flash-entry")
            command = f"flash vdp {path}"

            def confirmation(data):
                lines, tail = returned_output(data, command, prompt)
                return (tail is not None and any(FLASH_BANNER in line for line in lines)
                        and (tail == FLASH_PROMPT or FLASH_PROMPT in lines))

            observer.exchange("ota-confirmation", command, confirmation, 25)
            target.keyboard()
            begin()
            record(target.out / "write-intent.json", {
                "method": "agon-flash", "sd_path": path, "app": app, "boot": before["boot"],
            })
            keyboard = Path(__file__).with_name("keyboard.py")
            subprocess.run([sys.executable, str(keyboard), "--url", target.url,
                            "--state", str(target.out / "keys-flash-yes.json"), "type", "y"],
                           check=True, timeout=15)
            observer.receive("FLASH checksum and reboot", bytearray(),
                             lambda data: b"checksum ok!" in data and REBOOT_NOTICE in data, 125)
            record(target.out / "ota-reboot-announced.json", {"checksum_ok": True, "reboot_announced": True})
            # Allow FLASH's automatic VDP restart to conclude before the
            # commissioned full Agon/P4 startup sequence.
            time.sleep(8)
    return before["boot"]


def app_readback(target, slot, table, image):
    """Enter the commissioned ROM once and read the selector and application."""
    before = target.keyboard()["boot"]
    rom = mainboard_rom()(target.c["ports"][0], 115200)
    try:
        rom.connect("default-reset", 1)
        mac = ":".join(f"{byte:02x}" for byte in rom.read_mac())
        if mac != target.config["mainboard_mac"].lower():
            raise RuntimeError("Classic ESP32 MAC differs from the commissioned board")
        stub = rom.run_stub()
        actual_table = stub.read_flash(0x8000, 0x1000)
        (target.out / "partition-table.bin").write_bytes(actual_table)
        if actual_table != table.ljust(0x1000, b"\xff"):
            raise RuntimeError("Live mainboard partition table differs from the pinned layout")
        selector = stub.read_flash(SELECTOR, 0x2000)
        (target.out / "ota-selector.bin").write_bytes(selector)
        actual_slot = selected_slot(selector)
        if actual_slot != slot:
            raise RuntimeError(f"FLASH selected app{actual_slot}, expected app{slot}")
        result = target.out / "readback.bin"
        data = stub.read_flash(SLOTS[slot], len(image))
        result.write_bytes(data)
        if data != image:
            raise RuntimeError(f"Independent app{slot} bytes differ from the pinned application")
        record(target.out / "selected-image.json",
               {"slot": slot, "address": hex(SLOTS[slot]), "bytes": len(data),
                "sha256": sha256(data).hexdigest(), "partition_table_sha256": sha256(actual_table).hexdigest(),
                "ota_selector_sha256": sha256(selector).hexdigest()})
        return before, result
    finally:
        if rom._port.is_open:
            rom._port.close()


def mos_witness(target, label):
    with open_passive_serial(target.c["ports"][0], timeout=0.2) as reader:
        with (target.out / f"{label}.bin").open("xb") as capture:
            observer = Observer(reader, capture, target.type_line)
            target.type_line(f"{label}-mirror-on", "VDU 2")
            prompt = observer.witness(label)
            observer.mirror_off(prompt, f"{label}-mirror-off")
    record(target.out / f"{label}.json", {"prompt": prompt.decode("ascii")})


def replace(target, spec, selection, image, table, begin):
    target.own()
    if getattr(target, "offboard", None):
        record(target.out / "updater.json", {"path": FLASH_PATH, "sha256": FLASH_SHA,
                                           "offboard_verification_sha256": target.offboard["verification_sha256"]})
    else:
        check_updater(target)
    boot_before_flash = invoke_flash(target, selection, spec[f"{selection}_app"], begin)
    reboot_pair(target, boot_before_flash)
    mos_witness(target, "after-flash-mos")
    target.validate_ports()
    target.idle()
    before, result = app_readback(target, spec[f"{selection}_slot"], table, image)
    target.validate_ports()
    target.idle()
    pulse(target.reset_config)
    boot = wait_boot(target.url, before, 60)
    record(target.out / "post-read-admitted.json", boot)
    mos_witness(target, "after-verification-mos")
    target.validate_ports()
    target.idle()
    return result, boot["boot"]
