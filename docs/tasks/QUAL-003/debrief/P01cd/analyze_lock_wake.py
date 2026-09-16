#!/usr/bin/env python3
"""Parse bounded NPLOCK counters. Times are elapsed microseconds, not CPU time."""
import argparse,json
from pathlib import Path
NAMES=('parser_wait','parser_hold','draw_wait','draw_hold','output_wait','output_hold','draw_notification_age','output_notification_age')
def parse(text,nonce):
 lines=text.splitlines();start=[i for i,s in enumerate(lines) if s.startswith('NPLOCK begin '+nonce+' ')]
 if len(start)!=1:raise ValueError('Expected exactly one matching marker')
 i=start[0];head=lines[i].split();assert head[3:]==['0','0'],'Unfinished or invalid trace'
 rows=[]
 for j,name in enumerate(NAMES):
  x=lines[i+1+j].split();assert x[:3]==['NPLOCK','row',str(j)]
  count,total,maximum,*bins=map(int,x[3:]);assert len(bins)==32 and sum(bins)==count
  def bound(q):
   acc=0
   for k,n in enumerate(bins):
    acc+=n
    if count and acc>=count*q:return (2**(k+1)-1)/1000
   return None
  rows.append(dict(metric=name,count=count,total_ms=total/1000,mean_ms=total/count/1000 if count else None,max_ms=maximum/1000,p95_bucket_upper_ms=bound(.95),p99_bucket_upper_ms=bound(.99),histogram=bins))
 assert lines[i+9]=='NPLOCK end'
 return dict(nonce=nonce,valid=True,elapsed_not_cpu_exclusive=True,rows=rows)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('log',type=Path);p.add_argument('--nonce',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(parse(a.log.read_text(errors='replace'),a.nonce),indent=2)+'\n')
