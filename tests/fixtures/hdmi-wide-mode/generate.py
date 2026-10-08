#!/usr/bin/env python3
"""848x480 mode96 pattern; reuse lcd-color-bars' VDU drawing idioms.

No mode command: startup owns mode selection. Build ID is supplied at creation
and displayed so screenshots identify the exact test article.
"""
import argparse
import re
import struct
from pathlib import Path


def pattern(build_id):
    if not re.fullmatch(r'hdmi-wide-mode-r01-b\d{4}(?:-\d{2}){5}Z', build_id):
        raise ValueError('Expected a full hdmi-wide-mode-r01 build identity')
    v = bytearray([20, 17, 128, 17, 7, 12, 23, 1, 0, 23, 0, 192, 0, 26])
    colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
              (0, 255, 255), (255, 0, 255), (255, 255, 0), (255, 255, 255)]
    for i, rgb in enumerate(colors):
        v.extend([19, i, 255, *rgb])

    def plot(op, x, y):
        assert 0 <= x < 848 and 0 <= y < 480
        v.extend(bytes([25, op]) + struct.pack('<HH', x, y))

    def line(c, x, y, x2, y2):
        v.extend([18, 0, c]); plot(4, x, y); plot(5, x2, y2)

    def rect(c, x, y, x2, y2):
        v.extend([18, 0, c]); plot(4, x, y); plot(101, x2, y2)

    def text(x, y, message):
        assert x + len(message) <= 106 and y < 60
        v.extend([17, 7, 17, 128, 31, x, y]); v.extend(message.encode('ascii'))

    text(2, 2, 'Visual validation - full-width 848x480, 64 colors')
    text(2, 3, build_id + ' (experimental)')
    text(2, 5, 'All four white edges visible; circle round; square square; Esc exits.')
    for i, name in enumerate(['Black', 'Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow', 'White']):
        rect(i, i * 106, 96, (i + 1) * 106 - 1, 223)
        text((i * 106 + 8) // 8, 9, name)
    # The middle square/circle exposes aspect errors. Dashed vertical guides
    # delimit where the familiar640-wide canvas sits in this same carrier.
    for y in range(8, 472, 16):
        line(7, 104, y, 104, y + 7); line(7, 743, y, 743, y + 7)
    for a, b in [((360, 264), (488, 264)), ((488, 264), (488, 392)),
                 ((488, 392), (360, 392)), ((360, 392), (360, 264))]:
        line(7, *a, *b)
    v.extend([18, 0, 6]); plot(4, 424, 328); plot(149, 488, 328)
    text(2, 52, 'Drawing reaches both sides beyond the dashed 640-pixel guide.')
    text(2, 55, 'Top-left (0,0)'); text(89, 55, 'Right edge x=847')
    text(2, 57, 'Bottom edge y=479; no pillarboxes in this logical mode.')
    for a, b in [((0, 0), (847, 0)), ((847, 0), (847, 479)),
                 ((847, 479), (0, 479)), ((0, 479), (0, 0))]:
        line(7, *a, *b)
    return bytes(v)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--build-id', required=True)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    a.output.write_bytes(pattern(a.build_id))
