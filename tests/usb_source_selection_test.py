#!/usr/bin/env python3
"""Check USB ownership in the canonical native P4 profile authority."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
document = json.loads((ROOT / "vdp/build/p4-profiles.json").read_text())
profile = document["profiles"]["p4-console"]
sources = set(profile["sources"])
dependencies = {**document["common"]["dependencies"],
                **profile["dependencies"]}

assert "video/extender/boot/p4_console.cpp" in sources
assert dependencies["espressif/usb_host_hid"] == "1.2.1"
assert "AGON_EXTENDER_REMOTE_KEYBOARD=1" in profile["definitions"]
assert not any("usb_keyboard" in source for source in sources)
print("PASS: native console profile owns the integrated USB input path")
