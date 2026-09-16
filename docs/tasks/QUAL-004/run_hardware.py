"""Run from repository root with a private common module on PYTHONPATH.
That module owns endpoint credentials, keyboard admission, and the state root.
No network identity is embedded in this tracked procedure.
"""
from common import *
import hashlib,struct
sys.path.insert(0,'docs/tasks/QUAL-004')
from capture import decode
from compare import evf,compare
from web_capture import capture
out=R/'runs01';out.mkdir(exist_ok=False)
cases=json.loads((R/'cases01/manifest.json').read_text())['cases']+json.loads((R/'shapes01/manifest.json').read_text())['cases']
def escape(name):
 k=KB(URL,R/(name+'-key.json'))
 try:
  st=k.status();k.open(st);k.send([(41,1),(41,0)]);Path('agents/video-throughput/cli-latest.json').write_text(json.dumps(k.cancel()))
 finally:k.lock.close()
def get_images(token,start):
 deadline=time.monotonic()+100
 while time.monotonic()<deadline:
  raw=(R/'serial.bin').read_bytes()[start:]
  if any(f'Q4END {token} {status}\n'.encode() in raw for status in (0,1)):
   found=decode(raw);assert len(found)==1 and found[0]['token']==token
   return found[0],raw
  time.sleep(.5)
 raise TimeoutError('No completed mainboard capture '+str(token))
# Do not run until queued deployment and startup are complete.
c=SD(URL,R/'run-start-sd.json')
try:c.connect();assert c.download('/autoexec.txt')==(R/'test-autoexec.txt').read_bytes();c.rpc(11)
finally:c.lock.close()
results=[]
for index,case in enumerate(cases):
 if time.time()>1789585860: # reserve final hour before eight-hour task deadline
  raise RuntimeError('Restoration reserve reached')
 name=case['name'];dest=out/name;dest.mkdir();record={'case':case,'start':time.time(),'status':'running'}
 (dest/'run.json').write_text(json.dumps(record,indent=2))
 print('BEGIN',index,name,flush=True)
 images=[]
 for repeat in range(2):
  token=100+index*2+repeat;offset=(R/'serial.bin').stat().st_size
  cli(f'{name}-m{repeat}','EMOS LEGACY --keep-display','LOAD /test/qual004/q4draw.bin',f'RUN . /test/qual004/{case["file"]} {token}')
  image,raw=get_images(token,offset);images.append(image);(dest/f'mainboard-{repeat}.serial').write_bytes(raw)
  escape(f'{name}-m{repeat}');time.sleep(1)
 assert images[0]['pixels']==images[1]['pixels'],'Mainboard static-scene repeat mismatch'
 cli(name+'-p','EMOS EXCOM --keep-display','LOAD /test/qual004/q4draw.bin',f'RUN . /test/qual004/{case["file"]}')
 time.sleep(3)
 capture(URL,dest/'web',4)
 web=[evf(p.read_bytes()) for p in sorted((dest/'web').glob('*.evf'))]
 assert web[-1]['pixels']==web[-2]['pixels'],'P4 static-scene repeat mismatch'
 assert web[-1]['sequence']!=web[-2]['sequence'],'No fresh P4 generation'
 result=compare(images[0],web[-1],dest/'images')
 record.update(status='pass' if result['match'] else 'mismatch',comparison=result,end=time.time(),mainboard_repeat_equal=True,p4_repeat_equal=True)
 (dest/'run.json').write_text(json.dumps(record,indent=2));results.append(record);(out/'results.json').write_text(json.dumps(results,indent=2))
 escape(name+'-p');time.sleep(1)
 print('END',name,record['status'],result['mismatches'],flush=True)
 # Mismatches are retained and enumerated, not repaired or silently waived.
cli('suite-finish','EMOS LEGACY --keep-display','LOAD /extender/sdserve.bin','RUN . /')
(out/'complete.json').write_text(json.dumps({'cases':len(results),'end':time.time()}))
