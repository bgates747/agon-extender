"""Generate ordinary MOS VDU commands and independent small bitmap expectations.

Select mode8 in startup/CLI before EXEC. The script restores ordinary coordinates,
font, viewport and affine selection; it never changes the video mode or transport.
Read-pixel requests join previous drawing before mutating referenced buffers.
"""
from pathlib import Path
import argparse
import hashlib
import json

COLOURS = {
    '.': [0, 0, 0], 'R': [255, 0, 0], 'G': [0, 255, 0],
    'B': [0, 0, 255], 'W': [255, 255, 255], 'Y': [255, 255, 0],
    'C': [0, 255, 255], 'M': [255, 0, 255], 'D': [85, 170, 255],
}
PATTERN = ['RGBW', 'Y.CR', 'MDR.']
RGBA8888, RGBA2222, MASK, COPY, MATRIX, BAKED = range(51000, 51006)


def make_case(output):
    output.mkdir(parents=True, exist_ok=False)
    lines, tiles = [], []

    def vdu(*values):
        line = 'VDU ' + ' '.join(str(value) for value in values)
        assert len(line.encode('ascii')) + 2 < 256, line
        lines.append(line)

    def buffer(identity, operation, *values):
        vdu(23, 0, 160, f'{identity};', operation, *values)

    def select(identity):
        vdu(23, 27, 32, f'{identity};')

    def completed_draw():
        vdu(23, 0, 132, '0;', '0;')

    def expect(name, x, y, rows):
        assert rows and len({len(row) for row in rows}) == 1
        tiles.append(dict(name=name, x=x, y=y, rows=rows))

    def draw(name, x, y, rows, direct=False):
        if direct:
            vdu(23, 27, 3, f'{x};', f'{y};')
        else:
            vdu(25, 237, f'{x};', f'{y};')
        completed_draw()
        expect(name, x, y, rows)

    def white_backdrop(x, y):
        vdu(18, 0, 15, 25, 4, f'{x};', f'{y};', 25, 101, f'{x+3};', f'{y+2};')
        completed_draw()

    def write_bitmap(identity, width, height, fmt, data):
        buffer(identity, 0, f'{len(data)};', *data)
        select(identity)
        vdu(23, 27, 33, f'{width};', f'{height};', fmt)

    def matrix(values):
        buffer(MATRIX, 32, 0)
        buffer(MATRIX, 32, 11, 192, *(f'{value & 65535};' for value in values))
        vdu(23, 0, 150, 1, f'{MATRIX};')

    rgba = []
    packed = []
    for i, symbol in enumerate(''.join(PATTERN)):
        # Invisible pixels carry blue RGB, so silently ignoring alpha fails.
        colour = COLOURS['B' if symbol == '.' else symbol]
        # Exercise nonzero alpha as opaque, not just the maximum alpha value.
        alpha8 = 0 if symbol == '.' else (1 if i == 0 else 128 if i == 1 else 255)
        rgba.extend([*colour, alpha8])
        alpha2 = 0 if symbol == '.' else (1 if i == 0 else 2 if i == 1 else 3)
        packed.append((colour[0]//85) | ((colour[1]//85) << 2) |
                      ((colour[2]//85) << 4) | (alpha2 << 6))

    vdu(4, 26, 23, 1, 0, 23, 0, 192, 0, 17, 128, 17, 15, 12)
    vdu(28, 0, 29, 39, 28, 18, 0, 15)
    vdu(23, 0, 248, '1;', '1;')
    vdu(23, 0, 150, 1, '65535;')
    for identity in [RGBA8888, RGBA2222, MASK, COPY, MATRIX, BAKED, 64042, 64043, 64044]:
        buffer(identity, 2)

    vdu(23, 27, 0, 42)
    vdu(23, 27, 1, '4;', '3;', *rgba)
    draw('stream-rgba8888-direct', 24, 32, PATTERN, direct=True)
    write_bitmap(RGBA8888, 4, 3, 0, rgba)
    white_backdrop(48, 32)
    draw('buffer-rgba8888-over-white', 48, 32, [row.replace('.', 'W') for row in PATTERN])
    write_bitmap(RGBA2222, 4, 3, 1, packed)
    draw('buffer-rgba2222', 72, 32, PATTERN)

    vdu(18, 0, 15)
    write_bitmap(MASK, 5, 3, 2, [0x80, 0xF8, 0x28])
    vdu(18, 0, 1)  # Mask retains the white used when it was created.
    draw('mono-creation-colour', 96, 32, ['W....', 'WWWWW', '..W.W'])
    vdu(18, 0, 15)
    vdu(23, 27, 0, 43)
    vdu(23, 27, 2, '4;', '3;', 85, 170, 255, 255)
    select(64043)
    draw('solid-and-id-alias', 120, 32, ['DDDD']*3)

    vdu(25, 4, '24;', '32;')
    vdu(25, 4, '27;', '34;')
    vdu(23, 27, 1, '44;', '0;')
    # Captured transparent areas become actual opaque black screen pixels.
    vdu(25, 4, '144;', '32;')
    vdu(25, 101, '147;', '34;')
    completed_draw()
    select(64044)
    draw('inclusive-screen-capture', 144, 32, PATTERN)
    select(RGBA2222)
    white_backdrop(168, 32)
    draw('rgba2222-over-white', 168, 32, [row.replace('.', 'W') for row in PATTERN])

    buffer(COPY, 13, f'{RGBA2222};', '65535;')
    select(COPY)
    vdu(23, 27, 33, '4;', '3;', 1)
    buffer(RGBA2222, 5, 2, '0;', 240)  # Change only original red to opaque blue.
    select(RGBA2222)
    draw('source-adjust', 24, 64, ['BGBW', *PATTERN[1:]])
    select(COPY)
    draw('copy-independent', 48, 64, PATTERN)

    vdu(24, '73;', '66;', '74;', '65;')  # left,bottom,right,top
    draw('plot-viewport-clip', 72, 64, ['....', '..C.', '.DR.'])
    vdu(26, 28, 0, 29, 39, 28)

    matrix([-1, 0, 3, 0, 1, 0])
    draw('affine-reflection', 24, 104, [row[::-1] for row in PATTERN])
    # Baked reflection uses explicit dimensions; no automatic bound rounding.
    buffer(BAKED, 40, 3, f'{MATRIX};', f'{COPY};', '4;', '3;')
    matrix([2, 0, 0, 0, 2, 0])
    scaled = [''.join(char*2 for char in row) for row in PATTERN for _ in range(2)]
    draw('affine-double-scale', 56, 104, scaled)
    vdu(23, 0, 150, 1, '65535;')
    select(BAKED)
    draw('generated-reflection', 96, 104, [row[::-1] for row in PATTERN])
    select(COPY)
    draw('affine-disabled', 120, 104, PATTERN)

    completed_draw()
    for identity in [RGBA8888, RGBA2222, MASK, COPY, MATRIX, BAKED, 64042, 64043, 64044]:
        buffer(identity, 2)
    vdu(4, 26, 28, 0, 29, 39, 28, 31, 0, 0, 23, 0, 192, 1)
    lines.append('ECHO Bitmap command case complete.')
    data = ('\r\n'.join(lines)+'\r\n').encode('ascii')
    (output/'bitmaps.txt').write_bytes(data)
    manifest = dict(script_sha256=hashlib.sha256(data).hexdigest(),
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    mode=8, surface=[320, 240], command_lines=len(lines),
                    colours=COLOURS, tiles=tiles,
                    scope='Static bitmap pixels; no timing or general compatibility claim')
    (output/'oracle.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ('tiles', 'colours')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    make_case(parser.parse_args().output)
