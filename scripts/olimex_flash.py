"""Bounded application writes for the commissioned Olimex ESP32 layouts."""

import argparse
from pathlib import Path
import struct
import subprocess
import zlib

from bench_process import record


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
    check_extent(component, specification, image)
    path = Path(out)
    (path / "write.bin").write_bytes(image)
    (path / "expected-partition-table.bin").write_bytes(table)
    begin()
    # Keep the commissioned esptool 4.x environment. A single child owns the
    # programmer serial handle across bootloader entry, reads and write.
    interpreter = Path(programmer).with_name("python")
    argv = [str(interpreter), "-u", str(Path(__file__).resolve()), component,
            str(port), mac, str(path)]
    with (path / "programmer.log").open("xb") as log:
        subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=330)
    return path / "readback.bin"


def session_operations(esp, write_flash, component, path):
    _, _, ota, offset, capacity = LAYOUTS[component]
    table = (path / "expected-partition-table.bin").read_bytes()
    actual_table = esp.read_flash(0x8000, len(table))
    (path / "partition-table.bin").write_bytes(actual_table)
    if actual_table != table:
        raise RuntimeError(f"{component} partition table differs from the pinned layout")
    selector = esp.read_flash(ota, 8192)
    (path / "ota-selector.bin").write_bytes(selector)
    check_app0(selector)
    frozen = path / "write.bin"
    size = frozen.stat().st_size
    if not 0 < size <= capacity or size % 4096:
        raise ValueError("Unsafe application write extent")
    record(path / "write-dispatched.json", {"offset": offset, "bytes": size})
    write_flash(esp, offset, frozen)
    (path / "readback.bin").write_bytes(esp.read_flash(offset, size))


def main():
    from esptool import __version__, get_default_connected_device
    from esptool.cmds import detect_flash_size, write_flash
    from esptool.util import flash_size_bytes

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=LAYOUTS)
    parser.add_argument("port")
    parser.add_argument("mac")
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    if not __version__.startswith("4.12."):
        raise RuntimeError("Expected the commissioned esptool 4.12 interpreter")
    chip, before, _, _, _ = LAYOUTS[args.component]

    def program(loader, offset, image):
        size = detect_flash_size(loader, args=None)
        if size is None:
            raise RuntimeError("Programmer could not determine the flash size")
        loader.flash_set_parameters(flash_size_bytes(size))
        loader.WRITE_FLASH_ATTEMPTS = 1
        with image.open("rb") as source:
            write_flash(loader, argparse.Namespace(
                addr_filename=[(offset, source)], chip=chip,
                flash_mode="keep", flash_size="keep", flash_freq="keep",
                compress=True, no_compress=False, no_stub=False, erase_all=False,
                force=False, encrypt=False, encrypt_files=None,
                ignore_flash_encryption_efuse_setting=False))

    esp = get_default_connected_device([args.port], args.port, 1, 115200,
                                       chip=chip, before=before)
    try:
        actual = ":".join(f"{value:02x}" for value in esp.read_mac())
        print(f"Commissioned {chip} programmer sees MAC {actual}", flush=True)
        if args.component == "mainboard" and actual != args.mac.lower():
            raise RuntimeError("Classic ESP32 MAC differs from the commissioned board")
        esp = esp.run_stub()
        esp.change_baud(460800)
        session_operations(esp, program, args.component, args.evidence)
    finally:
        esp._port.close()


if __name__ == "__main__":
    main()
