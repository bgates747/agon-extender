#!/usr/bin/env python3
"""Generate deterministic VDU stream; mode belongs to autoexec, not the program."""
import struct
from pathlib import Path
import sys
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
b=bytearray()
def v(*x):b.extend(x)
def word(x):b.extend(struct.pack('<H',x))
def text(x,y,s):v(31,x,y);b.extend(s.encode('ascii'))
def flag(n):v(23,0,248);word(0x10f1);word(n)
def plot(k,x,y):v(25,k);word(x);word(y)
v(12,23,1,0,23,0,192,0,4,17,15,17,128)
text(3,2,'Transparent text - rainbow review')
text(3,4,'Visual validation - screenshot requested')
for i,rgb in enumerate([(255,0,0),(255,170,0),(255,255,0),(0,255,0),(0,255,255),(0,0,255),(170,0,255),(255,0,255)]):
 c=i+1;v(19,c,255,*rgb)
 v(18,0,c);plot(4,i*80,72);plot(101,i*80+79,351)
flag(0);text(4,12,'Opaque text: the background is painted black')
text(4,14,'The quick brown fox jumps over the lazy dog. 0123456789')
flag(1);text(4,23,'Transparent text: the rainbow stays visible')
text(4,25,'The quick brown fox jumps over the lazy dog. 0123456789')
text(4,32,'Spaces leave the stripes untouched too.')
flag(0);text(3,48,'Both examples use ordinary text-cursor printing (VDU 4).')
text(3,50,'Only the background-painting flag differs.')
text(3,53,'Press any key to return to MOS; opaque text is restored.')
(out/'rainbow.vdu').write_bytes(b)
# Native parser coalesces text inconsistently across emulator UART scheduling.
# A stock buffered command submits this visual sequence as one VDP workload.
(out/'buffered.vdu').write_bytes(bytes([23,0,160,0,125,2,23,0,160,0,125,0])+struct.pack('<H',len(b))+b+bytes([23,0,160,0,125,1]))
(out/'demo.asm').write_text('''    assume adl=1
    org 0x040000
    jp start
    align 64
    db "MOS",0,1
start:
    push ix
    push iy
    ld hl,commands
    ld bc,commands_end-commands
    rst.lil 0x18
    xor a
    rst.lil 0x08
    ld hl,finish
    ld bc,finish_end-finish
    rst.lil 0x18
    pop iy
    pop ix
    ld hl,0
    ret
commands:
    incbin "buffered.vdu"
commands_end:
finish:
    db 23,0,248,241,16,0,0,23,1,1,31,0,56,13,10
finish_end:
''')
