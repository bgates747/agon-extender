"""Check all live fills offline, or check the final two USB-retrieved slot payloads."""
import argparse
import ctypes
from pathlib import Path
import re


BAR_PIXELS = (104, 108, 104, 108, 104, 108, 104, 108)
BLACK, RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE = (
    bytes.fromhex(s) for s in ("000000", "0000ff", "00ff00", "ff0000",
                              "00ffff", "ff00ff", "ffff00", "ffffff")
)
BAR_ROW = b"".join(pixel * width for pixel, width in zip(
    (BLACK, RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE), BAR_PIXELS))
AMBER = bytes.fromhex("00aaff")
PAIR_BYTES = 5088
FRAME_COUNT = 300


def bit_strip(value):
    return b"".join((WHITE if (value >> bit) & 1 else BLACK) * 4 for bit in range(9))


ROW_STRIPS = [bit_strip(y) for y in range(480)]
FRAME_STRIPS = [bit_strip(frame) for frame in range(FRAME_COUNT)]


def expected(frame, pair):
    first_y = 2 * pair
    base = BAR_ROW[:776 * 3]
    if first_y < 24:
        start_x = 8 if frame // 60 % 2 == 0 else 644
        primed = frame == 0 and pair < 2
        base = base[:start_x * 3] + (AMBER if primed else GREEN) * 80 + base[(start_x + 80) * 3:]
    frame_id = FRAME_STRIPS[frame]
    return base + ROW_STRIPS[first_y] + frame_id + base + ROW_STRIPS[first_y + 1] + frame_id


def check(frame, pair, got):
    want = expected(frame, pair)
    if len(got) != len(want):
        raise ValueError(f"frame {frame} pair {pair}: {len(got)} bytes, expected {len(want)}")
    if got != want:
        index = next(i for i in range(len(want)) if got[i] != want[i])
        row, pos = divmod(index, 848 * 3)
        raise ValueError(f"frame {frame} y={pair*2+row} x={pos//3} BGR byte {pos%3}: "
                         f"got {got[index]}, expected {want[index]}")


def check_kernel(library):
    fill = ctypes.CDLL(str(library.resolve())).test_pair_pixels
    fill.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_bool]
    fill.restype = None
    storage = ctypes.create_string_buffer(5120 + 192)
    ctypes.memset(storage, 0xa5, ctypes.sizeof(storage))
    dst = ((ctypes.addressof(storage) + 63) & ~63) + 64
    for frame in range(FRAME_COUNT):
        for pair in range(240):
            # Poison each payload with a byte absent from the oracle: a missed
            # store cannot accidentally pass by inheriting the previous fill.
            ctypes.memset(dst, 0xa5, PAIR_BYTES)
            fill(dst, frame, pair, frame == 0 and pair < 2)
            check(frame, pair, ctypes.string_at(dst, PAIR_BYTES))
            if (ctypes.string_at(dst - 64, 64) != b"\xa5" * 64 or
                    ctypes.string_at(dst + PAIR_BYTES, 64) != b"\xa5" * 64):
                raise ValueError(f"frame {frame} pair {pair}: out-of-range store")
    print("72000 pairs matched, including 2 primed pairs; guard bytes intact")


def check_receipt(path):
    slots = {}
    for line in path.read_bytes().splitlines():
        if not line.startswith(b"PAIR_SLOT "):
            continue
        match = re.fullmatch(rb"PAIR_SLOT ([01]) ([a-fA-F0-9]{10176})", line)
        if not match:
            raise ValueError("malformed or truncated PAIR_SLOT")
        slot = int(match[1])
        if slot in slots:
            raise ValueError(f"duplicate slot {slot}; supply one run or dump")
        slots[slot] = bytes.fromhex(match[2].decode("ascii"))
    if slots.keys() != {0, 1}:
        raise ValueError("incomplete final slot dump")
    for slot, got in slots.items():
        check(299, 238 + slot, got)
    print("Final USB slots matched frame 299, rows 476–479 (10176 payload bytes)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--library", type=Path, help="Native shared library built from pair_pixels_host.c")
    source.add_argument("--receipt", type=Path, help="Raw P4 USB capture covering exactly one report")
    args = parser.parse_args()
    (check_kernel(args.library) if args.library else check_receipt(args.receipt))
