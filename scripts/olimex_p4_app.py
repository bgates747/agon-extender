"""Application replacement for the commissioned Olimex P4-PC using stock esptool."""

from contextlib import contextmanager
from hashlib import sha256
import subprocess
import sys
import time

from bench_process import record
from olimex_flash import check_app0, check_extent
from p4_boot_guard import check_startup
from reset_agon import wait_boot
from reset_agon_usb import hold


PAD = b"Parallel boot pads released; awaiting EMOS"


def stock(out, label, port, before, *args):
    argv = [sys.executable, "-m", "esptool", "--chip", "esp32p4", "--port", str(port),
            "--baud", "460800", "--before", before, "--after", "no-reset", *map(str, args)]
    record(out / f"{label}-argv.json", argv)
    with (out / f"{label}.log").open("xb") as log:
        subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=110)


def reset_until_pads_release(bench):
    """Restart the P4 while its caller holds Agon in reset."""
    from esptool.reset import HardReset
    import serial

    bench.own()
    out = bench.out
    console = serial.Serial(port=None, baudrate=115200, timeout=0.15, exclusive=True)
    console.dtr = console.rts = False
    console.port = bench.c["ports"][1]
    with console, (out / "p4-boot.bin").open("xb") as capture:
        record(out / "p4-reset-issued.json", {"epoch": time.time()})
        HardReset(console, uses_usb=True).reset()
        until = time.monotonic() + 50
        received = bytearray()
        while PAD not in received:
            if time.monotonic() >= until or len(received) > 4 * 1024 * 1024:
                raise TimeoutError("P4 did not report boot pad release")
            data = console.read(min(4096, console.in_waiting or 1))
            capture.write(data)
            received.extend(data)
            check_startup(received, PAD)
        record(out / "p4-pad-release.json", {"epoch": time.time()})


@contextmanager
def hold_agon(bench):
    bench.own()
    with hold(bench.reset_config):
        record(bench.out / "agon-hold-asserted.json", {"epoch": time.time()})
        yield
    record(bench.out / "agon-hold-released.json", {"epoch": time.time()})


def reboot_pair(bench, before_boot):
    """Start Agon after the installed P4 has released its boot pads."""
    with hold_agon(bench):
        reset_until_pads_release(bench)
    record(bench.out / "agon-admitted.json", wait_boot(bench.url, before_boot, 60))


def replace(bench, spec, image, table, before_boot, begin, *, required_entry=None):
    from esptool import __version__

    if __version__ != "5.1.0":
        raise RuntimeError("P4-PC requires the commissioned stock esptool 5.1.0")
    check_extent("p4", spec, image)
    bench.own()
    port = bench.c["ports"][1]
    out = bench.out
    partition = out / "partition-table.bin"
    selector = out / "ota-selector.bin"
    write = out / "write.bin"
    readback = out / "readback.bin"
    write.write_bytes(image)

    # The same hold, stock CLI flags and pad-release boundary as NET-009.
    # Keep the mainboard held while the P4 GPIO boot pads may be driven.
    with hold_agon(bench):
        stock(out, "partition", port, "usb-reset", "read-flash", "0x8000", "0x1000",
              partition)
        stock(out, "selector", port, "no-reset", "read-flash", "0xf000", "0x2000", selector)
        if partition.read_bytes()[:len(table)] != table:
            raise RuntimeError("P4 partition table differs from the pinned layout")
        check_app0(selector.read_bytes())
        if required_entry is not None:
            entry = out / "entry-readback.bin"
            stock(out, "entry", port, "no-reset", "read-flash", "0x20000",
                  hex(len(image)), entry)
            if entry.read_bytes() != required_entry:
                raise RuntimeError("Existing P4 application differs from the production entry")
        begin()
        record(out / "write-intent.json", {"offset": 0x20000, "bytes": len(image)})
        stock(out, "write", port, "no-reset", "write-flash", "--flash-mode", "keep",
              "--flash-freq", "keep", "--flash-size", "keep", "0x20000", write)
        stock(out, "readback", port, "no-reset", "read-flash", "0x20000", hex(len(image)),
              readback)
        if readback.read_bytes() != image:
            raise RuntimeError("Independent P4 application readback differs")
        record(out / "write-verified.json", {
            "bytes": len(image), "write_sha256": sha256(image).hexdigest(),
        })
        reset_until_pads_release(bench)
    record(out / "agon-admitted.json", wait_boot(bench.url, before_boot, 60))
    return readback
