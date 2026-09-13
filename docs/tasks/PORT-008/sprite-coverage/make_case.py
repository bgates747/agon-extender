"""Generate finite sprite setup/update/cleanup scripts and literal pixel oracles.

Select the mode before setup.txt. Capture each completed stage before invoking
the next. Frame storage stays alive until cleanup has reset the sprites.
Software sprites are tested only in single-buffer mode8. Hardware cases also
exercise output colour over mode11 and mixed software/hardware layer order.
"""
from pathlib import Path
import argparse
import hashlib
import json

COLOURS = {'.': [0, 0, 0], 'R': [255, 0, 0], 'G': [0, 255, 0],
           'B': [0, 0, 255], 'W': [255, 255, 255],
           'M': [255, 0, 255], 'C': [0, 255, 255]}
A, BLUE, GREEN, RED, RED8, WHITE, ALIAS = (*range(51300, 51306), 64073)
PATTERN = ['R.GR', '.BR.', 'RR.B']
WHITE_PATTERN = ['W..W', '.WW.', 'W..W']


def make_case(output, hardware, mode):
    if mode == 11 and not hardware:
        raise ValueError('This slice tests software mode8, hardware modes8/11')
    output.mkdir(parents=True, exist_ok=False)
    scripts = {name: [] for name in ('setup', 'update', 'cleanup')}
    tiles = {name: [] for name in scripts}
    stage = 'setup'
    sprite_count = 0
    reactivation_lines = []

    def vdu(*values):
        line = 'VDU ' + ' '.join(str(v) for v in values)
        assert len(line.encode('ascii')) + 2 < 256, line
        scripts[stage].append(line)

    def command(op, *values):
        vdu(23, 27, op, *values)

    def select(identity):
        command(4, identity)

    def buffer(identity, op, *values):
        vdu(23, 0, 160, f'{identity};', op, *values)

    def join():
        command(15)
        vdu(23, 0, 132, '0;', '0;')

    def rectangle(x, y, index):
        vdu(18, 0, index, 25, 4, f'{x};', f'{y};', 25, 101, f'{x+3};', f'{y+2};')
        join()

    def tile(name, initial, updated=None, background=None):
        width = max(map(len, initial))
        assert len({len(row) for row in initial}) == 1
        updated = initial if updated is None else updated
        background = ['.'*width]*len(initial) if background is None else background
        assert len(updated) == len(background) == len(initial)
        assert all(len(row) == width for row in [*updated, *background])
        number = len(tiles['setup'])
        x, y = 24+(number % 6)*44, 32+(number//6)*40
        assert x+width+2 < 320 and y+len(initial)+2 < 220
        for name_stage, rows in zip(scripts, (initial, updated, background)):
            tiles[name_stage].append(dict(name=name, x=x, y=y, rows=rows))
        return x, y

    def sprite(frames, x, y, hw=None, paint=0, frame=0, alias=False):
        nonlocal sprite_count
        identity = sprite_count
        sprite_count += 1
        select(identity)
        command(5)
        for bitmap in frames:
            command(6, bitmap-64000) if alias else command(38, f'{bitmap};')
        command(18, paint)
        command(19 if (hardware if hw is None else hw) else 20)
        command(10, frame)
        command(13, f'{x};', f'{y};')
        command(11)
        return identity

    def later(identity, *operations, rebind=False):
        nonlocal stage
        stage = 'update'
        if rebind:
            # Stock command20 only toggles a flag; active hardware sprites have
            # no saved-background allocation. Deactivate before changing kind,
            # then reactivate through the ordinary allocation-owning API. Direct
            # active conversion crashes stock; retain that separate evidence.
            command(7, 0)
        select(identity)
        for values in operations:
            command(*values)
        if rebind:
            # The final contiguous sprite count is known after setup generation.
            reactivation_lines.append(len(scripts['update']))
            scripts['update'].append('')
        join()
        stage = 'setup'

    # MODE was selected externally, clearing old context/sprite state. Prefer
    # software by default; each hardware sprite is explicitly marked below.
    vdu(23, 0, 249, '1024;', 23, 0, 249, '2;')
    command(17)
    vdu(4, 26, 20, 23, 1, 0, 23, 0, 192, 0, 17, 128, 12)
    vdu(28, 0, 29, 39, 28)
    if hardware:
        vdu(23, 0, 248, '2;', '1;')

    assets = [(A, PATTERN, 1), (BLUE, ['BBBB']*3, 1),
              (GREEN, ['GG']*2, 1), (RED, ['RRRR']*3, 1),
              (RED8, ['RRRR']*3, 0), (WHITE, ['WWWW']*3, 1),
              (ALIAS, WHITE_PATTERN, 0)]
    for identity, rows, fmt in assets:
        buffer(identity, 2)
        data = []
        for index, symbol in enumerate(''.join(rows)):
            rgb = COLOURS['B' if symbol == '.' else symbol]
            alpha = 0 if symbol == '.' else (1 if index == 0 else 3)
            if fmt == 1:
                data.append(rgb[0]//85 | ((rgb[1]//85) << 2) | ((rgb[2]//85) << 4) | (alpha << 6))
            else:
                data.extend([*rgb, 0 if alpha == 0 else 1 if alpha == 1 else 255])
        buffer(identity, 0, f'{len(data)};', *data)
        command(32, f'{identity};')
        command(33, f'{len(rows[0])};', f'{len(rows)};', fmt)

    x, y = tile('rgba2222-colour-and-alpha', PATTERN)
    sprite([A], x, y)
    x, y = tile('rgba8888-byte-id-and-alpha', WHITE_PATTERN)
    sprite([ALIAS], x, y, alias=True)

    x, y = tile('next-frame', PATTERN, ['BBBB']*3)
    later(sprite([A, BLUE, GREEN], x, y), (8,))
    x, y = tile('previous-frame-wrap', PATTERN, ['GG..', 'GG..', '....'])
    later(sprite([A, BLUE, GREEN], x, y), (9,))
    x, y = tile('next-frame-wrap', ['GG..', 'GG..', '....'], PATTERN)
    later(sprite([A, BLUE, GREEN], x, y, frame=2), (8,))
    x, y = tile('explicit-frame-invalid-ignored', PATTERN, ['BBBB']*3)
    later(sprite([A, BLUE, GREEN], x, y), (10, 1), (10, 99))

    x, y = tile('replace-current-frame-long-id', PATTERN, ['GG..', 'GG..', '....'])
    later(sprite([A], x, y), (53, f'{GREEN};'))
    x, y = tile('replace-current-frame-byte-id', PATTERN, WHITE_PATTERN)
    later(sprite([A], x, y), (21, 73))
    x, y = tile('hide-restores-background', PATTERN, ['....']*3)
    later(sprite([A], x, y), (12,))

    x, y = tile('absolute-move-restores-old-position',
                [row+'......' for row in PATTERN], ['......'+row for row in PATTERN])
    later(sprite([A], x, y), (12,), (13, f'{x+6};', f'{y};'), (11,))
    initial = ['..........']*3 + ['......'+row for row in PATTERN]
    updated = [row+'......' for row in PATTERN] + ['..........']*3
    x, y = tile('signed-relative-movement', initial, updated)
    later(sprite([A], x+6, y+3), (14, '65530;', '65533;'))
    x, y = tile('clear-active-frames', PATTERN, ['....']*3)
    later(sprite([A], x, y), (5,))

    overlap = ['RRRR..', 'RRGGGG', 'RRGGGG', '..GGGG']
    x, y = tile('higher-id-overlaps-lower-id', overlap)
    sprite([RED], x, y)
    # A separate full-size green frame makes overlap boundaries literal.
    green_large = 51306
    buffer(green_large, 2)
    buffer(green_large, 0, '12;', *([204]*12))
    command(32, f'{green_large};')
    command(33, '4;', '3;', 1)
    sprite([green_large], x+2, y+1)

    bg = 'W' if mode == 11 else 'B'
    xor = 'C' if mode == 11 else 'M'
    x, y = tile('rgba2222-xor', [xor*4]*3, background=[bg*4]*3)
    rectangle(x, y, 1 if mode == 11 else 12)
    sprite([RED], x, y, paint=3)
    value = 'R' if hardware else xor
    x, y = tile('rgba8888-hardware-xor-falls-back-to-set' if hardware else 'rgba8888-software-xor',
                [value*4]*3, background=[bg*4]*3)
    rectangle(x, y, 1 if mode == 11 else 12)
    sprite([RED8], x, y, paint=3)

    mixed = ['RRRR..', 'RRRRWW', 'RRRRWW', '..WWWW'] if hardware else ['RRRR..', 'RRWWWW', 'RRWWWW', '..WWWW']
    x, y = tile('hardware-above-higher-id-software' if hardware else 'software-overlap-white', mixed)
    sprite([RED], x, y)
    sprite([WHITE], x+2, y+1, hw=False)

    if hardware:
        sw = 'W' if mode == 11 else 'R'
        x, y = tile('deactivate-rebind-hardware-to-software', ['RRRR']*3, [sw*4]*3)
        later(sprite([RED], x, y), (20,), rebind=True)
        x, y = tile('deactivate-rebind-software-to-hardware', [sw*4]*3, ['RRRR']*3)
        later(sprite([RED], x, y, hw=False), (19,), rebind=True)

    x, y = tile('drawing-under-visible-sprite', PATTERN, ['WWWW']*3, ['WWWW']*3)
    identity = sprite([A], x, y)
    stage = 'update'
    rectangle(x, y, 1 if mode == 11 else 15)
    select(identity)
    command(12)
    join()
    stage = 'setup'

    # Only mutate state after this script has activated/refreshed the full set.
    # A distant graphics viewport and origin must not clip/offset sprites.
    vdu(24, '0;', '2;', '2;', '0;', 29, '100;', '100;')
    command(7, sprite_count)
    join()
    for index in reactivation_lines:
        assert scripts['update'][index] == ''
        scripts['update'][index] = f'VDU 23 27 7 {sprite_count}'
    # Keep the deliberately unrelated graphics origin/viewport through the
    # setup capture. Restore them only when the update script begins, before
    # its ordinary background draw. Restoring before capture would weaken this
    # assertion because ECHO could redraw software sprites with a full viewport.
    scripts['update'].insert(0, 'VDU 26 29 0; 0; 28 0 29 39 28')
    for name in ('setup', 'update'):
        stage = name
        vdu(31, 0, 0)
        scripts[name].append(f'ECHO Sprite {name} complete.')

    stage = 'cleanup'
    command(17)
    join()
    for identity in [*(item[0] for item in assets), green_large]:
        buffer(identity, 2)
    vdu(23, 0, 249, '2;', 23, 0, 249, '1024;', 20, 4, 26,
        28, 0, 29, 39, 28, 31, 0, 0, 23, 0, 192, 1)
    scripts[stage].append('ECHO Sprite cleanup complete.')

    results = []
    for name, lines in scripts.items():
        assert all(line and len(line.encode('ascii'))+2 < 256 for line in lines)
        data = ('\r\n'.join(lines)+'\r\n').encode('ascii')
        (output/(name+'.txt')).write_bytes(data)
        manifest = dict(script_sha256=hashlib.sha256(data).hexdigest(),
                        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                        stage=name, mode=mode, hardware=hardware, sprites=sprite_count,
                        surface=[320, 240], command_lines=len(lines), colours=COLOURS,
                        tiles=tiles[name], scope='Static sprite states; no performance or general qualification claim')
        (output/(name+'-oracle.json')).write_text(json.dumps(manifest, indent=2)+'\n')
        results.append({k: v for k, v in manifest.items() if k not in ('tiles', 'colours')})
    (output/'manifest.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--hardware', action='store_true')
    parser.add_argument('--mode', type=int, choices=(8, 11), default=8)
    args = parser.parse_args()
    make_case(args.output, args.hardware, args.mode)
