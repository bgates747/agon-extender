#!/usr/bin/env python3
"""Explicit isolated P4 UART peripheral loopback; no modem commands or flashing.

External modem GPIOs remain inputs. This validates the serializer/FIFO/ISR/ring
and concurrent producer/CRC consumer, not external wiring or an ESP8266 ceiling.
"""
import argparse,json,os,subprocess,time
from pathlib import Path
from passive_serial import open_passive_serial
ROOT=Path(__file__).resolve().parents[1]
def save(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def accepted(event,seconds):
 return (event.get('pass') is True and event.get('uart_retired') is True and
         event.get('tx_frames',0)==event.get('rx_frames',-1)>0 and
         all(event.get(k,-1)==0 for k in ['uart_errors','crc_errors','frame_errors','fifo_errors','ring_errors']) and
         event.get('queue_peak',128)<128 and event.get('rx_elapsed_us',0)>=seconds*1000000)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['port','lease','manifest','out']:p.add_argument('--'+name,required=True,type=Path if name in ['manifest','out'] else str)
 a=p.parse_args();a.out.mkdir(exist_ok=False);m=json.loads(a.manifest.read_text());pending=bytearray();cases=[];start=time.monotonic();result={'pass':False,'hardware_scope':'internal UART peripheral loopback, external GPIOs inputs','cases':cases}
 def own():
  r=json.loads(subprocess.run([str(ROOT.parent/'agon-dev-env/.venv/bin/python'),str(ROOT.parent/'agon-dev-env/cross-agent/olimex-bench/bench_lease.py'),'assert-owner','--owner','linux-extender','--lease',a.lease],check=True,capture_output=True,text=True).stdout)
  if not r.get('hardware_ready') or r.get('phase')!='consumer':raise RuntimeError('Actual sole admitted consumer custody required')
 def events(serial,deadline):
  report=0
  while time.monotonic()<deadline:
   chunk=serial.read(4096)
   if chunk:
    with (a.out/'console.bin').open('ab')as f:f.write(chunk)
    pending.extend(chunk)
   if len(pending)>32768:raise ValueError('Oversized control response')
   if time.monotonic()-report>5:
    report=time.monotonic();print('Host waiting for bounded UART control result; elapsed %.1fs'%(report-start),flush=True)
   while b'\n'in pending:
    line,_,tail=pending.partition(b'\n');pending[:]=tail
    if line.startswith(b'NET008 '):yield json.loads(line[7:])
 def send(serial,text):
  own();serial.write((text+'\n').encode('ascii'));serial.flush()
  with (a.out/'commands.jsonl').open('a')as f:f.write(json.dumps(dict(epoch=time.time(),command=text))+'\n')
 try:
  own()
  with open_passive_serial(a.port,timeout=.1)as serial:
   send(serial,'STATUS')
   for e in events(serial,time.monotonic()+8):
    if e.get('event')=='ready':
     if e.get('build')!=m['build_id'] or e.get('source')!=m['source_commit']:raise ValueError('Actual P4 identity mismatch')
     break
   else:raise TimeoutError('Stopped appliance unavailable')
   # Controlled source comparison at the old failing rate, then qualify the
   # corrected platform independently at the full selected UART ceiling.
   for baud,seconds,profile in [(384000,2,p)for p in range(5)]+[(1152000,s,4)for s in [2,10,30,60]]:
    if time.monotonic()-start>330:raise TimeoutError('Original finite control bound')
    ms=(seconds+2)*1000;send(serial,f'LOOPBACK {baud} {ms} {profile}');terminal=None;beg=time.monotonic()
    for e in events(serial,beg+ms/1000+25):
     if e.get('event')=='bw_task_unjoined':raise RuntimeError('Unjoined P4 TX task; no successor')
     if e.get('event')=='loop_end':terminal=e;break
    if terminal is None:raise TimeoutError('No loopback terminal; no replay')
    record=dict(baud=baud,required_seconds=seconds,profile=profile,native=terminal,accepted=accepted(terminal,seconds),elapsed_host_seconds=time.monotonic()-beg)
    cases.append(record);save(a.out/f'case-{len(cases):02d}.json',record);print(json.dumps(record),flush=True)
    if terminal.get('uart_retired') is not True:raise RuntimeError('UART not retired; no successor')
    if profile==4 and not record['accepted']:raise RuntimeError('Corrected platform failed; no modem ceiling claim')
   result['pass']=True;result['external_module_qualified']=False
  return 0
 except Exception as e:result['error']=str(e);return 1
 finally:result['elapsed_host_seconds']=time.monotonic()-start;save(a.out/'result.json',result)
if __name__=='__main__':raise SystemExit(main())
