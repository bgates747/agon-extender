"""Loopback recovery, bad-frame, fragmented-WebSocket and Worker deadline checks."""
import argparse,asyncio,json,struct,time
from pathlib import Path
from aiohttp import web,WSMsgType
from playwright.async_api import async_playwright
from replay import packet

def fragment(data,opcode,fin):
 n=len(data);h=bytes([(128 if fin else 0)|opcode]);return h+(bytes([n]) if n<126 else b'\x7e'+struct.pack('>H',n) if n<65536 else b'\x7f'+struct.pack('>Q',n))+data

async def run(a):
 a.output.mkdir(exist_ok=False);manifest=json.loads((a.corpus/'manifest.json').read_text());case=manifest[0];valid=packet(case,a.corpus,'srle2',0);raw=packet(case,a.corpus,'raw',0);active=None;mode='valid';sends=0;result=[];started=time.time()
 async def socket(req):
  nonlocal active,sends
  ws=web.WebSocketResponse();await ws.prepare(req)
  if active is not None and not active.closed:await active.close(code=1000,message=b'replaced')
  active=ws;local=mode;seq=0
  try:
   async for msg in ws:
    if msg.type!=WSMsgType.TEXT or msg.data!='frame':await ws.close(code=1002);break
    if seq>=3:continue
    data=valid if req.query.get('srle2')=='1' else raw
    if local=='bad-after-valid' and seq==1:data=b'EVS1'
    if local=='slow':await asyncio.sleep(.15)
    if local=='fragment':
     req.transport.write(fragment(data[:17],2,False));await asyncio.sleep(.01);req.transport.write(fragment(data[17:],0,True))
    else:await ws.send_bytes(data)
    sends+=1;seq+=1
  finally:
   if active is ws:active=None
  return ws
 async def index(req):return web.FileResponse(a.client/'index.html')
 async def hung(req):return web.Response(text='self.onmessage=()=>{while(true){}};',content_type='text/javascript')
 app=web.Application();app.router.add_get('/video',socket);app.router.add_get('/hung.js',hung);app.router.add_get('/',index);app.router.add_static('/',a.client);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();url='http://127.0.0.1:'+str(site._server.sockets[0].getsockname()[1])
 def record(name,**kw):result.append(dict(case=name,passed=True,**kw));(a.output/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(name,'PASS',flush=True)
 try:
  async with async_playwright() as pw:
   browser=await pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
   try:
    page=await browser.new_page()
    await page.add_init_script("window.wss=[];const N=WebSocket;window.WebSocket=class extends N{constructor(...a){super(...a);window.wss.push(this);}};")
    await page.goto(url)
    mutations={'short':b'EVS1','truncated':valid[:-1]}
    alpha=(a.native_edges/'alpha.srle2').read_bytes();b=bytearray(valid[:40]);struct.pack_into('<HHII',b,12,3,1,3,3);struct.pack_into('<II',b,32,len(alpha),16);mutations['asset-alpha-not-composed-frame']=bytes(b)+alpha
    for name,offset,values in [('zero-width',12,b'\0\0'),('bad-version',4,b'\2'),('bad-szip-version',53,b'\x7f'),('bad-order',64,b'\xff'),('bad-index',61,b'\xff\xff\xff'),('bad-mid',36,b'\xff\xff\xff\x7f'),('reserved',28,b'\1'),('bad-encoded-size',32,b'\0\0\0\0'),('oversized-width',12,b'\x01\x02'),('bad-record-size',65,b'\x02')]:
     b=bytearray(valid);b[offset:offset+len(values)]=values;mutations[name]=bytes(b)
    for name,data in mutations.items():
     got=await page.evaluate('''async ({data,valid})=>{const {FrameDecoder}=await import('./decoder.js');const d=new FrameDecoder();let error='';try{await d.decode(new Uint8Array(data).buffer);}catch(e){error=e.message;}if(!error)throw Error('bad frame accepted');const good=await d.decode(new Uint8Array(valid).buffer);d.reset();return {error,bytes:good.buffer.byteLength};}''',dict(data=list(data),valid=list(valid)))
     assert got['bytes']==len(raw);record(name,**got)
    timeout=await page.evaluate('''async()=>{const {FrameDecoder}=await import('./decoder.js');let ticks=0;const timer=setInterval(()=>ticks++,5);const d=new FrameDecoder({timeoutMs:80,workerURL:new URL('/hung.js',location.href)});let error='';try{await d.decode(new TextEncoder().encode('EVS1').buffer);}catch(e){error=e.message;}clearInterval(timer);d.reset();return {error,ticks};}''');assert timeout['error']=='Decoder timeout' and timeout['ticks']>1;record('worker-timeout-page-responsive',**timeout)
    # A single Worker must survive changing sizes and sort histories, not only identical frames.
    await page.evaluate("async()=>{const {FrameDecoder}=await import('./decoder.js');window.mixedDecoder=new FrameDecoder();}")
    for mixed in manifest+list(reversed(manifest)):
     b=packet(mixed,a.corpus,'srle2',0);expected=(a.corpus/mixed['name']/'raw.bin').read_bytes()
     exact=await page.evaluate('''async({data,expected})=>{const {parseFrame}=await import('./frame_protocol.js');const d=await window.mixedDecoder.decode(new Uint8Array(data).buffer);const p=parseFrame(d.buffer).pixels;return p.length===expected.length&&p.every((v,i)=>v===expected[i]);}''',dict(data=list(b),expected=list(expected)));assert exact,mixed['name']
    await page.evaluate('window.mixedDecoder.reset()');record('mixed-fixture-worker-reuse',frames=2*len(manifest))
    busy=await page.evaluate('''async(data)=>{const {FrameDecoder}=await import('./decoder.js');const d=new FrameDecoder();const a=d.decode(new Uint8Array(data).buffer);let error='';try{await d.decode(new Uint8Array(data).buffer);}catch(e){error=e.message;}await a;d.reset();return error;}''',list(valid));assert busy=='Decoder busy';record('single-inflight-admission')
    # Actual retained page: fragmented transport, slow source, protocol rejection and reconnect.
    for selected in ('fragment','slow','bad-after-valid','valid'):
     mode=selected;await page.goto(url);await page.evaluate("window.seen=[];window.addEventListener('agon-frame-decoded',e=>window.seen.push(Array.from(e.detail.pixels)));")
     await page.click('#connect')
     expected=1 if selected=='bad-after-valid' else 3
     await page.wait_for_function('(n)=>window.seen.length>=n',arg=expected,timeout=15000)
     if selected=='bad-after-valid':
      try:await page.wait_for_function("document.querySelector('#state').textContent==='disconnected'",timeout=10000)
      except Exception:
       (a.output/'unexpected-state.json').write_text(json.dumps(await page.evaluate("({state:document.querySelector('#state').textContent,seen:window.seen.length,sockets:window.wss.map(x=>x.readyState)})")));await page.screenshot(path=str(a.output/'unexpected.png'));raise
      count=await page.evaluate('window.seen.length');assert count==1
      assert await page.evaluate('window.wss[0].readyState')==3
      await page.screenshot(path=str(a.output/'last-valid-frame-retained.png'))
     pixels=await page.evaluate('window.seen');assert all(bytes(x)==(a.corpus/case['name']/'raw.bin').read_bytes() for x in pixels)
     record('client-'+selected,frames=len(pixels))
    # Withhold credit: producer must not send unsolicited frames or queue growth.
    mode='valid'
    slow=await page.evaluate('''async()=>{const s=new WebSocket(location.origin.replace('http','ws')+'/video');s.binaryType='arraybuffer';let n=0;s.onmessage=()=>n++;await new Promise(r=>s.onopen=r);await new Promise(r=>setTimeout(r,100));const before=n;s.send('frame');await new Promise(r=>setTimeout(r,200));const after=n;await new Promise(r=>setTimeout(r,200));const held=n;s.close();return {before,after,held};}''');assert slow==dict(before=0,after=1,held=1);record('slow-consumer-credit',**slow)
    # Non-negotiating clients receive raw; second connection displaces first.
    mode='valid'
    lifecycle=await page.evaluate('''async()=>{const url=location.origin.replace('http','ws')+'/video';const a=new WebSocket(url);a.binaryType='arraybuffer';await new Promise(r=>a.onopen=r);const closed=new Promise(r=>a.onclose=e=>r(e.code));const b=new WebSocket(url);b.binaryType='arraybuffer';await new Promise(r=>b.onopen=r);const next=new Promise(r=>b.onmessage=e=>r(String.fromCharCode(...new Uint8Array(e.data,0,4))));b.send('frame');const magic=await next;const close=await closed;b.close();return {magic,close};}''');assert lifecycle==dict(magic='EVF1',close=1000);record('takeover-and-raw-fallback',**lifecycle)
    (a.output/'complete.json').write_text(json.dumps(dict(complete=True,cases=len(result),sends=sends,seconds=time.time()-started))+'\n')
   finally:await browser.close()
 finally:
  if active is not None:await active.close()
  await runner.cleanup()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True);p.add_argument('--client',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--native-edges',type=Path,required=True);a=p.parse_args()
 try:asyncio.run(asyncio.wait_for(run(a),180))
 except Exception as e:a.output.mkdir(exist_ok=True);(a.output/'failure.json').write_text(json.dumps(dict(error=str(e),type=type(e).__name__))+'\n');raise
