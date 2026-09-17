"""Loopback-only EVC1 browser qualification. Never contacts a physical device."""
import argparse,asyncio,json,struct,time,shutil,statistics,platform
from pathlib import Path
from aiohttp import web,WSMsgType
from playwright.async_api import async_playwright
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent.parent

def packet(c,v,seq):
 payload=(a.native/c['name']/(v['id']+'.bin')).read_bytes();head=bytearray(32);head[:4]=b'EVC1';struct.pack_into('<BBBBIHHII',head,4,1,32,{'raw':0,'rle2':1,'szip':2,'srle2':3,'png':4}[v['kind']],0,seq,c['width'],c['height'],c['width']*c['height'],len(payload));return bytes(head)+payload

def select(rows,variants,cases):
 for v in variants:
  assert sum(r['exact'] for r in rows if r['variant']==v['id'])==len(cases),v
 return variants

async def run():
 a.out.mkdir(exist_ok=False);start=time.time();client=a.out/'client';client.mkdir();cases=json.loads((a.native/'manifest.json').read_text());variants=json.loads((a.native/'variants.json').read_text());native=json.loads((a.native/'results.json').read_text());selected=select(native,variants,cases);(a.out/'selected.json').write_text(json.dumps(selected,indent=2))
 for name in ('client.js','worker.js','decoder.js','envelope.js'):shutil.copy(root/name,client/name)
 shutil.copy(root.parent/'srle2/vendor/COPYING.GPL-2',client/'COPYING.GPL-2')
 for name in ('szip.js','szip.wasm'):shutil.copy(a.build/name,client/name)
 shutil.copy(root.parent/'codec/web_decode.js',client/'web_decode.js')
 for name in ('webgl2_presenter.js','frame_protocol.js'):shutil.copy(root.parent/'srle2/web/client-source'/name,client/name)
 (client/'index.html').write_text('<!doctype html><canvas></canvas><script type="module" src="client.js"></script>')
 setting={};results=[];events=(a.out/'events.jsonl').open('w')
 async def raw(req):return web.FileResponse(a.native/req.match_info['name']/'raw.bin')
 async def socket(req):
  ws=web.WebSocketResponse();await ws.prepare(req);cfg=dict(setting);seq=0;last=0
  async for msg in ws:
   if msg.type!=WSMsgType.TEXT or msg.data!='frame':await ws.close();break
   if seq>=cfg['count']:continue
   if cfg['pace']:await asyncio.sleep(max(0,last+1/cfg['pace']-time.monotonic()))
   c=cfg['cases'][seq%len(cfg['cases'])];actual=cfg['variant'];data=packet(c,actual,seq)
   if cfg.get('fallback') and len(data)>=32+c['width']*c['height']:actual=variants[0];data=packet(c,actual,seq)
   await ws.send_bytes(data);last=time.monotonic();events.write(json.dumps(dict(at=time.time(),seq=seq,case=c['name'],variant=actual['id'],bytes=len(data)))+'\n');events.flush();seq+=1
  return ws
 app=web.Application();app.router.add_get('/video',socket);app.router.add_get('/raw/{name}',raw);app.router.add_get('/',lambda r:web.FileResponse(client/'index.html'));app.router.add_static('/',client);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();port=site._server.sockets[0].getsockname()[1]
 try:
  async with async_playwright() as pw:
   browser=await pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader']);page=await browser.new_page();await page.goto(f'http://127.0.0.1:{port}');await page.wait_for_function('window.ready===true')
   for phase in ('exact','paced','fallback'):
    for v in (selected if phase!='fallback' else [next(v for v in selected if v['kind']=='srle2')]):
     groups=[[c] for c in cases] if phase=='exact' else ([cases] if phase=='fallback' else [[c for c in cases if c['width']==512]])
     for group in groups:
      count=8 if phase=='exact' else 24 if phase=='fallback' else 90;setting.update(cases=group,variant=v,count=count,pace=30 if phase=='paced' else 0,fallback=phase=='fallback')
      samples=await page.evaluate('(c)=>window.run(c)',dict(cases=[c['name'] for c in group],count=count,verify=phase!='paced'));assert all(s['mismatch']==-1 for s in samples)
      steady=samples[2:];intervals=[b['at']-x['at'] for x,b in zip(steady,steady[1:])]
      result=dict(phase=phase,variant=v['id'],cases=[c['name'] for c in group],frames=count,exact=phase!='paced',decode_wall_ms=statistics.mean(s['decodeWallMs'] for s in steady),decode_ms=statistics.mean(s.get('decodeMs',0) for s in steady),submit_ms=statistics.mean(s['submitMs'] for s in steady),fps=1000/statistics.mean(intervals),samples=samples)
      results.append(result);(a.out/'results.json').write_text(json.dumps(results,indent=2));print(phase,v['id'],group[0]['name'],'PASS',flush=True)
   # Invalid envelope, unknown codec, malformed CmpS/PNG, recovery after each.
   c=cases[0];rawv=variants[0];valid=packet(c,rawv,0);bad=[b'x',valid[:-1]];b=bytearray(valid);b[6]=99;bad.append(bytes(b))
   for kind in ('srle2',):
    v=next(v for v in selected if v['kind']==kind);b=bytearray(packet(c,v,0));b[32]=0;bad.append(bytes(b))
   edges=[]
   for b in bad:
    answer=await page.evaluate('(b)=>window.edge(b)',list(b));assert answer!='accepted';assert await page.evaluate('(b)=>window.edge(b)',list(valid))=='accepted';edges.append(answer)
   edges.append(await page.evaluate('(b)=>window.timeoutEdge(b)',list(packet(c,next(v for v in selected if v['kind']=='srle2'),0))))
   assert await page.evaluate('(b)=>window.edge(b)',list(valid))=='accepted'
   (a.out/'edges.json').write_text(json.dumps(edges,indent=2));await page.screenshot(path=str(a.out/'last-frame.png'))
   (a.out/'complete.json').write_text(json.dumps(dict(seconds=time.time()-start,browser=browser.version,platform=platform.platform(),transport='loopback',presentation='headless Chromium WebGL2 SwiftShader; submission not physical display',selected=len(selected)),indent=2));await browser.close()
 finally:events.close();await runner.cleanup()
asyncio.run(run())
