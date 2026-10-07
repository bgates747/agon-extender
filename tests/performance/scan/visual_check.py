#!/usr/bin/env python3
"""Off-bench native VDP check, reusing console_peer.NativeVdp outside timing.
Checks partial scrolling, one-line clipping and stationary sidebar integrity.
Does not establish moving-image flicker, mainboard scanout or hardware speed.
"""
import argparse,json,sys,time,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from console_peer import NativeVdp
from build import agnb,frame,TILES

p=argparse.ArgumentParser();p.add_argument('--vdp',type=Path,required=True);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
v=NativeVdp(a.vdp)
stop=False
def ticks():
    while not stop:
        v.lib.signal_vblank();time.sleep(1/60)
threading.Thread(target=ticks,daemon=True).start()
def wait():
    v.receive();v.send(bytes([23,0,0x84,0,0,0,0]));end=time.monotonic()+5;reply=b''
    while time.monotonic()<end:
        reply+=v.receive()
        if b'\x84\x04' in reply:return
        time.sleep(.002)
    raise RuntimeError('pixel fence timeout: '+reply.hex())
def image():
    v.scanout();assert (v.width.value,v.height.value)==(512,384)
    return bytes(v.frame)[:512*384*3]
def rgb(value):return bytes([(value&3)*85,((value>>2)&3)*85,((value>>4)&3)*85])
def strip_pixels(b,x0,x1,y0,y1):
    return b''.join(b[(y*512+x0)*3:(y*512+x1)*3] for y in range(y0,y1))
try:
    v.send(bytes([23,0,128,1]));time.sleep(.3)
    # Host preflight owns mode, just as autoexec does for the eZ80 fixtures.
    v.send(bytes([22,20]));time.sleep(.3);wait()
    records=agnb(a.bundle/'sdcard/test/nurples/scan-r01/game.agnb')
    results=[]
    for case in (3,7,8):
        base=a.bundle/f'sdcard/extender/scan-r01/t{case:02}'
        v.send((base/'setup.bin').read_bytes());wait()
        before=image();side=None
        for u in range(32):
            v.send(frame(case,u));wait();after=image()
            sides=strip_pixels(after,0,128,48,384)+strip_pixels(after,384,512,48,384)
            if side is None:side=sides
            assert side==sides,('sidebar changed',case,u)
            if case==3:
                assert strip_pixels(after,128,384,49,384)==strip_pixels(before,128,384,48,383),('scroll mismatch',u)
                expected=bytearray()
                for x in range(256):
                    value=records[512+TILES[(x//16+u//16)%16]][2][(15-u%16)*16+x%16]
                    if not value>>6:value=records[1024][2][(255-u%256)*256+x]
                    expected+=rgb(value)
                assert strip_pixels(after,128,384,48,49)==expected,('incoming clipped row mismatch',u)
            before=after
        v.capture(a.output/f't{case:02}.png');results.append({'case':case,'updates':32,'sidebars_unchanged':True,'pixel_scroll_and_incoming_row':case==3})
    (a.output/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results),flush=True)
finally:
    stop=True;v.lib.vdp_shutdown()
