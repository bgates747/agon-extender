from pathlib import Path
import queue,concurrent.futures.thread,sys,json,time,re,subprocess,urllib.request
sys.path.insert(0,'agents/qual004');from common import cli,SD,URL,path_payload
from playwright.sync_api import sync_playwright
r=Path('agents/pair-rle');out=r/'nurples';out.mkdir(exist_ok=False)
source=Path('agents/rle2-60');symbols={m.group(1):int(m.group(2),16) for m in re.finditer(r'^(\w+) \$([0-9a-fA-F]+)',(source/'cadence.symbols').read_text(),re.M)}
addr=symbols['bench_begin'];length=symbols['bench_end']-addr
names=['prior','pair','auto']
cli('pairrle-nurples-mkdir','MKDIR /test/pairrle','LOAD /extender/sdserve.bin','RUN . /')
c=SD(URL,out/'stage.json')
try:
 c.connect();c.upload('/test/pairrle/cadence.bin',Path('agents/srle2-hardware/cadence-fixedmode.bin').read_bytes(),True)
 for name in names:
  batch=f'EMOS EXCOM --keep-display\r\nCD /test/nurples\r\nLOAD /test/pairrle/cadence.bin\r\nRUN\r\nSAVE /test/pairrle/{name}.trace &{addr:X} &{length:X}\r\nSAVE /test/pairrle/{name}.tele &{symbols["telemetry_begin"]:X} &50\r\nEMOS LEGACY --keep-display\r\nLOAD /extender/sdserve.bin\r\nRUN . /\r\n'
  c.upload('/test/pairrle/'+name+'.txt',batch.encode(),True)
 # Previous transaction backup already preserved locally; keep it again before cleanup.
 (out/'previous-startup-backup.txt').write_bytes(c.download('/autoexec.txt.p17bak'));c.rpc(10,b'\3'+path_payload('/autoexec.txt'))
 startup=b'EMOS KEYINPUT extender\r\nEMOS LEGACY\r\nVDU 22 20\r\nEMOS EXCOM\r\nVDU 22 20\r\nEMOS LEGACY --keep-display\r\nLOAD /extender/sdserve.bin\r\nRUN . /\r\n'
 c.upload('/autoexec.txt',startup,True);c.rpc(11)
finally:c.lock.close()
subprocess.run(['/home/smith/Desktop/reset-agon.sh'],check=True);time.sleep(10)
c=SD(URL,out/'ready.json')
try:c.connect();assert c.download('/autoexec.txt')==startup;c.rpc(11)
finally:c.lock.close()
observer='''(() => {window.samples=[];window.closed=[];window.requests=[];window.presentations=[];let last=-1;function poll(){let e=document.querySelector("#presented");let n=e?parseInt(e.textContent):0;if(n!==last){window.presentations.push({ms:performance.now(),count:n});last=n;}requestAnimationFrame(poll);}requestAnimationFrame(poll);const Native=window.WebSocket;window.WebSocket=class extends Native{send(data){if(data==="frame")window.requests.push(performance.now());return super.send(data);}constructor(url,...args){let u=new URL(url);if(u.pathname==='/video')u.search=QUERY;super(u.href,...args);this.addEventListener('message',e=>{let b=e.data;if(!(b instanceof ArrayBuffer)||b.byteLength<32)return;let v=new DataView(b);window.samples.push({ms:performance.now(),magic:String.fromCharCode(...new Uint8Array(b,0,4)),bytes:b.byteLength,w:v.getUint16(12,true),h:v.getUint16(14,true),seq:v.getUint32(8,true),bits:b.byteLength>32?v.getUint8(32):null});});this.addEventListener('close',e=>window.closed.push(e.code));}};})();'''
def stats():return json.load(urllib.request.urlopen(URL+'/diagnostics/video-timing',timeout=20))
with sync_playwright() as pw:
 for name in names:
  subprocess.run(['/home/smith/Desktop/reset-agon.sh'],check=True);time.sleep(12)
  c=SD(URL,out/(name+'-fresh.json'))
  try:c.connect();c.rpc(11)
  finally:c.lock.close()
  browser=page=None;errors=[]
  if name!='off':
   query={'prior':'?rle2=1&packed=2','pair':'?pair=1','auto':'?rle2=1&packed=2&pair=1'}[name]
   browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader']);page=browser.new_page();page.add_init_script(observer.replace('QUERY',json.dumps(query)));page.on('pageerror',lambda e:errors.append(str(e)));page.goto(URL,wait_until='domcontentloaded');page.click('#connect');page.wait_for_timeout(1000)
  before=stats();began=time.time();cli('pairrle-nurples-'+name,'EXEC /test/pairrle/'+name+'.txt');print('Started',name,flush=True)
  c=SD(URL,out/(name+'-sd.json'))
  try:
   deadline=time.monotonic()+300
   while time.monotonic()<deadline:
    if page:page.wait_for_timeout(1000)
    else:time.sleep(1)
    if c.status()['online']:break
   else:raise RuntimeError('Fixture did not return; preserve state')
   # Close output before retrieval so service traffic does not pollute samples.
   result=dict(seconds=time.time()-began,errors=errors,stats_before=before,stats_after=stats())
   if page:
    result.update(page.evaluate('({frames:window.samples,requests:window.requests,presentations:window.presentations,closes:window.closed,received:document.querySelector("#received").textContent,presented:document.querySelector("#presented").textContent})'));browser.close()
   c.connect();trace=c.download('/test/pairrle/'+name+'.trace');tele=c.download('/test/pairrle/'+name+'.tele');(out/(name+'.trace')).write_bytes(trace);(out/(name+'.tele')).write_bytes(tele)
   assert trace[:8]==b'B003TIME' and len(trace)==length
   assert tele[:4]==b'PNST' and not tele[0x44]&1,'Vblank timeout'
   c.rpc(11)
  finally:c.lock.close()
  (out/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n');assert not errors,errors;print('Finished',name,flush=True)
(out/'complete.json').write_text(json.dumps(dict(complete=True,time=time.time()))+'\n')
