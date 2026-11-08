"""Bounded host readiness leaf controls. No ports/network/firmware/reset used."""
from pathlib import Path
from urllib.error import URLError,HTTPError
import importlib.util,json
P=Path(__file__).resolve().parents[2]/'scripts/native_bootstrap.py'
s=importlib.util.spec_from_file_location('native_bootstrap',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
GOOD={'available':True,'rolling':{'faults':0}}
def case(sequence,*,signature=True,fatal=False):
 now=[0];calls=[];missing=[];raw=bytearray()
 def observe(marker):
  now[0]+=1
  if fatal:raise RuntimeError('fatal startup guard')
  if signature:raw.extend(m.PAD+b' build_id='+m.BUILD if not raw else b'')
 def get():
  calls.append(now[0]);item=sequence[min(len(calls)-1,len(sequence)-1)]
  if isinstance(item,Exception):raise item
  return item
 try:value=m.wait_p4_initialization(observe,get,raw,clock=lambda:now[0],record_missing=lambda n,r:missing.append(r))
 except Exception as e:return dict(error=type(e).__name__,seconds=now[0],calls=calls,missing=missing)
 return dict(value=value,seconds=now[0],calls=calls,missing=missing)
rows={}
r=rows['healthy']=case([GOOD]);assert r['seconds']==6 and r['value'][1]==0
r=rows['one_timeout']=case([URLError(TimeoutError('one')),GOOD]);assert r['seconds']==7 and r['value'][1]==1 and len(r['missing'])==1
r=rows['reset_stability']=case([GOOD]*4+[TimeoutError('middle'),GOOD]);assert r['seconds']==11 and r['value'][1]==1
r=rows['fault_resets_stability']=case([GOOD]*4+[{'available':True,'rolling':{'faults':1}},GOOD]);assert r['seconds']==11
r=rows['unavailable_resets_stability']=case([GOOD]*4+[{'available':False},GOOD]);assert r['seconds']==11
r=rows['bounded_all_timeouts']=case([URLError(TimeoutError('all'))]);assert r['error']=='TimeoutError' and r['seconds']==60 and len(r['missing'])==60
r=rows['wrong_signature']=case([GOOD],signature=False);assert r['error']=='TimeoutError' and r['seconds']==60 and not r['calls']
r=rows['fatal_serial']=case([GOOD],fatal=True);assert r['error']=='RuntimeError' and not r['calls']
r=rows['non_timeout_http']=case([HTTPError('test',500,'error',{},None)]);assert r['error']=='HTTPError' and len(r['calls'])==1
r=rows['connection_refusal']=case([URLError(ConnectionRefusedError('no'))]);assert r['error']=='URLError' and len(r['calls'])==1
r=rows['malformed_json']=case([ValueError('json')]);assert r['error']=='ValueError' and len(r['calls'])==1
# This helper has no reset/command operation; original outer single-reset and
# positive CLI requirements remain separate and are not mocked into a pass.
print(json.dumps(dict(passed=True,controls=len(rows),rows=rows,no_target=True)))
