#!/usr/bin/env python3
"""Build a stopped mode20 live/replay app; never deploy or operate hardware."""
import argparse
import ctypes
import ctypes.util
from datetime import datetime
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from controller_input import validate_capture, BUTTONS


def replay(capture):
    validate_capture(capture)
    records=[];generation=0;sequence=0;hat=0;hat_presses=[0]*4;presses=[0]*15
    last_ms=0
    def record(row,state,connected):
        nonlocal sequence,last_ms,hat,presses
        sequence+=1;last_ms=row['t_ns']//1_000_000
        if connected:
            axes={int(k):v for k,v in state['axes'].items()}
            keys=set(state['buttons'])
            held=sum(1<<i for i,k in enumerate(BUTTONS) if k in keys)
            for code,minus,plus in ((16,11,12),(17,13,14)):
                if axes[code]:held|=1<<(plus if axes[code]>0 else minus)
            new_hat=held&0x7800
            if row['kind']!='connect':
                for i in range(4):
                    if new_hat&(1<<(11+i)) and not hat&(1<<(11+i)):hat_presses[i]+=1
            hat=new_hat
            presses=[state['presses'][str(k)] for k in BUTTONS]+hat_presses
            sticks=[axes[k] for k in (0,1,3,4)];triggers=[axes[k] for k in (2,5)]
        else:held=0;sticks=[0]*4;triggers=[0]*2
        if max(presses)>65535:raise ValueError('Replay count exceeds unsigned16')
        records.append(struct.pack('<IIHBB4h2BH15H',last_ms,sequence,generation,
                                   3 if connected else 0,0,*sticks,*triggers,held,*presses))
    with capture.open() as stream:
        for line in stream:
            row=json.loads(line)
            if row['kind']=='connect':
                generation+=1;hat=0;hat_presses=[0]*4;presses=[0]*15
                record(row,row['state'],True)
            elif row['kind']=='frame':record(row,row['state'],True)
            elif row['kind'] in ('disconnect','end'):record(row,None,False)
            elif row['kind']=='resync':raise ValueError('Input-gap replay needs explicit unknown-history UI')
    if not records:raise ValueError('Capture contains no controller states')
    return struct.pack('<4sIII',b'CVR1',len(records),last_ms,0)+b''.join(records),len(records),last_ms


def font_data():
    font=ImageFont.truetype('DejaVuSansMono-Bold.ttf',16)
    data=bytearray()
    for code in range(256):
        image=Image.new('1',(12,16));draw=ImageDraw.Draw(image)
        if 32<=code<127:draw.text((1,-2),chr(code),font=font,fill=1)
        for y in range(16):
            bits=sum(1<<(15-x) for x in range(12) if image.getpixel((x,y)))
            data+=struct.pack('>H',bits)
    return data


def raster(svg,png):
    rsvg=ctypes.CDLL(ctypes.util.find_library('rsvg-2'))
    cairo=ctypes.CDLL(ctypes.util.find_library('cairo'))
    gobject=ctypes.CDLL(ctypes.util.find_library('gobject-2.0'))
    rsvg.rsvg_handle_new_from_data.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_void_p]
    rsvg.rsvg_handle_new_from_data.restype=ctypes.c_void_p
    rsvg.rsvg_handle_render_cairo.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
    cairo.cairo_image_surface_create.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int]
    cairo.cairo_image_surface_create.restype=ctypes.c_void_p
    cairo.cairo_create.argtypes=[ctypes.c_void_p];cairo.cairo_create.restype=ctypes.c_void_p
    cairo.cairo_surface_write_to_png.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
    cairo.cairo_destroy.argtypes=[ctypes.c_void_p];cairo.cairo_surface_destroy.argtypes=[ctypes.c_void_p]
    gobject.g_object_unref.argtypes=[ctypes.c_void_p]
    data=svg.read_bytes();handle=rsvg.rsvg_handle_new_from_data(data,len(data),None)
    if not handle:raise ValueError('Invalid generated SVG')
    surface=cairo.cairo_image_surface_create(0,1024,768);context=cairo.cairo_create(surface)
    try:
        if not rsvg.rsvg_handle_render_cairo(handle,context):raise ValueError('SVG rendering failed')
        if cairo.cairo_surface_write_to_png(surface,os.fsencode(png)):raise ValueError('PNG writing failed')
    finally:cairo.cairo_destroy(context);cairo.cairo_surface_destroy(surface);gobject.g_object_unref(handle)


def build(args):
    identity=json.loads((HERE/'identity.json').read_text())
    if args.build_id!='UNVERSIONED-DO-NOT-DEPLOY':
        prefix=identity['source_identity']+'-b'
        if not args.build_id.startswith(prefix):raise ValueError('Build identity must match approved source identity')
        datetime.strptime(args.build_id[len(prefix):],'%Y-%m-%d-%H-%M-%SZ')
        if subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain']):
            raise ValueError('Identified viewer builds require clean committed source')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    package=output/'package';package.mkdir();work=output/'application';src=work/'src';src.mkdir(parents=True)
    for name in ('main.cpp','view.hpp','live.hpp'):shutil.copy2(HERE/name,src/name)
    (src/'identity.hpp').write_text('// Generated build identity; do not edit.\n#define CONTROLLER_BUILD_ID '+json.dumps(args.build_id)+'\n')
    shutil.copy2(HERE.parent/'scroll/mode_lifecycle.hpp',src/'mode_lifecycle.hpp')
    shutil.copy2(HERE/'mos_io.asm',src/'mos_io.asm')
    wire=ROOT/'vdp/video/extender/input/controller/appliance_wire.h'
    if wire.read_bytes()!=(args.emos_source/'src/emos_controller_wire.h').read_bytes():
        raise ValueError('EMOS/P4 controller wire definitions disagree')
    shutil.copy2(wire,src/'controller_wire.h')
    canonical_api=(args.emos_source/'src/mos_api.inc').read_text()
    definitions=[]
    for symbol,owner in (('MOS_GETFUNCTION','mos_getfunction'),('EMOS_GATEWAY','mos_emos_gateway'),
                         ('EMOS_FUNCTION_GATEWAY','mos_function_emos_gateway')):
        match=re.search(r'^'+owner+r':\s+EQU\s+([0-9a-f]+)h',canonical_api,re.I|re.M)
        if not match:raise ValueError('Missing canonical EMOS binding: '+owner)
        definitions.append(f'.equ {symbol}, 0x{match[1]}')
    (src/'emos_api.inc').write_text('; Generated from maintained EMOS mos_api.inc; do not edit.\n'+'\n'.join(definitions)+'\n')
    font=font_data()
    (src/'font.hpp').write_text('// Generated12x16 monochrome font; do not edit.\n'
                              'static const unsigned char controller_font[]={'+','.join(str(b) for b in font)+'};\n')
    (work/'Makefile').write_text('NAME=ctrlview\nLDHAS_ARG_PROCESSING=1\nLDHAS_EXIT_HANDLER=0\n'
                               'include $(shell agondev-config --makefile)\n'
                               'CXXFLAGS += -std=c++17 -fno-exceptions -fno-rtti -Wall -Wextra -Werror\n')
    env=dict(os.environ,PATH=str(args.toolchain_bin.resolve())+os.pathsep+os.environ['PATH'])
    subprocess.run(['make','-C',str(work)],env=env,check=True)
    shutil.copy2(work/'bin/ctrlview.bin',package/'ctrlview.bin')
    data,count,duration=replay(args.capture)
    (package/'capture.cvr').write_bytes(data)
    with (output/'preview.svg').open('w') as stream:
        native=output/'native-preview'
        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(HERE/'native.cpp'),'-o',str(native)],check=True)
        subprocess.run([str(native)],stdout=stream,check=True)
    raster(output/'preview.svg',output/'preview.png')
    (package/'README.txt').write_text('Live input needs the matched controller-enabled EMOS/P4 candidates.\n'
        'Deploy under /extender/controller. Do not change autoexec.\n'
        'CD /extender/controller\nLOAD ctrlview.bin\nRUN &040000\n'
        'The app saves its entry mode, selects/settles mode20 if needed, and restores the entry mode on exit.\n'
        'For explicitly labelled recorded input use: RUN &040000 replay\n'
        'Esc exits; R clears displayed press counts. Recorded timing is nominal.\n')
    manifest=dict(status='experimental',build_id=args.build_id,mode=20,
                  git_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
                  source_dirty=bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain'])),
                  font_data_sha256=hashlib.sha256(font).hexdigest(),
                  compiler_sha256=hashlib.sha256((args.toolchain_bin/'ez80-none-elf-clang').resolve().read_bytes()).hexdigest(),
                  width=512,height=384,colours=64,live_input=True,live_input_hardware_tested=False,replay_records=count,
                  replay_duration_ms=duration,render_rate_hz=20,
                  capture_sha256=hashlib.sha256(args.capture.read_bytes()).hexdigest(),
                  files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in package.iterdir()},
                  inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                          (HERE/'main.cpp',HERE/'live.hpp',HERE/'view.hpp',HERE/'native.cpp',HERE/'build.py',HERE/'identity.json',
                           HERE.parent/'scroll/mode_lifecycle.hpp',HERE/'mos_io.asm',wire)},
                  emos_api_sha256=hashlib.sha256((args.emos_source/'src/mos_api.inc').read_bytes()).hexdigest())
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(output)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--build-id',default='UNVERSIONED-DO-NOT-DEPLOY')
    parser.add_argument('--capture',type=Path,required=True)
    parser.add_argument('--toolchain-bin',type=Path,required=True)
    parser.add_argument('--emos-source',type=Path,default=ROOT.parent/'agon-emos')
    build(parser.parse_args())
