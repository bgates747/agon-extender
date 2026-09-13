"""Check literal colour tiles plus untouched halos against native PNG or EVF1."""
from pathlib import Path
import argparse
import importlib.util
import hashlib
import json

# Reuse the preceding task's strictly validated capture decoder. Neither case
# promotes this exploratory helper into a public/production API.
decoder = Path(__file__).resolve().parents[1]/'font-coverage/check_pixels.py'
spec = importlib.util.spec_from_file_location('font_capture_decoder', decoder)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def check(oracle, capture, reference=None):
    data = json.loads(oracle.read_text())
    image, scale = module.load_pixels(capture, data['surface'])
    if reference:
        stock, stock_scale = module.load_pixels(reference, data['surface'])
    results = []
    for tile in data['tiles']:
        rows = tile['rows']
        width, height = len(rows[0]), len(rows)
        mismatch = []
        reference_mismatch = []
        for y in range(-2, height+2):
            for x in range(-2, width+2):
                symbol = rows[y][x] if 0 <= y < height and 0 <= x < width else '.'
                expected = tuple(data['colours'][symbol])
                px, py = (tile['x']+x)*scale, (tile['y']+y)*scale
                actual = {image.getpixel((px+sx, py+sy))
                          for sy in range(scale) for sx in range(scale)}
                if actual != {expected}:
                    mismatch.append(dict(x=x, y=y, expected=expected, actual=sorted(actual)))
                if reference:
                    rx, ry = (tile['x']+x)*stock_scale, (tile['y']+y)*stock_scale
                    values = {stock.getpixel((rx+sx, ry+sy))
                              for sy in range(stock_scale) for sx in range(stock_scale)}
                    if len(values) != 1 or actual != values:
                        reference_mismatch.append(dict(x=x, y=y, stock=sorted(values), actual=sorted(actual)))
        result = dict(name=tile['name'], mismatches=len(mismatch), first=mismatch[:12])
        if reference:
            result.update(reference_mismatches=len(reference_mismatch), reference_first=reference_mismatch[:12])
        results.append(result)
    result = dict(oracle=str(oracle), capture=str(capture), scale=scale,
                  ideal_pixels_match=all(item['mismatches'] == 0 for item in results), tiles=results)
    result['acceptance_basis'] = 'independent ideal pixels'
    result['passed'] = result['ideal_pixels_match']
    if reference:
        result.update(reference=str(reference), reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
                      acceptance_basis='exact stock parity in declared regions, not mathematical correctness',
                      passed=all(item['reference_mismatches'] == 0 for item in results))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('oracle', type=Path)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference', type=Path, help='Compare exact stock pixels; ideal deviations remain reported')
    args = parser.parse_args()
    result = check(args.oracle, args.capture, args.reference)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
