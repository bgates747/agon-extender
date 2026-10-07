#!/usr/bin/env python3
"""Build static full-palette charts for the supplemental conversion control.

No video mode command is generated: the MOS startup script selects the mode.
Explicit RRGGBB palette definitions make the reference chart reproducible.
"""
import argparse, datetime, hashlib, html, json, shutil, subprocess
from pathlib import Path
from generate import MODES, cmd, colour, plot

HERE = Path(__file__).resolve().parent
PALETTE16 = [0, 32, 8, 40, 2, 34, 10, 42, 21, 48, 12, 60, 3, 51, 15, 63]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pattern(mode):
    width, height, count, doubled = MODES[mode]
    palette = list(range(64)) if count == 64 else PALETTE16
    white = count - 1
    # Reset sprites, contexts, origin/viewports, cursor and coordinate scaling.
    data = cmd(23,27,7,0,23,27,17,20,26,23,0,192,0,18,0,0,12,16,23,1,0)
    for index, physical in enumerate(palette):
        data += cmd(19,index,physical,0,0,0)
    def text(x, y, message, ink=white):
        return colour(ink) + plot(4,x,y) + cmd(5) + message.encode('ascii') + cmd(4)
    data += text(8,16,f'Mode {mode} {width}x{height} {count} colours')
    data += text(8,height-8,'Static conversion control - Esc exits')
    side = 8 if count == 64 else 4
    cells, svg = [], []
    for index, physical in enumerate(palette):
        x0 = (index % side)*width//side
        x1 = (index % side+1)*width//side-1
        y0 = 24+(index//side)*(height-48)//side
        y1 = 24+(index//side+1)*(height-48)//side-1
        rgb = [((physical >> shift)&3)*85 for shift in (4,2,0)]
        ink = 0 if sum(rgb) > 360 else white
        data += colour(index)+plot(4,x0,y0)+plot(101,x1,y1)
        data += text(x0+4,y0+14,f'{index:02}',ink)
        cells.append(dict(index=index,physical_rrggbb=physical,rgb=rgb,bounds=[x0,y0,x1,y1]))
        fill = '#'+''.join(f'{v:02x}' for v in rgb)
        svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0+1}" height="{y1-y0+1}" fill="{fill}"/><text x="{x0+4}" y="{y0+14}" fill="{"black" if ink == 0 else "white"}">{index:02}</text>')
    if doubled:
        # Draw back once and expose it once; no swaps during measurement.
        data += cmd(23,0,195)
    title = f'Mode {mode}: {width}x{height}, {count} colours'
    image = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" style="background:black;font:12px monospace"><text x="8" y="16" fill="white">{html.escape(title)}</text>'+''.join(svg)+'</svg>'
    return data, cells, image

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assembler',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    identity = 'render-load-static-r01-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
    source = HERE/'static_conversion.asm'
    record = dict(build_id=identity,status='experimental',source_sha256=sha(source),generator_sha256=sha(Path(__file__)),assembler_sha256=sha(args.assembler),modes={})
    for mode in MODES:
        out = args.output/f'mode{mode}';out.mkdir()
        shutil.copyfile(source,out/'static.asm')
        data,cells,svg = pattern(mode)
        tag = int.from_bytes(hashlib.sha256(f'{identity}:{mode}'.encode()).digest()[:3],'little')
        marker = cmd(23,0,160,255,255,0,12,0)+b'B009'+cmd(1,0,0,0,1)+tag.to_bytes(3,'little')
        text = f'EXPECT_MODE: equ {mode}\nmarker: db '+','.join(map(str,marker))+'\nchart:\n'
        text += ''.join(' db '+','.join(map(str,data[i:i+24]))+'\n' for i in range(0,len(data),24))+'chart_end:\n'
        (out/'chart.inc').write_text(text)
        (out/'reference.svg').write_text(svg)
        binary=identity+f'-mode{mode}.bin'
        subprocess.run([str(args.assembler.resolve()),'static.asm',binary,'-l','-s','-c'],cwd=out,check=True)
        assert (out/binary).stat().st_size < 8192
        record['modes'][str(mode)] = dict(binary=binary,bytes=(out/binary).stat().st_size,sha256=sha(out/binary),chart_bytes=len(data),chart_sha256=hashlib.sha256(data).hexdigest(),include_sha256=sha(out/'chart.inc'),tag=tag,cells=cells)
    (args.output/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    print(identity)

if __name__ == '__main__':
    main()
