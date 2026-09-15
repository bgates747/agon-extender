"""Read the NP01 fixed-size pilot result; never treat submissions as completions."""
import argparse,json,statistics,hashlib
from pathlib import Path

def parse(path):
 b=path.read_bytes();assert len(b)==6608 and b[:4]==b'NP01',(path,len(b),b[:8])
 count=int.from_bytes(b[4:7],'little');assert count==600 and b[7]==0,(count,b[7])
 rows=[b[8+i*11:19+i*11] for i in range(count)]
 ticks=[int.from_bytes(x[:3],'little') for x in rows]
 delta=[(ticks[i]-ticks[i-1])&0xffffff for i in range(121,count)]
 ordered=sorted(delta);p95=ordered[(len(ordered)*95+99)//100-1]
 return dict(file=path.name,count=count,failed=b[7],warmup_boundaries=120,intervals=len(delta),
  elapsed_ticks=sum(delta),mean_frame_ms=statistics.mean(delta)*1000/120,
  completed_fps=len(delta)*120/sum(delta),p95_frame_ms=p95*1000/120,
  maximum_frame_ms=max(delta)*1000/120,
  tick_histogram={str(k):delta.count(k) for k in sorted(set(delta))},
  state_sha256=hashlib.sha256(b''.join(x[3:] for x in rows)).hexdigest(),
  completion_scope='one pixel query per frame in fenced variant; no hardware-sprite scanout proof')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('files',type=Path,nargs='+');p.add_argument('--output',type=Path);a=p.parse_args()
 results=[parse(f) for f in a.files];s=json.dumps(results,indent=2);print(s)
 if a.output:a.output.write_text(s+'\n')
