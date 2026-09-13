"""Compare captured pixels with independently declared monochrome glyph rows."""
from pathlib import Path
import argparse
import json
import struct
from PIL import Image


def load_pixels(path, surface):
    if path.suffix == '.evf':
        data = path.read_bytes()
        if data[:4] != b'EVF1' or data[6] != 2:
            raise ValueError('Expected an EVF1 RGB222 frame')
        width, height, stride = struct.unpack_from('<HHI', data, 12)
        if stride < width or len(data) != 32 + stride*height:
            raise ValueError('Inconsistent frame layout')
        pixels = bytes(component for y in range(height)
                       for value in data[32+y*stride:32+y*stride+width]
                       for component in ((value & 3)*85, ((value >> 2) & 3)*85,
                                         ((value >> 4) & 3)*85))
        image = Image.frombytes('RGB', (width, height), pixels)
    else:
        image = Image.open(path).convert('RGB')
    width, height = surface
    scale = image.width // width
    if scale < 1 or image.size != (width*scale, height*scale):
        raise ValueError(f'Unexpected capture size {image.size}')
    return image, scale


def check(oracle, capture):
    spec = json.loads(oracle.read_text())
    image, scale = load_pixels(capture, spec['surface'])
    results = []
    for tile in spec['tiles']:
        mismatch = []
        # The halo detects misplaced glyphs and writes beyond a narrow width.
        for y in range(-2, 10):
            for x in range(-2, 10):
                set_pixel = (0 <= y < 8 and 0 <= x < tile['width'] and
                             tile['rows'][y] & (128 >> x))
                expected = tuple(tile['foreground'] if set_pixel else tile['background'])
                cell = ((tile['x']+x)*scale, (tile['y']+y)*scale)
                actual = {image.getpixel((cell[0]+sx, cell[1]+sy))
                          for sy in range(scale) for sx in range(scale)}
                if actual != {expected}:
                    mismatch.append(dict(x=x, y=y, expected=expected, actual=sorted(actual)))
        results.append(dict(name=tile['name'], mismatches=len(mismatch), first=mismatch[:8]))
    return dict(oracle=str(oracle), capture=str(capture), scale=scale,
                passed=all(item['mismatches'] == 0 for item in results), tiles=results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('oracle', type=Path)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = check(args.oracle, args.capture)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
