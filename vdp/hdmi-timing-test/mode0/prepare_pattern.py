#!/usr/bin/env python3
"""Extract the frozen mode-preview-r02 bitmap for the standalone mode 0 fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


PACKED_SHA256 = "5cb9d7c30c0ae3b9569b5ddf51e0eea3b032e877472721c200656f53a7ec7445"
PIXELS_SHA256 = "3528544408f51b23f9135c89d05d4c4b02f7143bb9e9a7a0e43f3eb724a7e25b"
PIXELS = 640 * 480


def extract_bitmap(data):
    if hashlib.sha256(data).hexdigest() != PACKED_SHA256:
        raise ValueError("Expected the frozen mode-preview-r02 packed m000.vdu")
    buffer_command = bytes((23, 0, 160, 0, 250))
    clear = buffer_command + bytes((2,))
    append = buffer_command + bytes((0,))
    pos = data.index(clear) + len(clear)
    packed = bytearray()
    while data.startswith(append, pos):
        length = struct.unpack_from("<H", data, pos + len(append))[0]
        pos += len(append) + 2
        packed.extend(data[pos:pos + length])
        pos += length
    if not data.startswith(buffer_command + bytes((65, 0, 250)), pos):
        raise ValueError("Expected the in-place VDP buffer decompression command")
    if struct.unpack_from("<4sI", packed) != (b"CmpT", PIXELS):
        raise ValueError("Expected the 640 by 480 TurboVega bitmap")

    # The stock codec's 10-bit big-endian codes reference a 256-byte window.
    # Only literal codes advance the window, including after a string reference.
    window = bytearray(256)
    write_pos = 0
    accumulator = 0
    bits = 0
    pixels = bytearray()
    for octet in packed[8:]:
        accumulator = (accumulator << 8) | octet
        bits += 8
        if bits < 10:
            continue
        bits -= 10
        code = accumulator >> bits
        accumulator &= (1 << bits) - 1
        command, value = divmod(code, 256)
        if command == 0:
            pixels.append(value)
            window[write_pos] = value
            write_pos = (write_pos + 1) & 255
        else:
            count = (4, 8, 16)[command - 1]
            pixels.extend(window[(value + i) & 255] for i in range(count))
    if len(pixels) != PIXELS or hashlib.sha256(pixels).hexdigest() != PIXELS_SHA256:
        raise ValueError("Decoded mode 0 bitmap does not match the retained upload")
    return pixels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packed", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    pixels = extract_bitmap(args.packed.read_bytes())
    with args.output.open("xb") as output:
        output.write(pixels)
    print(json.dumps({"packed_sha256": PACKED_SHA256, "pixels_sha256": PIXELS_SHA256,
                      "pixel_format": "AABBGGRR", "bytes": len(pixels)}))


if __name__ == "__main__":
    main()
