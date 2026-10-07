#!/usr/bin/env python3
"""Build visual-only familiar game art; keep benchmark source/data unchanged.

Read original RGBA2222 bytes. Asset directories are explicit local inputs, not
vendored game data. Public MOS keyboard/pixel-query APIs and ordinary VDU output
are the only runtime interfaces. Startup selects the mode and EMOS route.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import zlib

from generate import asset, bitmap, cmd, colour, plot

HERE = Path(__file__).resolve().parent
MODES = {20: (512, 384, False), 8: (320, 240, False), 136: (320, 240, True)}
NURPLES = ('ship_0l', 'seeker_000', 'turret_000', 'fireball_2_000')
WALLS = ('10_035', '11_035', '14_035', '17_035')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def raw(asset_dir, name, width, height, owner):
    path = asset_dir / (name + '.rgba2')
    data = path.read_bytes()
    assert len(data) == width * height, (path, len(data), width, height)
    return dict(owner=owner, name=name, width=width, height=height,
                source=str(path.resolve()), sha256=sha(path)), data


def graphic_text(x, y, text):
    return colour(63) + plot(4, x, y) + cmd(5) + text.encode('ascii') + cmd(4)


def positions(width, pose):
    left = (width - 256) // 2
    # Four16px sprites, each moving over its own64px game-texture column.
    return [(left + i * 64 + 8 + ((pose + i * 2) % 5) * 8,
             84 + ((pose // 2 + i) % 4) * 8) for i in range(4)]


def background(mode):
    width, height, _ = MODES[mode]
    left = (width - 256) // 2
    # Stock Context::cls (VDU12) deactivates all sprites. CLG clears the shared
    # pixel plane without that side effect; do not put CLS in a pose redraw.
    data = cmd(26, 18, 0, 0, 16, 23, 1, 0)
    data += graphic_text(8, 16, 'Game art review - mode ' + str(mode))
    data += graphic_text(8, 32, '2 poses/s  P pause  Space step')
    for i, name in enumerate(('Ship', 'Seeker', 'Turret', 'Fireball')):
        data += bitmap(i, left + i * 64 + 24, 42)
        data += graphic_text(left + i * 64, 72, name)
    for row in range(2):
        for i in range(4):
            data += bitmap(4 + i, left + i * 64, 80 + row * 64)
    data += graphic_text(8, height - 16, 'Nurples / AgonWolf3D - Esc exits')
    return data


def sprite_definition():
    # The benchmark helper attaches bitmap2 to all sprites; this review uses
    # a different familiar bitmap for each. Keep explicit type/paint setup.
    data = cmd(23, 27, 7, 0, 23, 27, 17, 23, 0, 248, 2, 0, 1, 0)
    for i in range(4):
        data += cmd(23, 27, 4, i, 23, 27, 5, 23, 27, 6, i,
                    23, 27, 18, 0, 23, 27, 20, 23, 27, 11)
    return data + cmd(23, 27, 7, 4)


def pose_bytes(mode, pose):
    width, _, doubled = MODES[mode]
    # Stock software sprites have automatic saved backgrounds only in single
    # buffering. In double buffering the application redraws the back plane.
    # Deactivate while rebuilding the back plane so stock's automatic redraw
    # after each primitive cannot stamp the old pose into the new background.
    data = cmd(23, 27, 7, 0) + background(mode) if doubled else b''
    for i, (x, y) in enumerate(positions(width, pose)):
        data += cmd(23, 27, 4, i, 23, 27, 13) + struct.pack('<HH', x, y)
    if doubled:
        data += cmd(23, 27, 7, 4)
    data += cmd(23, 27, 15)
    if doubled:
        data += cmd(23, 0, 195)
    return data


def emit(data):
    return ''.join(' db ' + ','.join(map(str, data[i:i + 24])) + '\n'
                   for i in range(0, len(data), 24))


def reference(path, mode, entries):
    """Exact-byte RGBA2222 pixel reference; captions remain in the live VDP."""
    width, height, _ = MODES[mode]
    pixels = bytearray(width * height * 3)
    left = (width - 256) // 2

    def draw(index, x, y):
        record, data = entries[index]
        for ay in range(record['height']):
            for ax in range(record['width']):
                value = data[ay * record['width'] + ax]
                if value >> 6:
                    p = ((y + ay) * width + x + ax) * 3
                    pixels[p:p + 3] = bytes(((value & 3) * 85,
                                             ((value >> 2) & 3) * 85,
                                             ((value >> 4) & 3) * 85))
    for row in range(2):
        for i in range(4):
            draw(4 + i, left + i * 64, 80 + row * 64)
    for i in range(4):
        draw(i, left + i * 64 + 24, 42)
    for i, (x, y) in enumerate(positions(width, 0)):
        draw(i, x, y)
    scan = b''.join(b'\0' + pixels[y * width * 3:(y + 1) * width * 3]
                    for y in range(height))

    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' +
                     chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) +
                     chunk(b'IDAT', zlib.compress(scan)) + chunk(b'IEND', b''))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nurples-assets', type=Path, required=True)
    parser.add_argument('--wolf-assets', type=Path, required=True)
    parser.add_argument('--assembler', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    identity = 'game-art-visual-r02-b' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
    entries = [raw(args.nurples_assets, n, 16, 16, 'Nurples') for n in NURPLES]
    entries += [raw(args.wolf_assets, n, 64, 63, 'AgonWolf3D') for n in WALLS]
    source = HERE / 'game_art_visual.asm'
    manifest = dict(build_id=identity, scope='visual-only; no benchmark results',
                    source_sha256=sha(source), generator_sha256=sha(__file__),
                    assembler_sha256=sha(args.assembler), nominal_poses_per_second=2,
                    raw_mos_clock_hz_nominal=120, pose_period_raw_ticks=60,
                    controls={'pause_resume': 'P', 'step': 'Space', 'exit': 'Escape'},
                    assets=[r for r, _ in entries], modes={})
    for mode in MODES:
        out = args.output / ('mode' + str(mode))
        out.mkdir()
        shutil.copyfile(source, out / 'review.asm')
        definitions = b''.join(asset(i, r['width'], r['height'], b)
                               for i, (r, b) in enumerate(entries))
        init = cmd(23, 27, 7, 0, 23, 27, 17, 20, 26, 23, 0, 192, 0)
        init += b''.join(cmd(19, i, i, 0, 0, 0) for i in range(64))
        init += definitions + background(mode)
        if MODES[mode][2]:
            init += cmd(23, 0, 195) + background(mode)
        init += sprite_definition()
        frames = [pose_bytes(mode, i) for i in range(16)]
        tag = int.from_bytes(hashlib.sha256(f'{identity}:{mode}'.encode()).digest()[:3], 'little')
        marker = cmd(23, 0, 160, 255, 255, 0, 12, 0) + b'B009' + cmd(1, 1, 220, 255, 1) + tag.to_bytes(3, 'little')
        assert len(marker) == 20
        include = f'EXPECT_MODE: equ {mode}\ninitial:\n' + emit(init) + 'initial_end:\n'
        include += 'ready_marker:\n' + emit(marker)
        include += 'pose_table: dl ' + ','.join('pose' + str(i) for i in range(16)) + '\n'
        for i, data in enumerate(frames):
            include += f'pose{i}: dw {len(data)}\n' + emit(data)
            for x, y in positions(MODES[mode][0], i):
                assert 0 <= x <= MODES[mode][0] - 16 and 0 <= y <= MODES[mode][1] - 16
        (out / 'scene.inc').write_text(include)
        binary = identity + '-mode' + str(mode) + '.bin'
        subprocess.run([str(args.assembler.resolve()), 'review.asm', binary, '-l', '-s', '-c'],
                       cwd=out, check=True, stdout=subprocess.DEVNULL)
        assert (out / binary).stat().st_size < 0x30000, 'Visual program exceeds its declared user-RAM range'
        reference(out / 'reference.png', mode, entries)
        manifest['modes'][str(mode)] = dict(binary=binary, bytes=(out / binary).stat().st_size,
                    sha256=sha(out / binary), scene_sha256=sha(out / 'scene.inc'),
                    pose_sha256=[hashlib.sha256(f).hexdigest() for f in frames],
                    readiness_tag=tag, readiness_case_id=65500,
                    double_buffered=MODES[mode][2],
                    background_policy='redraw-back-plane' if MODES[mode][2] else 'automatic-software-sprite-restoration')
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(identity, flush=True)


if __name__ == '__main__':
    main()
