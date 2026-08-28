#!/usr/bin/env python3
"""Generate PORT-003 Phase F fixtures without importing production code.

The expected values in this file are derived from the frozen Phase F contracts,
official Agon documentation, and narrowly selected retained VDP data files.  It
must never import or execute the C++ or JavaScript implementation under test.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
from collections import Counter
from pathlib import Path

import yaml


HEADER = struct.Struct("<4sBBBBIHHIIII")
MAX_WIDTH = 1024
MAX_HEIGHT = 768
MAX_PAYLOAD = MAX_WIDTH * MAX_HEIGHT * 3


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_record(identifier: str, path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {"id": identifier, "sha256": sha256(data), "bytes": len(data)}


def parse_font(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"static\s+const\s+uint8_t\s+FONT_AGON_BITMAP\[\]\s*=\s*\{(.*?)\};",
        text,
        re.DOTALL,
    )
    if match is None:
        raise ValueError("FONT_AGON_BITMAP initializer not found")
    body = re.sub(r"//.*", "", match.group(1))
    values = bytes(int(token, 16) for token in re.findall(r"0x[0-9A-Fa-f]{2}", body))
    if len(values) != 256 * 8:
        raise ValueError(f"expected 2048 font bytes, found {len(values)}")
    return values


def parse_screen_modes(path: Path) -> list[dict[str, object]]:
    modes: list[dict[str, object]] = []
    seen: set[int] = set()
    row = re.compile(
        r"^\|(?:[^|]*?)\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)hz\s*\|"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        match = row.match(line)
        if match is None:
            continue
        mode, width, height, colours, refresh = map(int, match.groups())
        if mode in seen or width > MAX_WIDTH or height > MAX_HEIGHT:
            continue
        seen.add(mode)
        modes.append(
            {
                "mode": mode,
                "width": width,
                "height": height,
                "colours": colours,
                "refresh_hz": refresh,
                "double_buffered": mode >= 128,
                "snapshot_stride_bytes": width * 3,
                "snapshot_payload_bytes": width * height * 3,
            }
        )
    if not modes or max(item["width"] for item in modes) != MAX_WIDTH:
        raise ValueError("documented mode table did not reach 1024 pixels")
    if max(item["height"] for item in modes) != MAX_HEIGHT:
        raise ValueError("documented mode table did not reach 768 pixels")
    return modes


def pixel_formula(width: int, height: int, sequence: int) -> bytes:
    data = bytearray(width * height * 3)
    offset = 0
    for y in range(height):
        for x in range(width):
            data[offset] = (x + sequence) & 0xFF
            data[offset + 1] = (2 * y) & 0xFF
            data[offset + 2] = ((x ^ y) + 3 * sequence) & 0xFF
            offset += 3
    return bytes(data)


def evf1_header(
    *,
    sequence: int,
    width: int,
    height: int,
    stride: int,
    payload_bytes: int,
    period_us: int,
    magic: bytes = b"EVF1",
    version: int = 1,
    header_bytes: int = 32,
    pixel_format: int = 1,
    flags: int = 3,
    reserved: int = 0,
) -> bytes:
    return HEADER.pack(
        magic,
        version,
        header_bytes,
        pixel_format,
        flags,
        sequence & 0xFFFFFFFF,
        width,
        height,
        stride,
        payload_bytes,
        period_us,
        reserved,
    )


def valid_vector(identifier: str, width: int, height: int, sequence: int, period: int) -> dict[str, object]:
    payload = pixel_formula(width, height, sequence)
    header = evf1_header(
        sequence=sequence,
        width=width,
        height=height,
        stride=width * 3,
        payload_bytes=len(payload),
        period_us=period,
    )
    result: dict[str, object] = {
        "id": identifier,
        "width": width,
        "height": height,
        "sequence": sequence & 0xFFFFFFFF,
        "stride_bytes": width * 3,
        "payload_bytes": len(payload),
        "present_period_us": period,
        "header_hex": header.hex(),
        "payload_sha256": sha256(payload),
        "message_sha256": sha256(header + payload),
    }
    if len(payload) <= 48:
        result["message_hex"] = (header + payload).hex()
    return result


def validate_evf1(message: bytes, message_type: str = "binary") -> str:
    if message_type != "binary":
        return "message-type"
    if len(message) < HEADER.size:
        return "truncated-header"
    (
        magic,
        version,
        header_bytes,
        pixel_format,
        flags,
        _sequence,
        width,
        height,
        stride,
        payload_bytes,
        _period,
        reserved,
    ) = HEADER.unpack_from(message)
    if magic != b"EVF1":
        return "magic"
    if version != 1:
        return "version"
    if header_bytes != HEADER.size:
        return "header-bytes"
    if pixel_format != 1:
        return "pixel-format"
    if flags & ~3:
        return "unknown-flags"
    if not flags & 1:
        return "full-frame-required"
    if width == 0 or height == 0:
        return "zero-dimension"
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        return "dimension-limit"
    if stride < width * 3:
        return "stride-too-small"
    computed = stride * height
    if computed > MAX_PAYLOAD:
        return "payload-limit"
    if payload_bytes != computed:
        return "payload-arithmetic"
    if reserved != 0:
        return "reserved"
    if len(message) != header_bytes + payload_bytes:
        return "message-length"
    return "accept"


def malformed_vectors() -> list[dict[str, object]]:
    payload = pixel_formula(2, 2, 7)
    base_header = evf1_header(
        sequence=7, width=2, height=2, stride=6, payload_bytes=12, period_us=16667
    )
    base = base_header + payload

    def changed(identifier: str, expected: str, **fields: object) -> dict[str, object]:
        values: dict[str, object] = {
            "sequence": 7,
            "width": 2,
            "height": 2,
            "stride": 6,
            "payload_bytes": 12,
            "period_us": 16667,
        }
        values.update(fields)
        message = evf1_header(**values) + payload
        assert validate_evf1(message) == expected, identifier
        return {"id": identifier, "expected_rejection": expected, "message_hex": message.hex()}

    vectors = [
        {"id": "text-message", "expected_rejection": "message-type", "message_hex": base.hex(), "message_type": "text"},
        {"id": "truncated-header", "expected_rejection": "truncated-header", "message_hex": base[:31].hex()},
        changed("bad-magic", "magic", magic=b"EVF0"),
        changed("bad-version", "version", version=2),
        changed("bad-header-size", "header-bytes", header_bytes=31),
        changed("bad-pixel-format", "pixel-format", pixel_format=2),
        changed("unknown-flags", "unknown-flags", flags=7),
        changed("missing-full-frame", "full-frame-required", flags=2),
        changed("zero-width", "zero-dimension", width=0),
        changed("zero-height", "zero-dimension", height=0),
        changed("width-limit", "dimension-limit", width=1025, stride=3075, payload_bytes=6150),
        changed("height-limit", "dimension-limit", height=769, payload_bytes=4614),
        changed("short-stride", "stride-too-small", stride=5, payload_bytes=10),
        changed("payload-arithmetic", "payload-arithmetic", payload_bytes=11),
        changed("reserved-nonzero", "reserved", reserved=1),
    ]
    short = base[:-1]
    long = base + b"\x00"
    assert validate_evf1(short) == "message-length"
    assert validate_evf1(long) == "message-length"
    vectors.extend(
        [
            {"id": "truncated-payload", "expected_rejection": "message-length", "message_hex": short.hex()},
            {"id": "trailing-byte", "expected_rejection": "message-length", "message_hex": long.hex()},
        ]
    )

    # This boundary vector is represented by an exact header and deterministic
    # payload recipe rather than embedding a 2.36 MiB rejected message.
    oversized_header = evf1_header(
        sequence=7,
        width=1024,
        height=768,
        stride=3073,
        payload_bytes=3073 * 768,
        period_us=16667,
    )
    oversized = oversized_header + bytes(3073 * 768)
    assert validate_evf1(oversized) == "payload-limit"
    vectors.append(
        {
            "id": "payload-limit",
            "expected_rejection": "payload-limit",
            "header_hex": oversized_header.hex(),
            "payload_recipe": "zero bytes; exact count is declared_payload_bytes",
            "declared_payload_bytes": 3073 * 768,
            "payload_sha256": sha256(bytes(3073 * 768)),
            "message_sha256": sha256(oversized),
        }
    )
    return vectors


def le16(value: int) -> list[int]:
    return [value & 0xFF, (value >> 8) & 0xFF]


def plot(command: int, x: int, y: int) -> list[int]:
    return [25, command, *le16(x), *le16(y)]


def build_visible_fixture(font: bytes) -> tuple[dict[str, object], bytes, str]:
    width, height = 320, 240
    frame = bytearray(width * height * 3)

    def colour(physical: int) -> tuple[int, int, int]:
        return (((physical >> 4) & 3) * 85, ((physical >> 2) & 3) * 85, (physical & 3) * 85)

    def set_pixel(x: int, y: int, rgb: tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            offset = (y * width + x) * 3
            frame[offset : offset + 3] = bytes(rgb)

    def draw_text(x: int, y: int, text: str, physical: int) -> None:
        rgb = colour(physical)
        for char in text.encode("latin-1"):
            glyph = font[char * 8 : char * 8 + 8]
            for gy, bits in enumerate(glyph):
                for gx in range(8):
                    if bits & (0x80 >> gx):
                        set_pixel(x + gx, y + gy, rgb)
            x += 8

    def draw_line(x1: int, y1: int, x2: int, y2: int, physical: int) -> None:
        if x1 != x2 and y1 != y2:
            raise ValueError("fixture oracle deliberately uses only axial lines")
        rgb = colour(physical)
        if y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                set_pixel(x, y1, rgb)
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                set_pixel(x1, y, rgb)

    def fill_rect(x1: int, y1: int, x2: int, y2: int, physical: int) -> None:
        rgb = colour(physical)
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                set_pixel(x, y, rgb)

    command_bytes: list[int] = []
    command_bytes.extend([22, 9])                    # MODE 9
    command_bytes.extend([23, 1, 0])                 # hide text cursor
    command_bytes.append(12)                         # CLS
    command_bytes.extend([17, 15])                   # white text
    command_bytes.extend(b"EXTENDER")
    command_bytes.extend([31, 4, 2, 17, 14])         # TAB(4,2), cyan text
    command_bytes.extend(b"P4 VDP")
    command_bytes.extend([23, 0, 0xC0, 0])           # physical top-left coordinates
    command_bytes.extend([18, 0, 9])                 # bright-red graphics
    command_bytes.extend(plot(4, 16, 80))
    command_bytes.extend(plot(5, 150, 80))
    command_bytes.extend(plot(4, 16, 80))
    command_bytes.extend(plot(5, 16, 160))
    command_bytes.extend(plot(4, 16, 160))
    command_bytes.extend(plot(5, 150, 160))
    command_bytes.extend([18, 0, 10])                # bright-green graphics
    command_bytes.extend(plot(4, 180, 90))
    command_bytes.extend(plot(0x65, 260, 150))
    command_bytes.extend([19, 3, 0x38, 0, 0, 0])     # logical 3 -> orange
    command_bytes.extend([18, 0, 3])
    command_bytes.extend(plot(4, 180, 170))
    command_bytes.extend(plot(0x65, 260, 210))

    draw_text(0, 0, "EXTENDER", 0x3F)
    draw_text(32, 16, "P4 VDP", 0x0F)
    draw_line(16, 80, 150, 80, 0x30)
    draw_line(16, 80, 16, 160, 0x30)
    draw_line(16, 160, 150, 160, 0x30)
    fill_rect(180, 90, 260, 150, 0x0C)
    fill_rect(180, 170, 260, 210, 0x38)

    pixels = bytes(frame)
    counts = Counter(tuple(pixels[i : i + 3]) for i in range(0, len(pixels), 3))
    histogram = [
        {"rgb": "#%02x%02x%02x" % rgb, "pixels": count}
        for rgb, count in sorted(counts.items())
    ]
    fixture = {
        "id": "accepted-visible-vdu-command",
        "authority": "official retained VDU byte vocabulary",
        "mode": 9,
        "width": width,
        "height": height,
        "pixel_format": "packed RGB888",
        "cursor": "disabled before visible drawing",
        "command_bytes_decimal": command_bytes,
        "command_bytes_hex": bytes(command_bytes).hex(),
        "command_stream_sha256": sha256(bytes(command_bytes)),
        "expected_rgb888_sha256": sha256(pixels),
        "expected_rgb888_bytes": len(pixels),
        "expected_histogram": histogram,
        "landmarks": [
            {"description": "white EXTENDER text", "x": 0, "y": 0},
            {"description": "cyan P4 VDP text", "x": 32, "y": 16},
            {"description": "red three-sided line", "x1": 16, "y1": 80, "x2": 150, "y2": 160},
            {"description": "green filled rectangle", "x1": 180, "y1": 90, "x2": 260, "y2": 150},
            {"description": "palette-remapped orange rectangle", "x1": 180, "y1": 170, "x2": 260, "y2": 210},
        ],
        "expected_image": "visible-vdu-command-expected.svg",
    }

    # Compact human-review image: coalesce every horizontal run of equal,
    # nonblack pixels into one SVG rectangle.
    rects: list[str] = []
    for y in range(height):
        x = 0
        while x < width:
            offset = (y * width + x) * 3
            rgb = tuple(pixels[offset : offset + 3])
            if rgb == (0, 0, 0):
                x += 1
                continue
            end = x + 1
            while end < width:
                next_offset = (y * width + end) * 3
                if tuple(pixels[next_offset : next_offset + 3]) != rgb:
                    break
                end += 1
            rects.append(
                f'<rect x="{x}" y="{y}" width="{end - x}" height="1" fill="#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"/>'
            )
            x = end
    svg = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480" viewBox="0 0 320 240" shape-rendering="crispEdges">',
            '<rect width="320" height="240" fill="#000000"/>',
            *rects,
            "</svg>",
            "",
        ]
    )
    return fixture, pixels, svg


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official-docs-root", type=Path, required=True)
    parser.add_argument("--retained-vdp-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-svg", type=Path, required=True)
    args = parser.parse_args()

    docs = args.official_docs_root / "docs/vdp"
    video = args.retained_vdp_root / "video"
    sources = [
        source_record("agon-docs:VDU-Commands.md", docs / "VDU-Commands.md"),
        source_record("agon-docs:Screen-Modes.md", docs / "Screen-Modes.md"),
        source_record("agon-docs:PLOT-Commands.md", docs / "PLOT-Commands.md"),
        source_record("retained-vdp:video/agon_fonts.h", video / "agon_fonts.h"),
        source_record("retained-vdp:video/agon_palette.h", video / "agon_palette.h"),
        source_record("retained-vdp:video/vdu.h", video / "vdu.h"),
        source_record("retained-vdp:video/context/graphics.h", video / "context/graphics.h"),
    ]
    font = parse_font(video / "agon_fonts.h")
    modes = parse_screen_modes(docs / "Screen-Modes.md")
    visible, _pixels, svg = build_visible_fixture(font)
    valid = [
        valid_vector("one-pixel", 1, 1, 0, 0),
        valid_vector("compact-exact-message", 2, 2, 7, 16667),
        valid_vector("accepted-fixture-size", 320, 240, 0xFFFFFFFF, 16667),
        valid_vector("maximum-retained-surface", 1024, 768, 0x1_0000_0000, 16667),
    ]
    malformed = malformed_vectors()
    for vector in malformed:
        if "message_hex" in vector:
            actual = validate_evf1(
                bytes.fromhex(vector["message_hex"]), vector.get("message_type", "binary")
            )
            assert actual == vector["expected_rejection"], vector["id"]

    output = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_independent_fixtures",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/generate-independent-fixtures.py",
        "oracle_independence": "imports no production C++ header, source, binary, or browser JavaScript",
        "authorities": sources,
        "snapshot_pool": {
            "allocation_cases": [
                {"id": "all-three-slots", "successful_allocations": 3, "expected_enabled": True, "expected_live_slots": 3},
                {"id": "fail-first-slot", "successful_allocations": 0, "expected_enabled": False, "expected_live_slots": 0},
                {"id": "fail-second-slot", "successful_allocations": 1, "expected_enabled": False, "expected_live_slots": 0},
                {"id": "fail-third-slot", "successful_allocations": 2, "expected_enabled": False, "expected_live_slots": 0},
            ],
            "documented_mode_profiles": modes,
            "reconfigure_cases": [
                {"id": "minimum-to-maximum", "from": [320, 200], "to": [1024, 768], "expected_reallocation": False, "expected_payload_bytes": MAX_PAYLOAD},
                {"id": "maximum-to-fixture", "from": [1024, 768], "to": [320, 240], "expected_reallocation": False, "expected_payload_bytes": 320 * 240 * 3},
                {"id": "same-mode", "from": [320, 240], "to": [320, 240], "expected_reallocation": False, "expected_payload_bytes": 320 * 240 * 3},
            ],
            "metadata_rejection_cases": [
                {"id": "zero-width", "width": 0, "height": 240, "expected": "reject-before-publish"},
                {"id": "zero-height", "width": 320, "height": 0, "expected": "reject-before-publish"},
                {"id": "width-limit", "width": 1025, "height": 1, "expected": "reject-before-publish"},
                {"id": "height-limit", "width": 1, "height": 769, "expected": "reject-before-publish"},
                {"id": "maximum", "width": 1024, "height": 768, "expected": "publish", "payload_bytes": MAX_PAYLOAD},
            ],
        },
        "evf1": {
            "validation_order": [
                "message-type", "truncated-header", "magic", "version", "header-bytes", "pixel-format",
                "unknown-flags", "full-frame-required", "zero-dimension", "dimension-limit", "stride-too-small",
                "payload-limit", "payload-arithmetic", "reserved", "message-length",
            ],
            "payload_formula": "R=(x+sequence)&255; G=(2*y)&255; B=((x^y)+3*sequence)&255; row-major",
            "valid_vectors": valid,
            "malformed_vectors": malformed,
        },
        "credit_and_reconnect_traces": [
            {
                "id": "present-before-next-credit",
                "events": ["open", "credit", "lease-generation-1", "send-complete", "parse", "animation-present", "credit"],
                "expected_credits_sent": 2,
                "expected_frames_presented": 1,
                "maximum_server_leases": 1,
                "maximum_browser_pending_frames": 1,
            },
            {
                "id": "disconnect-during-send",
                "events": ["open", "credit", "lease-generation-4", "disconnect", "release-generation-4"],
                "expected_server_state": "disconnected",
                "expected_live_leases": 0,
            },
            {
                "id": "reconnect-receives-retained-latest",
                "events": ["open", "credit", "lease-generation-8", "disconnect", "release-generation-8-as-latest", "open", "credit", "lease-generation-8"],
                "expected_connection_generation_reset": True,
                "expected_reacquired_generation": 8,
                "maximum_server_leases": 1,
            },
            {
                "id": "slow-browser-collapses-intermediate-generations",
                "events": ["credit", "lease-generation-10", "send-complete", "parse", "publish-11", "publish-12", "animation-present", "credit", "lease-generation-12"],
                "expected_next_generation": 12,
                "expected_sequence_gap": 1,
                "expected_queued_frames": 0,
            },
            {
                "id": "second-client-refused",
                "events": ["first-client-open", "second-client-open"],
                "expected_second_client_close_code": 1013,
                "expected_active_clients": 1,
            },
            {
                "id": "duplicate-credit-is-protocol-error",
                "events": ["open", "credit", "credit"],
                "expected_close_code": 1002,
                "expected_live_leases": 0,
            },
        ],
        "visible_vdu_command": visible,
        "result": "pass",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.expected_svg.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(output, sort_keys=False, width=110), encoding="utf-8", newline="\n")
    args.expected_svg.write_text(svg, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
