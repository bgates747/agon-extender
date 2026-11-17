"""Bounded application writes for the commissioned Olimex ESP32 layouts."""

from pathlib import Path
import re
import struct
import subprocess
import zlib


LAYOUTS = {
    "mainboard": ("esp32", "default_reset", 0xE000, 0x10000, 0x140000),
    "p4": ("esp32p4", "usb_reset", 0xF000, 0x20000, 0x700000),
}


def check_extent(component, specification, image):
    _, _, _, offset, capacity = LAYOUTS[component]
    if (int(specification["offset"], 0) != offset
            or specification["partition_bytes"] != capacity
            or len(image) != specification["write_bytes"]
            or not 0 < len(image) <= capacity
            or len(image) % 4096):
        raise ValueError(f"{component} application write does not fit the commissioned slot")


def check_app0(selector):
    if len(selector) != 8192:
        raise ValueError("Unexpected OTA selector extent")
    entries = []
    for offset in (0, 4096):
        record = selector[offset:offset + 32]
        if record == b"\xff" * 32:
            continue
        sequence, state, checksum = struct.unpack("<I20xII", record)
        if (sequence not in (0, 0xffffffff) and state not in (3, 4)
                and checksum == zlib.crc32(record[:4], 0xffffffff)):
            entries.append((sequence, state))
    if entries:
        sequence, state = max(entries)
        if state in (2, 0xffffffff) and (sequence - 1) % 2 == 0:
            return
    elif selector == b"\xff" * len(selector):
        # An erased selector boots app0 on the two pinned no-factory layouts.
        return
    raise ValueError("The OTA selector does not establish a confirmed app0")


def flash_application(component, programmer, port, mac, specification, image, table,
                      out, begin):
    chip, first_reset, ota, offset, _ = LAYOUTS[component]
    check_extent(component, specification, image)
    path = Path(out)

    def command(name, *arguments, before="no_reset"):
        argv = [programmer, "--chip", chip, "--port", str(port), "--baud", "460800",
                "--connect-attempts", "1", "--before", before, "--after", "no_reset",
                *map(str, arguments)]
        with (path / f"{name}.log").open("xb") as log:
            subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=90)

    if component == "mainboard":
        command("identity", "read_mac", before=first_reset)
        report = (path / "identity.log").read_text()
        if re.search(r"^MAC: " + re.escape(mac) + r"\s*$", report, re.M | re.I) is None:
            raise RuntimeError("Classic ESP32 MAC differs from the commissioned board")
        first_reset = "no_reset"
    actual_table = path / "partition-table.bin"
    command("partition-table", "read_flash", "0x8000", len(table), actual_table,
            before=first_reset)
    if actual_table.read_bytes() != table:
        raise RuntimeError(f"{component} partition table differs from the pinned layout")
    selector = path / "ota-selector.bin"
    command("ota-selector", "read_flash", hex(ota), 8192, selector)
    check_app0(selector.read_bytes())
    frozen = path / "write.bin"
    frozen.write_bytes(image)
    begin()
    command("write", "write_flash", "--no-progress", hex(offset), frozen)
    result = path / "readback.bin"
    command("readback", "read_flash", hex(offset), len(image), result)
    return result
