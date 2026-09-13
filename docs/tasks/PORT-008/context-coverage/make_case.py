"""Finite ordinary MOS context commands with independently specified pixel tiles.

Select mode8 outside this script. Context/buffer IDs are owned by this case;
MODE clears prior contexts before entry. No direct UART, private reply handler,
firmware change or visual timing claim is involved. The bitmap checker's strict
PNG/EVF decoder accepts the generated oracle without sampling renderer code.
"""
from pathlib import Path
import argparse
import hashlib
import json

COLOURS = {'.': [0, 0, 0], 'R': [255, 0, 0], 'G': [0, 255, 0],
           'B': [0, 0, 255], 'W': [255, 255, 255], 'M': [255, 0, 255]}
STACKS = (41, 42, 43, 44, 45)
BITMAPS = (51100, 51101)


def make_case(output):
    output.mkdir(parents=True, exist_ok=False)
    lines, tiles = [], []

    def vdu(*values):
        line = 'VDU ' + ' '.join(str(value) for value in values)
        assert len(line.encode('ascii')) + 2 < 256, line
        lines.append(line)

    def context(operation, *args):
        vdu(23, 0, 200, operation, *args)

    def join():
        vdu(23, 0, 132, '0;', '0;')

    def origin(x, y):
        vdu(29, f'{x};', f'{y};')

    def move(x, y):
        vdu(25, 4, f'{x};', f'{y};')

    def rect(x, y):
        move(x, y)
        vdu(25, 101, f'{x+3};', f'{y+2};')
        join()

    def colour(index, mode=0):
        vdu(18, mode, index)

    def full_viewport():
        vdu(26, 28, 0, 29, 39, 28)

    def base():
        context(0, 0)
        context(7)
        vdu(20, 4, 23, 1, 0, 23, 0, 192, 0)
        origin(0, 0)
        full_viewport()
        colour(9)

    def tile(name, rows):
        assert rows and len({len(row) for row in rows}) == 1
        number = len(tiles)
        x, y = 24 + (number % 6)*44, 32 + (number//6)*40
        assert x+len(rows[0])+2 < 320 and y+len(rows)+2 < 220
        tiles.append(dict(name=name, x=x, y=y, rows=rows))
        return x, y

    def buffer(identity, operation, *values):
        vdu(23, 0, 160, f'{identity};', operation, *values)

    def bitmap(identity):
        vdu(23, 27, 32, f'{identity};')

    def plot_bitmap(x, y):
        vdu(25, 237, f'{x};', f'{y};')
        join()

    base()
    vdu(26, 12)
    full_viewport()
    for identity in STACKS:
        context(1, identity)
    for identity in BITMAPS:
        buffer(identity, 2)

    x, y = tile('saved-foreground', ['GGGG..RRRR']*3)
    context(3)
    colour(10)
    rect(x, y)
    context(4)
    rect(x+6, y)

    base()
    x, y = tile('saved-origin', ['RRRR..GGGG']*3)
    origin(x, y)
    context(3)
    origin(x+6, y)
    colour(10)
    rect(0, 0)
    context(4)
    rect(0, 0)

    base()
    x, y = tile('saved-graphics-viewport', ['.RR...GGGG']*3)
    vdu(24, f'{x+1};', f'{y+2};', f'{x+2};', f'{y};')
    context(3)
    full_viewport()
    colour(10)
    rect(x+6, y)
    context(4)
    rect(x, y)

    base()
    x, y = tile('saved-relative-graphics-cursor', ['....', '..R.', '....'])
    move(x, y)
    context(3)
    move(x+12, y+12)
    context(4)
    vdu(25, 65, '2;', '1;')
    join()

    base()
    x, y = tile('saved-xor-painting', ['MMMM']*3)
    colour(12)
    rect(x, y)
    colour(9, 3)
    context(3)
    colour(10)
    context(4)
    rect(x, y)

    base()
    x, y = tile('named-stacks-independent', ['RRRR..GGGG']*3)
    context(0, 41)
    colour(10)
    context(0, 0)
    rect(x, y)
    context(0, 41)
    rect(x+6, y)

    base()
    x, y = tile('select-clones-saved-stack', ['RRRR']*3)
    context(3)
    colour(10)
    context(0, 42)
    context(4)
    rect(x, y)

    base()
    x, y = tile('save-copy-existing', ['GGGG..RRRR']*3)
    context(5, 41)
    rect(x, y)
    context(4)
    rect(x+6, y)

    base()
    x, y = tile('save-copy-keeps-stack-id', ['BBBB..GGGG']*3)
    context(5, 41)
    colour(12)
    context(0, 42)
    context(0, 0)
    rect(x, y)
    context(0, 41)
    rect(x+6, y)

    base()
    x, y = tile('save-copy-absent-still-saves', ['RRRR']*3)
    context(5, 45)
    colour(10)
    context(4)
    rect(x, y)

    base()
    x, y = tile('restore-all-oldest', ['RRRR']*3)
    context(3)
    colour(10)
    context(3)
    colour(12)
    context(6)
    rect(x, y)

    base()
    x, y = tile('clear-stack-keeps-current', ['GGGG']*3)
    context(3)
    colour(10)
    context(7)
    context(4)
    context(6)
    rect(x, y)

    base()
    x, y = tile('delete-inactive-then-clone', ['RRRR']*3)
    context(0, 43)
    colour(10)
    context(0, 0)
    context(1, 43)
    context(0, 43)
    rect(x, y)

    base()
    x, y = tile('delete-active-is-noop', ['GGGG']*3)
    context(0, 44)
    colour(10)
    context(1, 44)
    context(0, 0)
    context(0, 44)
    rect(x, y)

    base()
    x, y = tile('reset-paint-preserves-origin-clip', ['.WW.']*3)
    vdu(24, f'{x+1};', f'{y+2};', f'{x+2};', f'{y};')
    origin(x, y)
    context(2, 1)
    rect(0, 0)

    base()
    x, y = tile('reset-position-preserves-paint', ['GGGG']*3)
    origin(100, 100)
    vdu(24, '0;', '2;', '2;', '0;')
    colour(10)
    context(2, 2)
    # Bit1 explicitly restores logical coordinates. Test a zero-origin,
    # unrestricted pixel draw after switching only that coordinate selector.
    vdu(23, 0, 192, 0)
    rect(x, y)

    base()
    x, y = tile('palette-storage-global', ['RRRR..BBBB']*3)
    colour(9)
    rect(x, y)
    context(3)
    vdu(19, 9, 255, 0, 0, 255)
    context(4)
    colour(9)
    rect(x+6, y)

    base()
    x, y = tile('bitmap-selection-local-storage-global', ['BB..GG'])
    for identity, data in zip(BITMAPS, ([195, 195], [204, 204])):
        buffer(identity, 0, '2;', *data)
        bitmap(identity)
        vdu(23, 27, 33, '2;', '1;', 1)
    bitmap(BITMAPS[0])
    context(3)
    bitmap(BITMAPS[1])
    plot_bitmap(x+4, y)
    buffer(BITMAPS[0], 5, 194, '0;', '2;', 240, 240)
    context(4)
    plot_bitmap(x, y)

    join()
    base()
    for identity in STACKS:
        context(1, identity)
    for identity in BITMAPS:
        buffer(identity, 2)
    vdu(20, 4, 26, 28, 0, 29, 39, 28, 31, 0, 0, 23, 0, 192, 1)
    lines.append('ECHO Context command case complete.')
    data = ('\r\n'.join(lines)+'\r\n').encode('ascii')
    (output/'contexts.txt').write_bytes(data)
    manifest = dict(script_sha256=hashlib.sha256(data).hexdigest(),
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    mode=8, surface=[320, 240], command_lines=len(lines),
                    colours=COLOURS, tiles=tiles,
                    scope='Static context pixels; no timing or general compatibility claim')
    (output/'oracle.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ('tiles', 'colours')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    make_case(parser.parse_args().output)
