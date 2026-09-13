"""Finite Copper stages with literal row-colour oracles, independent of VDP code.

Select mode9/10/11 before EXEC setup.txt; capture every stage in order. Palette
and bitmap resources remain owned until cleanup. Inputs never switch modes.
"""
from pathlib import Path
import argparse
import hashlib
import json

STAGES = ('setup', 'edit', 'replace', 'reset', 'cleanup')
MODES = {16: 9, 4: 10, 2: 11}
COLOURS = {'.': [0, 0, 0], 'W': [255, 255, 255], 'R': [255, 0, 0],
           'G': [0, 255, 0], 'B': [0, 0, 255], 'Y': [255, 255, 0],
           'M': [255, 0, 255], 'C': [0, 255, 255], 'L': [170, 170, 170]}
PALETTES = (1001, 1002, 1003, 1004)
LIST, WHITE, CYAN = 51400, 51401, 51402
MASK = ['W.WW', '.WW.', 'WW.W', 'W..W', '.WWW', 'WWW.']


def row_colour(stage, y):
    # Literal documented row intervals, deliberately not parsed from the
    # generated command buffer or copied from retained controller algorithms.
    if stage == 'setup':
        return 'W' if y < 48 else 'R' if y < 80 else 'G' if y < 112 else 'B' if y < 144 else 'W'
    if stage == 'edit':
        return 'L' if y < 48 else 'M' if y < 80 else 'L' if y < 112 else 'G' if y < 144 else 'W' if y < 176 else 'L'
    if stage == 'replace':
        return 'C' if y < 64 else 'L' if y < 96 else 'M'
    if stage == 'reset':
        return 'L'
    raise ValueError(stage)


def make_case(output, depth):
    output.mkdir(parents=True, exist_ok=False)
    scripts = {stage: [] for stage in STAGES}
    stage = 'setup'
    tiles = []

    def vdu(*values):
        line = 'VDU ' + ' '.join(str(value) for value in values)
        assert len(line.encode('ascii')) + 2 < 256, line
        scripts[stage].append(line)

    def copper(op, *values):
        vdu(23, 0, 196, op, *values)

    def palette(identity, symbol, index=1):
        copper(2, f'{identity};', index, *COLOURS[symbol])

    def buffer(identity, op, *values):
        vdu(23, 0, 160, f'{identity};', op, *values)

    def join():
        vdu(23, 27, 15, 23, 0, 132, '0;', '0;')

    def signal_list(pairs, extra_block=False):
        buffer(LIST, 2)
        values = [f'{value};' for pair in pairs for value in pair]
        buffer(LIST, 0, f'{len(pairs)*4};', *values)
        if extra_block:
            # If a consumer erroneously reads the last block instead of the
            # first, this makes the entire image blue. If it concatenates the
            # blocks, rows192 onward become blue instead of the first block's
            # extended primary-colour tail. Both mistakes have visible pixels.
            buffer(LIST, 0, '4;', '240;', '1003;')
        copper(3, f'{LIST};')
        # Copper owns the copied output list, not the source buffer lifetime.
        buffer(LIST, 2)
        copper(3, f'{LIST};')  # absent source must leave the installed list

    def rectangle(x, y, width, height):
        vdu(18, 0, 1, 25, 4, f'{x};', f'{y};', 25, 101,
            f'{x+width-1};', f'{y+height-1};')
        join()

    def tile(name, x, y, rows, kind='framebuffer', delayed=False):
        tiles.append(dict(name=name, x=x, y=y, rows=rows,
                          kind=kind, delayed=delayed))

    def sprite(identity, asset, x, y, hardware):
        vdu(23, 27, 4, identity, 23, 27, 5, 23, 27, 38, f'{asset};',
            23, 27, 19 if hardware else 20, 23, 27, 13, f'{x};', f'{y};',
            23, 27, 11)

    vdu(23, 27, 17, 23, 0, 249, '1024;', 23, 0, 248, '2;', '1;',
        23, 0, 248, '784;', '0;')
    vdu(4, 26, 20, 23, 1, 0, 23, 0, 192, 0, 17, 128, 12)
    vdu(28, 0, 29, 39, 28)
    # Keep all unused entries black. White sprite assets continue selecting
    # index1 after primary white becomes light grey; duplicate white entries
    # in the default16-colour palette would make that assertion ambiguous.
    for index in range(depth):
        vdu(19, index, 255, *(COLOURS['W'] if index == 1 else COLOURS['.']))
    vdu(18, 0, 128)
    copper(4)
    for identity in PALETTES:
        copper(1, f'{identity};')
    for identity in (LIST, WHITE, CYAN):
        buffer(identity, 2)
    copper(0, '1001;')
    palette(1001, 'R')
    copper(0, '1002;')
    palette(1002, 'G')
    palette(1003, 'B', depth+1)  # implicit create, wrapped entry index1
    copper(0, '1004;')  # unchanged copy of primary white

    for identity, symbol in ((WHITE, 'W'), (CYAN, 'C')):
        rgb = COLOURS[symbol]
        packed = rgb[0]//85 | (rgb[1]//85 << 2) | (rgb[2]//85 << 4) | 192
        data = [packed if pixel == 'W' else 0 for pixel in ''.join(MASK)]
        buffer(identity, 0, f'{len(data)};', *data)
        vdu(23, 27, 32, f'{identity};', 23, 27, 33, '4;', '6;', 1)

    tile('primary-index-strip-crosses-every-boundary', 24, 32, ['WWWW']*180)
    rectangle(24, 32, 4, 180)
    tile('bitmap-crosses-copy-palette-boundary', 72, 142, MASK)
    vdu(23, 27, 32, f'{WHITE};', 25, 237, '72;', '142;')
    join()
    tile('software-sprite-follows-copper', 120, 78, MASK)
    sprite(0, WHITE, 120, 78, False)
    tile('hardware-sprite-ignores-copper', 168, 46,
         [row.replace('W', 'C') for row in MASK], kind='hardware')
    sprite(1, CYAN, 168, 46, True)
    # Hardware wins overlaps but transparent pixels reveal the indexed layer.
    mixed = []
    for row in MASK:
        pixels = list(row+'..')
        for x, pixel in enumerate(row):
            if pixel == 'W':
                pixels[x+2] = 'C'
        mixed.append(''.join(pixels))
    tile('hardware-over-software-at-row-boundary', 212, 110, mixed, kind='mixed')
    sprite(2, WHITE, 212, 110, False)
    sprite(3, CYAN, 214, 110, True)
    tile('draw-after-primary-mutation', 264, 32, ['WWWW']*180, delayed=True)
    vdu(23, 27, 7, 4)
    join()
    signal_list([(48, 0), (32, 1001), (32, 1002), (32, 1003),
                 (32, 1004), (16, 1005)], extra_block=True)

    stage = 'edit'
    vdu(19, 1, 255, 170, 170, 170)
    palette(1001, 'M')
    copper(1, '1002;')
    palette(1002, 'C')  # new ID does not relink entries redirected to primary
    palette(1003, 'G', depth+1)
    copper(1, '1005;')  # absent palette is harmless
    rectangle(264, 32, 4, 180)

    stage = 'replace'
    copper(0, '1004;')  # explicit create again copies current primary light grey
    # Shorten six nodes to four. The fourth entry begins below the image and
    # must not replace the magenta rows still visible through row239.
    signal_list([(64, 1002), (32, 1004), (144, 1001), (16, 1003)])

    stage = 'reset'
    copper(4)
    copper(1, '0;')  # default palette cannot be deleted
    # Never use delete-all here: the retained implementation erases the map
    # while iterating it; its lifetime safety is a separate unresolved case.
    for identity in PALETTES:
        copper(1, f'{identity};')
    join()

    stage = 'cleanup'
    vdu(23, 27, 17)
    join()
    copper(4)
    for identity in (LIST, WHITE, CYAN):
        buffer(identity, 2)
    vdu(23, 0, 249, '2;', 23, 0, 249, '784;', 23, 0, 249, '1024;',
        4, 26, 20, 17, 128, 12, 28, 0, 29, 39, 28, 23, 0, 192, 1)

    manifests = []
    for stage in STAGES:
        vdu(31, 0, 0)
        scripts[stage].append(f'ECHO Copper {stage} complete.')
        data = ('\r\n'.join(scripts[stage])+'\r\n').encode('ascii')
        (output/(stage+'.txt')).write_bytes(data)
        expected = []
        for item in tiles:
            rows = []
            for y, row in enumerate(item['rows']):
                if stage == 'cleanup' or (stage == 'setup' and item['delayed']):
                    rows.append('.'*len(row))
                else:
                    rows.append(row.replace('W', row_colour(stage, item['y']+y)))
            expected.append(dict(name=item['name'], x=item['x'], y=item['y'], rows=rows))
        manifest = dict(stage=stage, mode=MODES[depth], depth=depth, surface=[320, 240],
                        script_sha256=hashlib.sha256(data).hexdigest(),
                        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                        command_lines=len(scripts[stage]), colours=COLOURS, tiles=expected,
                        scope='Static Copper output states; no timing or full API qualification')
        (output/(stage+'-oracle.json')).write_text(json.dumps(manifest, indent=2)+'\n')
        manifests.append({k: v for k, v in manifest.items() if k not in ('colours', 'tiles')})
    (output/'manifest.json').write_text(json.dumps(manifests, indent=2)+'\n')
    print(json.dumps(manifests, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--depth', type=int, required=True, choices=MODES)
    args = parser.parse_args()
    make_case(args.output, args.depth)
