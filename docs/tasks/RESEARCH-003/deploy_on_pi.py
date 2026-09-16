#!/usr/bin/env python3
"""Task-local application-only deploy; configuration and dumps stay private."""
from pathlib import Path
import sys,json,hashlib,subprocess,os,time
r=Path(__file__).resolve().parent;c=json.loads((r/'bench.json').read_text())
def identity():
 p=Path(c['port']).resolve(strict=True)
 d=dict(x.split('=',1) for x in subprocess.check_output(['udevadm','info','--query=property','--name',str(p)],text=True).splitlines() if '=' in x)
 norm=lambda x:x.replace(':','').lower()
 assert norm(d.get('ID_SERIAL_SHORT',''))==norm(c['serial']) and os.access(p,os.R_OK|os.W_OK)
 return p
def command(label,args):
 identity()
 with (r/(label+'.log')).open('w') as f:subprocess.run([c['esptool'],'--chip','esp32p4','--port',c['port'],'--baud','460800',*args],stdout=f,stderr=subprocess.STDOUT,check=True)
for name in ['candidate.bin','baseline.bin','partitions.bin']:
 assert hashlib.sha256((r/name).read_bytes()).hexdigest()==c['hashes'][name]
command('preserve',['--before','usb_reset','--after','no_reset','read_flash','0x0','0x200000',str(r/'before.bin')])
data=(r/'before.bin').read_bytes();baseline=(r/'baseline.bin').read_bytes()
assert len(baseline)+0x20000<=len(data)
assert data[0x20000:0x20000+len(baseline)]==baseline,'Unexpected app, stopped before write'
assert data[0x8000:0x8c00]==(r/'partitions.bin').read_bytes()[:3072],'Unexpected partition'
command('write',['--before','no_reset','--after','no_reset','write_flash','0x20000',str(r/'candidate.bin')])
command('verify',['--before','no_reset','--after','hard_reset','verify_flash','0x20000',str(r/'candidate.bin')])
(r/'deployment.json').write_text(json.dumps({'app_verified':True,'boot_partition_nvs_written':False,'build_id':c['build_id'],'hashes':c['hashes'],'before_sha256':hashlib.sha256(data).hexdigest()},indent=2)+'\n')
