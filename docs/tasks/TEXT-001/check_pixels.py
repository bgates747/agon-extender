#!/usr/bin/env python3
"""Actual native VDP pixel test; no hardware performance claim."""
import sys,time,os,json
from pathlib import Path
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'scripts'))
from console_peer import NativeVdp
from PIL import Image
n=NativeVdp(Path(sys.argv[1]).resolve());out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
def pump():
 for _ in range(35):n.lib.signal_vblank();n.scanout();n.receive();time.sleep(.01)
def send(b):n.send(b);pump()
def pixels():
 n.scanout();return Image.frombytes('RGB',(n.width.value,n.height.value),bytes(n.frame)[:n.width.value*n.height.value*3])
def flag(v):return bytes([23,0,248,241,16,v,0])
time.sleep(.15);send(bytes([23,0,128,1]));send(bytes([22,0,23,1,0,12,17,15,17,128]))
# Cell (10,10), 8x8 system font. First derive mask from opaque white on black.
send(bytes([31,10,10])+b'A');opaque=pixels().crop((80,80,88,88));mask=[p!=(0,0,0) for p in opaque.getdata()];assert any(mask) and not all(mask)
# Blue full-screen background, then transparent glyph; only mask pixels may change.
send(bytes([17,132,12,17,128]));bg=pixels().crop((80,80,88,88));send(flag(1)+bytes([31,10,10])+b'A');actual=pixels().crop((80,80,88,88))
expected=[a if bit else b for a,b,bit in zip(opaque.getdata(),bg.getdata(),mask)]
assert list(actual.getdata())==expected,'transparent glyph pixels differ'
send(bytes([31,10,10])+b' ');assert list(pixels().crop((80,80,88,88)).getdata())==expected,'space erases'
send(flag(0)+bytes([31,10,10])+b'A');assert list(pixels().crop((80,80,88,88)).getdata())==list(opaque.getdata()),'opaque restore'
# VDU4 must retain flag; save/restore context must restore it.
send(flag(1)+bytes([5,4,23,0,200,3])+flag(0)+bytes([23,0,200,4,17,132,12,17,128,31,10,10])+b'A')
assert list(pixels().crop((80,80,88,88)).getdata())==expected,'context/cursor restoration'
send(bytes([31,11,10,127]));assert all(p==(0,0,0) for p in pixels().crop((80,80,88,88)).getdata()),'delete should erase'
send(flag(1)+bytes([23,0,200,2,0,17,132,12,17,128,31,10,10])+b'A')
assert list(pixels().crop((80,80,88,88)).getdata())==list(opaque.getdata()),'context reset should restore opaque'
send((root/'agents/text-001/demo/rainbow.vdu').read_bytes());pixels().save(out/'rainbow.png')
(out/'results.json').write_text(json.dumps({'pass':True,'checks':['transparent glyph exact pixels','transparent spaces','opaque restore','VDU4/5 and context push/pop','delete erase','context reset'],'scope':'native VDP only'},indent=2))
print('PASS: native transparent-text pixels and state transitions',flush=True);os._exit(0)
