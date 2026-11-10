#!/usr/bin/env python3
"""Explicit NET-008 CRC baud ladder under an already-admitted retained bench.

No flashing, reset, startup write, original-firmware restore or bench release.
Pi5 TCP listener and passive P4 USB console belong only to this finite process.
"""
import argparse,hashlib,json,os,secrets,socket,subprocess,time
from pathlib import Path
from passive_serial import open_passive_serial
from modem_bw_peer import Peer
ROOT=Path(__file__).resolve().parents[1]
RATES=[115200,230400,384000,576000,1152000]

def save(path,value):
 with Path(path).open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def evaluate(native,peer,seconds):
 if not native.get('pass') or not peer.get('pass'):raise ValueError('An endpoint failed')
 if not native.get('cleanup') or not native.get('uart_retired'):raise ValueError('Modem cleanup/retirement failed')
 if any(native.get(k,-1)!=0 for k in ['uart_errors','crc_errors','frame_errors']):raise ValueError('P4 error counters nonzero/missing')
 if native['tx_frames']!=peer['rx_frames'] or native['rx_frames']!=peer['tx_frames']:raise ValueError('Endpoint frame counts differ')
 if native['tx_bytes']!=peer['rx_bytes'] or native['rx_bytes']!=peer['tx_bytes']:raise ValueError('Endpoint byte counts differ')
 if not native['tx_frames'] or not native['rx_frames']:raise ValueError('No useful data')
 if native['rx_elapsed_us']<seconds*1e6 or peer['rx_elapsed_seconds']<seconds:raise ValueError('Receive window shorter than required')
 return dict(pass_case=True,p4_to_pi_bytes_per_second=peer['rx_bytes']/peer['rx_elapsed_seconds'],pi_to_p4_bytes_per_second=native['rx_bytes']/(native['rx_elapsed_us']/1e6),p4_rx_seconds=native['rx_elapsed_us']/1e6,pi_rx_seconds=peer['rx_elapsed_seconds'])

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['port','lease','manifest','out']:p.add_argument('--'+n,required=True,type=Path if n in ['manifest','out'] else str)
 p.add_argument('--qualify-baud',type=int,choices=RATES,help='Deliberate lower-rate qualification after retained first failure and positive command-mode reconciliation')
 p.add_argument('--bind',help='Actual private Pi5 IPv4 reachable by modem');p.add_argument('--start-baud',type=int,default=115200);p.add_argument('--info-only',action='store_true');a=p.parse_args()
 if a.start_baud not in RATES:p.error('Known starting baud must be an Agon-exact ladder rate')
 if not a.info_only and not a.bind:p.error('TCP test requires explicit private --bind address')
 m=json.loads(a.manifest.read_text());a.out.mkdir(exist_ok=False)
 def own():
  r=json.loads(subprocess.run([str(ROOT.parent/'agon-dev-env/.venv/bin/python'),str(ROOT.parent/'agon-dev-env/cross-agent/olimex-bench/bench_lease.py'),'assert-owner','--owner','linux-extender','--lease',a.lease],check=True,capture_output=True,text=True).stdout)
  if r.get('hardware_ready') is not True or r.get('phase')!='consumer':raise RuntimeError('Genuine custody/admission required')
 own();raw=(a.out/'console.bin').open('xb');pending=bytearray();all_records=[];suite_start=time.monotonic();current=a.start_baud;cases=[]
 def records(s,deadline):
  report=0
  while time.monotonic()<deadline:
   if time.monotonic()-report>=5:
    report=time.monotonic();print('Host waiting for bounded modem result; suite elapsed %.1fs'%(report-suite_start),flush=True)
   chunk=s.read(4096)
   if not chunk:continue
   raw.write(chunk);raw.flush();pending.extend(chunk)
   while b'\n' in pending:
    line,_,tail=pending.partition(b'\n');pending[:]=tail
    if not line.startswith(b'NET008 '):continue
    r=json.loads(line[7:]);all_records.append(r)
    with (a.out/'events.jsonl').open('a') as f:f.write(json.dumps(r)+'\n');f.flush()
    if r.get('event')=='bw_progress':print(json.dumps(r),flush=True)
    yield r
   if len(pending)>16384:raise RuntimeError('Oversized diagnostic line')
 def send(s,text):
  own();s.write((text+'\n').encode('ascii'));s.flush()
  with (a.out/'commands.jsonl').open('a') as f:f.write(json.dumps(dict(epoch=time.time(),command=text))+'\n');f.flush();os.fsync(f.fileno())
 result={'pass':False,'cases':cases,'firmware_retained':True,'bench_held':True}
 try:
  with open_passive_serial(a.port,timeout=.1) as s:
   send(s,'STATUS');matched=False
   for r in records(s,time.monotonic()+8):
    if r.get('event')=='ready':
     matched=r.get('build')==m['build_id'] and r.get('source')==m['source_commit'];break
   if not matched:raise RuntimeError('Actual stopped firmware differs from selected manifest')
   if a.info_only:
    send(s,f'INFO {current}')
    for r in records(s,time.monotonic()+15):
     if r.get('event')=='bw_info_end':result.update(pass_info=r.get('pass') is True,info=r);break
    else:raise TimeoutError('No bounded modem INFO result')
    return 0 if result.get('pass_info') else 1
   def case(baud,seconds):
    nonlocal current
    if time.monotonic()-suite_start>2700:raise TimeoutError('Original whole-suite deadline expired')
    nonce=secrets.randbelow(2**32-1)+1;ms=(seconds+(2 if seconds==60 else 1))*1000
    folder=a.out/f'case-{len(cases)+1:02d}-{baud}-{seconds}s';folder.mkdir()
    peer=Peer(a.bind,folder/'pi',nonce,baud,ms);native=None;case_records=[]
    start=time.monotonic();save(folder/'issued.json',dict(epoch=time.time(),known_old_baud=current,baud=baud,required_seconds=seconds,producer_ms=ms,nonce=nonce,port=peer.port))
    try:
     send(s,f'BENCH {current} {baud} {ms} {a.bind} {peer.port} {nonce}')
     for r in records(s,time.monotonic()+ms/1000+55):
      case_records.append(r)
      if r.get('event')=='bw_baud':current=baud;save(folder/'positive-baud.json',r)
      if r.get('event')=='bw_end':native=r;break
     if native is None:raise TimeoutError('No original finite P4 case terminal; no replay')
     if native['phase']=='new_baud_AT':current=baud
     peer.finished.wait(timeout=3)
     record=dict(baud=baud,required_seconds=seconds,host_seconds=time.monotonic()-start,native=native,pi=dict(peer.result),records=case_records,pass_case=False)
     try:record.update(evaluate(native,peer.result,seconds))
     except (ValueError,KeyError,TypeError) as e:record['error']=str(e)
     cases.append(record);save(folder/'result.json',record);print(json.dumps({k:record.get(k) for k in ['baud','required_seconds','pass_case','error','p4_to_pi_bytes_per_second','pi_to_p4_bytes_per_second']}),flush=True)
     if not native.get('cleanup') or not native.get('uart_retired'):raise RuntimeError('Retain failed case: cleanup unresolved, no next rate')
     return record['pass_case']
    finally:peer.close()
   highest=-1
   rates=[a.qualify_baud] if a.qualify_baud else RATES
   for i,baud in enumerate(rates):
    if not case(baud,2):break
    highest=i
   while highest>=0:
    qualified=True
    for seconds in [10,30,60]:
     if not case(rates[highest],seconds):qualified=False;break
    if qualified:
     result.update(pass_suite=True,max_qualified_baud=rates[highest],scope='Exact P4/AT1.3 ESP8266/Pi5 simultaneous CRC-checked workload; C8 untested');break
    highest-=1
   if not result.get('pass_suite'):result['error']='No rate met the full minute criterion'
  return 0 if result.get('pass_suite') else 1
 except Exception as e:result['error']=repr(e);raise
 finally:
  raw.flush();os.fsync(raw.fileno());raw.close();result['pass']=bool(result.get('pass_suite') or result.get('pass_info'));result.update(cases=cases,current_expected_modem_baud=current,elapsed_host_seconds=time.monotonic()-suite_start,console_sha256=hashlib.sha256((a.out/'console.bin').read_bytes()).hexdigest());save(a.out/'result.json',result)
if __name__=='__main__':raise SystemExit(main())
