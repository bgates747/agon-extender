#!/usr/bin/env python3
"""Build bounded all-mode derivatives without modifying frozen SCAN evidence.

Synthetic cases retain SCAN's PRT/aggregate carrier. Nurples derivatives keep
the repaired simulation, map and keys; only screen bounds/origin, admission,
explicit double-bank initialization/swap and asset paths change. They are test
articles, not replacement game releases. Cross-mode timings are not comparable.
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
MODES = {0: (640,480,16,False), 3: (640,240,64,False),
         8: (320,240,64,False), 20: (512,384,64,False), 136: (320,240,64,True)}
NAMES = {1:'bitmap-light',2:'bitmap-heavy',3:'partial-scroll',4:'software-static',
         5:'software-scroll',6:'nurples-software',7:'hardware-static',8:'nurples-hardware'}
spec = importlib.util.spec_from_file_location('scan_builder', HERE/'build.py')
old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def cmd(*args): return bytes(args)


def geometry(mode):
    w,h,colors,db=MODES[mode]
    return w,h,colors,db,(w-256)//2,48,h-48


def field(mode):
    w,h,c,db,x,y,fh=geometry(mode)
    return old.origin(x,y)+old.viewport(0,0,255,fh-1)


def background(mode):
    w,h,c,db,x,y,fh=geometry(mode)
    out=cmd(20,26,23,0,192,0,18,0,0,12,16,23,1,0)
    # Protected sidebars give inexpensive ordinary pixel-query controls.
    for xx in (0,w-16):
        for yy in range(0,h,16):
            out+=old.colour(1+(yy//16)%(c-1))+old.plot(4,xx,yy)+old.plot(101,xx+15,min(h-1,yy+15))
    out+=field(mode)
    for yy in range(0,fh,16):
        for xx in range(0,256,16):
            out+=old.bitmap(512+old.TILES[(xx//16+yy//16)%16],xx,yy)
    return out


def setup(mode,case):
    out=cmd(23,27,7,0,23,27,17)+background(mode)
    if MODES[mode][3]:
        out+=cmd(23,0,195)+background(mode)+cmd(23,0,195)
    count=32 if case in (4,5) else 16 if case==7 else 0
    if count:
        out+=cmd(23,0,248,2,0,1,0)
        for i in range(count):
            out+=cmd(23,27,4,i,23,27,5,23,27,38)+old.word(old.ART[i%4])
            out+=cmd(23,27,18,0,23,27,19 if case==7 else 20,23,27,11)
        out+=cmd(23,27,7,count)
    return out


def frame(mode,case,u):
    w,h,c,db,x,y,fh=geometry(mode)
    out=b''
    if case in (1,2):
        out+=old.origin(0,0)+old.viewport(16,0,w-17,h-1)
        cols=(w-32)//24
        for i in range(16 if case==1 else 64):
            xx=16+(i%cols)*24+(u+i)%8
            yy=(i//cols)*24+(u*2+i)%8
            assert xx+16<=w-16 and yy+16<=h
            out+=old.bitmap(old.ART[i%4],xx,yy)
    if case in (3,5):
        # Double-bank pages advance by two rows per visit, maintaining the
        # same displayed scroll velocity; each row gets its proper tile data.
        for step in range(2 if db else 1):
            row=u-step if db else u
            out+=field(mode)+cmd(23,7,2,2,1)+old.viewport(0,0,255,0)
            out+=old.bitmap(1024,0,(row%256)-255)
            for i in range(16):
                out+=old.bitmap(512+old.TILES[(i+row//16)%16],i*16,(row%16)-15)
        out+=field(mode)
    if case in (4,5,7):
        out+=old.origin(0,0)+old.viewport(x,y,x+255,h-1)
        for i in range(16 if case==7 else 32):
            xx=x+(i%8)*32+(3*u+5*i+9)%16
            yy=y+8+(i//8)*40+(2*u+3*i)%16
            assert x<=xx and xx+16<=x+256 and y<=yy and yy+16<=h
            out+=cmd(23,27,4,i,23,27,13)+old.word(xx)+old.word(yy)
        out+=cmd(23,27,15)
    if db: out+=cmd(23,0,195)
    return out


def runner(mode):
    text=(HERE/'runner.inc').read_text()
    text=old.patch(text,'    cp 20\n',f'    cp {mode}\n')
    text=text.replace('SCAN: mode 20/VDP reply/clock required.',f'MQ: mode {mode}/VDP reply/clock required.')
    # Each new job resets only diagnostic counters, after all prior evidence
    # was collected. Use the existing official discarded-buffer carrier.
    text=old.patch(text,'    call sc_prepare\n','    xor a\n    call sc_marker\n    call sc_prepare\n')
    return text


def build(args):
    out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    source=args.source.resolve()
    previous=json.loads((source/'manifest.json').read_text())
    if previous['source_head']!='0c741d5e2021927adfa440f45b8e04b950114889':
        raise ValueError('Require the retained repaired Nurples fixture input')
    build_id='render-qualification-r01-b'+dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
    card=out/'sdcard'; root=card/'extender/render-qualification-r01'
    root.mkdir(parents=True)
    assets=source/'sdcard/test/nurples/scan-r02'
    records=old.agnb(assets/'game.agnb')
    blob=b''.join(old.upload(i,records[i]) for i in old.ART+[512+t for t in old.TILES]+[1024])
    (root/'assets.bin').write_bytes(blob)
    entries=[]
    def assemble(folder,main):
        (folder/'identity.inc').write_text('db '+json.dumps(build_id)+'\n')
        p=subprocess.run([str(args.assembler.resolve()),main,'fixture.bin','-l','-s'],cwd=folder,capture_output=True,text=True)
        (folder/'build.log').write_text(p.stdout+p.stderr)
        if p.returncode: raise RuntimeError((p.stdout+p.stderr)[-2000:])
        return folder/'fixture.bin'
    for mode in MODES:
        for case in NAMES:
            folder=out/f'source-m{mode}-c{case}'; folder.mkdir()
            remote=f'/extender/render-qualification-r01/m{mode}/c{case}'
            target=card/remote.lstrip('/');target.mkdir(parents=True)
            if case in (6,8):
                shutil.copytree(source/'nurples-source/asm',folder,dirs_exist_ok=True)
                game=(folder/'game.inc').read_text().replace('sc_case: equ 9',f'sc_case: equ {case}')
                if case==8:
                    game=old.patch(game,'    call game_init','    ld hl,sc_hw_enable\n    ld bc,7\n    rst.lil 18h\n    call game_init')
                    game=old.patch(game,'sc_sw_packet: db 23,27,18,0,23,27,20','sc_sw_packet: db 23,27,18,0,23,27,19\nsc_hw_enable: db 23,0,248,2,0,0,0')
                if mode==136:
                    # Preserve the existing game's single-bank incremental
                    # scene algorithm. Both banks get a full initial scene;
                    # subsequent updates alternate. This is explicitly a
                    # double-bank stress derivative, not a production port.
                    game=old.patch(game,'    call game_init\n','    call game_init\n    call vdu_flip\n    call game_init\n')
                    game=old.patch(game,'    call telemetry_tick\n','    call telemetry_tick\n    call vdu_flip\n')
                (folder/'game.inc').write_text(game)
                screen=(folder/'screen.inc').read_text();w,h,c,db,x,y,fh=geometry(mode)
                for before,after in [('screen_right: equ 511',f'screen_right: equ {w-1}'),('screen_bottom: equ 383',f'screen_bottom: equ {h-1}'),('origin_left: equ 128',f'origin_left: equ {x}')]:
                    screen=old.patch(screen,before,after)
                (folder/'screen.inc').write_text(screen)
                for name in ('game.agnb','ui.agnb','fonts/Lat38-VGA8_8x8.font'):
                    # Share immutable game assets already retained on card;
                    # fixed absolute paths remove ten redundant uploads.
                    for p in folder.glob('*.inc'):
                        t=p.read_text();replacement='/test/nurples/scan-r01/'+name
                        t=t.replace('"'+name+'"','"'+replacement+'"');p.write_text(t)
                main='nurples.asm'
            else:
                data=setup(mode,case);(target/'setup.bin').write_bytes(data)
                frames=bytearray();table=[]
                for u in range(256):
                    if u>=128:
                        table.append(table[u-128]);continue
                    table.append(0x50000+len(frames)); f=frame(mode,case,u)
                    frames+=old.triple(len(f))+f
                assert len(frames)<0x30000
                (target/'frames.bin').write_bytes(frames)
                (folder/'frames.inc').write_text('frame_table:\n'+''.join(f' dl {n}\n' for n in table))
                (folder/'case.inc').write_text(f'sc_case: equ {case}\nsetup_size: equ {len(data)}\n')
                text=(HERE/'synthetic.asm').read_text()
                start=text.index('sc_prepare:\n');end=text.index('sc_work:\n',start)
                prepare='sc_prepare:\n    ld hl,assets_name\n    call sc_load\n    ret nz\n'
                for offset in range(0,len(blob),60000):
                    prepare+=f'    ld hl,050000h+{offset}\n    ld bc,{min(60000,len(blob)-offset)}\n    rst.lil 18h\n'
                prepare+=f'    ld hl,setup_name\n    call sc_load\n    ret nz\n    ld hl,050000h\n    ld bc,{len(data)}\n    rst.lil 18h\n    ld hl,frames_name\n    call sc_load\n    ret\n'
                text=text[:start]+prepare+text[end:]
                text=text.replace('asciz "setup.bin"',f'asciz "{remote}/setup.bin"').replace('asciz "frames.bin"',f'asciz "{remote}/frames.bin"')
                text=text.replace('setup_name:','assets_name: asciz "/extender/render-qualification-r01/assets.bin"\nsetup_name:')
                # Mode 0's valid white is 15; default system text white7 is
                # portable. No production palette/colour semantics change.
                text=text.replace('17,63,17,128','17,7,17,128')
                (folder/'synthetic.asm').write_text(text);main='synthetic.asm'
            (folder/'runner.inc').write_text(runner(mode))
            binary=assemble(folder,main);shutil.copyfile(binary,target/'fixture.bin')
            if binary.stat().st_size>=65536: raise ValueError('Fixture overlaps staged frame RAM')
            entries.append(dict(mode=mode,case=case,name=NAMES[case],geometry=list(MODES[mode]),
                                sd_dir=remote,binary_sha256=sha(binary),build_id=build_id,
                                game=case in (6,8),hardware=case in (7,8),
                                page_policy='alternate initialized banks' if mode==136 else 'single bank',
                                limits='Nurples geometry derivative; original artwork may be clipped; mode136 is bank stress, not production gameplay' if case in (6,8) else 'geometry-bounded synthetic workload'))
    manifest=dict(build_id=build_id,source_fixture=previous['build_id'],source_head=previous['source_head'],
                  assembler_sha256=sha(args.assembler),builder_sha256=sha(__file__),cases=entries,
                  files=[dict(path=str(p.relative_to(card)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(card.rglob('*')) if p.is_file()])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(build_id, len(entries), 'fixtures')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','assembler','output'):p.add_argument('--'+name,type=Path,required=True)
    build(p.parse_args())
