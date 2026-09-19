"""All-mode bench runner. Private common module owns endpoint and reset wiring.
Modes selected in temporary startup only. Durable per-mode progress; fail stops.
"""
from pathlib import Path
import queue,concurrent.futures.thread,sys,json,time,subprocess,argparse,urllib.request
sys.path.insert(0,'agents/qual004');from common import cli,SD,URL,KB
T=Path('docs/tasks/BENCH-005/composed-packing');R=Path('agents/composed-packing')
p=argparse.ArgumentParser();p.add_argument('--modes',default='');p.add_argument('--label',required=True);p.add_argument('--seconds',type=float,default=4);a=p.parse_args();out=R/a.label;out.mkdir(exist_ok=False)
modes=json.loads((T/'modes.json').read_text())
if a.modes:modes=[m for m in modes if m['mode'] in list(map(int,a.modes.split(',')))]
def command(name,*args):cli('pack-'+a.label+'-'+name,*args)
def key(name,code):
 k=KB(URL,out/(name+'-key.json'))
 try:
  st=k.status();k.open(st);k.send([(code,1),(code,0)]);Path('agents/video-throughput/cli-latest.json').write_text(json.dumps(k.cancel()))
 finally:k.lock.close()
def sd(name):return SD(URL,out/(name+'-sd.json'))
for m in modes:
 mode=m['mode'];label=str(mode);dest=out/label;dest.mkdir();start=time.time();(dest/'progress.json').write_text(json.dumps({'mode':m,'state':'preparing','start':start}))
 command(label+'-service','EMOS LEGACY','LOAD /extender/sdserve.bin','RUN . /')
 startup=f"SET KEYBOARD 1\r\nEMOS KEYINPUT extender\r\nEMOS EXCOM\r\nVDU 22 {mode}\r\nLOAD /test/packing/packtest.bin\r\nRUN . /test/packing/c{7 if mode==7 else m['colours']}.vdu {m['width']} {m['height']} {m['colours']} {int(m['double'])}\r\n".encode()
 c=sd(label+'-startup')
 try:c.connect();c.upload('/autoexec.txt',startup,True);assert c.download('/autoexec.txt')==startup;c.rpc(11)
 finally:c.lock.close()
 subprocess.run(['/home/smith/Desktop/reset-agon.sh'],check=True,stdout=subprocess.DEVNULL);time.sleep(12)
 for activity in ['static','moving'] if mode!=7 else ['static']:
  if activity=='moving':key(label+'-animate',4);time.sleep(1)
  subprocess.run([sys.executable,str(T/'observe.py'),'--url',URL,'--output',str(dest/activity),'--seconds',str(a.seconds)],check=True)
  samples=json.loads((dest/activity/'samples.json').read_text())
  assert all(s['samples'][-1]['w']==m['width'] and s['samples'][-1]['h']==m['height'] for s in samples),'Mode geometry mismatch'
  if activity=='static':
   pixels=[(dest/activity/(name+'.rgb222')).read_bytes() for name in ['raw','rle2','packed','auto']]
   assert all(p==pixels[0] for p in pixels),'Static encoding pixel mismatch'
 key(label+'-exit',41);time.sleep(1)
 (dest/'progress.json').write_text(json.dumps({'mode':m,'state':'pass','start':start,'end':time.time()}))
 print('MODE',mode,'PASS',round(time.time()-start,1),'seconds',flush=True)
(out/'complete.json').write_text(json.dumps({'end':time.time(),'modes':[m['mode'] for m in modes]}))
