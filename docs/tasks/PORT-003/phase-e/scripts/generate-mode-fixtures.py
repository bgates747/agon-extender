#!/usr/bin/env python3
"""Generate independent Phase E mode and VDU lifecycle fixtures."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import write_canonical  # noqa: E402


MODES: dict[int, tuple[int, int, int, int]] = {
    0: (640, 480, 16, 60), 1: (640, 480, 4, 60), 2: (640, 480, 2, 60),
    3: (640, 240, 64, 60), 4: (640, 240, 16, 60), 5: (640, 240, 4, 60),
    6: (640, 240, 2, 60), 7: (640, 480, 16, 60), 8: (320, 240, 64, 60),
    9: (320, 240, 16, 60), 10: (320, 240, 4, 60), 11: (320, 240, 2, 60),
    12: (320, 200, 64, 70), 13: (320, 200, 16, 70), 14: (320, 200, 4, 70),
    15: (320, 200, 2, 70), 16: (800, 600, 4, 60), 17: (800, 600, 2, 60),
    18: (1024, 768, 2, 60), 19: (1024, 768, 4, 60), 20: (512, 384, 64, 60),
    21: (512, 384, 16, 60), 22: (512, 384, 4, 60), 23: (512, 384, 2, 60),
    24: (640, 512, 16, 60), 25: (640, 512, 4, 60), 26: (640, 512, 2, 60),
    27: (640, 256, 64, 60), 28: (640, 256, 16, 60), 29: (640, 256, 4, 60),
    30: (640, 256, 2, 60),
    129: (640, 480, 4, 60), 130: (640, 480, 2, 60),
    132: (640, 240, 16, 60), 133: (640, 240, 4, 60), 134: (640, 240, 2, 60),
    136: (320, 240, 64, 60), 137: (320, 240, 16, 60), 138: (320, 240, 4, 60),
    139: (320, 240, 2, 60), 140: (320, 200, 64, 70), 141: (320, 200, 16, 70),
    142: (320, 200, 4, 70), 143: (320, 200, 2, 70), 145: (800, 600, 2, 60),
    146: (1024, 768, 2, 60), 149: (512, 384, 16, 60), 150: (512, 384, 4, 60),
    151: (512, 384, 2, 60), 153: (640, 512, 4, 60), 154: (640, 512, 2, 60),
    156: (640, 256, 16, 60), 157: (640, 256, 4, 60), 158: (640, 256, 2, 60),
}

LEGACY = {
    0: (1024, 768, 2, 60),
    1: (512, 384, 16, 60),
    2: (320, 200, 64, 75),
    3: (640, 480, 16, 60),
}

FORMAT = {2: "PALETTE2", 4: "PALETTE4", 8: "PALETTE8", 16: "PALETTE16", 64: "SBGR2222"}


def mode_case(mode: int, spec: tuple[int, int, int, int], legacy: bool | str) -> dict[str, Any]:
    width, height, colours, refresh = spec
    return {
        "id": f"mode-{mode}-{'legacy' if legacy is True else 'current' if legacy is False else 'either'}",
        "mode": mode,
        "legacy_modes": legacy,
        "width": width,
        "height": height,
        "colours": colours,
        "native_format": FORMAT[colours],
        "refresh_hz": refresh,
        "period_microseconds": (1_000_000 + refresh // 2) // refresh,
        "double_buffered": mode > 128,
        "logical_scale": {"x_numerator": 1280, "x_denominator": width, "y_numerator": 1024, "y_denominator": height},
        "rectangular_pixels": width / height > 2,
        "teletext": mode == 7,
    }


def event_trace(attempts: list[dict[str, Any]], double_buffered: bool, mouse_visible: bool) -> list[str]:
    events = ["context.cls", "display.wait-vsync", "teletext.disable", "callbacks.remove-all-vsync"]
    events.extend(f"facade.change-mode:{item['mode']}:{item['result']}" for item in attempts)
    events.append("contexts.reset-all")
    if double_buffered:
        events.extend(["display.swap", "context.cls"])
    if mouse_visible:
        events.append("cursor.show")
    events.append("cursor-positioner.reset")
    if mouse_visible:
        events.append("mouse-variables.update")
    events.extend([
        "callbacks.call-mode-change",
        "callbacks.call-sending-mode-packet",
        "packet.send-mode",
    ])
    return events


def lifecycle_case(case_id: str, requested: int, old_mode: int, attempts: list[dict[str, Any]],
                   result_mode: int, double_buffered: bool, mouse_visible: bool,
                   width: int, height: int, colours: int, chars: tuple[int, int]) -> dict[str, Any]:
    char_width, char_height = chars
    packet = [width & 255, width >> 8, height & 255, height >> 8,
              char_width, char_height, colours, result_mode]
    return {
        "id": case_id,
        "initial": {"video_mode": old_mode, "teletext": old_mode == 7, "mouse_visible": mouse_visible},
        "requested_mode": requested,
        "attempts": attempts,
        "result": {"video_mode": result_mode, "double_buffered": double_buffered, "width": width,
                   "height": height, "colours": colours, "char_width": char_width, "char_height": char_height},
        "expected_events": event_trace(attempts, double_buffered, mouse_visible),
        "expected_mode_packet": packet,
    }


def build() -> dict[str, Any]:
    modes = []
    for mode, spec in MODES.items():
        if mode in LEGACY:
            modes.append(mode_case(mode, LEGACY[mode], True))
            modes.append(mode_case(mode, spec, False))
        else:
            modes.append(mode_case(mode, spec, "either"))
    lifecycle = [
        lifecycle_case("requested-success", 8, 1, [{"mode": 8, "result": 0}], 8, False, False, 320, 240, 64, (40, 30)),
        lifecycle_case("requested-fails-old-succeeds", 18, 4, [{"mode": 18, "result": 2}, {"mode": 4, "result": 0}], 4, False, True, 640, 240, 16, (80, 30)),
        lifecycle_case("requested-and-old-fail-default-succeeds", 18, 4, [{"mode": 18, "result": 2}, {"mode": 4, "result": 2}, {"mode": 1, "result": 0}], 1, False, False, 640, 480, 4, (80, 60)),
        lifecycle_case("invalid-mode-falls-back", 31, 9, [{"mode": 31, "result": -1}, {"mode": 9, "result": 0}], 9, False, False, 320, 240, 16, (40, 30)),
        lifecycle_case("teletext-init-fails-old-succeeds", 7, 3, [{"mode": 7, "result": 3}, {"mode": 3, "result": 0}], 3, False, False, 640, 240, 64, (80, 30)),
        lifecycle_case("double-buffer-success-visible-cursor", 129, 1, [{"mode": 129, "result": 0}], 129, True, True, 640, 480, 4, (80, 60)),
        lifecycle_case("service-start-fails-old-succeeds", 12, 1, [{"mode": 12, "result": 2}, {"mode": 1, "result": 0}], 1, False, False, 640, 480, 4, (80, 60)),
    ]
    payload = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_e_mode_fixtures",
        "generated_by": "docs/tasks/PORT-003/phase-e/scripts/generate-mode-fixtures.py",
        "oracle": "independent transcription of official documentation and the frozen Phase E contract; no production import or output",
        "mode_cases": modes,
        "lifecycle_cases": lifecycle,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["fixture_set_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return payload


def main() -> int:
    output = ROOT / "docs/tasks/PORT-003/phase-e/fixtures/modes-and-lifecycle.yaml"
    write_canonical(output, build())
    print(f"wrote {len(build()['mode_cases'])} mode and {len(build()['lifecycle_cases'])} lifecycle fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
