"""One additional attempt for the known mainboard scanout crash, never a fix.

Run via the private common bench adapter after previous controllers stop.
Unknown acquisition failures stop immediately. Failed attempts remain failures.
"""
from common import *
import argparse,re,gzip

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',required=True)
p.add_argument('--cases',required=True,type=Path)
p.add_argument('--first-attempt',type=int,default=1,choices=(1,2))
p.add_argument('--token-base',type=int,required=True)
a=p.parse_args();out=R/a.output;out.mkdir(exist_ok=False)
names=json.loads(a.cases.read_text());results=[]
for index,name in enumerate(names):
 paired=False
 for attempt in range(a.first_attempt if index==0 else 1,3):
  if time.time()>1789585860:raise RuntimeError('Restoration reserve reached')
  # Each child ends with SD running on success. Recovery resets before retry.
  reset_mainboard(f'{out.name}-{name}-{attempt}-admission')
  offset=(R/'serial.bin').stat().st_size
  child=f'{a.output}/{name}-a{attempt}';log=out/f'{name}-a{attempt}.log'
  start=time.time()
  with log.open('w') as f:
   proc=subprocess.run([sys.executable,'docs/tasks/QUAL-004/run_hardware.py',
       '--output',child,'--cases',name,'--fresh-mainboard',
       '--token-base',str(a.token_base+index*4+(attempt-1)*2)],stdout=f,stderr=subprocess.STDOUT)
  if proc.returncode==0:
   record=json.loads((R/child/name/'run.json').read_text())
   results.append(dict(case=name,attempt=attempt,status=record['status'],path=child))
   paired=True
   print(name,record['status'],'attempt',attempt,flush=True)
   break
  raw=(R/'serial.bin').read_bytes()[offset:]
  known=(b'Guru Meditation Error' in raw and
         re.search(rb'PC\s+: 0x40083247\b',raw) is not None and
         re.search(rb'EXCVADDR: 0x0000001c\b',raw) is not None)
  dest=R/child/name;dest.mkdir(exist_ok=True)
  (dest/'failure.serial.gz').write_bytes(gzip.compress(raw,mtime=0))
  record_path=dest/'run.json'
  record=json.loads(record_path.read_text()) if record_path.exists() else {'case':{'name':name},'start':start}
  record.update(status='invalid_mainboard_crash' if known else 'invalid_acquisition',
                end=time.time(),returncode=proc.returncode,
                retry_policy='At most one additional attempt for exact known stock scanout signature')
  record_path.write_text(json.dumps(record,indent=2)+'\n')
  results.append(dict(case=name,attempt=attempt,status=record['status'],path=child))
  (out/'attempts.json').write_text(json.dumps(results,indent=2)+'\n')
  if not known:raise RuntimeError(name+': unknown acquisition failure; inspect before continuing')
  print(name,'known stock crash; attempt',attempt,flush=True)
 if not paired:print(name,'unqualified after bounded attempts',flush=True)
 (out/'attempts.json').write_text(json.dumps(results,indent=2)+'\n')
# Final case can have failed; establish a fresh known startup/service regardless.
reset_mainboard(out.name+'-finish')
(out/'complete.json').write_text(json.dumps({'end':time.time(),'cases':len(names),
 'paired':sum(x['status'] in ('pass','mismatch') for x in results),
 'unqualified':sum(not any(x['case']==n and x['status'] in ('pass','mismatch') for x in results) for n in names)},indent=2)+'\n')
