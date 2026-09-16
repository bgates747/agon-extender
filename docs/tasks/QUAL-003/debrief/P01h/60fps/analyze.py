"""Analyze retained BENCH-003-format single-vblank traces and browser samples."""
import sys,json,statistics,importlib.util
from pathlib import Path
# Repository-relative canonical trace parser.
spec=importlib.util.spec_from_file_location('cadence','docs/tasks/BENCH-003/analyze.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=Path(sys.argv[1]);out={}
for name in ('off60','rle60','raw60'):
 if not (r/(name+'.trace')).exists():continue
 t=m.trace(r/(name+'.trace'));t.pop('rows');tele=(r/(name+'.tele')).read_bytes();assert tele[:4]==b'PNST' and not tele[68]&1
 assert int.from_bytes(tele[32:35],'little')==t['frames_recorded']==1800
 out[name]={'application':t,'vdu_faults':tele[68]}
 d=json.loads((r/(name+'.json')).read_text());assert not d['errors']
 if name!='off60':
  segments=[[]]
  for f in d['frames']:
   if (f['w'],f['h'])==(512,384):segments[-1].append(f)
   elif segments[-1]:segments.append([])
  frames=max(segments,key=len);lo,hi=frames[0]['ms']+500,frames[-1]['ms']-500
  frames=[f for f in frames if lo<=f['ms']<=hi];assert len(frames)>10
  out[name]['browser']={'frames':len(frames),'intervals':m.stats([b['ms']-a['ms'] for a,b in zip(frames,frames[1:])]),'mean_message_bytes':statistics.mean(f['bytes'] for f in frames),'magic':sorted(set(f['magic'] for f in frames))}
(r/'analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
