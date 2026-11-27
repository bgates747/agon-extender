"""Bounded application writes for the commissioned Olimex ESP32 layouts."""

import argparse
from pathlib import Path
import struct
import subprocess
import sys
import zlib

from bench_process import record


LAYOUTS = {
    "mainboard": (0xE000, 0x10000, 0x140000),
    "p4": (0xF000, 0x20000, 0x700000),
}


def check_extent(component, specification, image):
    _, offset, capacity = LAYOUTS[component]
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


def flash_application(component, port, mac, specification, image, table,
                      out, begin, *, required_entry=None):
    if component != "mainboard":
        raise ValueError("The standalone USB writer supports only the classic ESP32 mainboard")
    check_extent(component, specification, image)
    path = Path(out)
    (path / "write.bin").write_bytes(image)
    (path / "expected-partition-table.bin").write_bytes(table)
    if required_entry is not None:
        (path / "expected-entry.bin").write_bytes(required_entry)
    begin()
    # Keep one serial handle across ROM entry, stub setup, write and readback.
    argv = [sys.executable, "-u", str(Path(__file__).resolve()), component,
            str(port), mac, str(path)]
    with (path / "programmer.log").open("xb") as log:
        subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=330)
    return path / "readback.bin"


def session_operations(esp, write_flash, component, path):
    ota, offset, capacity = LAYOUTS[component]
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
    expected = path / "expected-entry.bin"
    if expected.is_file():
        data = expected.read_bytes()
        if len(data) != size:
            raise ValueError("Entry verification must cover the write extent")
        entry = esp.read_flash(offset, size)
        (path / "entry-readback.bin").write_bytes(entry)
        if entry != data:
            raise RuntimeError("Existing firmware differs from the production entry image")
    record(path / "write-intent.json", {"offset": offset, "bytes": size})
    write_flash(esp, offset, frozen)
    (path / "readback.bin").write_bytes(esp.read_flash(offset, size))


def configure_flash_size(loader, detect_flash_size, flash_size_bytes):
    # Match esptool's --flash_size keep behavior. Live partition equality and
    # the commissioned device/slot bound were already checked.
    size = detect_flash_size(loader)
    if size is not None:
        loader.flash_set_parameters(flash_size_bytes(size))
    else:
        print("Flash ID did not report a size; retaining the programmer's default parameters.")


def mainboard_rom():
    from esptool import __version__
    from esptool.targets.esp32 import ESP32ROM

    if __version__ != "5.1.0":
        raise RuntimeError(f"Expected standalone esptool 5.1.0, got {__version__}")
    return ESP32ROM


def mainboard_programmer():
    from esptool.cmds import detect_flash_size, write_flash
    from esptool.util import flash_size_bytes

    rom_type = mainboard_rom()

    def program(loader, offset, image):
        configure_flash_size(loader, detect_flash_size, flash_size_bytes)
        loader.WRITE_FLASH_ATTEMPTS = 1
        record(image.parent / "write-dispatched.json",
               {"offset": offset, "bytes": image.stat().st_size})
        write_flash(loader, [(offset, str(image))], flash_freq="keep", flash_mode="keep",
                    flash_size="keep", compress=True)

    return rom_type, program


def program_mainboard(port, mac, evidence):
    rom_type, program = mainboard_programmer()
    print("esptool 5.1.0, ROM entry 115200, flash transfer 460800", flush=True)
    rom = rom_type(port, 115200)
    try:
        rom.connect("default-reset", 1)
        actual = ":".join(f"{value:02x}" for value in rom.read_mac())
        if actual != mac.lower():
            raise RuntimeError("Classic ESP32 MAC differs from the commissioned board")
        stub = rom.run_stub()
        stub.change_baud(460800)
        session_operations(stub, program, "mainboard", evidence)
    finally:
        if rom._port.is_open:
            rom._port.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=("mainboard",))
    parser.add_argument("port")
    parser.add_argument("mac")
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    program_mainboard(args.port, args.mac, args.evidence)


if __name__ == "__main__":
    main()
