"""Reuse the existing font command/oracle case as an ordinary binary VDU scene."""
from pathlib import Path
import argparse,hashlib,json,runpy,struct
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--target',type=Path,required=True);a=p.parse_args()
module=runpy.run_path(str(ROOT/'docs/tasks/PORT-008/font-coverage/make_case.py'));module['make_case'](a.output)
data=bytearray()
for line in (a.output/'fonts.txt').read_text().splitlines():
 if not line.startswith('VDU '):continue
 for token in line.split()[1:]:
  if token.endswith(';'):data+=struct.pack('<H',int(token[:-1])&65535)
  else:data.append(int(token))
name='FONT01';(a.target/(name+'.vdu')).write_bytes(data)
p=a.target/'manifest.json';m=json.loads(p.read_text());assert not any(c['name']==name for c in m['cases'])
m['cases'].append(dict(name=name,file=name+'.vdu',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),source='PORT-008 font-coverage',adaptation='binary VDU transport; mode20 instead of8, same8x8 pixel geometry; omit ECHO'))
p.write_text(json.dumps(m,indent=2)+'\n')
