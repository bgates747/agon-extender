"""Linux serial command client; do not toggle P4 USB modem-control lines.
The ESP USB Serial/JTAG controller interprets DTR/RTS edges as reset requests.
pyserial's open-time updates caused resets on this Pi; use raw termios instead
and disable HUPCL. A command is complete only after its own echo and prompt.
"""
import argparse
import os
import re
from pathlib import Path
import select
import termios
import time
import tty

p=argparse.ArgumentParser()
p.add_argument('--port',required=True)
p.add_argument('--log',type=Path)
p.add_argument('--timeout',type=float,default=15)
p.add_argument('command')
a=p.parse_args()
if '\n' in a.command or '\r' in a.command or not 0<len(a.command)<=120:
    p.error('Expected one command, 1..120 characters')
if not 0<a.timeout<=60:p.error('Timeout must be 0..60 seconds')
fd=os.open(a.port,os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)
output=bytearray();success=False
try:
    termios.tcflush(fd,termios.TCIFLUSH)
    tty.setraw(fd,termios.TCSANOW)
    cfg=termios.tcgetattr(fd)
    cfg[2]=(cfg[2]|termios.CLOCAL|termios.CREAD)&~termios.HUPCL
    cfg[4]=cfg[5]=termios.B115200
    termios.tcsetattr(fd,termios.TCSANOW,cfg)
    os.write(fd,(a.command+'\n').encode('ascii'))
    end=time.monotonic()+a.timeout
    while time.monotonic()<end:
        if select.select([fd],[],[],.1)[0]:
            chunk=os.read(fd,8192)
            if not chunk:break
            output.extend(chunk)
        # A partial command ending in our command (e.g. "old info") must not
        # satisfy the echo check. Accept only the complete line after a prompt
        # or at the start of the capture. Command errors are failures too.
        echo=rb'(?:^|p4pc> )'+re.escape(a.command.encode())+rb'\r\n'
        match=re.search(echo,output)
        if match and output.endswith(b'p4pc> '):
            if re.search(rb'(?:^|\r?\n)ERR\b',output[match.end():]):break
            success=True;break
finally:
    os.close(fd)
if a.log:a.log.write_bytes(output)
print(output.decode(errors='replace'),end='')
if not success:raise SystemExit('No completion for this command; a startup prompt alone is not success')
