#!/usr/bin/env python3
"""Run supplemental presentation controls with benchmark-specific P4 hooks absent.

The caller installs/verifies the preserved ordinary image and proves CLI first.
This runner never selects or flashes firmware. Selection files retain affected
runs/cases and their setup prefixes. Ordinary serial logging can suppress a
zero-update window; silence is therefore inconclusive output evidence.
"""
import argparse,datetime,hashlib,json,os,select,sys,termios,threading,time,tty,urllib.request
from pathlib import Path
from render_load import Bench,utc,digest
HOST_SOURCE_SHA256=digest(Path(__file__).read_bytes())

def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def status(b,path):
 with urllib.request.urlopen(b.config['p4']+path,timeout=5) as r:return json.load(r)

def verify_image(config,image):
 manifest=json.loads((image/'manifest.json').read_text())
 current=json.loads(Path(config['installation_record']).read_text())
 receipt=json.loads(Path(current['receipt']).read_text())
 assert current['variant']=='ordinary-hdmi' and current['build_id']==manifest['build_id']==receipt['build_id'] and receipt['outcome']=='pass'
 assert manifest['idf_commit']=='b774170ff46c393eeb5e495ea37936038d3f4f4f' and manifest['display_output']=='hdmi'
 compile_path=image/'build/compile_commands.json'
 expected=next(a['sha256'] for a in manifest['artifacts'] if a['path'].endswith('/compile_commands.json'))
 assert digest(compile_path.read_bytes())==expected
 commands=json.loads(compile_path.read_text())
 relevant=[c for c in commands if any(c['file'].endswith(n) for n in ('hdmi_output.cpp','stock_p4_service.cpp','stock_native_access.cpp','video.ino.cpp'))]
 assert len(relevant)>=3
 for command in relevant:
  text=command.get('command',' '.join(command.get('arguments',[])))
  assert 'AGON_EXTENDER_RENDER_BENCHMARK' not in text and 'AGON_EXTENDER_BENCH_HOLD' not in text and 'AGON_EXTENDER_BENCH_OFF' not in text
 assert all('AGON_EXTENDER_RENDER_BENCHMARK' not in c.get('command',' '.join(c.get('arguments',[]))) for c in commands)
 return dict(build_id=manifest['build_id'],installation_receipt=current['receipt'],manifest_sha256=digest((image/'manifest.json').read_bytes()),compile_commands_sha256=expected,checked_translation_units=[Path(c['file']).name for c in relevant],scope='Benchmark-specific window/phase/marker hooks absent; ordinary image logging retained')

class PassiveSerial:
 def __init__(self,config,out):
  self.out=out;self.stop=threading.Event();self.errors=[];self.count=0
  port=Path(config['serial_port']);node=port.resolve(strict=True)
  device=(Path('/sys/class/tty')/node.name/'device').resolve()
  serials=[(p/'serial').read_text().strip() for p in device.parents if (p/'serial').is_file()]
  assert config['usb_serial'] in serials
  self.fd=os.open(str(port),os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)
  tty.setraw(self.fd,termios.TCSANOW);cfg=termios.tcgetattr(self.fd)
  cfg[2]=(cfg[2]|termios.CLOCAL|termios.CREAD)&~termios.HUPCL;cfg[4]=cfg[5]=termios.B115200
  termios.tcsetattr(self.fd,termios.TCSANOW,cfg)
  self.started=time.monotonic();self.utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
  self.thread=threading.Thread(target=self.read,daemon=True);self.thread.start()
 def read(self):
  try:
   with (self.out/'passive-serial.log').open('wb',buffering=0) as log,(self.out/'serial-chunks.jsonl').open('w') as chunks:
    while not self.stop.is_set() and time.monotonic()-self.started<7200:
     if select.select([self.fd],[],[],.25)[0]:
      data=os.read(self.fd,8192)
      if not data:raise RuntimeError('Serial endpoint closed during control')
      chunks.write(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-self.started,offset=self.count,bytes=len(data)))+'\n');chunks.flush()
      log.write(data);self.count+=len(data)
  except Exception as error:self.errors.append(repr(error))
 def close(self):
  self.stop.set();self.thread.join(3);os.close(self.fd)
  path=self.out/'passive-serial.log'
  return dict(started_utc=self.utc,elapsed_seconds=time.monotonic()-self.started,bytes=self.count,sha256=digest(path.read_bytes()) if path.exists() else None,errors=self.errors,serial_commands_sent=False,modem_lines_toggled=False,clock_scope='Host arrival timestamps; serial backlog and ordinary report windows prevent exact per-case output attribution')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--selection',type=Path,required=True);p.add_argument('--image',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
 assert not a.receipt.exists(),'Preserve the previous control receipt'
 a.receipt.parent.mkdir(parents=True,exist_ok=True)
 assert not (a.receipt.parent/'passive-serial.log').exists(),'Choose a fresh capture directory'
 b=Bench(a.config,a.evidence);assert b.config.get('require_benchmark_telemetry') is False
 image=verify_image(b.config,a.image);selection=json.loads(a.selection.read_text())
 assert selection and all(0<=r['first']<r['end']<=94 for r in selection)
 receipt=dict(started_utc=utc(),outcome='running',image=image,selection=selection,runs=[],host_source_sha256=HOST_SOURCE_SHA256,limits='No physical displayed-FPS observation. Ordinary logger omits all-zero submission windows; silence cannot prove zero output.')
 write(a.receipt,receipt)
 # Read-only admitted metadata establishes CLI before typing listener commands.
 code,_=b.request('HEAD','/autoexec.txt',timeout=5)
 if code!=200:
  receipt.update(outcome='preparation-fail',failure=f'CLI metadata not admitted: {code}');write(a.receipt,receipt);raise RuntimeError(receipt['failure'])
 before=status(b,'/keyboard/status');capture=PassiveSerial(b.config,a.receipt.parent)
 try:
  b.fast_start()
  for row in selection:
   context=dict(scope='Benchmark-specific P4 hooks absent; eZ80 timing reads suppressed; bounded fence watchdog retained',original_runs=row['source_runs'],affected_cases=row['affected_cases'],history_first_case=row['first'],history_end_case=row['end'],frame_count_limit='Original 20s/10s key cadence retained; repeat counts may differ without probes')
   folder=b.run(row['mode'],'p4',row['first'],row['end'],20,1100,'normal',10,disable_timing=True,suite='presentation-no-hook-controls-r04',pass_number=0,control_context=context)
   meta=json.loads((folder/'run.json').read_text());receipt['runs'].append(dict(run=folder.name,outcome=meta['outcome']));write(a.receipt,receipt)
   if meta['outcome']!='pass':raise RuntimeError('Control did not complete its selected prefix; retain evidence for recovery')
  receipt['outcome']='controls-complete-restoration-pending'
 except Exception as error:
  receipt.update(outcome='stopped-on-unresolved-boundary',failure=repr(error));raise
 finally:
  receipt['serial']=capture.close()
  try:after=status(b,'/keyboard/status');receipt['p4_boot_unchanged']=before['boot']==after['boot']
  except Exception as error:receipt['post_status_error']=repr(error)
  receipt['finished_utc']=utc();write(a.receipt,receipt)
  if b.sd:b.sd.lock.close();b.sd=None
 # The ordinary image stays installed. Restore startup before resetting either
 # processor; a recovery boundary above leaves state intact instead of typing.
 assert status(b,'/sd/status')['online'];b=Bench(a.config,a.evidence);b.restore()
 if b.config.get('p4_reset_command'):
  import subprocess
  with (a.receipt.parent/'p4-final-reset.log').open('w') as log:subprocess.run(b.config['p4_reset_command'],check=True,timeout=30,stdout=log,stderr=subprocess.STDOUT)
  boot_limit=time.monotonic()+30
  while time.monotonic()<boot_limit:
   try:status(b,'/keyboard/status');break
   except Exception:time.sleep(.5)
  else:raise RuntimeError('Ordinary P4 application did not become reachable before Agon re-enrolment')
  b.reset()
 limit=time.monotonic()+45
 while time.monotonic()<limit:
  try:
   if status(b,'/keyboard/status').get('ready'):break
  except Exception:pass
  time.sleep(.5)
 else:raise RuntimeError('Ordinary-image input admission did not recover')
 code,data=b.request('GET','/autoexec.txt',timeout=60);assert code==200 and data==(a.evidence/'original-autoexec.txt').read_bytes()
 receipt['restoration']=dict(outcome='pass',startup_sha256=digest(data),keyboard=status(b,'/keyboard/status'),display=status(b,'/display/status'));receipt['outcome']='completed-controls-output-observation-inconclusive';write(a.receipt,receipt)
 print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
