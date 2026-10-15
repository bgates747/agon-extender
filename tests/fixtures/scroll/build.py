#!/usr/bin/env python3
"""Build a stopped scrolling fixture; never connects to or invokes hardware."""
import argparse
import ctypes
import ctypes.util
from datetime import datetime, timezone
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
from PIL import Image, ImageDraw
from geometry import cases

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def raster(svg, width, height, target):
    rsvg = ctypes.CDLL(ctypes.util.find_library('rsvg-2'))
    cairo = ctypes.CDLL(ctypes.util.find_library('cairo'))
    gobj = ctypes.CDLL(ctypes.util.find_library('gobject-2.0'))
    rsvg.rsvg_handle_new_from_data.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_void_p]
    rsvg.rsvg_handle_new_from_data.restype = ctypes.c_void_p
    rsvg.rsvg_handle_render_cairo.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    rsvg.rsvg_handle_render_cairo.restype = ctypes.c_int
    cairo.cairo_image_surface_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    cairo.cairo_image_surface_create.restype = ctypes.c_void_p
    cairo.cairo_create.argtypes = [ctypes.c_void_p]
    cairo.cairo_create.restype = ctypes.c_void_p
    cairo.cairo_surface_write_to_png.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    cairo.cairo_destroy.argtypes = [ctypes.c_void_p]
    cairo.cairo_surface_destroy.argtypes = [ctypes.c_void_p]
    gobj.g_object_unref.argtypes = [ctypes.c_void_p]
    raw = svg.encode()
    handle = rsvg.rsvg_handle_new_from_data(raw, len(raw), None)
    if not handle:
        raise RuntimeError('Cannot parse pattern SVG')
    surface = cairo.cairo_image_surface_create(0, width, height)
    ctx = cairo.cairo_create(surface)
    try:
        if not rsvg.rsvg_handle_render_cairo(handle, ctx):
            raise RuntimeError('Cannot render pattern SVG')
        if cairo.cairo_surface_write_to_png(surface, os.fsencode(target)):
            raise RuntimeError('Cannot save rendered pattern')
    finally:
        cairo.cairo_destroy(ctx)
        cairo.cairo_surface_destroy(surface)
        gobj.g_object_unref(handle)


def build(args):
    rows = cases(args.width, args.height, args.margin)
    config = shutil.which('agondev-config')
    tools = args.toolchain_bin or (Path(config).parent if config else None)
    if tools is None or not (tools/'agondev-config').is_file():
        raise ValueError('Supply --toolchain-bin or put agondev-config on PATH')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    package = out/'package'
    package.mkdir()
    source = (ROOT/'tests/fixtures/display-pattern/pattern-wide.svg').read_text()
    spec = importlib.util.spec_from_file_location('pattern_palette', HERE.parent/'mode-preview/palette.py')
    palettes = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(palettes)
    palette = palettes.default_palette(ROOT, args.colours)
    # Exact native 3x5 digits preserve nominal legibility at 240p.
    glyphs = ('111101101101111','010110010010111','111001111100111',
              '111001111001111','101101111001001','111100111001111',
              '111100111101111','111001001001001','111101111101111','111101111001111')
    for id, (name, direction, partial, region) in enumerate(rows):
        svg = source.replace('width="1920" height="1080" viewBox="0 0 1024 576"',
            f'width="{args.width}" height="{args.height}" viewBox="128 0 768 576" preserveAspectRatio="none"')
        svg = svg.replace('MODE 20  /  512 × 384  /  INDEXED',
            f'MODE {args.mode} / {args.width} × {args.height} / {args.colours} COLOURS')
        svg = svg.replace('STATIC PATTERN · RGB SOURCE',
            html.escape(name.upper()+' · WRAP · 1 PX/VBLANK'))
        svg = re.sub(r'<text[^>]*font-size="14"[^>]*>\d{2}</text>', '', svg)
        png = out/f'c{id:02d}.png'
        raster(svg, args.width, args.height, png)
        image = Image.open(png).convert('RGB')
        draw = ImageDraw.Draw(image)
        scale = max(1, round(args.height/240))
        for i in range(64):
            x0, x1 = (round((i%32)*args.width/32), round((i%32+1)*args.width/32))
            y0, y1 = (round((528+i//32*24)*args.height/576),
                      round((552+i//32*24)*args.height/576))
            rgb = (((i>>4)&3)*85, ((i>>2)&3)*85, (i&3)*85)
            draw.rectangle((x0+1,y0+1,x1-2,y1-2), fill=rgb)
            ink = 'black' if sum(a*b for a,b in zip(rgb,(.2126,.7152,.0722)))>135 else 'white'
            gx, gy = (x0+x1-7*scale)//2, (y0+y1-5*scale)//2
            for n, ch in enumerate(f'{i:02d}'):
                for k, bit in enumerate(glyphs[int(ch)]):
                    if bit=='1':
                        x,y = gx+(n*4+k%3)*scale,gy+k//3*scale
                        draw.rectangle((x,y,x+scale-1,y+scale-1),fill=ink)
        image = palettes.quantize(image, palette)
        image.save(png)
        pixels = bytes(0xc0 | (r//85) | ((g//85)<<2) | ((b//85)<<4)
                       for r,g,b in image.get_flattened_data())
        # No VDU22. Mode and route are established before explicit invocation.
        data = bytearray([23,1,0,26,23,0,192,0,29,0,0,0,0,18,0,15%args.colours])
        data += bytes([23,0,160])+struct.pack('<H',64000)+bytes([2])
        for pos in range(0,len(pixels),4096):
            block = pixels[pos:pos+4096]
            data += bytes([23,0,160])+struct.pack('<H',64000)+bytes([0])+struct.pack('<H',len(block))+block
        data += bytes([23,0,160])+struct.pack('<H',64000)+bytes([14])
        data += bytes([23,27,32])+struct.pack('<H',64000)
        data += bytes([23,27,33])+struct.pack('<HHB',args.width,args.height,1)
        data += bytes([25,0xED,0,0,0,0])
        (package/f'c{id:02d}.vdu').write_bytes(data)
    work = out/'application'
    (work/'src').mkdir(parents=True)
    shutil.copy2(HERE/'main.cpp',work/'src/main.cpp')
    shutil.copy2(HERE/'selection.hpp',work/'src/selection.hpp')
    shutil.copy2(HERE/'mode_lifecycle.hpp',work/'src/mode_lifecycle.hpp')
    shutil.copy2(ROOT/'tests/performance/ez80/entries.asm',work/'src/entries.asm')
    # AgonDev LLVM15 cannot lower SJLJ exception contexts emitted by RAII.
    # This finite appliance uses ordinary return cleanup, not C++ exceptions;
    # remove the explicit exception restriction only with a qualified backend.
    (work/'Makefile').write_text('NAME=scroll\nLDHAS_ARG_PROCESSING=0\nLDHAS_EXIT_HANDLER=0\ninclude $(shell agondev-config --makefile)\nCXXFLAGS += -std=c++17 -fno-exceptions -fno-rtti\n')
    env = dict(os.environ, PATH=str(tools.resolve())+os.pathsep+os.environ.get('PATH',''))
    subprocess.run(['make','-C',str(work)],env=env,check=True)
    shutil.copy2(work/'bin/scroll.bin',package/'scroll.bin')
    (package/'scroll.cfg').write_text(f'{args.width} {args.height} {args.margin} {args.steps} {args.mode} {args.colours} {args.instrument} {args.result}\n')
    for selector in ['all']+[name for name,_,_,_ in rows]:
        command=f'CD /extender/scroll-r01\r\nLOAD scroll.bin\r\nRUN &040000 {selector}\r\n'
        (package/('run.txt' if selector=='all' else selector+'.txt')).write_text(command)
    manifest = dict(fixture='pattern-scroll-r03',
                    build_id=datetime.now(timezone.utc).strftime('pattern-scroll-r03-b%Y-%m-%d-%H-%M-%SZ'),
                    status='draft',mode=args.mode,
                    width=args.width,height=args.height,margin=args.margin,steps=args.steps,colours=args.colours,
                    instrument=args.instrument,cases=[dict(name=n,direction=d,partial=p,
                    region=vars(r)) for n,d,p,r in rows],palette=palette,
                    lifecycle=dict(entry_mode_restore=True,settle_mos_ticks=160,
                                   single_buffer_entry_only=True,completion_route='invoking',
                                   startup_unchanged=True),
                    git_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
                    source_dirty=bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain'])),
                    inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (HERE/'build.py',HERE/'main.cpp',HERE/'selection.hpp',HERE/'mode_lifecycle.hpp',HERE/'geometry.py',
                                      ROOT/'tests/fixtures/display-pattern/pattern-wide.svg',
                                      HERE.parent/'mode-preview/palette.py',
                                      ROOT/'tests/performance/ez80/entries.asm')},
                    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in package.iterdir()})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(out)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--toolchain-bin',type=Path)
    p.add_argument('--mode',type=int,default=8)
    p.add_argument('--width',type=int,default=320)
    p.add_argument('--height',type=int,default=240)
    p.add_argument('--colours',type=int,choices=[2,4,16,64],default=64)
    p.add_argument('--margin',type=int,default=32)
    p.add_argument('--steps',type=int,default=600)
    p.add_argument('--instrument',type=int,choices=[0,1],default=1)
    p.add_argument('--result',required=True)
    a=p.parse_args()
    if not 0<=a.mode<128 or not 1<=a.steps<=10000:
        p.error('Single-buffer mode and 1..10000 steps required')
    if not re.fullmatch(r'/agents/extender/results/[A-Za-z0-9_-]{1,48}\.csv',a.result):
        p.error('Result must be a new CSV in /agents/extender/results')
    build(a)
