#!/usr/bin/env python3
from pathlib import Path
import subprocess,datetime,json,os,hashlib
root=Path(__file__).resolve().parent;repo=root.parents[2]
assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo).strip(),'Commit inputs first'
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
id='research003-reference-r01-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
with (root/'private/build.log').open('w') as f:subprocess.run([str(repo/'.venv/bin/pio'),'run','-d',str(root/'firmware')],env=dict(os.environ,R3_BUILD_ID=id),stdout=f,stderr=subprocess.STDOUT,check=True)
b=root/'firmware/.pio/build/reference';out={}
for name in ['firmware.bin','bootloader.bin','partitions.bin']:
 data=(b/name).read_bytes();out[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
assert id.encode() in (b/'firmware.bin').read_bytes()
(root/'BUILD.json').write_text(json.dumps({'build_id':id,'status':'experimental','commit':commit,'dirty':False,'outputs':out},indent=2)+'\n')
print(id,flush=True)
