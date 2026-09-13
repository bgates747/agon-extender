"""Generate ordinary VDU depth/palette cases; choose MODE outside each script.

Paletted modes recolour existing white pixels to red after the final palette
change. Mode8 stores actual RGB222 pixels and retains white. Expected literal
tiles encode that documented difference without importing renderer code.
"""
from pathlib import Path
import argparse
import hashlib
import json

MODES = {64: 8, 16: 9, 4: 10, 2: 11}
COLOURS = {'.': [0, 0, 0], 'W': [255, 255, 255],
           'R': [255, 0, 0], 'B': [0, 0, 255]}
PATTERN = ['W.tB', 'tW.B', 'BWt.']
OVER_WHITE = ['W.WB', 'WW.B', 'BWW.']
OWNED = (51200, 51201, 51202, 64061, 64062)


def make_case(output, depth):
    output.mkdir(parents=True, exist_ok=False)
    lines, tiles = [], []

    def vdu(*values):
        line = 'VDU ' + ' '.join(str(value) for value in values)
        assert len(line.encode('ascii')) + 2 < 256, line
        lines.append(line)

    def join():
        vdu(23, 0, 132, '0;', '0;')

    def buffer(identity, operation, *values):
        vdu(23, 0, 160, f'{identity};', operation, *values)

    def bitmap(identity):
        vdu(23, 27, 32, f'{identity};')

    def tile(name, rows, after=False):
        if depth == 2:
            # Retained vdp-gl uses HSV distance, not Euclidean RGB. Against
            # black/white, saturated blue shares white's V and maps to white.
            # Initial case01 assumed RGB distance and was disproved by stock;
            # preserve that evidence instead of treating this as a port repair.
            rows = [row.replace('B', 'W') for row in rows]
        if not after and depth != 64:
            rows = [row.replace('W', 'R') for row in rows]
        number = len(tiles)
        x, y = 24+(number % 6)*44, 32+(number//6)*40
        assert rows and len({len(row) for row in rows}) == 1
        tiles.append(dict(name=name, x=x, y=y, rows=rows))
        return x, y

    def rect(x, y, width=4, height=3):
        vdu(25, 4, f'{x};', f'{y};', 25, 101,
            f'{x+width-1};', f'{y+height-1};')
        join()

    def plot(x, y, direct=False):
        if direct:
            vdu(23, 27, 3, f'{x};', f'{y};')
        else:
            vdu(25, 237, f'{x};', f'{y};')
        join()

    def create(identity, width, height, fmt, data):
        buffer(identity, 0, f'{len(data)};', *data)
        bitmap(identity)
        vdu(23, 27, 33, f'{width};', f'{height};', fmt)

    vdu(4, 26, 20, 23, 1, 0, 23, 0, 192, 0, 17, 128, 12)
    vdu(28, 0, 29, 39, 28)
    for index in range(depth):
        # All indexed-mode entries are distinct. Blue is exact except in the
        # two-colour black/white mode, where the retained HSV LUT maps it white.
        if index == 1:
            vdu(19, index, 255, 255, 255, 255)
        else:
            vdu(19, index, index, 0, 0, 0)
    vdu(18, 0, 1, 18, 0, 128)
    for identity in OWNED:
        buffer(identity, 2)

    x, y = tile('paint-before-palette-change', ['WWWW']*3)
    rect(x, y)

    rgba, packed = [], []
    for i, symbol in enumerate(''.join(PATTERN)):
        rgb = [255, 0, 255] if symbol == 't' else COLOURS[symbol]
        alpha = 0 if symbol == 't' else (1 if i == 0 else 128 if i == 5 else 255)
        rgba.extend([*rgb, alpha])
        alpha2 = 0 if symbol == 't' else (1 if i == 0 else 2 if i == 5 else 3)
        packed.append((rgb[0]//85) | ((rgb[1]//85) << 2) |
                      ((rgb[2]//85) << 4) | (alpha2 << 6))

    create(51200, 4, 3, 0, rgba)
    x, y = tile('rgba8888-alpha-and-palette', OVER_WHITE)
    rect(x, y)
    plot(x, y)
    captured_origin = (x, y)

    create(51201, 4, 3, 1, packed)
    x, y = tile('rgba2222-alpha-and-palette', OVER_WHITE)
    rect(x, y)
    plot(x, y)

    mask = ['W.......W', 'WW.W.W.W.', '..WWW....']
    mask_bytes = []
    for row in mask:
        value = int(''.join('1' if pixel == 'W' else '0' for pixel in row).ljust(16, '0'), 2)
        mask_bytes.extend([value >> 8, value & 255])
    create(51202, 9, 3, 2, mask_bytes)
    vdu(18, 0, 0)
    x, y = tile('mono-byte-row-and-creation-colour', mask)
    plot(x, y)
    vdu(18, 0, 1)

    vdu(23, 27, 0, 61, 23, 27, 2, '4;', '3;', 255, 255, 255, 255)
    bitmap(64061)
    x, y = tile('solid-bitmap-and-alias', ['WWWW']*3)
    plot(x, y, direct=True)

    cx, cy = captured_origin
    vdu(25, 4, f'{cx};', f'{cy};', 25, 4, f'{cx+3};', f'{cy+2};')
    vdu(23, 27, 1, '62;', '0;')
    bitmap(64062)
    x, y = tile('screen-capture-before-remap', OVER_WHITE)
    rect(x, y)
    plot(x, y)

    x, y = tile('xor-white-erases-selected-pixels', ['W..W']*3)
    rect(x, y)
    vdu(18, 3, 1)
    rect(x+1, y, width=2)
    vdu(18, 0, 1)

    # This changes existing indexed pixels. The 64-colour frame retains actual
    # RGB values, so its prior pixels remain white. Keep this palette in place
    # until capture; ordinary recovery VDU20 restores defaults afterward.
    join()
    vdu(19, 1, 48, 0, 0, 0)
    vdu(18, 0, 1)
    x, y = tile('paint-after-palette-change', ['RRRR']*3, after=True)
    rect(x, y)
    vdu(19, 1, 254, 0, 255, 0)
    vdu(18, 0, 1)
    x, y = tile('invalid-physical-colour-ignored', ['RRRR']*3, after=True)
    rect(x, y)

    join()
    for identity in OWNED:
        buffer(identity, 2)
    vdu(4, 26, 28, 0, 29, 39, 28, 31, 0, 0, 17, 1, 23, 0, 192, 1)
    lines.append(f'ECHO Palette case complete: {depth} colours.')
    data = ('\r\n'.join(lines)+'\r\n').encode('ascii')
    (output/'palette.txt').write_bytes(data)
    manifest = dict(script_sha256=hashlib.sha256(data).hexdigest(),
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    mode=MODES[depth], depth=depth, surface=[320, 240],
                    command_lines=len(lines), colours=COLOURS, tiles=tiles,
                    scope='Static palette/depth pixels; no timing or full mode qualification')
    (output/'oracle.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ('tiles', 'colours')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--depth', required=True, type=int, choices=MODES)
    args = parser.parse_args()
    make_case(args.output, args.depth)
