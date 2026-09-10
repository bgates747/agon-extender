"""Exercise real BSP stages with SDL keys/captures and bounded debugger checks."""
import argparse
import json
import os
from pathlib import Path
import pty
import re
import select
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'


def review(page=None,output=None,escape_stage=None,expect_error=False,repeat=1):
    catalog=json.loads((BUILD/'bitmaps-catalog.json').read_text())['pages']
    stages=[(p,s) for p in catalog if page is None or p['page']==page for s in p['stages']]
    if escape_stage:stages=stages[:escape_stage]
    if expect_error:stages=stages[:1]
    stages_per_run=len(stages)
    assert repeat==1 or (page is not None and not escape_stage and not expect_error)
    stages=stages*repeat
    output=Path(output or BUILD/'bitmap-review').resolve();output.mkdir(parents=True,exist_ok=True)
    symbols={k:int(v,16) for k,v in re.findall(r'^(\S+) \$([0-9a-fA-F]+)',
                  (BUILD/'bitmaps.symbols').read_text(),re.M)}
    keys=output/'keys';keys.write_bytes(b'');capture=output/'capture-request';capture.unlink(missing_ok=True)
    library=BUILD/'sdl_review.so'
    if not library.exists() or library.stat().st_mtime<(ROOT/'tests/sdl_review.c').stat().st_mtime:
        subprocess.run(['gcc','-Wall','-Werror','-shared','-fPIC','-I',str(Path.home()/'.local/include'),
                        str(ROOT/'tests/sdl_review.c'),'-ldl','-o',str(library)],check=True)
    env=os.environ|{'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','LD_PRELOAD':str(library),
                    'SHAPES_REVIEW_KEYS':str(keys),'SHAPES_REVIEW_CAPTURE':str(capture)}
    profile=ROOT/'.emulator';startup=profile/'sdcard/autoexec.txt';previous=startup.read_bytes()
    startup.write_bytes(('SET KEYBOARD 1\r\nVDU 22 20\r\ncd /extender\r\nload bitmaps.bin\r\n'+
                         (f'run . {page}' if page else 'run')+'\r\n').encode())
    master,slave=pty.openpty()
    proc=subprocess.Popen(['./fab-agon-emulator','--renderer','sw','--scale','integer',
                           '--debugger','--breakpoint',hex(symbols['waitKeypress']),
                           '--breakpoint',hex(symbols['bitmaps_review_done']),'-z'],
                           cwd=profile,env=env,stdin=slave,stdout=slave,stderr=slave)
    os.close(slave);transcript=[];records=[]
    def send(text):os.write(master,text.encode())
    def receive(marker='>> ',timeout=40):
        end=time.monotonic()+timeout;data=''
        while marker not in data:
            if time.monotonic()>end:raise TimeoutError(f'{marker}: {data[-1500:]}')
            if select.select([master],[],[],.1)[0]:
                chunk=os.read(master,65536).decode(errors='replace');data+=chunk;transcript.append(chunk)
        return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]','',data)
    def command(text):send(text+'\n');return receive()
    def memory(address,size):
        text=command(f'mem {hex(address)} {hex(size)}');data=[]
        for line in text.splitlines():
            match=re.match(r'^[0-9a-f]{6}: ((?:[0-9a-f]{2} ?)+) \|',line)
            if match:data.extend(int(v,16) for v in match[1].split())
        assert len(data)==size,(address,size,text)
        return data
    def byte(name):return memory(symbols[name],1)[0]
    def shot(name):
        target=output/name;target.unlink(missing_ok=True)
        time.sleep(.12)
        temp=capture.with_suffix('.tmp');temp.write_text(str(target)+'\n');temp.replace(capture)
        end=time.monotonic()+6
        while not target.exists() or capture.exists():
            if time.monotonic()>end:raise TimeoutError('SDL capture')
            time.sleep(.03)
    try:
        receive()
        for index,(p,stage) in enumerate(stages):
            state=command('state')
            assert f'{symbols["waitKeypress"]:06x}:' in state,state
            actual_page=byte('current_page');actual_stage=byte('current_stage');error=byte('load_error')
            if expect_error:
                assert error in (1,2),error
                shot('asset-error.bmp')
            else:
                expected_stage=p['stages'].index(stage)+1
                assert (actual_page,actual_stage,error)==(p['page'],expected_stage,0),(actual_page,actual_stage,error)
                count=byte('probe_total');good=byte('probe_passed');bad=byte('probe_failed');timeouts=byte('probe_timeouts')
                rgb=memory(symbols['observed_pixels'],(good+bad)*3) if good+bad else []
                probes=[dict(probe,actual=rgb[i*3:i*3+3] if i<good+bad else None) for i,probe in enumerate(stage['probes'])]
                records.append(dict(page=actual_page,stage=actual_stage,caption=stage['caption'],
                    total=count,correct=good,wrong=bad,timeouts=timeouts,probes=probes))
                shot((f'run{index//stages_per_run+1}-' if repeat>1 else '')+stage['name']+'.bmp')
                print(f'BSP-{actual_page:02}.{actual_stage:02}: {good}/{count}, {bad} wrong, {timeouts} timeouts',flush=True)
            send('continue\n');time.sleep(.18)
            with keys.open('ab') as f:f.write(b'\x1b' if expect_error or (escape_stage and index==len(stages)-1) else b' ')
            receive()
            if repeat>1 and (index+1)%stages_per_run==0:
                state=command('state')
                assert 'HL:000000' in state and f'{symbols["bitmaps_review_done"]:06x}:' in state,state
                shot(f'exit-run{index//stages_per_run+1}.bmp')
                if index+1<len(stages):
                    send('continue\n');time.sleep(.3)
                    with keys.open('ab') as f:f.write(f'run . {page}\n'.encode())
                    receive()
        state=command('state')
        expected_hl=1 if expect_error else 0
        assert re.search(f'HL:{expected_hl:06x}',state),state
        assert f'{symbols["bitmaps_review_done"]:06x}:' in state,state
        shot('exit.bmp')
        if escape_stage or expect_error:
            from PIL import Image
            im=Image.open(output/'exit.bmp').convert('RGB')
            assert im.crop((8,0,512,384)).getbbox() is None
            assert im.crop((0,8,8,384)).getbbox() is None
        (output/'results.json').write_text(json.dumps(records,indent=2)+'\n')
        send('exit\n');proc.wait(timeout=5)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        os.close(master);startup.write_bytes(previous)
        (output/'debugger.log').write_text(''.join(transcript))
    return sum(r['wrong']+r['timeouts'] for r in records)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page',type=int,choices=range(1,33))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--escape-stage',type=int)
    parser.add_argument('--expect-error',action='store_true')
    parser.add_argument('--repeat',type=int,default=1)
    parser.add_argument('--isolated-all',action='store_true')
    parser.add_argument('--fault',choices=('missing','truncated','oversized'))
    args=parser.parse_args()
    if args.isolated_all:
        output=args.output or BUILD/'bitmap-review/isolated'
        failures=sum(review(n,output/f'p{n:02}') for n in range(1,33))
    elif args.fault:
        asset=ROOT/'.emulator/sdcard/extender/assets/bitmaps/axes2.rgba2'
        previous=asset.read_bytes()
        try:
            if args.fault=='missing':asset.unlink()
            else:asset.write_bytes(previous[:-1] if args.fault=='truncated' else previous+b'\0')
            failures=review(1,args.output,expect_error=True)
        finally:asset.write_bytes(previous)
    else:failures=review(args.page,args.output,args.escape_stage,args.expect_error,args.repeat)
    raise SystemExit(bool(failures))


if __name__=='__main__':main()
