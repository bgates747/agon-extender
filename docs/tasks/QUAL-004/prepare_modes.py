"""Small independent lower-depth and displayed-page controls; no mode commands.

Reuse the retained literal palette oracle. The page controls use documented
VDU23,0,&C3 swaps and deliberately leave different contents on the drawing page.
Mode selection belongs to autoexec, outside each scene.
"""
from pathlib import Path
import argparse, hashlib, json, runpy, struct

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[2]

def binary(script):
    out = bytearray()
    for line in script.splitlines():
        if not line.startswith('VDU '):
            continue
        for token in line.split()[1:]:
            out.extend(struct.pack('<H', int(token[:-1]) & 65535)
                       if token.endswith(';') else bytes([int(token)]))
    return bytes(out)

def save(folder, name, data, mode, **metadata):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / (name + '.vdu')).write_bytes(data)
    # These small controls contain their own stock completion/query fences.
    (folder / (name + '.vdu.bar')).write_bytes(
        b'Q4B1' + len(data).to_bytes(3, 'little') + b'\0\0')
    return dict(name=name, file=name+'.vdu', bytes=len(data), mode=mode,
                sha256=hashlib.sha256(data).hexdigest(), **metadata)

def main(output):
    output.mkdir(parents=True, exist_ok=False)
    make_palette = runpy.run_path(str(ROOT / 'docs/tasks/PORT-008/palette-coverage/make_case.py'))['make_case']
    make_copper = runpy.run_path(str(ROOT / 'docs/tasks/PORT-008/copper-coverage/make_case.py'))['make_case']
    for depth, mode in ((16, 9), (4, 10), (2, 11)):
        folder = output / f'mode{mode}'
        make_palette(folder / 'oracle', depth)
        row = save(folder, f'PAL{depth}', binary((folder/'oracle/palette.txt').read_text()),
                   mode, source='PORT-008 palette-coverage', oracle='oracle/oracle.json')
        rows=[row]
        make_copper(folder/'copper-oracle',depth)
        accumulated=b''
        for stage in ('setup','edit','replace','reset'):
            accumulated+=binary((folder/'copper-oracle'/(stage+'.txt')).read_text())
            if depth!=16 and stage!='setup':continue
            rows.append(save(folder,f'COP{depth}_{stage.upper()}',accumulated,mode,
                             source='PORT-008 copper-coverage',stage=stage,
                             scope='Static row palettes and composed SW/HW sprites'))
        (folder/'manifest.json').write_text(json.dumps({'cases': rows}, indent=2)+'\n')
    # Both pages are cleared before each independent case; no inherited pixels.
    initial = 'VDU 4 26 20 23 1 0 23 0 192 0 17 128 12 23 0 202 23 0 195 12 23 0 202 23 0 195\n'
    red_front = 'VDU 17 129 12 18 0 15 25 4 40; 40; 25 101 79; 79; 23 0 202 23 0 195\n'
    green_back = 'VDU 17 130 12 18 0 15 25 4 120; 100; 25 101 159; 139; 23 0 202\n'
    rows = []
    for name, extra, colour, rect in (
            ('PAGE_FRONT', '', [170, 0, 0], [40,40,79,79]),
            ('PAGE_SWAP', 'VDU 23 0 195\n', [0,170,0], [120,100,159,139])):
        rows.append(save(output/'mode136', name, binary(initial+red_front+green_back+extra),
                         136, source='QUAL-004 literal page control',
                         expected_background_rgb=colour, expected_white_rectangle=rect))
    (output/'mode136/manifest.json').write_text(json.dumps({'cases': rows}, indent=2)+'\n')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    main(p.parse_args().output)
