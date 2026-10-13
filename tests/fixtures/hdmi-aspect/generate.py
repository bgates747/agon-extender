#!/usr/bin/env python3
"""Mode-3 physical-aspect review through ordinary MOS VDU commands.

Startup selects the mode. This batch draws and returns to a Legacy listener;
it invokes no application and changes no logical mode or SD file.
"""
import argparse
from pathlib import Path
import re
import struct


def pattern(build_id,firmware_id):
    if not re.fullmatch(r'hdmi-aspect-r01-b\d{4}(?:-\d{2}){5}Z',build_id):
        raise ValueError('Expected full hdmi-aspect-r01 build identity')
    if not re.fullmatch(r'[A-Za-z0-9-]{1,68}',firmware_id):
        raise ValueError('Expected printable firmware build identity')
    data=bytearray([23,27,7,0,23,1,0,23,0,149,0,255,255,0,20,26,23,0,192,0,
                    29,0,0,0,0,19,1,48,0,0,0,19,2,12,0,0,0,19,4,3,0,0,0,
                    19,7,63,0,0,0,17,128,17,7,12])
    def plot(op,x,y):
        if not (0<=x<640 and 0<=y<240):raise ValueError('Outside mode3')
        data.extend(bytes([25,op])+struct.pack('<HH',x,y))
    def line(color,x,y,x2,y2):
        data.extend([18,0,color]);plot(4,x,y);plot(5,x2,y2)
    def text(x,y,value):
        if x+len(value)>80 or not 0<=y<30:raise ValueError('Text outside mode3')
        data.extend([17,7,17,128,31,x,y]);data.extend(value.encode('ascii'))
    text(2,2,'Visual validation - mode 3 aspect')
    text(2,3,build_id)
    text(2,4,firmware_id)
    text(2,6,'White box should look square. All four outer edges should be visible.')
    text(2,8,'Logical image 640x240; expected presentation 640x480, centered.')
    for a,b in [((272,104),(367,104)),((367,104),(367,151)),
                ((367,151),(272,151)),((272,151),(272,104))]:line(7,*a,*b)
    text(48,14,'96x48 logical pixels')
    text(48,16,'96x96 output pixels')
    for row,color in ((180,1),(184,2),(188,4)):
        line(color,128,row,511,row)
    text(2,25,'Each colored line should occupy two physical output rows.')
    text(2,27,'Review only - no benchmark or performance result.')
    for a,b in [((0,0),(639,0)),((639,0),(639,239)),
                ((639,239),(0,239)),((0,239),(0,0))]:line(7,*a,*b)
    data.extend([23,0,195])
    return bytes(data)


def commands(build_id,firmware_id):
    data=pattern(build_id,firmware_id)
    lines=['EMOS EXCOM --keep-display']
    for offset in range(0,len(data),16):
        lines.append('VDU '+' '.join(map(str,data[offset:offset+16])))
    lines+=['EMOS LEGACY --keep-display','EMOS sdserve --fast /']
    return ('\r\n'.join(lines)+'\r\n').encode('ascii')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-id',required=True);p.add_argument('--firmware-id',required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    with a.output.open('xb') as f:f.write(commands(a.build_id,a.firmware_id))
