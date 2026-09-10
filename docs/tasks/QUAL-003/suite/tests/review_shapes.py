"""Run the deployed tour in stock Fab, capture real frames and check MOS results."""
import argparse
import json
import os
from pathlib import Path
import pty
import re
import select
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pages', type=int, default=24)
    parser.add_argument('--output', type=Path, default=BUILD/'review')
    parser.add_argument('--escape-last', action='store_true')
    args = parser.parse_args()
    symbols = dict(re.findall(r'^(\S+) \$([0-9a-fA-F]+)',
                             (BUILD/'shapes.symbols').read_text(), re.M))
    address = lambda name: int(symbols[name], 16)
    output = args.output.resolve()
    output.mkdir(exist_ok=True)
    keys = output/'keys'
    keys.write_bytes(b'')
    capture = output/'capture-request'
    capture.unlink(missing_ok=True)
    library = BUILD/'sdl_review.so'
    subprocess.run(['gcc','-Wall','-Werror','-shared','-fPIC','-I',str(Path.home()/'.local/include'),
                    str(ROOT/'tests/sdl_review.c'),'-ldl','-o',str(library)], check=True)
    env = os.environ | {'SDL_VIDEODRIVER':'dummy', 'SDL_AUDIODRIVER':'dummy',
                        'LD_PRELOAD':str(library),'SHAPES_REVIEW_KEYS':str(keys),
                        'SHAPES_REVIEW_CAPTURE':str(capture)}
    master, slave = pty.openpty()
    profile = ROOT/'.emulator'
    proc = subprocess.Popen(['./fab-agon-emulator','--firmware','platform',
                             '--mos',str(profile/'mos_platform.bin'),
                             '--sdcard',str(profile/'sdcard'),'--renderer','sw','--scale','integer',
                             '--debugger','--breakpoint',hex(address('waitKeypress')),
                             '--breakpoint',hex(address('shapes_review_done')),'-z'],
                            cwd=profile,env=env,stdin=slave,stdout=slave,stderr=slave)
    os.close(slave)
    transcript=[]
    def send(text): os.write(master,text.encode())
    def receive(marker,timeout=20):
        end=time.monotonic()+timeout;data=''
        while marker not in data:
            if time.monotonic()>end: raise TimeoutError(f'Waiting for {marker!r}: {data[-1000:]}')
            if select.select([master],[],[],0.1)[0]:
                chunk=os.read(master,65536).decode(errors='replace')
                data+=chunk;transcript.append(chunk)
        return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]','',data)
    def command(text):
        send(text+'\n'); return receive('>> ')
    def capture_frame(shot):
        time.sleep(0.15)
        shot.unlink(missing_ok=True)
        request_tmp=capture.with_suffix('.tmp')
        request_tmp.write_text(str(shot)+'\n')
        request_tmp.replace(capture)
        end=time.monotonic()+5
        while not shot.exists() or capture.exists():
            if time.monotonic()>end:raise TimeoutError('Frame capture')
            time.sleep(0.05)
    records=[]
    try:
        receive('>> ')
        for index in range(args.pages):
            current=command(f'mem {hex(address("current_page"))} 1')
            match=re.search(rf'{address("current_page"):06x}: ([0-9a-f]{{2}})',current)
            page=int(match[1],16)
            text=command(f'mem {hex(address("results")+(page-1)*4)} 4')
            match=re.search(rf'{address("results")+(page-1)*4:06x}: ((?:[0-9a-f]{{2}} ?){{4}})',text)
            record=[int(v,16) for v in match[1].split()]
            received=record[1]+record[2]
            observed=[]
            if received:
                raw=command(f'mem {hex(address("observed_pixels"))} {hex(received*3)}')
                for line in raw.splitlines():
                    match=re.match(r'^[0-9a-f]{6}: ((?:[0-9a-f]{2} ?)+) \|',line)
                    if match:observed.extend(int(v,16) for v in match[1].split())
                assert len(observed)==received*3,(len(observed),received)
            manifest=json.loads((BUILD/f'shp{page:02}.json').read_text())
            samples=[]
            for i,(name,x,y,expected) in enumerate(manifest['probes']):
                actual=observed[i*3:i*3+3] if i<received else None
                samples.append(dict(name=name,x=x,y=y,expected=expected,actual=actual,
                                    correct=actual==expected if actual is not None else None))
            records.append({'page':page,'total':record[0],'correct':record[1],
                            'wrong':record[2],'timeouts':record[3],'samples':samples})
            capture_frame(output/f'shp{page:02}.bmp')
            print(f'SHP-{page:02}: {record[1]}/{record[0]}, {record[2]} wrong, {record[3]} timeouts',flush=True)
            send('continue\n')
            time.sleep(0.15)
            with keys.open('ab') as stream:
                stream.write(b'\x1b' if args.escape_last and index==args.pages-1 else b' ')
            receive('>> ')
        state=command('state')
        assert re.search(r'HL:000000',state),state
        assert f'{address("shapes_review_done"):06x}:' in state,state
        capture_frame(output/'exit.bmp')
        if args.escape_last:
            from PIL import Image
            image=Image.open(output/'exit.bmp').convert('RGB')
            # Cursor may blink in the home cell; every other pixel must be black.
            assert image.crop((8,0,512,384)).getbbox() is None
            assert image.crop((0,8,8,384)).getbbox() is None
            print('Escape cleared the screen and returned HL=0.',flush=True)
        command('mem '+hex(address('results'))+' '+hex(24*4))
        (output/'results.json').write_text(json.dumps(records,indent=2)+'\n')
        send('exit\n');proc.wait(timeout=5)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        os.close(master)
        (output/'debugger.log').write_text(''.join(transcript))
    if any(r['correct']!=r['total'] or r['timeouts'] for r in records):raise SystemExit(1)


if __name__=='__main__':main()
