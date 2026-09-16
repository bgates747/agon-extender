"""Independent public pixel-query check; run only after the image controller ends.

The private common adapter owns endpoints/admission. No capture opcode is used.
Ordinary pixel queries return RGB through MOS, then the fixture writes an SD
record. This cross-checks the scanout decoder against a different acquisition path.
"""
from common import *
import struct

out=R/'queries01';out.mkdir(exist_ok=False)
c=SD(URL,out/'stage.json')
try:
 c.connect();c.upload('/test/qual004/q4probe.bin',Path('docs/tasks/QUAL-004/probe/bin/q4probe.bin').read_bytes(),True);c.rpc(11)
finally:c.lock.close()
results=[]
for route in ('LEGACY','EXCOM'):
 cli('queries-'+route, 'EMOS '+route+' --keep-display',
     'LOAD /test/qual004/q4draw.bin','RUN . /test/qual004/CAL.vdu')
 time.sleep(3)
 k=KB(URL,out/(route+'-escape.json'))
 try:
  st=k.status();k.open(st);k.send([(41,1),(41,0)])
  Path('agents/video-throughput/cli-latest.json').write_text(json.dumps(k.cancel()))
 finally:k.lock.close()
 time.sleep(1)
 cli('probe-'+route, 'LOAD /test/qual004/q4probe.bin','RUN',
     'EMOS LEGACY --keep-display','LOAD /extender/sdserve.bin','RUN . /')
 c=SD(URL,out/(route+'-sd.json'))
 try:
  c.connect();raw=c.download('/test/qual004/probe.bin')
  (out/(route+'.bin')).write_bytes(raw)
  assert len(raw)==48 and raw[:8]==b'Q4PR\1\5\0\0'
  expected=[(80,40,(170,0,0)),(144,40,(0,170,0)),
            (208,40,(0,0,170)),(336,40,(255,255,255)),(16,200,(0,0,0))]
  rows=[]
  for i,(x,y,rgb) in enumerate(expected):
   xx,yy,status,r,g,b=struct.unpack('<HHBBBB',raw[8+i*8:16+i*8])
   rows.append(dict(x=xx,y=yy,status=status,rgb=[r,g,b],expected=list(rgb),
                    match=(xx,yy)==(x,y) and status==0 and (r,g,b)==rgb))
  results.append(dict(route=route,queries=rows,match=all(r['match'] for r in rows)))
  (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
  if route=='LEGACY':c.rpc(11)
 finally:c.lock.close()
print(json.dumps(results),flush=True)
