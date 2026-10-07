#!/usr/bin/env python3
"""Audit raw benchmark provenance and execution coverage without bench access.

Valid statistical coverage remains separate from attempted/failed execution.
A boundary failure's case is inferred from the contiguous preceding checkpoints;
its cause and any physical frame delivery remain unproven.
"""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests/performance/render_load'))
from codec import decode
from generate import MODES

def key(meta,case):return (meta['variant'],meta['mode'],meta['endpoint'],meta['pass_number'],case)
def identity(meta,result):
 geometry=MODES[meta['mode']]
 if (result['mode'],result['tag'],result['width'],result['height'],result['colours'])!=(meta['mode'],meta['tag'],*geometry[:3]):return False
 return not meta.get('fixture') or result['build_id']==meta['fixture']['build_id']

def audit(evidence,analysis,out):
 contract=json.loads((ROOT/'tests/performance/render_load/contract-r04.json').read_text())
 valid_rows=json.loads((analysis/'cases.json').read_text())
 valid={(r['run'],r['case']) for r in valid_rows if r['pass'] in (1,2,3) and not r['disable_timing']}
 attempts={};issues=[];raw_files=[];boundaries=[]
 for folder in sorted(evidence.glob('BENCH-009-*')):
  path=folder/'run.json'
  if not path.exists():continue
  meta=json.loads(path.read_text())
  if meta.get('suite')!=contract['identity'] or meta.get('pass_number') not in (1,2,3) or meta.get('disable_timing'):continue
  result=None;checkpoint_error=False;raw=folder/'results.bin'
  if raw.exists():
   data=raw.read_bytes();digest=hashlib.sha256(data).hexdigest()
   try:
    if meta.get('result_sha256') and digest!=meta['result_sha256']:raise ValueError('raw result hash differs from runner receipt')
    result=decode(data)
    if not identity(meta,result):raise ValueError('raw identity differs from mode/tag/geometry/build')
    ids=[c['id'] for c in result['cases']]
    if ids!=list(range(meta['first'],meta['first']+len(ids))) or len(ids)>meta['end']-meta['first']:raise ValueError('raw checkpoint selection/order differs')
    decoded=folder/'decoded.json'
    if not decoded.exists() or json.loads(decoded.read_text())!=result:raise ValueError('derived decoded records differ from raw bytes')
   except Exception as error:
    issues.append(dict(run=folder.name,kind='raw-provenance',failure=repr(error)));result=None;checkpoint_error=True
   else:
    raw_files.append(dict(run=folder.name,bytes=len(data),sha256=digest,runner_digest_available=bool(meta.get('result_sha256'))))
    for case in result['cases']:
     entry=dict(run=folder.name,case=case['id'],outcome='valid measurement' if (folder.name,case['id']) in valid else 'invalid measurement',error=case['error'],truncated=case['truncated'],frames=case['total_frames'])
     attempts.setdefault(key(meta,case['id']),[]).append(entry)
  failure=folder/'failure.bin'
  if failure.exists():
   data=failure.read_bytes()
   try:
    header=decode(data)
    if len(data)!=128 or not identity(meta,header):raise ValueError('failure receipt identity differs')
   except Exception as error:issues.append(dict(run=folder.name,kind='failure-provenance',failure=repr(error)));continue
   code=data[19]
   if code==4:
    if checkpoint_error:
     boundaries.append(dict(run=folder.name,failure_code=code,scope='Checkpoint provenance unresolved; no boundary case inferred'));continue
    cases=result['cases'] if result else []
    failed=cases[-1]['id'] if cases and cases[-1]['error'] else cases[-1]['id']+1 if cases else meta['first']
    if failed<meta['end']:
     entry=dict(run=folder.name,case=failed,outcome='fence failure',failure_code=code,location='measured case' if cases and cases[-1]['error'] else 'case boundary; inferred from checkpoints')
     attempts.setdefault(key(meta,failed),[]).append(entry)
   else:boundaries.append(dict(run=folder.name,mode=meta['mode'],endpoint=meta['endpoint'],pass_number=meta['pass_number'],failure_code=code,scope='Preparation or I/O failure; no additional executed case inferred'))
  elif meta.get('outcome')=='fail' and not result:
   boundaries.append(dict(run=folder.name,mode=meta.get('mode'),endpoint=meta.get('endpoint'),pass_number=meta.get('pass_number'),failure=meta.get('failure'),scope='Run boundary without verified original case records'))
 groups=[]
 for output in contract['p4_outputs']:
  modes=contract['modes'] if output=='normal' else contract['output_control_modes']
  for mode in modes:
   for endpoint in ('mainboard','p4') if output=='normal' else ('p4',):
    for number in range(1,contract['passes']+1):
     observed={i:attempts.get((output,mode,endpoint,number,i),[]) for i in range(94)}
     complete=[i for i,a in observed.items() if any(r['outcome']=='valid measurement' for r in a)]
     failed=[i for i,a in observed.items() if a and i not in complete]
     missing=[i for i,a in observed.items() if not a]
     groups.append(dict(output=output,mode=mode,endpoint=endpoint,pass_number=number,valid_cases=complete,failed_or_invalid_cases=failed,unperformed_cases=missing,execution_accounted=not missing,attempts=[dict(case=i,records=a) for i,a in observed.items() if a]))
 receipt=dict(suite=contract['identity'],expected_case_executions=3948,executions_accounted=sum(94-len(g['unperformed_cases']) for g in groups),valid_measurements=sum(len(g['valid_cases']) for g in groups),failed_or_invalid_executions=sum(len(g['failed_or_invalid_cases']) for g in groups),execution_coverage_complete=all(g['execution_accounted'] for g in groups),raw_provenance_complete=not issues,raw_files=raw_files,issues=issues,run_boundaries=boundaries,groups=groups,limits='Execution coverage does not prove failure controls or restoration complete; physical displayed FPS unobserved. Boundary case IDs are explicitly inferred.')
 out.write_text(json.dumps(receipt,indent=2)+'\n');return receipt

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--analysis',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 result=audit(a.evidence,a.analysis,a.output);print(json.dumps({k:result[k] for k in ('expected_case_executions','executions_accounted','valid_measurements','failed_or_invalid_executions','execution_coverage_complete','raw_provenance_complete')}))

if __name__=='__main__':main()
