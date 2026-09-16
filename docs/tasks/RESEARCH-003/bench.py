#!/usr/bin/env python3
"""Task-owned orchestration; machine identities supplied only in private config."""
from pathlib import Path
import subprocess,json,sys,hashlib,time,shutil,urllib.request
r=Path(__file__).resolve().parent;c=json.loads((r/'private/config.json').read_text());opts=c['ssh_options'];host=c['ssh_host'];remote=c['remote'];python=c['remote_python']
def ssh(*args):return subprocess.run(['ssh',*opts,host,*args],check=True)
def copy(files):subprocess.run(['scp','-q',*opts,*map(str,files),host+':'+remote+'/'],check=True)
if sys.argv[1]=='deploy':
 b=json.loads((r/'BUILD.json').read_text());d=r/'private/deploy';d.mkdir(exist_ok=True)
 for source,name in [(r/'firmware/.pio/build/reference/firmware.bin','candidate.bin'),(Path(c['baseline_dir'])/'firmware.bin','baseline.bin'),(Path(c['baseline_dir'])/'partitions.bin','partitions.bin')]:shutil.copy2(source,d/name)
 assert (r/'firmware/.pio/build/reference/partitions.bin').read_bytes()==(d/'partitions.bin').read_bytes()
 cfg={k:c[k] for k in ['port','serial','esptool']};cfg.update(build_id=b['build_id'],hashes={n:hashlib.sha256((d/n).read_bytes()).hexdigest() for n in ['candidate.bin','baseline.bin','partitions.bin']})
 (d/'bench.json').write_text(json.dumps(cfg))
 ssh('mkdir','-p',remote);copy([r/'deploy_on_pi.py',r/'receiver.py',*d.iterdir()])
 try:ssh(python,remote+'/deploy_on_pi.py')
 finally:subprocess.run(['scp','-q',*opts,host+':'+remote+'/deployment.json',str(d)+'/'],check=False)
 print('Flash verified; waiting for Ethernet',flush=True)
 for _ in range(30):
  try:
   with urllib.request.urlopen('http://'+c['p4_host']+'/status',timeout=2) as f:s=json.load(f)
   print(s,flush=True);break
  except Exception:time.sleep(1)
 else:raise RuntimeError('HTTP startup unavailable')
elif sys.argv[1]=='test':
 out=r/'evidence';out.mkdir(exist_ok=True)
 for repeat in range(2):
  for fps in [30,60]:
   for mode in ['render','send','combined']:
    name=f'{repeat}-{fps}-{mode}.json';print('RUN '+name,flush=True)
    progress={'state':'running','case':name,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};(r/'private/progress.json').write_text(json.dumps(progress))
    try:ssh(python,remote+'/receiver.py','--host',c['p4_host'],'--mode',mode,'--fps',str(fps),'--frames','600','--out',remote+'/'+name)
    finally:subprocess.run(['scp','-q',*opts,host+':'+remote+'/'+name,str(out)+'/'],check=False)
 (r/'private/progress.json').write_text(json.dumps({'state':'complete'}))
