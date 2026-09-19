from pathlib import Path
import queue,concurrent.futures.thread,sys,json,time,urllib.request
from playwright.sync_api import sync_playwright
sys.path.insert(0,'agents/qual004');from common import cli,SD,URL
R=Path('agents/pair-rle');T=Path('docs/tasks/BENCH-005/composed-packing/pair-rle')
for n in ['app.js','frame_protocol.js']:
 assert urllib.request.urlopen(URL+'/'+n,timeout=10).read()==(R/'web'/n).read_bytes()
c=SD(URL,R/'smoke02-sd.json')
try:c.connect();c.rpc(11)
finally:c.lock.close()
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader']);p=b.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.add_init_script('window.framesSeen=[];const Native=window.WebSocket;window.WebSocket=class extends Native{constructor(u,...a){super(u,...a);this.addEventListener("message",e=>{if(e.data instanceof ArrayBuffer&&e.data.byteLength>=32){let v=new DataView(e.data);window.framesSeen.push({magic:String.fromCharCode(...new Uint8Array(e.data,0,4)),w:v.getUint16(12,true),h:v.getUint16(14,true)});}})}};')
 p.goto(URL);p.click('#connect');cli('pair-default-smoke02','EXEC /test/pairrle/smoke.txt')
 c=SD(URL,R/'smoke02-end.json')
 try:
  end=time.monotonic()+180
  while time.monotonic()<end:
   p.wait_for_timeout(1000)
   if c.status()['online']:break
  else:raise RuntimeError('Nurples did not return')
  frames=p.evaluate('window.framesSeen');b.close();assert not errors and len(frames)>100
  assert all(f['magic']!='EVQ1' for f in frames)
  c.connect();tele=c.download('/test/pairrle/smoke.tele');assert tele[:4]==b'PNST' and not tele[0x44]&1;c.rpc(11)
 finally:c.lock.close()
(T/'SMOKE.json').write_text(json.dumps({'frames':len(frames),'formats':sorted({f['magic'] for f in frames}),'errors':errors,'served_assets_exact':True,'vblank_timeout':False,'observer_closed':True,'time':time.time()},indent=2)+'\n')
