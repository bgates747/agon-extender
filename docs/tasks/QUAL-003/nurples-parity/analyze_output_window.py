"""Strict window-local diagnosis; retain any original observer failure verdict."""
import argparse,json
from pathlib import Path

def analyze(j):
 b,e=j['before'],j['after']
 for r in (b,e):
  assert r['totals_valid']
  assert all(p['active']['state']==0 and p['active']['consistent'] for p in r['phases'])
 for k in ('lost_completions','overlapping_calls','busy_reads'):assert b[k]==e[k]
 g=j['gate_final'];assert g['inflight']==0 and g['sent']==g['received'] and not g['closes'] and not j['errors']
 expected={'snapshot':196608,'socket_send':196640,'credit_to_ready':1,'ready_to_send':1,'row_wait_sum':384,'row_work_sum':384}
 assert [p['name'] for p in b['phases']]==list(expected)
 rows=[]
 for x,y in zip(b['phases'],e['phases']):
  assert x['name']==y['name'];n=y['count']-x['count'];assert n>0
  assert y['units']-x['units']==n*expected[x['name']]
  us=y['total_us']-x['total_us'];assert us>=0
  rows.append(dict(phase=x['name'],count=n,mean_ms=us/n/1000))
 assert len({r['count'] for r in rows})==1
 frames=[f for f in g['frames'] if j['start_ms']<=f['ms']<=j['end_ms']]
 assert len(frames)>1 and all((f['width'],f['height'],f['bytes'])==(512,384,196640) for f in frames)
 return dict(scope='Window-local output diagnosis only; original observer verdict retained; not game FPS',original_status=j['status'],historical_losses=b['lost_completions'],new_losses=0,phases=rows,received_fps=(len(frames)-1)*1000/(frames[-1]['ms']-frames[0]['ms']))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(analyze(json.loads(a.input.read_text())),indent=2)+'\n')
