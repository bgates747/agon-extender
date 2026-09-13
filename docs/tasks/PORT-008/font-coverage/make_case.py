"""Generate a finite, ordinary MOS EXEC input and independent glyph oracle.

No firmware/transport bypass. Each line is a complete VDU command, safely below
MOS's line limit. Select mode 8 before EXEC; this script never changes mode.
Readback commands flush prior drawing before mutable font storage is changed.
They are stock commands, not private performance fences or timing evidence.
"""
from pathlib import Path
import argparse
import hashlib
import json

CUSTOM = 50000
COPY = 50001
SYSTEM_ROWS = [0x80, 0xC0, 0xA0, 0x90, 0x88, 0x84, 0x82, 0xFF]
CUSTOM_ROWS = [0xF0, 0x88, 0x84, 0x82, 0xFE, 0x82, 0x84, 0x88]


def make_case(output):
    output.mkdir(parents=True, exist_ok=False)
    lines, tiles = [], []

    def vdu(*values):
        line = 'VDU ' + ' '.join(str(value) for value in values)
        assert len(line.encode('ascii')) + 2 < 256
        lines.append(line)

    def font(operation, identity, *values):
        vdu(23, 0, 149, operation, f'{identity};', *values)

    def buffer(identity, operation, *values):
        vdu(23, 0, 160, f'{identity};', operation, *values)

    def completed_draw():
        vdu(23, 0, 132, '0;', '0;')

    def expect(name, x, y, rows, width=8):
        tiles.append(dict(name=name, x=x, y=y, width=width, height=8,
                          rows=rows, bits='MSB left', foreground=[255]*3,
                          background=[0]*3))

    def glyph(name, x, y, char, rows, width=8):
        vdu(25, 4, f'{x};', f'{y};')
        vdu(27, char)
        completed_draw()
        expect(name, x, y, rows, width)

    # Keep the final MOS prompt and any command error out of the glyph region.
    vdu(4, 26, 23, 1, 0, 23, 0, 192, 0, 17, 128, 17, 15, 12)
    vdu(28, 0, 29, 39, 28)
    vdu(18, 0, 15)
    buffer(CUSTOM, 2)
    buffer(COPY, 2)
    vdu(5)
    font(0, 65535, 0)
    vdu(23, 0, 144, 161, *SYSTEM_ROWS)
    glyph('redefined-system', 32, 40, 161, SYSTEM_ROWS)
    font(5, COPY)
    vdu(23, 0, 145)  # Restore system; the copy must remain independent.
    font(0, COPY, 0)
    glyph('copy-after-system-restore', 56, 40, 161, SYSTEM_ROWS)

    buffer(CUSTOM, 3, '2048;')
    buffer(CUSTOM, 5, 194, '520;', '8;', *CUSTOM_ROWS)
    font(1, CUSTOM, 8, 8, 7, 0)
    font(0, CUSTOM, 0)
    glyph('created-font', 32, 96, 65, CUSTOM_ROWS)
    changed = [255, *CUSTOM_ROWS[1:]]
    buffer(CUSTOM, 5, 2, '520;', 255)
    glyph('buffer-adjust-visible', 56, 96, 65, changed)
    font(2, CUSTOM, 0, '4;')
    glyph('four-pixel-width', 80, 96, 65, changed, 4)

    # Deselect before deleting. Deletion preserves the uploaded font bytes.
    font(0, 65535, 0)
    font(4, CUSTOM)
    font(1, CUSTOM, 8, 8, 7, 0)
    font(0, CUSTOM, 0)
    glyph('recreated-from-preserved-buffer', 104, 96, 65, changed)
    glyph('unpopulated-glyph', 128, 96, 66, [0]*8)

    # Text and graphics have independent font selections. Text at row20 fits
    # wholly above the reserved prompt area; graphics must keep CUSTOM.
    vdu(4, 26)
    font(0, COPY, 0)
    vdu(31, 10, 20, 27, 161)
    completed_draw()
    expect('text-cursor-copy', 80, 160, SYSTEM_ROWS)
    vdu(5)
    glyph('graphics-cursor-keeps-custom', 104, 160, 65, changed)

    font(0, 65535, 0)
    vdu(4)
    font(0, 65535, 0)
    font(4, CUSTOM)
    font(4, COPY)
    buffer(CUSTOM, 2)
    buffer(COPY, 2)
    vdu(28, 0, 29, 39, 28, 31, 0, 0, 23, 0, 192, 1)
    lines.append('ECHO Font command case complete.')
    data = ('\r\n'.join(lines) + '\r\n').encode('ascii')
    (output / 'fonts.txt').write_bytes(data)
    manifest = dict(script_sha256=hashlib.sha256(data).hexdigest(),
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    mode=8, surface=[320, 240], command_lines=len(lines),
                    tiles=tiles, scope='Static glyph rendering; no timing, replies or general qualification claim')
    (output / 'oracle.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({key: value for key, value in manifest.items() if key != 'tiles'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    make_case(parser.parse_args().output)
