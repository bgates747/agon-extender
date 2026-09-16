#!/usr/bin/env python3
"""Compare MOS-quantized application pacing and independent browser intervals."""
import argparse,json,statistics,struct
from pathlib import Path

def stats(v):
 if not v:return {'n':0}
 s=sorted(v);return {'n':len(s),'mean_ms':statistics.mean(s),'median_ms':statistics.median(s),'p95_ms':s[min(len(s)-1,int(.95*len(s)))],'max_ms':max(s),'effective_fps':1000/statistics.mean(s) if statistics.mean(s)>0 else None}
def trace(path):
 b=path.read_bytes();assert b[:8]==b'B003TIME' and b[11]==1 and len(b)==10812
 n=int.from_bytes(b[8:11],'little');assert 2<=n<=1800
 r=[{'tick':int.from_bytes(b[12+i*6:15+i*6],'little'),'state':int.from_bytes(b[15+i*6:18+i*6],'little')} for i in range(n)]
 intervals=[((y['tick']-x['tick'])&0xffffff)*1000/120 for x,y in zip(r,r[1:])]
 from collections import Counter
 return {'frames_recorded':n,'intervals':stats(intervals),'histogram_ms':dict(Counter(round(t,3) for t in intervals)),'states':dict(Counter(hex(x['state']) for x in r)),'rows':r}
def browser(path):
 d=json.loads(path.read_text());assert not d.get('error'),d.get('error');segments=[[]]
 for row in d['frames']:
  if (row['width'],row['height'])==(512,384):segments[-1].append(row)
  elif segments[-1]:segments.append([])
 f=max(segments,key=len)
 assert len(f)>10
 # Drop loading/mode-edge frames. Report timing only for the interior game window.
 lo,hi=f[0]['ms']+500,f[-1]['ms']-500;f=[r for r in f if lo<=r['ms']<=hi]
 p=[];last_count=0
 for row in d['presentations']:
  if row['count']>last_count and lo<=row['ms']<=hi:p.append(row)
  last_count=row['count']
 req=[r['requestMs'] for r in f]
 assert min(y-x for x,y in zip(req,req[1:]))>=33.333,'Credit limit violated'
 return {'frames':len(f),'receive_intervals':stats([y['ms']-x['ms'] for x,y in zip(f,f[1:])]),'submission_intervals':stats([y['ms']-x['ms'] for x,y in zip(p,p[1:])]),'request_intervals':stats([y-x for x,y in zip(req,req[1:])]),'identical_adjacent_pixel_hashes':sum(x['pixelHash']==y['pixelHash'] for x,y in zip(f,f[1:])),'scope':'Wired Pi headless Chromium; WebGL submission, not panel scanout; FNV equality is a content fingerprint, not a game frame identifier.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();out={}
 for f in a.root.glob('*-trace.bin'):out[f.stem]=trace(f)
 for f in a.root.glob('browser*/result.json'):out[str(f.parent.name)]=browser(f)
 (a.root/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:{x:y for x,y in v.items() if x!='rows'} for k,v in out.items()},indent=2))
