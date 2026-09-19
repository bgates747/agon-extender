from pathlib import Path
import subprocess,os,json,datetime,hashlib,shutil
r=Path('agents/pair-rle');o=Path('agents/rle2-execution/candidate02')
m={'build_id':'composed-packing-pair-rle-r01-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ'),'parent_build_id':json.loads(Path('agents/sixbit/manifest.json').read_text())['build_id'],'status':'experimental','commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'outputs':{}}
with (r/'build.log').open('w') as f:
 subprocess.run([str(Path('.venv/bin/pio').resolve()),'run','-d',str((o/'source/vdp').resolve()),'-c',str((o/'platformio.ini').resolve()),'-e','p4-console'],env=dict(os.environ,AGON_EXTENDER_BUILD_ID=m['build_id'],AGON_EXTENDER_DSP_LIFETIME_FIX='1'),stdout=f,stderr=subprocess.STDOUT,check=True)
for n in ['firmware.bin','firmware.factory.bin','firmware.elf','bootloader.bin','partitions.bin']:
 shutil.copy2(o/'build/p4-console'/n,r/n);data=(r/n).read_bytes();m['outputs'][n]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
(r/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(m['build_id'])
