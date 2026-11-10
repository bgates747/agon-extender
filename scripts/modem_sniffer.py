#!/usr/bin/env python3
"""One finite NET-008 directional capture under a genuine admitted sole lease.

No flash/reset/JOIN/release. Analyzer acquires only the existing D0,D3 pair.
This is one selected arm, never an automatic retry/ladder. Capture starts before
BENCH and is joined even when an endpoint fails. Raw public test bytes retained.
"""
import argparse,hashlib,json,os,re,secrets,subprocess,time
from pathlib import Path
from passive_serial import open_passive_serial
from modem_bw_peer import Peer
from bench_process import identity,members
ROOT=Path(__file__).resolve().parents[1]
def save(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['port','lease','manifest','out','bind','analyzer']:p.add_argument('--'+key,required=True)
 p.add_argument('--baud',type=int,choices=[384000,576000,1152000],required=True);p.add_argument('--old-baud',type=int,required=True);p.add_argument('--direction',choices=['up','down'],required=True);a=p.parse_args()
 out=Path(a.out);out.mkdir(exist_ok=False);manifest=json.loads(Path(a.manifest).read_text());capture=None;peer=None;result={'endpoint_pass':False};records=[]
 def own():
  r=json.loads(subprocess.check_output([str(ROOT.parent/'agon-dev-env/.venv/bin/python'),str(ROOT.parent/'agon-dev-env/cross-agent/olimex-bench/bench_lease.py'),'assert-owner','--owner','linux-extender','--lease',a.lease],text=True));assert r['hardware_ready'] and r['phase']=='consumer'
 def read_until(s,event,seconds):
  pending=bytearray();deadline=time.monotonic()+seconds
  while time.monotonic()<deadline:
   b=s.read(4096)
   if b:
    console.write(b);console.flush();pending.extend(b)
   while b'\n' in pending:
    line,_,pending=pending.partition(b'\n')
    if line.startswith(b'NET008 '):
     r=json.loads(line[7:]);records.append(r)
     if r.get('event')==event:return r
   if len(pending)>16384:raise ValueError('Oversized diagnostic line')
  raise TimeoutError('No finite '+event)
 def send(s,line):
  own();s.write((line+'\n').encode());s.flush()
  with (out/'commands.jsonl').open('a') as f:f.write(json.dumps({'epoch':time.time(),'command':line})+'\n');f.flush()
 console=(out/'console.bin').open('xb');log=(out/'sigrok.log').open('xb')
 try:
  own()
  scan=subprocess.check_output([a.analyzer,'--scan','--show'],text=True,timeout=15);(out/'scan.txt').write_text(scan)
  rows=[x for x in scan.splitlines() if x.startswith('fx2lafw')]
  if len(rows)!=1:raise ValueError('Analyzer identity ambiguous')
  match=re.fullmatch(r'fx2lafw:conn=(\d+\.\d+) - Saleae Logic \[S/N: Saleae Logic\] with 8 channels: D0 D1 D2 D3 D4 D5 D6 D7',rows[0])
  if not match:raise ValueError('Analyzer connection not positively identified; no acquisition')
  with open_passive_serial(a.port,timeout=.1) as s:
   send(s,'STATUS');r=read_until(s,'ready',8);assert r['build']==manifest['build_id'] and r['source']==manifest['source_commit']
   send(s,f'INFO {a.old_baud}');r=read_until(s,'bw_info_end',15);assert r['pass'] and r['uart_retired'],'Known baud/command mode not established'
   nonce=secrets.randbelow(2**32-1)+1;peer=Peer(a.bind,out/'pi',nonce,a.baud,3000,a.direction)
   argv=[a.analyzer,'--loglevel','2','--driver','fx2lafw:conn='+match[1],'--config','samplerate=24000000','--channels','D0,D3','--samples','288000000','--output-format','binary','--output-file',str(out/'logic.raw')]
   # sigrok drops to its capture account; precreate a readable public-test file.
   raw_path=out/'logic.raw'
   raw_path.touch(exist_ok=False);os.chmod(raw_path,0o666)
   own();capture=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save(out/'capture-actor.json',dict(**identity(capture.pid),argv=argv))
   deadline=time.monotonic()+8
   while not (out/'logic.raw').exists() or (out/'logic.raw').stat().st_size<65536:
    assert capture.poll() is None and time.monotonic()<deadline,'Acquisition not delivering samples';time.sleep(.025)
   save(out/'issued.json',dict(epoch=time.time(),baud=a.baud,old_baud=a.old_baud,direction=a.direction,nonce=nonce,producer_ms=3000,channels={'D0':'P4 TX to ESP RX','D3':'ESP TX to P4 RX'}))
   send(s,f'{a.direction.upper()} {a.old_baud} {a.baud} 3000 {a.bind} {peer.port} {nonce}')
   native=read_until(s,'bw_end',58);peer.finished.wait(4)
   result.update(native=native,pi=dict(peer.result))
   result['endpoint_pass']=bool(native.get('pass') and peer.result.get('pass') and native['tx_frames']==peer.result['rx_frames'] and native['rx_frames']==peer.result['tx_frames'])
   assert capture.wait(timeout=20)==0 and not members(capture.pid)
   raw=out/'logic.raw';assert raw.stat().st_size==288000000,'Incomplete acquisition'
   save(out/'capture-terminal.json',dict(returncode=capture.returncode,direct_child_joined=True,live_group_members=members(capture.pid),samples=raw.stat().st_size,rate=24000000,sha256=hashlib.file_digest(raw.open('rb'),'sha256').hexdigest()))
   return 0 if result['endpoint_pass'] else 1
 finally:
  if peer:peer.close()
  if capture:
   if capture.poll() is None:capture.terminate();capture.wait(timeout=5)
   if not (out/'capture-terminal.json').exists():save(out/'capture-aborted.json',dict(returncode=capture.returncode,direct_child_joined=True,live_group_members=members(capture.pid)))
  console.flush();os.fsync(console.fileno());console.close();log.close();save(out/'result.json',dict(**result,records=records))
if __name__=='__main__':raise SystemExit(main())
