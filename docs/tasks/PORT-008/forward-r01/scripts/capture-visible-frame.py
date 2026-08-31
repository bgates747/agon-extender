#!/usr/bin/env python3
"""Capture and verify the exact PORT-008 browser-visible RGB888 frame.

This is read-only qualification tooling for an already-running P4. It sends
only the established browser-frame credit over WebSocket; it does not send a
VDU/EDU command or touch transport GPIO. The supplied endpoint is deliberately
omitted from durable output.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
PHASE_F_LIVE_CHECK = (
    ROOT / "docs/tasks/PORT-003/phase-f/scripts/check-p4-browser-runtime.py"
)
EXPECTED_BYTES = 230400
EXPECTED_SHA256 = "d368967667b3eee2315e2bb86129e7f423d904abd203c93dd0810906d08783d8"


def load_live_checker() -> Any:
    spec = importlib.util.spec_from_file_location(
        "port003_phase_f_live_checker", PHASE_F_LIVE_CHECK
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {PHASE_F_LIVE_CHECK}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--payload-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    args = parser.parse_args()
    for output in (args.payload_output, args.report_output):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite evidence: {output}")

    checker = load_live_checker()
    client = checker.WebSocket(args.host, args.port, args.timeout)
    try:
        client.send_text(b"frame")
        message = client.read_binary_message()
    finally:
        client.close()
    frame = checker.parse_evf1(message)
    payload = message[32:]
    observed_sha256 = hashlib.sha256(payload).hexdigest()
    if len(payload) != EXPECTED_BYTES:
        raise RuntimeError(
            f"RGB888 payload is {len(payload)} bytes, expected {EXPECTED_BYTES}"
        )
    if observed_sha256 != EXPECTED_SHA256:
        raise RuntimeError(
            f"RGB888 payload SHA-256 is {observed_sha256}, expected {EXPECTED_SHA256}"
        )

    args.payload_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.payload_output.write_bytes(payload)
    report = {
        "schema_version": 1,
        "artifact_kind": "port_008_forward_visible_frame",
        "generated_by": (
            "docs/tasks/PORT-008/forward-r01/scripts/capture-visible-frame.py"
        ),
        "derived_from_parser": (
            "docs/tasks/PORT-003/phase-f/scripts/check-p4-browser-runtime.py"
        ),
        "endpoint_recorded": False,
        "frame": frame,
        "oracle": {
            "payload_bytes": EXPECTED_BYTES,
            "payload_sha256": EXPECTED_SHA256,
        },
        "checks": {
            "evf1_valid": True,
            "payload_size_exact": True,
            "payload_sha256_exact": True,
        },
        "result": "pass",
    }
    args.report_output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(args.report_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
