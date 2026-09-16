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
import argparse
p=argparse.ArgumentParser();p.add_argument('--output',default='runs01');p.add_argument('--cases');p.add_argument('--token-base',type=int,default=100)
p.add_argument('--manifest',type=Path);p.add_argument('--startup',type=Path);p.add_argument('--serial',type=Path);args=p.parse_args()
out=R/args.output;out.mkdir(exist_ok=False)
original_cli=cli
def cli(name,*commands):return original_cli(out.name+'-'+name,*commands)
cases=json.loads((R/'cases01/manifest.json').read_text())['cases']+json.loads((R/'shapes01/manifest.json').read_text())['cases']
if args.manifest:cases=json.loads(args.manifest.read_text())['cases']
serial_path=args.serial or R/'serial.bin'
if args.cases:
 selected=args.cases.split(',');lookup={c['name']:c for c in cases};cases=[lookup[n] for n in selected]
assert 0<args.token_base<65535-len(cases)*2
def escape(name):
 k=KB(URL,out/(name+'-key.json'))
 try:
  st=k.status();k.open(st);k.send([(41,1),(41,0)]);Path('agents/video-throughput/cli-latest.json').write_text(json.dumps(k.cancel()))
 finally:k.lock.close()
def get_images(token,start):
 deadline=time.monotonic()+100
 while time.monotonic()<deadline:
  raw=serial_path.read_bytes()[start:]
  if any(f'Q4END {token} {status}\n'.encode() in raw for status in (0,1)):
   found=decode(raw);assert len(found)==1 and found[0]['token']==token
   return found[0],raw
  time.sleep(.5)
 raise TimeoutError('No completed mainboard capture '+str(token))
# Do not run until queued deployment and startup are complete.
c=SD(URL,out/'start-sd.json')
try:c.connect();assert c.download('/autoexec.txt')==(args.startup or R/'test-autoexec.txt').read_bytes();c.rpc(11)
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
  token=args.token_base+index*2+repeat;offset=serial_path.stat().st_size
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
