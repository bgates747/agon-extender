"""Find declared command boundaries; never scan opaque bitmap bytes for opcodes."""
from pathlib import Path
import argparse,hashlib,json,sys
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[2]
sys.path.insert(0,str(ROOT/'docs/tasks/QUAL-003/timing/scripts'))
from vdu_framer import Framer
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('inputs',nargs='+',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
rows=[]
for folder in a.inputs:
 for case in json.loads((folder/'manifest.json').read_text())['cases']:
  f=folder/case['file'];raw=f.read_bytes();assert hashlib.sha256(raw).hexdigest()==case['sha256']
  offsets=[];pos=0
  if case['name']!='FONT01':
   parser=Framer();commands=parser.feed(raw);assert not parser.pending
   assert b''.join(commands)==raw
   for command in commands:
    if len(command)==6 and command[:3]==b'\x17\0\xa0' and command[5]==2:offsets.append(pos)
    pos+=len(command)
  # FONT01 already has explicit query fences before mutable font changes.
  data=b'Q4B1'+len(raw).to_bytes(3,'little')+len(offsets).to_bytes(2,'little')+b''.join(x.to_bytes(3,'little') for x in offsets)
  (a.output/(case['file']+'.bar')).write_bytes(data)
  rows.append(dict(case=case['name'],scene_sha256=case['sha256'],barrier_offsets=offsets,sha256=hashlib.sha256(data).hexdigest()))
(a.output/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n');print(len(rows),'sidecars')
