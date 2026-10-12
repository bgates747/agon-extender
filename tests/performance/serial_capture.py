#!/usr/bin/env python3
"""Bounded programming-console capture; caller owns device identity and reset policy.

Uses the maintained joined-DTR/RTS opener. Qualify the selected USB device before
application admission; this is not a universal no-reset guarantee. Never
open this reader during a measurement, flash, or another reader's ownership.
"""
import argparse,signal,time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"scripts"))
from passive_serial import open_passive_serial
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=int,default=1800);a=p.parse_args()
if not 1<=a.seconds<=7200:p.error('duration must be 1..7200 seconds')
stop=False
def done(*_):
 global stop
 stop=True
signal.signal(signal.SIGTERM,done);signal.signal(signal.SIGINT,done)
with a.output.open('xb') as f:
 s=open_passive_serial(a.port,timeout=.25);print('Console capture opened',flush=True)
 try:
  end=time.monotonic()+a.seconds
  while not stop and time.monotonic()<end:
   b=s.read(4096)
   if b:f.write(b);f.flush()
 finally:s.close()
print('Console capture closed',flush=True)
