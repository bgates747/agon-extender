#!/usr/bin/env python3
"""Compare complete strip-composed frames against independent RGBA2222 pixels.

The scaffold compiles the unchanged retained stock function. This checks byte
correctness across DMA strip boundaries; it makes no hardware timing claim.
"""
import ctypes, pathlib, subprocess, tempfile, re, os, hashlib, json
os.chdir(pathlib.Path(__file__).resolve().parents[2])
root=pathlib.Path.cwd(); temporary=tempfile.TemporaryDirectory(prefix='dsi-strip-host-'); out=pathlib.Path(temporary.name)
(out/'esp_attr.h').write_text('#pragma once\n#define IRAM_ATTR\n')
subprocess.run(['g++','-std=c++17','-O2','-shared','-fPIC','-I'+str(out),'-Ivdp/dsi-strip-test/main','vdp/dsi-strip-test/main/stock_sprite_probe.cpp','-o',str(out/'probe.so')],check=True)
lib=ctypes.CDLL(str(out/'probe.so'));lib.stock_probe_compose.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint,ctypes.c_uint]
art=(root/'vdp/dsi-strip-test/main/nurples_art.h').read_text().split('=',1)[1]
values=bytes(map(int,re.findall(r'\d+',art)))
assert len(values)==4*256
assets=[values[i*256:(i+1)*256] for i in range(4)]
provenance=json.loads((root/'vdp/dsi-strip-test/main/source-provenance.json').read_text())
for data, record in zip(assets,provenance['assets']):
 assert hashlib.sha256(data).hexdigest()==record['sha256']
source=(root/provenance['stock_source']).read_text()
a=source.index('void IRAM_ATTR VGAPalettedController::rawDrawSpriteScanline(')
b=source.index('void IRAM_ATTR VGAPalettedController::drawSpriteScanLine(',a)
assert hashlib.sha256(source[a:b].encode()).hexdigest()==provenance['function_sha256']
retained=(root/'vdp/dsi-strip-test/main/stock_sprite_body.inc').read_text()
assert retained[retained.index('void IRAM_ATTR'):]==source[a:b]

records=[]
for frame in [0,599,600,1199,1200,1799,1800,3599]:
 count=[1,8,16,32][min(frame//600,3)]
 original=bytearray(bytes(((x+y)&3)*85 for y in range(480) for x in range(848*3)))
 expected=original.copy()
 for i in range(count):
  sx=168+(frame*2+i*37)%(512-16);sy=48+(frame+i*23)%(384-16)
  for y in range(16):
   for x in range(16):
    p=assets[i%4][y*16+x]
    if p&192:
     at=((sy+y)*848+sx+x)*3
     expected[at:at+3]=bytes((((p>>4)&3)*85,((p>>2)&3)*85,(p&3)*85))
 for blocks in (8,12):
  rows=480//blocks
  actual=(ctypes.c_uint8*len(original)).from_buffer_copy(original)
  for block in range(blocks):lib.stock_probe_compose(ctypes.byref(actual,block*rows*848*3),block*rows,rows,frame)
  assert bytes(actual)==expected,(frame,blocks)
  records.append({'frame':frame,'sprites':count,'blocks':blocks,'all_pixels_match':True})
import json
print(json.dumps({'stock_body_unchanged':True,'all_pixels_match':True,'frames':records},indent=2))
