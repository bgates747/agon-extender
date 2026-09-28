#!/usr/bin/env python3
"""Generate VDU stream for mode 0 (640x480), selected by autoexec, never here."""
import struct
from pathlib import Path
v=bytearray([20,17,128,17,7,12,23,1,0,23,0,192,0,26])
colors=[(0,0,0),(255,0,0),(0,255,0),(0,0,255),(0,255,255),(255,0,255),(255,255,0),(255,255,255)]
for i,rgb in enumerate(colors):v.extend([19,i,255,*rgb])
def plot(n,x,y):v.extend(bytes([25,n])+struct.pack('<HH',x,y))
def rect(c,x,y,x2,y2):v.extend([18,0,c]);plot(4,x,y);plot(101,x2,y2)
def text(x,y,s,fg=7,bg=0):v.extend([17,fg,17,128+bg,31,x,y]);v.extend(s.encode('ascii'))
text(2,2,'LCD color bars r01 - ribbon at left')
text(2,3,'Top edge WHITE / bottom edge MAGENTA / Esc exits')
names=['BLACK','RED','GREEN','BLUE','CYAN','MAGENTA','YELLOW','WHITE']
for i,name in enumerate(names):
 rect(i,i*80,112,i*80+79,359);text(i*10+1,6,name)
text(2,24,'Expected pure primaries above; labels name the intended color.')
text(2,26,'Left border RED; right border BLUE. No white at bottom.')
text(2,27,'Top-left W / top-right Y; bottom-left C / bottom-right M.')
rect(1,0,1,0,478);rect(3,639,1,639,478)
rect(7,0,0,639,0);rect(5,0,479,639,479)
rect(7,1,8,16,23);rect(6,623,8,638,23)
rect(4,1,456,16,471);rect(5,623,456,638,471)
Path(__file__).with_name('bars.vdu').write_bytes(v)
