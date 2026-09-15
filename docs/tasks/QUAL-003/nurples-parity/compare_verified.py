"""Compare nonce-verified NP04 runs, retaining warmup and sprite-load strata."""
import argparse,json,statistics
from pathlib import Path
from analyze import parse

def stats(values):
 if not values:return None
 s=sorted(values)
 return {'intervals':len(s),'mean_ms':statistics.mean(s)*1000/120,'p95_ms':s[(len(s)*95+99)//100-1]*1000/120,'max_ms':max(s)*1000/120}

def main():
 p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 cases=json.loads(a.manifest.read_text());out={'scope':'NP04 verified boundary intervals; query/unfenced and HW scanout limits remain explicit','cases':{}}
 for case in cases:
  f=a.manifest.parent/case['file'];j=parse(f,case['variant'],bytes.fromhex(case['nonce']),case['capacity']);assert j['provenance']=='nonce_verified'
  b=f.read_bytes();rows=[b[24+12*i:36+12*i] for i in range(j['count'])]
  ticks=[int.from_bytes(r[:3],'little') for r in rows];delta=[(ticks[i]-ticks[i-1])&0xffffff for i in range(1,len(rows))]
  by_load={}
  for lo,hi in ((0,4),(5,8),(9,20)):
   v=[delta[i-1] for i in range(121,len(rows)) if lo<=rows[i][11]<=hi];by_load[f'{lo}-{hi}']=stats(v)
  out['cases'][case['label']]={'summary':j,'first_120_intervals':stats(delta[:120]),'all_intervals':stats(delta),'post_warmup_by_live_sprites':by_load}
 # Different variants retain identical game code addresses and record layouts.
 # Never silently compare a changed deterministic workload.
 assert len({c['summary']['state_sha256'] for c in out['cases'].values()})==1,'Workload fingerprints differ'
 a.output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
