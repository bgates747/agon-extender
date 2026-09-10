"""Build literal VDU command streams and pixel oracles for SHP-01..24.

This constructs commands; all rendering is performed by the Agon VDP.
PLOT coordinates are explicitly packed as signed little-endian 16-bit values.
"""

from pathlib import Path
import json
import struct
from shapes_pages import PAGES, OWNED_BUFFERS, buffered, transform


ROOT = Path(__file__).resolve().parent.parent
CATALOG = []


class Page:
    def __init__(self, title, commands, expected):
        self.data = bytearray((6, 15, 4, 20, 26, 23, 0, 0xC0, 0,
                               23, 23, 1, 17, 128, 12, 23, 1, 0))
        self.probes = []
        self.plots = []
        self.resources = set()
        self.transformed = False
        self.title = title
        self.commands = commands
        self.expected = expected
        self.data.extend((23, 0, 0xF2, 0))
        self.label(2, 1, title, 15)
        self.label(2, 3, commands, 14)
        self.label(2, 5, expected, 15)
        self.colour(7)
        self.line((16, 52), (495, 52))
        self.data.extend((18, 0, 128))  # graphics background = black

    def label(self, x, y, value, colour=15):
        assert 0 <= x and x + len(value) <= 64 and 0 <= y < 48
        self.data.extend((17, colour, 31, x, y))
        self.data.extend(value.encode("ascii"))

    def colour(self, colour, mode=0):
        self.data.extend((18, mode, colour))

    def palette(self, index, r, g, b):
        self.data.extend((19, index, 255, r, g, b))

    def flush(self):
        self.data.extend((23, 0, 0xCA))

    def origin(self, x, y):
        self.data.extend(b'\x1d' + struct.pack('<hh', x, y))

    def viewport(self, left, top, right, bottom):
        self.data.extend(b'\x18' + struct.pack('<hhhh', left, bottom, right, top))

    def reset_position(self):
        self.data.extend((4, 26, 23, 0, 0xC0, 0))

    def rect(self, left, top, right, bottom):
        self.plot(4, left, top)
        self.plot(0x65, right, bottom)

    def outline(self, left, top, right, bottom):
        self.polygon([(left, top), (right, top), (right, bottom), (left, bottom)])

    def polygon(self, points, fill=None):
        self.plot(4, *points[0])
        if fill:
            assert len(points) == 3
            self.plot(4, *points[1]); self.plot(fill, *points[2])
        else:
            for point in points[1:] + points[:1]:
                self.plot(5, *point)

    def circle(self, centre, radius, filled=False, relative=False):
        self.plot(4, *centre)
        self.plot((0x99 if filled else 0x91) + (0 if relative else 4),
                  radius if relative else centre[0] + radius,
                  0 if relative else centre[1])

    def cross(self, x, y, size):
        self.line((x-size, y), (x+size, y))
        self.line((x, y-size), (x, y+size))

    def plot(self, code, x, y):
        self.plots.append((len(self.data), code, x, y))
        self.data.extend(bytes((25, code)) + struct.pack("<hh", x, y))

    def line(self, start, end, relative=False, reverse=False):
        if reverse:
            start, end = end, start
        self.plot(4, *start)
        if relative:
            self.plot(1, end[0] - start[0], end[1] - start[1])
        else:
            self.plot(5, *end)

    def probe(self, name, x, y, white):
        # Monochrome oracles avoid dependence on palette-index/RGB ordering.
        rgb = ((255 if white else 0),) * 3 if isinstance(white, bool) else white
        assert len(rgb) == 3 and all(0 <= v <= 255 for v in rgb)
        self.probes.append((name, x, y, rgb))

    def save(self, name):
        self.flush()
        if self.transformed:
            transform(self, 65535)
            self.data.extend((23, 0, 0xF9, 1, 0))
        for ident in sorted(self.resources):
            buffered(self, ident, 2)
        self.reset_position()
        self.data.extend((20, 23, 23, 1, 23, 0, 0xF2, 0))
        self.flush()  # complete drawing/state changes before queries
        build = ROOT / "build"
        build.mkdir(exist_ok=True)
        (build / f"{name}.vdu").write_bytes(self.data)
        probes = bytearray()
        for _, x, y, rgb in self.probes:
            probes.extend(bytes((23, 0, 0x84)) + struct.pack("<hh", x, y))
            probes.extend(rgb)
        assert len(self.probes) < 100
        (build / f"{name}.probes").write_bytes(probes)
        (build / f"{name}.json").write_text(json.dumps({
            "title": self.title, "commands": self.commands,
            "expected": self.expected, "plots": self.plots, "probes": self.probes,
            "resources": sorted(self.resources),
        }, indent=2) + "\n")
        CATALOG.append((name, len(self.data), len(self.probes)))


def page_one():
    p = Page("SHAPES / SHP-01 - MOVEMENT AND POINTS",
             "PLOT &00/&04 MOVE, &01/&05 LINE, &40-&47 POINT",
             "Paths match. Moves leave gaps. Points are single pixels.")
    p.label(2, 8, "ABSOLUTE (&04 / &05)", 11)
    p.label(33, 8, "RELATIVE (&00 / &01)", 11)
    p.colour(15)
    # A discontinuous outline: the sloping move is intentionally invisible.
    path = [(4, 48, 96), (5, 208, 96), (5, 208, 128),
            (4, 160, 160), (4, 160, 160), (5, 80, 160),
            (5, 48, 128), (5, 48, 96)]
    for shift, relative in ((0, False), (248, True)):
        previous = None
        for code, x, y in path:
            x += shift
            if relative and previous is not None:
                p.plot(code - 4, x - previous[0], y - previous[1])
            else:
                p.plot(code, x, y)
            previous = (x, y)
        p.probe("top line", 120 + shift, 96, True)
        p.probe("move gap", 184 + shift, 144, False)
        p.probe("negative-offset line", 112 + shift, 160, True)
        p.probe("interior remains empty", 120 + shift, 128, False)
    p.label(2, 22, "No line across the diagonal gap; zero moves do nothing.")
    p.label(2, 25, "POINT SAMPLES: 5 x 5 dots, spaced six pixels apart", 14)
    for i, (caption, code) in enumerate((
        ("ABS FG", 0x45), ("REL FG", 0x41), ("ABS BG", 0x47),
        ("REL BG", 0x43), ("ABS INV", 0x46), ("REL INV", 0x42),
    )):
        x = 16 + i * 80
        p.label(x // 8, 28, caption, 11)
        p.colour(15)
        white_patch = i >= 2
        if white_patch:
            # Only solid lines prepare the backgrounds: no later shape tests.
            for y in range(260, 305):
                p.line((x + 4, y), (x + 52, y))
        p.plot(0x44, x + 4, 248)
        p.plot(0x40, 8, 0)
        p.plot(0x40, -8, 0)
        p.plot(0x40, 0, 0)
        p.probe("point-family moves do not draw", x + 8, 248, False)
        for row in range(5):
            for col in range(5):
                px, py = x + 16 + col * 6, 270 + row * 6
                if code & 4:
                    p.plot(code, px, py)
                else:
                    # Both negative and positive relative point offsets.
                    p.plot(4, px + 3, py - 2)
                    p.plot(code, -3, 2)
        p.probe(caption + " point", x + 16, 270, not white_patch)
        p.probe(caption + " between points", x + 17, 270, white_patch)
        if i >= 4:
            # Invert the centre twice total: it must return to white.
            px, py = x + 28, 282
            if code & 4:
                p.plot(code, px, py)
            else:
                p.plot(4, px, py)
                p.plot(code, 0, 0)
            p.probe("inverse twice restores", px, py, True)
    p.label(2, 40, "FG: white dots. BG/INV: black dots on white.")
    p.label(2, 42, "INV centre is white again after drawing it twice.", 14)
    p.save("shp01")


def page_two():
    p = Page("SHAPES / SHP-02 - SOLID LINES IN ALL DIRECTIONS",
             "PLOT &04 MOVE + &05 ABSOLUTE / &01 RELATIVE LINE",
             "Compare 16 spokes: axes, diagonals, shallow and steep.")
    offsets = [(88, 0), (88, 30), (56, 56), (30, 60), (0, 60),
               (-30, 60), (-56, 56), (-88, 30), (-88, 0),
               (-88, -30), (-56, -56), (-30, -60), (0, -60),
               (30, -60), (56, -56), (88, -30)]
    for cx, cy, relative, reverse, caption, row in (
        (128, 144, False, False, "ABSOLUTE: CENTRE -> END", 8),
        (384, 144, True, False, "RELATIVE: CENTRE -> END", 8),
        (128, 280, False, True, "ABSOLUTE: END -> CENTRE", 26),
        (384, 280, True, True, "RELATIVE: END -> CENTRE", 26),
    ):
        p.label(2 if cx == 128 else 34, row, caption, 11)
        p.colour(15)
        for dx, dy in offsets:
            p.line((cx, cy), (cx + dx, cy + dy), relative, reverse)
        for dx, dy in offsets:
            p.probe("spoke endpoint", cx + dx, cy + dy, True)
        p.probe("shared centre", cx, cy, True)
        p.probe("horizontal midpoint", cx + 44, cy, True)
        p.probe("off-line pixel", cx + 44, cy + 1, False)
    p.label(2, 43, "All endpoints included. Reverse slopes may differ in ties.", 14)
    p.save("shp02")


if __name__ == "__main__":
    page_one()
    page_two()
    for build_page in PAGES:
        build_page(Page)
    assert len(CATALOG) == 24
    lines = ['; Generated descriptor: 24-bit stream, length, probes; byte count.',
             'page_table:']
    for name, length, count in CATALOG:
        lines += [f'    dl {name}_stream,{length},{name}_probes', f'    db {count}']
    for name, _, _ in CATALOG:
        lines += [f'{name}_stream:', f'    incbin "{name}.vdu"',
                  f'{name}_probes:', f'    incbin "{name}.probes"']
    (ROOT / 'build/shapes-data.inc').write_text('\n'.join(lines) + '\n')
    (ROOT / 'build/catalog.json').write_text(json.dumps(CATALOG, indent=2) + '\n')
