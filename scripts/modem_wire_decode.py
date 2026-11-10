"""Decode packed sigrok binary UART samples; no device or credential access.

Binary output preserves physical D0,D3 at bits 0,3, one byte per sample.
The retained real capture was decoded against its known AT replies to verify this. Decode
8N1 at the selected nominal baud. Framing errors and incomplete tails invalidate
whole-stream conclusions; preserve them rather than silently dropping errors.
"""
import argparse,json,mmap
from pathlib import Path

def decode(samples,bit,rate,baud):
 import numpy as np
 period=rate/baud;end=len(samples);last=0;next_start=0;out=bytearray();positions=[];errors=[]
 for base in range(0,end,1048576):
  block=np.frombuffer(samples,dtype=np.uint8,count=min(1048576,end-base),offset=base)
  levels=(block>>bit)&1
  edges=np.flatnonzero((levels[:-1]==1)&(levels[1:]==0))+base+1
  if len(levels) and last==1 and levels[0]==0:edges=np.concatenate(([base],edges))
  if len(levels):last=int(levels[-1])
  for edge in edges:
   edge=int(edge)
   if edge<next_start:continue
   if edge+9.5*period>=end:
    errors.append({'sample':edge,'error':'incomplete_tail'});continue
   if (samples[int(edge+.5*period)]>>bit)&1:continue
   value=sum(((samples[int(edge+(1.5+i)*period)]>>bit)&1)<<i for i in range(8))
   if not (samples[int(edge+9.5*period)]>>bit)&1:errors.append({'sample':edge,'error':'stop_bit'})
   out.append(value);positions.append(edge);next_start=edge+9.75*period
 return bytes(out),positions,errors

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw',type=Path);p.add_argument('--rate',type=int,default=24000000);p.add_argument('--baud',type=int,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=False)
 with a.raw.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
  result={}
  for bit,name in [(0,'p4-tx'),(3,'esp-tx')]:
   wire,pos,errors=decode(data,bit,a.rate,a.baud);(a.out/(name+'.bin')).write_bytes(wire);result[name]={'bytes':len(wire),'first_sample':pos[0] if pos else None,'last_sample':pos[-1] if pos else None,'framing_errors':errors}
 (a.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
