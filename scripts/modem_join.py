#!/usr/bin/env python3
"""One private, runtime-only ESP8266 CUR association under admitted NET-008 custody.

OS Python alone supplies libsecret/GI; its stdout is a private pipe, never a
credential file or command argument. No flash, reset, sniffing or lease release.
"""
import argparse,json,os,resource,subprocess,sys,time,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def harden():
 os.umask(0o077);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 import ctypes
 if ctypes.CDLL(None,use_errno=True).prctl(4,0,0,0,0)!=0:raise RuntimeError('Cannot disable process dumps')

def wipe(data):data[:]=b'\0'*len(data)

def wire_packet(packet):
 if len(packet)<10 or packet[:4]!=b'MWJ1':raise ValueError('Invalid private credential format')
 ns,np=packet[4:6]
 if not 1<=ns<=32 or np>64 or len(packet)!=10+ns+np:raise ValueError('Invalid private credential length')
 if zlib.crc32(memoryview(packet)[:-4])!=int.from_bytes(packet[-4:],'little'):raise ValueError('Invalid private credential checksum')
 if any(c<32 or c==127 for c in packet[6:6+ns]) or any(c<32 or c>126 for c in packet[6+ns:-4]):raise ValueError('Invalid private credential character')
 return bytearray(packet[4:-4])

def emit_private():
 harden()
 if sys.stdout.isatty():raise RuntimeError('Private supplier requires a pipe')
 os.environ['DBUS_SESSION_BUS_ADDRESS']='unix:path=/run/user/'+str(os.getuid())+'/bus'
 sys.path.insert(0,str(ROOT.parent/'agon-hardware-wroom-reference/extender/scripts'))
 from wifi_credential_store import LoginKeyring
 packet=bytearray()
 try:
  with LoginKeyring() as store:packet=store.load()
  wire=wire_packet(packet);wipe(wire)
  view=memoryview(packet)
  while view:
   n=os.write(sys.stdout.fileno(),view);view=view[n:]
 finally:wipe(packet)

def load_private():
 packet=bytearray(128);used=0
 try:
  with subprocess.Popen(['/usr/bin/python3',str(Path(__file__).resolve()),'--emit-private-packet'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL) as child:
   try:
    # Supplier is finite; select avoids an indefinitely unavailable keyring.
    import select
    end=time.monotonic()+15
    while used<len(packet):
     if not select.select([child.stdout],[],[],max(0,end-time.monotonic()))[0]:raise TimeoutError('Private keyring supplier timed out')
     n=os.readv(child.stdout.fileno(),[memoryview(packet)[used:]])
     if not n:break
     used+=n
     if time.monotonic()>=end:raise TimeoutError('Private keyring supplier timed out')
    if used==len(packet):raise ValueError('Oversized private credential packet')
    if child.wait(timeout=2)!=0:raise RuntimeError('Pi keyring entry unavailable or locked; no credentials transmitted')
   finally:
    if child.poll() is None:child.kill();child.wait()
  del packet[used:]
  return wire_packet(packet)
 finally:wipe(packet)

def main():
 harden()
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['port','lease','manifest','out']:p.add_argument('--'+name,required=True,type=Path if name in ['manifest','out'] else str)
 p.add_argument('--baud',type=int,default=115200);a=p.parse_args()
 if a.baud not in [115200,230400,384000,576000,1152000]:p.error('Unknown modem baud')
 from passive_serial import open_passive_serial
 manifest=json.loads(a.manifest.read_text());a.out.mkdir(exist_ok=False)
 def own():
  r=json.loads(subprocess.run([str(ROOT.parent/'agon-dev-env/.venv/bin/python'),str(ROOT.parent/'agon-dev-env/cross-agent/olimex-bench/bench_lease.py'),'assert-owner','--owner','linux-extender','--lease',a.lease],check=True,capture_output=True,text=True).stdout)
  if r.get('hardware_ready') is not True or r.get('phase')!='consumer':raise RuntimeError('Current admitted consumer custody required')
 pending=bytearray();wire=bytearray();result={'pass':False,'bench_held':True,'firmware_retained':True};start=time.monotonic()
 def events(serial,deadline):
  while time.monotonic()<deadline:
   pending.extend(serial.read(4096))
   if len(pending)>16384:raise RuntimeError('Unexpected oversized USB response')
   while b'\n' in pending:
    line,_,tail=pending.partition(b'\n');pending[:]=tail
    if not line.startswith(b'NET008 '):continue
    event=json.loads(line[7:])
    # Never store raw console bytes or arbitrary firmware fields in this path.
    yield event
 try:
  own();wire=load_private()
  with open_passive_serial(a.port,timeout=.1) as serial:
   own();serial.write(b'STATUS\n');serial.flush()
   for event in events(serial,time.monotonic()+8):
    if event.get('event')=='ready':
     if event.get('build')!=manifest['build_id'] or event.get('source')!=manifest['source_commit']:raise RuntimeError('Stopped P4 identity differs from manifest')
     break
   else:raise TimeoutError('No identified stopped P4 response')
   own();serial.write(('JOIN '+str(a.baud)+'\n').encode('ascii'));serial.flush()
   for event in events(serial,time.monotonic()+5):
    if event.get('event')=='join_input_ready':break
   else:raise TimeoutError('No private input-ready response; credentials withheld')
   own();serial.write(wire);serial.flush();wipe(wire)
   for event in events(serial,time.monotonic()+100):
    kind=event.get('event')
    if kind=='join_progress':
     phase=event.get('phase')
     if phase in ['association','DHCP']:print('Modem connection phase: '+phase,flush=True)
    if kind=='join_end':
     phase=event.get('phase')
     if phase not in ['credentials','private_input','uart_init','AT','station_mode','association','DHCP','complete']:raise RuntimeError('Unknown private result phase')
     safe={k:event.get(k) is True for k in ['pass','ip_ready','uart_retired']};safe['phase']=phase
     result.update(safe);result['pass']=all(safe[k] for k in ['pass','ip_ready','uart_retired']);break
   else:raise TimeoutError('No bounded JOIN terminal; no replay')
  return 0 if result['pass'] else 1
 except Exception as error:
  # Exceptions from packet/supplier code contain only fixed diagnostic text.
  result['error_type']=type(error).__name__;print('Connection attempt stopped: '+type(error).__name__,file=sys.stderr);return 1
 finally:
  wipe(wire);wipe(pending);result['elapsed_host_seconds']=time.monotonic()-start
  with (a.out/'result.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
if __name__=='__main__':
 if sys.argv[1:]==['--emit-private-packet']:
  try:emit_private()
  except Exception:raise SystemExit(2)
 else:raise SystemExit(main())
