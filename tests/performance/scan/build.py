#!/usr/bin/env python3
"""Build SCAN01-S05 in a fresh directory from S01-pinned inputs; never edit game.

Derived stream idioms: render_load/generate.py and familiar game-art loader.
Paths and card deployment are caller inputs, not tracked machine configuration.
"""
import argparse
import datetime as dt
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def word(n): return struct.pack('<H', n & 65535)
def triple(n): return n.to_bytes(3, 'little')
def cmd(*n): return bytes(n)
def origin(x,y): return cmd(29)+word(x)+word(y)
def viewport(x,y,r,b): return cmd(24)+word(x)+word(b)+word(r)+word(y)
def select(i): return cmd(23,27,32)+word(i)
def bitmap(i,x,y): return select(i)+cmd(25,0xed)+word(x)+word(y)
def colour(n): return cmd(18,0,n)
def plot(op,x,y): return cmd(25,op)+word(x)+word(y)
def field(): return origin(128,48)+viewport(0,0,255,335)
ART = [371,339,383,270]
TILES = [0,89,90,91,73,75,57,58,59,129,147,206,207,208,190,192]
COUNTS = [0,0,0,4,8,16,32,32]

def chunks(b, start=0):
    while start < len(b):
        typ=b[start:start+4]; n=struct.unpack_from('<I',b,start+4)[0]
        assert start+8+n <= len(b)
        yield typ,b[start+8:start+8+n]
        start += 8+(n+3)//4*4
    assert start == len(b)

def agnb(path):
    b=path.read_bytes(); assert b[:4]==b'RIFF' and b[8:12]==b'AGNB'
    assert int.from_bytes(b[4:8],'little')+8==len(b)
    out={}
    for typ,payload in chunks(b,12):
        if typ!=b'LIST': continue
        assert payload[:4]==b'BUFR'
        d=dict(chunks(payload,4)); ident=int.from_bytes(d[b'BHDR'],'little')
        w,h,fmt=struct.unpack('<HHB',d[b'IMAG'])
        assert fmt==1 and len(d[b'DATA'])==w*h and ident not in out
        out[ident]=(w,h,d[b'DATA'])
    return out

def upload(i,record):
    w,h,data=record
    out=cmd(23,0,160)+word(i)+cmd(2)
    for n in range(0,len(data),8192):
        part=data[n:n+8192]
        out+=cmd(23,0,160)+word(i)+cmd(0)+word(len(part))+part
    out+=cmd(23,0,160)+word(i)+cmd(14)
    return out+select(i)+cmd(23,27,33)+word(w)+word(h)+cmd(1)

def setup(count,records):
    out=cmd(23,27,7,0,23,27,17,20,26,23,0,192,0,18,0,0,12,16,23,1,0)
    for i in ART+[512+t for t in TILES]+[1024]: out+=upload(i,records[i])
    # Same recognizable stationary sidebars and initial field in all eight cases.
    for x in (0,384):
        for y in range(0,384,32):
            out+=colour(1+(y//32)%7)+plot(4,x,y)+plot(101,x+127,y+31)
    out+=cmd(17,63,17,128,31,17,1)+b'SCAN partial scroll / software sprites'
    out+=field()+bitmap(1024,0,0)+bitmap(1024,0,256)
    for y in range(0,336,16):
        for x in range(0,256,16): out+=bitmap(512+TILES[(x//16+y//16)%16],x,y)
    out+=origin(0,0)+viewport(128,48,383,383)
    for i in range(count):
        out+=cmd(23,27,4,i,23,27,5,23,27,38)+word(ART[i%4])
        out+=cmd(23,27,18,0,23,27,20,23,27,11)
    out+=cmd(23,27,7,count)
    return out

def sprite_frame(count,u):
    out=b''
    for i in range(count):
        x=128+32*(i%8)+(3*u+5*i+0xb009)%16
        y=48+80*(i//8)+(2*u+3*i)%16
        assert 128<=x<=368 and 48<=y<=368
        out+=cmd(23,27,4,i,23,27,13)+word(x)+word(y)
    return out+(cmd(23,27,15) if count else b'')

def frame(case,u):
    out=b''
    if 2<=case<=7:
        out+=field()+cmd(23,7,2,2,1)
    if 3<=case<=7:
        out+=viewport(0,0,255,0)+bitmap(1024,0,(u%256)-255)
        for i in range(16):out+=bitmap(512+TILES[(i+u//16)%16],i*16,(u%16)-15)
        out+=field()
    if COUNTS[case-1]:out+=sprite_frame(COUNTS[case-1],u)
    return out

def config(case,frames,warm,path,fence_off=False,extra_flags=0,window_tag=0):
    assert 1<=case<=9 and 1<=frames<=3600 and 0<=warm<=120
    assert 0<=extra_flags<8 and 0<=window_tag<1<<24
    assert bool(extra_flags&4)==bool(window_tag), 'window marker requires a nonzero correlation tag'
    b=bytearray(128);b[:4]=b'SSC'+bytes([case]);b[4:7]=triple(frames);b[7:10]=triple(warm)
    b[10]=int(fence_off or case==9)|extra_flags
    b[11:14]=triple(window_tag)
    p=path.encode('ascii');assert len(p)<111 and p.startswith(b'/agents/extender/results/')
    b[16:16+len(p)]=p
    return bytes(b)

def patch(text,old,new,count=1):
    assert text.count(old)==count,(old[:90],text.count(old),count)
    return text.replace(old,new)

def derivative(source,out):
    asm=out/'asm';shutil.copytree(source/'src/asm',asm)
    original={p.name:p.read_text() for p in asm.glob('*') if p.is_file()}
    s=original['nurples.asm']
    s=patch(s,'main:\n','main:\n    jp sc_main\noriginal_main:\n')
    # Original game loop is retained unreachable for a reviewable diff.
    s=patch(s,'main_end:\n','original_main_end:\nmain_end:\n')
    s=patch(s,'    call vdu_set_screen_mode','    ; SCAN: startup alone selects the mode')
    s=patch(s,'    include "tables.inc"','    include "game.inc"\n    include "tables.inc"')
    (asm/'nurples.asm').write_text(s)
    s=original['state_game_init.inc']
    s=patch(s,'    call vdu_set_screen_mode','    ; SCAN: startup alone selects the mode',3)
    s=patch(s,'    call choose_joystick','    call player_joystick_disable')
    s=patch(s,'    call waitKeypress','    ; SCAN: finite, noninteractive fixture',4)
    (asm/'state_game_init.inc').write_text(s)
    s=original['player_state.inc']
    s=patch(s,'    ld bc,0*256','    ld bc,sprite_right*128',2)
    s=patch(s,'    ld de,sprite_bottom*256','    ld de,sprite_bottom*128',2)
    (asm/'player_state.inc').write_text(s)
    s=patch(original['player_shields.inc'],'update_shields:\n',
            'update_shields:\n    ld a,64\n    ld (player_shields),a\n    or a\n    ret ; SCAN invulnerability; production damage code remains below\n')
    (asm/'player_shields.inc').write_text(s)
    s=patch(original['player_input.inc'],'MOSCALL    mos_getkbmap ;ix = pointer to MOS virtual keys table',
            'MOSCALL    mos_getkbmap ; ordinary MOS poll retained\n    ld ix,sc_keys ; SCAN deterministic substitution, not input-delivery evidence')
    (asm/'player_input.inc').write_text(s)
    s=patch(original['timer.inc'],'timestamp_tick:\n','timestamp_tick:\n    jp sc_sim_tick ; SCAN simulation only, PRT/MOS remain real\n')
    (asm/'timer.inc').write_text(s)
    s=original['vdu_sprites.inc']
    # Each frame attachment establishes software type, including runtime spawns.
    for label,end in [('vdu_sprite_add_bmp:','@end:'),('vdu_sprite_add_buff:','@end:')]:
        a=s.index(label);z=s.index(end,a);part=s[a:z]
        part=patch(part,'    rst.lil $18','    rst.lil $18\n    call sc_force_software')
        s=s[:a]+part+s[z:]
    (asm/'vdu_sprites.inc').write_text(s)
    diff=''
    for name,before in original.items():
        after=(asm/name).read_text()
        if before!=after:diff+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='nurples-repair/'+name,tofile='scan-fixture/'+name))
    (out/'source-transform.diff').write_text(diff)
    # All executable mode-call sites must be disabled, including unreachable exit.
    assert not re.search(r'^\s*call vdu_set_screen_mode', '\n'.join(p.read_text() for p in asm.glob('*.inc'))+'\n'+s, re.M)
    for name in ('game.inc','runner.inc'):shutil.copyfile(HERE/name,asm/name)
    return asm

def build(args):
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    pin=json.loads(args.pin.read_text())
    for f in pin['files']:
        assert sha(args.source/f['path'])==f['sha256'], 'S01 source changed: '+f['path']
    ident='scan-scroll-suite-r02-b'+dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
    records=agnb(args.assets/'game.agnb')
    manifest={'build_id':ident,'status':'experimental','source_head':pin['head'],
              'source_pin_sha256':sha(args.pin),'assembler_sha256':sha(args.assembler),
              'contract_sha256':sha(ROOT/'docs/tasks/SCAN-001/S04-TEST-CONTRACT.md'),
              'art_ids':ART,'tile_ids':TILES,'cases':[],
              'source_files':{p.name:sha(p) for p in HERE.iterdir() if p.is_file()}}
    def assemble(cwd,src):
        (cwd/'identity.inc').write_text('db '+repr(ident).replace("'",'"')+'\n')
        p=subprocess.run([str(args.assembler.resolve()),src,'scan.bin','-l','-s'],cwd=cwd,capture_output=True,text=True)
        (cwd/'build.log').write_text(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError((cwd/'build.log').read_text()[-2500:])
    sd=out/'sdcard'
    for case in range(1,10):
        base=(sd/'test/nurples/scan-r02') if case==9 else (sd/f'extender/scan-r02/t{case:02}')
        base.mkdir(parents=True)
        if case<9:
            builddir=out/f't{case:02}-source';builddir.mkdir()
            data=setup(COUNTS[case-1],records);(base/'setup.bin').write_bytes(data)
            frames=bytearray();table=[]
            for u in range(256):
                table.append(0x50000+len(frames));f=frame(case,u);frames+=triple(len(f))+f
            assert len(frames)<0x30000 and len(data)<0x30000
            (base/'frames.bin').write_bytes(frames)
            (builddir/'frames.inc').write_text('frame_table:\n'+''.join(' dl '+str(n)+'\n' for n in table))
            (builddir/'case.inc').write_text(f'sc_case: equ {case}\nsetup_size: equ {len(data)}\n')
            for n in ('synthetic.asm','runner.inc'):shutil.copyfile(HERE/n,builddir/n)
            assemble(builddir,'synthetic.asm')
            assert (builddir/'scan.bin').stat().st_size<0x10000
        else:
            builddir=derivative(args.source,out/'nurples-source')
            assemble(builddir,'nurples.asm')
            # Sprite/tile tables occupy uninitialised RAM after the binary.
            syms=(builddir/'nurples.symbols').read_text() if (builddir/'nurples.symbols').exists() else (builddir/'scan.symbols').read_text()
            (out/'nurples-symbols.txt').write_text(syms)
            for asset in ['game.agnb','ui.agnb','fonts/Lat38-VGA8_8x8.font']:
                target=base/asset;target.parent.mkdir(exist_ok=True)
                shutil.copyfile(args.assets/asset,target)
        shutil.copyfile(builddir/'scan.bin',base/'scan.bin')
        for variant,n in [('full',3600 if case==9 else 600),('smoke',120)]:
            # Deployment carries templates; each physical run gets a fresh output.
            result=f'/agents/extender/results/scan-r02/{variant}-t{case:02}.bin'
            (base/f'{variant}.cfg').write_bytes(config(case,n,120 if case==9 else 60,result))
        if case in (7,8,9):
            for name,flags in [('natural',1),('no-timing',2)]:
                (base/(name+'.cfg')).write_bytes(config(case,120,120 if case==9 else 60,
                    f'/agents/extender/results/scan-r02/{name}-t{case:02}.bin',extra_flags=flags))
        shutil.copyfile(base/'smoke.cfg',base/'run.cfg')
        manifest['cases'].append({'id':f'SCAN01-T{case:02}','sd_dir':'/'+str(base.relative_to(sd)),
            'binary_sha256':sha(base/'scan.bin'),'warmup':120 if case==9 else 60,
            'frames':3600 if case==9 else 600,'software_sprites':COUNTS[case-1] if case<9 else 'ordinary game allocation'})
    (sd/'agents/extender/results/scan-r02').mkdir(parents=True)
    for route in ['legacy','excom']:
        (out/f'autoexec-{route}.txt').write_bytes(('SET KEYBOARD 1\r\nEMOS KEYINPUT extender\r\nEMOS '+route+'\r\nVDU 22 20\r\nCD /extender/scan-r02/t01\r\nLOAD scan.bin\r\n').encode())
    manifest['files']=[{'path':str(p.relative_to(sd)), 'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(sd.rglob('*')) if p.is_file()]
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(ident, len(manifest['files']),'files')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','assets','pin','assembler','output']:p.add_argument('--'+name,type=Path,required=True)
    build(p.parse_args())
