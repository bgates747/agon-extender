"""Disable the retained test fixture's mode setter; startup owns video mode.

This is a one-byte test-only derivative, not a production Nurples change.
The exact parent identity and instruction are mandatory. Symbol addresses,
game logic, pacing and telemetry storage remain unchanged.
"""
import argparse
import hashlib
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('parent', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
b = bytearray(a.parent.read_bytes())
assert hashlib.sha256(b).hexdigest() == '8bd48c691b3f48289554762d99be12f75e66b7ef8ea454c4a62fe71f69559379'
assert b[0x1500] == 0x32
b[0x1500] = 0xc9  # RET at vdu_set_screen_mode, address 0x041500.
assert hashlib.sha256(b).hexdigest() == '68fb3d4ce4b33d7ff325781f9a76e74a87500894acb119180f2bd8e51c31b03e'
with a.output.open('xb') as f:
    f.write(b)
