from pathlib import Path
import json,datetime,hashlib,shutil,subprocess,os
r=Path('agents/web60');o=Path('agents/rle2-execution/candidate02');web=o/'source/vdp/video/extender/web';base=Path('agents/rle2-fullscreen-controls')
m=json.loads((base/'manifest.json').read_text());original={n:(web/n).read_bytes() for n in ['app.js','index.html','style.css']};(r/'web').mkdir(exist_ok=True)
try:
 for n in original:
  data=(base/'web'/n).read_bytes()
  if n=='app.js':
   assert data.count(b'1000/30')==1;data=data.replace(b'1000/30',b'1000/60')
  (web/n).write_bytes(data);(r/'web'/n).write_bytes(data)
 m['parent_build_id']=m['build_id'];m['build_id']='browser-credit60-r01-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
 with (r/'build.log').open('w') as f:subprocess.run([str(Path('.venv/bin/pio').resolve()),'run','-d',str((o/'source/vdp').resolve()),'-c',str((o/'platformio.ini').resolve()),'-e','p4-console'],env=dict(os.environ,AGON_EXTENDER_BUILD_ID=m['build_id'],AGON_EXTENDER_DSP_LIFETIME_FIX='1'),stdout=f,stderr=subprocess.STDOUT,check=True)
 m['outputs']={}
 for n in ['firmware.bin','firmware.factory.bin','firmware.elf','bootloader.bin','partitions.bin']:
  shutil.copy2(o/'build/p4-console'/n,r/n);data=(r/n).read_bytes();m['outputs'][n]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
 m['change']='Installed fullscreen r02 web assets, only credit cap 30 to 60';(r/'manifest.json').write_text(json.dumps(m,indent=2))
finally:
 for n,data in original.items():(web/n).write_bytes(data)
