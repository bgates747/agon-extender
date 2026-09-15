"""Validate a complete nonce-bound P4 refresh trace; USB dump is after timing."""
import argparse,json,re,statistics
from pathlib import Path

def analyze(text,nonce,expected,target='p4'):
 assert target in ('p4','mainboard')
 n=re.escape(nonce)
 starts=list(re.finditer(r'NPTRACE begin '+n+r' (\d+) (\d+) (\d+) ([01])\r?\n',text))
 assert len(starts)==1,'Missing/duplicate trace start'
 m=starts[0]; tail=text[m.end():];end=re.search(r'NPTRACE end '+n+r'\r?\n',tail)
 assert end,'Missing terminal trace marker'
 submitted,completed,pending,invalid=map(int,m.groups())
 assert submitted==completed==expected and not invalid,'Unbalanced/overflow/missing refresh work'
 rows=[tuple(map(int,x)) for x in re.findall(r'NPTRACE row (\d+) (\d+) (\d+)\r?\n',tail[:end.start()])]
 assert len(rows)==expected and [r[0] for r in rows]==list(range(expected)),'Missing/duplicate/out-of-order samples'
 delta=lambda a,b:(a-b)&0xffffffff
 durations=[delta(rows[i][2],rows[i-1][2]) for i in range(121,len(rows))]
 arrivals=[delta(rows[i][1],rows[i-1][1]) for i in range(121,len(rows))]
 latency=[delta(r[2],r[1]) for r in rows[120:]]
 assert all(v<10000000 for v in durations+arrivals+latency),'Invalid timestamp ordering or stalled renderer'
 def stats(v):
  s=sorted(v);return {'count':len(v),'mean_ms':statistics.mean(v)/1000,'p95_ms':s[(len(s)*95+99)//100-1]/1000,'max_ms':max(v)/1000}
 return {'scope':target+' completed explicit RefreshSprites boundaries; not physical scanout or web delivery','nonce':nonce,'submitted':submitted,'completed':completed,'maximum_pending_refreshes':pending,'warmup':120,'completed_fps':1000000/statistics.mean(durations),'completion_intervals':stats(durations),'enqueue_intervals':stats(arrivals),'enqueue_to_completion':stats(latency),'elapsed_first_to_last_ms':delta(rows[-1][2],rows[0][2])/1000}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture',type=Path);p.add_argument('--nonce',required=True);p.add_argument('--expected',type=int,default=2400);p.add_argument('--output',type=Path,required=True);p.add_argument('--target',choices=['p4','mainboard'],default='p4');a=p.parse_args()
 r=analyze(a.capture.read_text(errors='replace'),a.nonce,a.expected,a.target);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
