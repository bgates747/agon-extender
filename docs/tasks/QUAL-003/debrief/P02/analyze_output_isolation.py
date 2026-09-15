"""Parse nonce-bound P02 accounting; distinguish operations from presentation."""
import argparse,json,re
from pathlib import Path

def analyze(text,nonce):
 starts=list(re.finditer(r'NPOUT begin '+re.escape(nonce)+r' (\d+) (\d+) ([01])\r?\n',text))
 assert len(starts)==1,'Missing/duplicate output record'
 m=starts[0];duration,pending,invalid=map(int,m.groups());assert duration>0 and not pending and not invalid
 end=text.find('NPOUT end',m.end());assert end>=0
 rows=[tuple(map(int,x)) for x in re.findall(r'NPOUT row (\d+) (\d+) (\d+) (\d+) (\d+)',text[m.end():end])]
 assert [x[0] for x in rows]==[0,1,2]
 phases={}
 for (i,calls,units,elapsed,failed),name in zip(rows,('compose','prebuilt','send')):
  assert not failed,(name,failed)
  phases[name]={'calls':calls,'units':units,'wall_ms_sum':elapsed/1000,'mean_operation_ms':elapsed/1000/calls if calls else None,'operations_per_window_second':calls*1e6/duration,'unit_kind':'EVF_header_plus_payload_bytes' if i==2 else 'RGB222_pixels'}
 mode=bytes.fromhex(nonce)[3];assert bytes.fromhex(nonce)[:3]==b'P02' and mode<=3
 c,p,s=(phases[n]['calls'] for n in ('compose','prebuilt','send'))
 if mode==0:assert c>0 and p==0 and s>0
 if mode==1:assert c==p==s==0
 if mode==2:assert c>0 and p==s==0
 if mode==3:assert p>0 and s>0 and c<=1,'More than one boundary carry-over composition'
 for i,name in enumerate(('compose','prebuilt','send')):
  v=phases[name];assert v['units']==v['calls']*(196640 if i==2 else 196608),'Unexpected geometry/partial frame accounting'
 return {'nonce':nonce,'mode':('normal','off','discard','prebuilt')[mode],'window_seconds':duration/1e6,'pending':pending,'invalid':invalid,'phases':phases,'boundary_composition_carryover':c if mode==3 else 0,'scope':'operations admitted in marker window; final in-flight completion joined; wall times include preemption; no physical presentation claim'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture',type=Path);p.add_argument('--nonce',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();j=analyze(a.capture.read_text(errors='replace'),a.nonce);a.output.write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j,indent=2))
