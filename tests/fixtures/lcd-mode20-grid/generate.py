#!/usr/bin/env python3
"""Generate a static native-pixel 512x384 grid with an app-owned mode switch."""
import struct
from pathlib import Path

WIDTH, HEIGHT = 512, 384
COLS, ROWS = 8, 6
CELL_W, CELL_H = WIDTH // COLS, HEIGHT // ROWS

v = bytearray([22, 20, 20, 17, 128, 17, 7, 12, 23, 1, 0,
               23, 0, 192, 0, 26])
palette = [
    (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (0, 255, 255), (255, 0, 255), (255, 255, 0), (255, 255, 255),
    (85, 0, 0), (0, 85, 0), (0, 0, 85), (85, 85, 0),
    (0, 85, 85), (85, 0, 85), (170, 85, 0), (85, 170, 255),
]
for logical, rgb in enumerate(palette):
    v.extend([19, logical, 255, *rgb])


def plot(code, x, y):
    v.extend(bytes([25, code]) + struct.pack('<HH', x, y))


def rect(colour, x0, y0, x1, y1):
    v.extend([18, 0, colour])
    plot(4, x0, y0)
    plot(101, x1, y1)


def text(column, row, value, foreground=7, background=0):
    v.extend([17, foreground, 17, 128 + background, 31, column, row])
    v.extend(value.encode('ascii'))


fills = [1, 4, 2, 5, 3, 6, 14, 15, 8, 12, 9, 13, 10, 11]
for row in range(ROWS):
    for column in range(COLS):
        fill = fills[(row * 5 + column * 3) % len(fills)]
        x0, y0 = column * CELL_W, row * CELL_H
        rect(fill, x0 + 1, y0 + 1, x0 + CELL_W - 2, y0 + CELL_H - 2)
        label = f'{chr(65 + column)}{row + 1}'
        ink = 0 if fill in (2, 4, 6, 7, 15) else 7
        text(column * 8 + 3, row * 8 + 3, label, ink, fill)

# Exact grid lines and asymmetric edge/corner keys expose clipping, mirroring,
# rotation and one-pixel displacement.
for x in range(0, WIDTH, CELL_W):
    rect(0, x, 0, x, HEIGHT - 1)
for y in range(0, HEIGHT, CELL_H):
    rect(0, 0, y, WIDTH - 1, y)
rect(7, 0, 0, WIDTH - 1, 0)                    # top: white
rect(1, 0, 1, 0, HEIGHT - 2)                   # left: red
rect(3, WIDTH - 1, 1, WIDTH - 1, HEIGHT - 2)   # right: blue
rect(5, 0, HEIGHT - 1, WIDTH - 1, HEIGHT - 1)  # bottom: magenta
rect(6, 1, 1, 8, 8)                            # upper-left: yellow
rect(4, WIDTH - 9, 1, WIDTH - 2, 8)            # upper-right: cyan
rect(2, 1, HEIGHT - 9, 8, HEIGHT - 2)          # lower-left: green
rect(7, WIDTH - 9, HEIGHT - 9, WIDTH - 2, HEIGHT - 2)  # lower-right

Path(__file__).with_name('grid.vdu').write_bytes(v)
