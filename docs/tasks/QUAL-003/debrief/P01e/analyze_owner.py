"""Reconstruct task residency, not CPU-exclusive time, around one native hold."""
import argparse,json,collections
from pathlib import Path
def analyze(text,nonce):
 lines=text.splitlines();hits=[i for i,x in enumerate(lines) if x.startswith('NPOWNER begin '+nonce+' ')];assert len(hits)==1,'Missing/duplicate marker'
 i=hits[0];bad,start,end,count,total,maximum=map(int,lines[i].split()[3:]);assert not bad,'Unfinished trace'
 fired,task,begin,finish,seq,core=map(int,lines[i+1].split()[2:]);events=[[],[]];rings={};j=i+2
 while lines[j]!='NPOWNER end':
  x=lines[j].split();assert x[0]=='NPOWNER'
  if x[1]=='ring':
   c,n,kept=map(int,x[2:]);assert c not in rings;rings[c]=(n,kept)
  elif x[1]=='event':
   c,index,t,tid,kind,prio=map(int,x[2:8]);assert kind in (0,1)
   events[c].append(dict(index=index,time_us=(t-start)&0xffffffff,task=tid,kind=kind,priority=prio,name=bytes.fromhex(x[8]).split(b'\0')[0].decode()))
  else:raise ValueError(x)
  j+=1
 for c,(n,k) in rings.items():
  assert len(events[c])==k and [x['index'] for x in events[c]]==list(range(n-k,n))
  assert all(b['time_us']>=a['time_us'] for a,b in zip(events[c],events[c][1:]))
 assert len(rings)==2
 result=dict(nonce=nonce,valid=True,window_ms=((end-start)&0xffffffff)/1000,holds=count,hold_mean_ms=total/count/1000 if count else None,hold_max_ms=maximum/1000,triggered=bool(fired),rings={str(c):dict(total=n,retained=k,overwritten=n-k) for c,(n,k) in rings.items()},events=events)
 if not fired:return result
 lo=(begin-start)&0xffffffff;hi=(finish-start)&0xffffffff;assert hi>=lo and core in (0,1)
 result['trigger']=dict(task=task,core=core,start_us=lo,end_us=hi,hold_ms=(hi-lo)/1000,refresh_submitted_sequence=seq)
 intervals=[];coverage=[]
 for c,ev in enumerate(events):
  covered=bool(ev) and ev[0]['time_us']<=lo;coverage.append(covered)
  current=None
  for e in ev:
   if e['kind']==1:
    assert current is None,'Missing switch-out';current=e
   else:
    if current is not None:
     assert e['task']==current['task'],'Unmatched task switch'
     a=max(lo,current['time_us']);b=min(hi,e['time_us'])
     if b>a:intervals.append(dict(core=c,start_us=a,end_us=b,elapsed_ms=(b-a)/1000,task=current['task'],name=current['name'],priority_at_entry=current['priority']))
    current=None
  if current is not None:
   a=max(lo,current['time_us'])
   if hi>a:intervals.append(dict(core=c,start_us=a,end_us=hi,elapsed_ms=(hi-a)/1000,task=current['task'],name=current['name'],priority_at_entry=current['priority']))
 result['full_hold_history_covered']=all(coverage);result['intervals']=intervals
 sums=collections.defaultdict(float)
 for e in intervals:sums[(e['core'],e['task'],e['name'])]+=e['elapsed_ms']
 result['residency']=[dict(core=c,task=t,name=n,elapsed_ms=v) for (c,t,n),v in sorted(sums.items(),key=lambda x:-x[1])]
 result['owner_core_unassigned_ms']=(hi-lo)/1000-sum(e['elapsed_ms'] for e in intervals if e['core']==core)
 result['scope']='Switch-bounded residency includes interrupts. No runnable-state or CPU-exclusive attribution. Ring overwrite is acceptable only with full selected-hold history.'
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture',type=Path);p.add_argument('--nonce',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(analyze(a.capture.read_text(errors='replace'),a.nonce),indent=2)+'\n')
