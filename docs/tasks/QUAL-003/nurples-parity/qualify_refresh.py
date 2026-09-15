"""Compare repeated raw nonce-bound refresh traces against every stock repeat.

This qualifies command-completion timing only. Live-output, pixel and bench
restoration gates are separately required by PLAN.md; never infer scanout FPS.
"""
import argparse,json
from pathlib import Path
from analyze import parse
from analyze_refresh_trace import analyze

def qualify(manifest,minimum=2):
 cases=json.loads(manifest.read_text());results=[];nonces=set()
 for c in cases:
  assert c['nonce'] not in nonces,'Repeated run identity';nonces.add(c['nonce'])
  game=parse(manifest.parent/c['file'],c['variant'],bytes.fromhex(c['nonce']),2400)
  assert game['count']==2400,'Closeout requires the complete sustained workload'
  trace=analyze((manifest.parent/c['trace_file']).read_text(),c['nonce'],game['count'],c['target'])
  results.append(dict(label=c['label'],target=c['target'],variant=c['variant'],game=game,trace=trace))
 assert len({r['game']['state_sha256'] for r in results})==1,'Different workloads'
 comparisons=[]
 for variant in ('unfenced-sw','unfenced-hw'):
  stock=[r for r in results if r['target']=='mainboard' and r['variant']==variant]
  p4=[r for r in results if r['target']=='p4' and r['variant']==variant]
  assert len(stock)>=minimum and len(p4)>=minimum,'Missing repeated baseline/candidate'
  for s in stock:
   for c in p4:
    b=s['trace']['completion_intervals'];t=c['trace']['completion_intervals']
    comparisons.append({'baseline':s['label'],'candidate':c['label'],'mean_duration_percent_above_stock':100*(t['mean_ms']/b['mean_ms']-1),'p95_duration_percent_above_stock':100*(t['p95_ms']/b['p95_ms']-1),'p95_extra_ms':t['p95_ms']-b['p95_ms'],'mean_pass':t['mean_ms']<=b['mean_ms']*1.05,'p95_pass':t['p95_ms']<=b['p95_ms']+1000/120})
 return {'scope':'Repeated explicit RefreshSprites completion timing, not distinct browser/scanout frames','minimum_runs_per_target_and_sprite_path':minimum,'timing_pass':all(c['mean_pass'] and c['p95_pass'] for c in comparisons),'cases':results,'comparisons':comparisons}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('--minimum',type=int,default=2);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert a.minimum>=1
 r=qualify(a.manifest,a.minimum);a.output.write_text(json.dumps(r,indent=2)+'\n');print('Repeated completion timing:',r['timing_pass']);raise SystemExit(0 if r['timing_pass'] else 1)
