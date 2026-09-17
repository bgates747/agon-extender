from pathlib import Path
import json,statistics,importlib.util,argparse,collections
p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args()
spec=importlib.util.spec_from_file_location('cadence','docs/tasks/BENCH-003/analyze.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);out={}
for path in sorted(a.run.glob('*.trace')):
 name=path.stem;t=m.trace(path);t.pop('rows');tele=path.with_suffix('.tele').read_bytes();assert tele[:4]==b'PNST' and tele[68]==0 and t['frames_recorded']==1800
 d=json.loads(path.with_suffix('.json').read_text());frames=d['frames'];end=frames[-1]['ms'];lo,hi=end-20000,end-5000;f=[x for x in frames if lo<=x['ms']<=hi and (x['w'],x['h'])==(512,384)];assert len(f)>10
 counters={k:d['stats_after'][k]-d['stats_before'][k] for k in d['stats_before'] if k!='stack_min_bytes'}
 presentations=[x['ms'] for x in d['presentations'] if lo<=x['ms']<=hi]
 out[name]=dict(application=t,errors=d['errors'],codec_counters=counters,browser=dict(intervals=m.stats([b['ms']-a['ms'] for a,b in zip(f,f[1:])]),submitted=m.stats([b-a for a,b in zip(presentations,presentations[1:])]),mean_bytes=statistics.mean(x['bytes'] for x in f),magic=dict(collections.Counter(x['magic'] for x in f))),seconds=d['seconds'])
(a.run/'analysis.json').write_text(json.dumps(out,indent=2))
for n,x in out.items():print(n,round(x['browser']['intervals']['effective_fps'],2),'fps',round(x['browser']['mean_bytes']),'bytes',x['codec_counters'])
