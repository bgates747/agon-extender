"""Summarize fixed-mode controls; input files may be unpacked from evidence/game-r03/."""
from pathlib import Path
import json,statistics,importlib.util,collections
spec=importlib.util.spec_from_file_location('cadence','docs/tasks/BENCH-003/analyze.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
import argparse
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();r=a.directory;out={}
for p in sorted(r.glob('*.trace')):
 name=p.stem;t=m.trace(p);t.pop('rows');tele=(r/(name+'.tele')).read_bytes();assert tele[:4]==b'PNST' and tele[68]==0 and t['frames_recorded']==1800
 d=json.loads((r/(name+'.json')).read_text());row={'application':t,'vdu_faults':tele[68],'errors':d['errors']}
 if name!='off':
  frames=d['frames'];end=frames[-1]['ms'];lo,hi=end-20000,end-5000
  f=[x for x in frames if lo<=x['ms']<=hi];assert len(f)>10;assert all((x['w'],x['h'])==(512,384) for x in f),'Wrong resolution in measurement window'
  row['browser']={'scope':'central 15 seconds, ending 5 seconds before final receipt; avoids loading and completion edges','intervals':m.stats([b['ms']-a['ms'] for a,b in zip(f,f[1:])]),'mean_bytes':statistics.mean(x['bytes'] for x in f),'magic':dict(collections.Counter(x['magic'] for x in f))}
  q=[x for x in d['requests'] if lo<=x<=hi];row['browser']['request_intervals']=m.stats([b-a for a,b in zip(q,q[1:])])
  q=[x['ms'] for x in d['presentations'] if lo<=x['ms']<=hi];row['browser']['submission_intervals']=m.stats([b-a for a,b in zip(q,q[1:])])
 row['codec_counters']={k:d['stats_after'][k]-d['stats_before'][k] for k in d['stats_before'] if k!='stack_min_bytes'}
 out[name]=row
(r/'analysis.json').write_text(json.dumps(out,indent=2))
for n,x in out.items():print(n,x['application']['intervals']['effective_fps'],x.get('browser',{}).get('intervals',{}).get('effective_fps'),x.get('browser',{}).get('mean_bytes'))
