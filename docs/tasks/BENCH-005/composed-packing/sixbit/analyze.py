from pathlib import Path
import json,sys,statistics,collections,hashlib
sys.path.insert(0,'docs/tasks/BENCH-003');from analyze import trace
r=Path('agents/sixbit/nurples');T=Path('docs/tasks/BENCH-005/composed-packing/sixbit');out=[]
for name in ['prior','six','auto']:
 d=json.loads((r/(name+'.json')).read_text());f=[x for x in d['frames'] if (x['w'],x['h'])==(512,384)];hi=f[-1]['ms']-5000;lo=hi-20000;f=[x for x in f if lo<=x['ms']<=hi];assert len(f)>10
 ps=[x for x in d['presentations'] if lo<=x['ms']<=hi];assert len(ps)>2
 row={'variant':name,'received_fps':(len(f)-1)*1000/(f[-1]['ms']-f[0]['ms']),'submitted_fps':(ps[-1]['count']-ps[0]['count'])*1000/(ps[-1]['ms']-ps[0]['ms']),'mean_wire_bytes':statistics.mean(x['bytes'] for x in f),'frames':len(f),'formats':dict(collections.Counter(x['magic']+('/6bit' if x['magic']=='EVP1' and x['bits']==6 else '') for x in f)),'errors':d['errors'],'host_seconds':d['seconds'],'application':trace(r/(name+'.trace'))}
 out.append(row)
(T/'NURPLES.json').write_text(json.dumps(out,indent=2)+'\n')
for row in out:print({k:v for k,v in row.items() if k!='application'},'app fps',row['application']['intervals']['effective_fps'])
