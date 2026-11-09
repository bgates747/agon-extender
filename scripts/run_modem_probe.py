#!/usr/bin/env python3
"""Explicitly invoke the stopped NET-008 P4 UART2 appliance once under a lease.

Never flashes, resets, changes startup or releases custody. The caller separately
owns temporary P4 installation and exact restoration. Raw serial and structured
results are durable even on failure. STATUS is not a workload invocation.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
from passive_serial import open_passive_serial
ROOT=Path(__file__).resolve().parents[1]
LEASE=ROOT.parent/'agon-dev-env/cross-agent/olimex-bench/bench_lease.py'
ENV_PY=ROOT.parent/'agon-dev-env/.venv/bin/python'
def validate(records,build):
 starts=[r for r in records if r.get('event')=='start']
 assert len(starts)==1 and starts[0]['build']==build and (starts[0]['tx'],starts[0]['rx'],starts[0]['baud'])==(47,48,115200),'Wrong/duplicate start'
 assert not any(r.get('event') in ['error','uart_error','refused'] for r in records),'Device error/refusal'
 tx=[r for r in records if r.get('event')=='tx'];rx=[r for r in records if r.get('event')=='rx'];results=[r for r in records if r.get('event')=='command_result']
 assert [r['seq'] for r in tx]==[1,2,3,4,5] and [r['seq'] for r in rx]==[1,2,3,4,5] and [r['seq'] for r in results]==[1,2,3,4,5],'Incomplete/out-of-order commands'
 for i,(a,b,c) in enumerate(zip(tx,rx,results),1):
  assert bytes.fromhex(a['hex'])==(b'AT+GMR\r\n' if i==2 else b'AT\r\n'),'Unexpected command'
  raw=bytes.fromhex(b['hex']);assert len(raw)==c['bytes'] and b'\nOK\r\n' in raw and b'\x00' not in raw,'Missing complete OK/raw mismatch'
  assert c['pass'] is True and c['terminal']==1 and c['identity'] is True,'Command failed'
  if i==2:assert b'AT version:' in raw,'Missing actual modem firmware identity'
 ends=[r for r in records if r.get('event')=='end'];assert len(ends)==1 and ends[0]['pass'] is True and ends[0]['uart_retired'] is True,'No positive terminal retirement'
 return {'pass':True,'commands':5,'gmr_hex':rx[1]['hex'],'scope':'Finite UART2 AT/firmware identity only; no supply margin or EMOS modem bridge claim'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True);p.add_argument('--lease',required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 m=json.loads(a.manifest.read_text());build=m['build_id'];a.out.mkdir(exist_ok=False)
 def owner():subprocess.run([str(ENV_PY),str(LEASE),'assert-owner','--owner','linux-extender','--lease',a.lease],check=True,capture_output=True)
 records=[];rawfile=(a.out/'serial.bin').open('xb');start=time.monotonic();pending=bytearray();invoked=False;result={'pass':False}
 def receive(s,deadline):
  while time.monotonic()<deadline:
   chunk=s.read(1024)
   if not chunk:continue
   rawfile.write(chunk);rawfile.flush();os.fsync(rawfile.fileno());pending.extend(chunk)
   while b'\n' in pending:
    line,_,rest=pending.partition(b'\n');pending[:]=rest
    if not line.startswith(b'NET008 '):continue
    value=json.loads(line[7:]);records.append(value)
    with (a.out/'events.jsonl').open('a') as f:f.write(json.dumps(value)+'\n');f.flush();os.fsync(f.fileno())
    yield value
   if len(pending)>8192:raise RuntimeError('Oversized serial line')
 try:
  owner()
  with open_passive_serial(a.port,timeout=.1) as s:
   owner();s.write(b'STATUS\n');s.flush()
   ready=None
   for r in receive(s,time.monotonic()+8):
    if r.get('event')=='ready':ready=r;break
   assert ready and ready['build']==build and ready['source']==m['source_commit'] and ready['used'] is False,'No matching stopped appliance'
   records.clear();owner();s.write(b'START\n');s.flush();invoked=True
   for r in receive(s,time.monotonic()+25):
    if r.get('event')=='end':break
   result=validate(records,build)
 except Exception as e:result={'pass':False,'error':str(e)}
 finally:
  rawfile.close();result.update(invoked=invoked,build=build,elapsed_host_seconds=time.monotonic()-start,serial_sha256=hashlib.sha256((a.out/'serial.bin').read_bytes()).hexdigest())
  (a.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2));return 0 if result['pass'] else 1
if __name__=='__main__':raise SystemExit(main())
