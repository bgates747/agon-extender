"""Read the NP01 fixed-size pilot result; never treat submissions as completions."""
import argparse,json,statistics,hashlib
from pathlib import Path

def parse(path, variant="fenced-sw"):
 assert variant in ("fenced-sw", "fenced-hw", "unfenced-sw")
 b=path.read_bytes();sustained=b[:4]==b'NP03'
 header,stride,capacity=(9,12,2400) if sustained else (8,11,600)
 assert len(b)==header+capacity*stride and b[:4] in (b'NP01',b'NP03'),(path,len(b),b[:9])
 count=int.from_bytes(b[4:7],'little');assert 122<=count<=capacity and b[7]==0,(count,b[7])
 reason=b[8] if sustained else 0
 assert (reason==0 and count==capacity) or (sustained and reason in (1,2)),(count,reason)
 rows=[b[header+i*stride:header+(i+1)*stride] for i in range(count)]
 ticks=[int.from_bytes(x[:3],'little') for x in rows]
 delta=[(ticks[i]-ticks[i-1])&0xffffff for i in range(121,count)]
 ordered=sorted(delta);p95=ordered[(len(ordered)*95+99)//100-1]
 result=dict(file=path.name,count=count,failed=b[7],warmup_boundaries=120,intervals=len(delta),
  elapsed_ticks=sum(delta),mean_frame_ms=statistics.mean(delta)*1000/120,
  completed_fps=len(delta)*120/sum(delta),p95_frame_ms=p95*1000/120,
  maximum_frame_ms=max(delta)*1000/120,
  tick_histogram={str(k):delta.count(k) for k in sorted(set(delta))},
  state_sha256=hashlib.sha256(b''.join(x[3:] for x in rows)).hexdigest(),
  variant=variant,
  completion_scope=('submission/vblank boundary; terminal fence only' if variant=='unfenced-sw' else 'pixel-query drawing completion boundary; no hardware-sprite scanout proof'))

 if sustained:
  live=[x[11] for x in rows]
  result.update(end_reason={0:'boundary_limit',1:'game_over',2:'victory'}[reason],live_sprites_max=max(live),live_sprites_mean=statistics.mean(live),live_sprites_histogram={str(k):live.count(k) for k in sorted(set(live))})
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('files',type=Path,nargs='+');p.add_argument('--output',type=Path);p.add_argument('--variant',choices=['fenced-sw','fenced-hw','unfenced-sw'],default='fenced-sw');a=p.parse_args()
 results=[parse(f,a.variant) for f in a.files];s=json.dumps(results,indent=2);print(s)
 if a.output:a.output.write_text(s+'\n')
