#!/usr/bin/env python3
"""Check the generated Phase F fixture package for internal consistency.

This checker consumes only the task fixture and its expected SVG.  It neither
imports production code nor imports the fixture generator.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

import yaml


HEADER = struct.Struct("<4sBBBBIHHIIII")
MAX_WIDTH = 1024
MAX_HEIGHT = 768
MAX_PAYLOAD = MAX_WIDTH * MAX_HEIGHT * 3


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def payload(width: int, height: int, sequence: int) -> bytes:
    result = bytearray(width * height * 3)
    offset = 0
    for y in range(height):
        for x in range(width):
            result[offset] = (x + sequence) & 0xFF
            result[offset + 1] = (2 * y) & 0xFF
            result[offset + 2] = ((x ^ y) + 3 * sequence) & 0xFF
            offset += 3
    return bytes(result)


def rejection(message: bytes, message_type: str = "binary") -> str:
    if message_type != "binary":
        return "message-type"
    if len(message) < HEADER.size:
        return "truncated-header"
    fields = HEADER.unpack_from(message)
    magic, version, header_bytes, pixel_format, flags = fields[:5]
    width, height, stride, declared, reserved = fields[6], fields[7], fields[8], fields[9], fields[11]
    if magic != b"EVF1":
        return "magic"
    if version != 1:
        return "version"
    if header_bytes != 32:
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
    if declared != computed:
        return "payload-arithmetic"
    if reserved:
        return "reserved"
    if len(message) != header_bytes + declared:
        return "message-length"
    return "accept"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--expected-svg", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    fixture = yaml.safe_load(args.input.read_text(encoding="utf-8"))

    authorities = fixture["authorities"]
    assert len({item["id"] for item in authorities}) == len(authorities)
    assert all(len(item["sha256"]) == 64 and item["bytes"] > 0 for item in authorities)

    snapshot = fixture["snapshot_pool"]
    allocation_ids = {item["id"] for item in snapshot["allocation_cases"]}
    assert allocation_ids == {"all-three-slots", "fail-first-slot", "fail-second-slot", "fail-third-slot"}
    assert all(
        item["expected_live_slots"] == (3 if item["expected_enabled"] else 0)
        for item in snapshot["allocation_cases"]
    )
    modes = snapshot["documented_mode_profiles"]
    assert len({item["mode"] for item in modes}) == len(modes)
    assert all(0 < item["width"] <= MAX_WIDTH and 0 < item["height"] <= MAX_HEIGHT for item in modes)
    assert all(item["snapshot_stride_bytes"] == item["width"] * 3 for item in modes)
    assert all(item["snapshot_payload_bytes"] == item["width"] * item["height"] * 3 for item in modes)
    assert any(item["width"] == MAX_WIDTH and item["height"] == MAX_HEIGHT for item in modes)
    assert all(not item["expected_reallocation"] for item in snapshot["reconfigure_cases"])

    evf1 = fixture["evf1"]
    valid_ids: list[str] = []
    for vector in evf1["valid_vectors"]:
        header = bytes.fromhex(vector["header_hex"])
        assert len(header) == HEADER.size
        fields = HEADER.unpack(header)
        assert fields[:5] == (b"EVF1", 1, 32, 1, 3)
        generated = payload(vector["width"], vector["height"], vector["sequence"])
        assert len(generated) == vector["payload_bytes"]
        assert sha256(generated) == vector["payload_sha256"]
        assert sha256(header + generated) == vector["message_sha256"]
        if "message_hex" in vector:
            assert bytes.fromhex(vector["message_hex"]) == header + generated
        assert rejection(header + generated) == "accept"
        valid_ids.append(vector["id"])

    malformed_ids: list[str] = []
    for vector in evf1["malformed_vectors"]:
        if "message_hex" in vector:
            actual = rejection(bytes.fromhex(vector["message_hex"]), vector.get("message_type", "binary"))
        else:
            header = bytes.fromhex(vector["header_hex"])
            declared = vector["declared_payload_bytes"]
            rejected_payload = bytes(declared)
            assert sha256(rejected_payload) == vector["payload_sha256"]
            assert sha256(header + rejected_payload) == vector["message_sha256"]
            actual = rejection(header + rejected_payload)
        assert actual == vector["expected_rejection"], vector["id"]
        malformed_ids.append(vector["id"])
    assert len(set(malformed_ids)) == len(malformed_ids)

    traces = fixture["credit_and_reconnect_traces"]
    assert len({item["id"] for item in traces}) == len(traces)
    trace_ids = {item["id"] for item in traces}
    assert {
        "present-before-next-credit",
        "disconnect-during-send",
        "reconnect-receives-retained-latest",
        "slow-browser-collapses-intermediate-generations",
        "second-client-refused",
        "duplicate-credit-is-protocol-error",
    } <= trace_ids

    visible = fixture["visible_vdu_command"]
    command = bytes(visible["command_bytes_decimal"])
    assert command.hex() == visible["command_bytes_hex"]
    assert sha256(command) == visible["command_stream_sha256"]
    assert command[:6] == bytes([22, 9, 23, 1, 0, 12])
    assert sum(item["pixels"] for item in visible["expected_histogram"]) == visible["width"] * visible["height"]
    assert visible["expected_rgb888_bytes"] == visible["width"] * visible["height"] * 3
    svg = args.expected_svg.read_bytes()
    assert b'viewBox="0 0 320 240"' in svg
    assert b'shape-rendering="crispEdges"' in svg

    output = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_independent_fixture_check",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/check-independent-fixtures.py",
        "oracle_independence": "no production C++, JavaScript, header, or binary imported",
        "authority_records": len(authorities),
        "documented_modes_checked": len(modes),
        "allocation_cases_checked": len(snapshot["allocation_cases"]),
        "reconfigure_cases_checked": len(snapshot["reconfigure_cases"]),
        "valid_evf1_vectors_checked": valid_ids,
        "malformed_evf1_vectors_checked": malformed_ids,
        "credit_reconnect_traces_checked": sorted(trace_ids),
        "visible_command_bytes": len(command),
        "visible_rgb888_sha256": visible["expected_rgb888_sha256"],
        "visible_expected_svg_sha256": sha256(svg),
        "result": "pass",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(output, sort_keys=False), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
