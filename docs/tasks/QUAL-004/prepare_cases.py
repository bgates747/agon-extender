"""Repackage existing immutable timing corpus, preserving stage dependencies."""
from pathlib import Path
import argparse,hashlib,json,struct
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=False)
base=ROOT/'docs/tasks/QUAL-003/timing/fixture';corpus=json.loads((base/'build/corpus.json').read_text())
selected=json.loads((ROOT/'docs/tasks/QUAL-003/timing/results/framebuffer-first/baseline39-corpus.json').read_text());names={c['name'] for c in selected['cases']}
rows=[];acc=bytearray();group=None
for c in corpus['cases']:
 if c['name'] not in names:continue
 raw=(base/'media'/(c['name']+'.DAT')).read_bytes();assert hashlib.sha256(raw).hexdigest()==c['sha256']
 if c['group']!=group:acc=bytearray();group=c['group']
 acc.extend(raw[:c['setup_bytes']+c['bytes']])
 # Each executable scene replays all preceding stages in its group, independently.
 name=c['name']+'.vdu';(out/name).write_bytes(acc)
 rows.append(dict(name=c['name'],file=name,group=group,bytes=len(acc),sha256=hashlib.sha256(acc).hexdigest(),source=c))
# Calibration: explicit physical coordinates, cursor disabled, clear, RGB blocks.
def word(*xs):return struct.pack('<'+'H'*len(xs),*xs)
data=bytearray([23,0,192,0,23,1,0,26,12])
for i,c in enumerate([0,1,2,4,7,15,63]):
 data+=bytes([18,0,c,25,4])+word(i*64,32)+bytes([25,101])+word(i*64+63,95)
(out/'CAL.vdu').write_bytes(data);rows.insert(0,dict(name='CAL',file='CAL.vdu',group=-1,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
(out/'manifest.json').write_text(json.dumps(dict(cases=rows,scope='39 retained cases plus calibration; independent group replay',missing_api_policy='enumerate only'),indent=2)+'\n')
print(len(rows),'scenes;',sum(x['bytes'] for x in rows),'bytes')
