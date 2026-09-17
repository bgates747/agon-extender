"""Loopback-only real-client SRLE2 replay and exact browser-pixel comparison."""
import argparse,asyncio,json,struct,time,hashlib,statistics,platform
from pathlib import Path
from aiohttp import web,WSMsgType
from playwright.async_api import async_playwright

def packet(case,root,codec,seq):
 payload=(root/case['name']/(codec+'.bin')).read_bytes();head=bytearray(40 if codec=='srle2' else 32)
 head[:4]={'raw':b'EVF1','rle2':b'EVR1','srle2':b'EVS1'}[codec]
 struct.pack_into('<BBBBIHHIIII',head,4,1,len(head),2,1,seq,case['width'],case['height'],case['stride'],case['width']*case['height'],33333,0)
 if codec=='srle2':struct.pack_into('<II',head,32,len(payload),case['files']['rle2']['bytes'])
 return bytes(head)+payload

def stats(v):
 s=sorted(v)
 return dict(n=len(s),mean=statistics.mean(s),p95=s[min(len(s)-1,int(len(s)*.95))],maximum=s[-1]) if s else None

async def run(a):
 a.output.mkdir(exist_ok=False);start=time.time();manifest=json.loads((a.corpus/'manifest.json').read_text());events=(a.output/'events.jsonl').open('w');active=None;setting={};results=[]
 def log(**v):events.write(json.dumps(dict(at=time.time(),**v))+'\n');events.flush()
 async def socket(req):
  nonlocal active
  ws=web.WebSocketResponse();await ws.prepare(req)
  if active and not active.closed:await active.close(code=1000,message=b'replaced')
  active=ws;selected=dict(setting);seq=0;last=0
  try:
   async for msg in ws:
    if msg.type not in (WSMsgType.TEXT,WSMsgType.BINARY):continue
    if msg.type!=WSMsgType.TEXT or msg.data!='frame':
     await ws.close(code=1002,message=b'invalid credit');break
    if seq>=a.count:continue
    if a.pace:await asyncio.sleep(max(0,last+1/a.pace-time.monotonic()))
    codec=selected['codec']
    if codec=='srle2' and req.query.get('srle2')!='1':codec='raw'
    data=packet(selected['case'],a.corpus,codec,seq);await ws.send_bytes(data);last=time.monotonic();log(event='send',case=selected['case']['name'],codec=codec,sequence=seq,bytes=len(data));seq+=1
  finally:
   if active is ws:active=None
  return ws
 async def index(req):return web.FileResponse(a.client/'index.html')
 app=web.Application();app.router.add_get('/video',socket);app.router.add_get('/',index);app.router.add_static('/',a.client)
 runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();port=site._server.sockets[0].getsockname()[1];url=f'http://127.0.0.1:{port}'
 try:
  async with async_playwright() as pw:
   options={'headless':True,'args':['--enable-unsafe-swiftshader']}
   if a.browser:options['executable_path']=a.browser
   browser=await pw.chromium.launch(**options)
   try:
    page=await browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    await page.add_init_script('''window.decodeRows=[];window.submitRows=[];window.expected=[];
window.addEventListener('agon-frame-decoded',e=>{const p=e.detail.pixels;let mismatch=p.length===window.expected.length?-1:Math.min(p.length,window.expected.length);for(let i=0;mismatch<0&&i<p.length;i++)if(p[i]!==window.expected[i])mismatch=i;window.decodeRows.push({at:performance.now(),mismatch,...e.detail.metrics});});
window.addEventListener('agon-frame-submitted',e=>window.submitRows.push(e.detail.ms));''')
    for case in manifest:
     for codec in ('raw','rle2','srle2'):
      setting.update(case=case,codec=codec);await page.goto(url,wait_until='domcontentloaded');await page.evaluate('(p)=>window.expected=p',list((a.corpus/case['name']/'raw.bin').read_bytes()));await page.click('#connect')
      await page.wait_for_function('(n)=>window.decodeRows.length>=n',arg=a.count,timeout=30000)
      await page.wait_for_function('(n)=>window.submitRows.length>=n',arg=a.count,timeout=5000)
      rows=await page.evaluate('({decode:window.decodeRows,submit:window.submitRows,state:document.querySelector("#state").textContent})')
      assert not errors,errors;assert all(x['mismatch']==-1 for x in rows['decode']),(case['name'],codec,rows)
      steady=rows['decode'][min(2,a.count-1):];intervals=[y['at']-x['at'] for x,y in zip(steady,steady[1:])]
      result=dict(case=case['name'],codec=codec,exact=True,frames=len(rows['decode']),message_bytes=len(packet(case,a.corpus,codec,0)),decode_ms=stats([x['totalMs'] for x in steady]),szip_ms=stats([x['szipMs'] for x in steady]),rle_ms=stats([x['rleMs'] for x in steady]),parse_ms=stats([x.get('parseMs',0) for x in steady]),submit_ms=stats(rows['submit'][min(2,a.count-1):]),receive_interval_ms=stats(intervals),samples=rows)
      results.append(result);(a.output/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(case['name'],codec,'PASS',flush=True)
    await page.screenshot(path=str(a.output/'last-frame.png'))
    (a.output/'environment.json').write_text(json.dumps(dict(browser=browser.version,platform=platform.platform(),transport='loopback',forced_codec=True,palette_conversion='GPU shader; inseparable from presentation submission',pace=a.pace,count=a.count,seconds=time.time()-start,errors=errors),indent=2)+'\n')
   finally:await browser.close()
 finally:
  if active:await active.close()
  await runner.cleanup();events.close()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True);p.add_argument('--client',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--pace',type=float,default=30);p.add_argument('--count',type=int,default=12);p.add_argument('--browser');a=p.parse_args();assert 0<=a.pace<=30 and 3<=a.count<=300
 try:asyncio.run(asyncio.wait_for(run(a),900))
 except Exception as e:
  a.output.mkdir(exist_ok=True);(a.output/'failure.json').write_text(json.dumps(dict(error=str(e),type=type(e).__name__))+'\n');raise
