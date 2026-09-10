"""Deterministic bitmap fixtures; PNG input and raw RGBA contracts, no VDP code."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/bitmaps/source'
TARGET = ROOT / 'tgt/assets/bitmaps'


def rgba2(image):
    # PingoASM agonImages.py contract: nearest 0/85/170/255; AA BB GG RR.
    raw=image.convert('RGBA').tobytes()
    return bytes(sum(min(3, (v + 42) // 85) << (2 * i)
                     for i, v in enumerate(raw[pos:pos+4]))
                 for pos in range(0,len(raw),4))


def build():
    TARGET.mkdir(parents=True, exist_ok=True)
    original = Image.open(SOURCE / 'blenderaxes.png').convert('RGBA')
    assert original.size == (34, 34)
    assert rgba2(original) == (SOURCE / 'blenderaxes.rgba2').read_bytes()
    assets = []

    def add(name, image=None, fmt=1, raw=None, size=None, description=''):
        if image is not None:
            size = image.size
            raw = image.convert('RGBA').tobytes() if fmt == 0 else rgba2(image)
        suffix = ('rgba8', 'rgba2', 'mask', 'packed')[fmt]
        filename = f'{name}.{suffix}'
        (TARGET / filename).write_bytes(raw)
        assert 0 < len(raw) < 32768
        assets.append(dict(index=len(assets), name=name, filename=filename,
                           width=size[0], height=size[1], format=fmt,
                           length=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                           description=description))
        return assets[-1]

    for fmt in (1, 0):
        tag = '2' if fmt else '8'
        add('axes'+tag, original, fmt, description='Unchanged source artwork')
        add('large'+tag, original.resize((68,68), Image.Resampling.NEAREST), fmt,
            description='Independent host nearest-neighbour 2x control')
        cut = original.copy()
        for y in range(34):
            for x in range(34):
                if x < 3 or y < 3 or x >= 31 or y >= 31 or (14 <= x < 20 and 9 <= y < 25):
                    cut.putpixel((x,y), (*cut.getpixel((x,y))[:3], 0))
        add('cut'+tag, cut, fmt, description='Geometric border and central cutout')
        alpha = Image.new('RGBA', (50,34))
        levels = (0,85,170,255,255) if fmt else (0,1,64,128,255)
        for y in range(34):
            for x in range(50):
                alpha.putpixel((x,y), (255,255,0,levels[x//10]))
        add('alpha'+tag, alpha, fmt, description='Explicit zero/nonzero alpha bands')
        for n in range(4):
            frame = cut.transpose((Image.Transpose.ROTATE_90,Image.Transpose.ROTATE_180,
                                   Image.Transpose.ROTATE_270,Image.Transpose.FLIP_LEFT_RIGHT)[n])
            ImageDraw.Draw(frame).rectangle((3,3,6+n*2,6), fill=(255,255,255,255))
            add(f'frame{n}_{tag}', frame, fmt, description='Host orthogonal marked frame')
        wide = cut.resize((50,26), Image.Resampling.NEAREST)
        add('wide'+tag, wide, fmt, description='Different frame dimensions: 50x26')
    for name, size in [('checker',(128,96)), ('stripes',(128,96))]:
        pic = Image.new('RGBA', size)
        for y in range(size[1]):
            for x in range(size[0]):
                phase = (x//8+y//8)%2 if name == 'checker' else (x//8)%2
                pic.putpixel((x,y), ((85,170,255,255) if phase else (170,85,0,255)))
        add(name, pic, description='Known physical RGB background')
    mask = bytes(sum((1 << (7-bit)) if (byte*8+bit < 34 and
                 ((byte*8+bit+y)//5)%2 == 0) else 0 for bit in range(8))
                 for y in range(34) for byte in range(5))
    add('mask', fmt=2, raw=mask, size=(34,34), description='34 pixels, 5 bytes per row')
    for bits in (1,2,4):
        data = bytearray()
        for y in range(34):
            row = [((x//4+y//4) % (1<<bits)) for x in range(34)]
            row += [0] * ((-len(row)) % (8//bits))
            for start in range(0,len(row),8//bits):
                value = 0
                for pixel in row[start:start+8//bits]: value = (value<<bits)|pixel
                data.append(value)
        add(f'packed{bits}', fmt=3, raw=bytes(data), size=(34,34),
            description=f'{bits} bpp, MSB first, byte-aligned rows')
    (TARGET/'manifest.json').write_text(json.dumps(assets,indent=2)+'\n')
    return {item['name']:item for item in assets}


if __name__ == '__main__':
    print(f'Generated {len(build())} bitmap assets.')
