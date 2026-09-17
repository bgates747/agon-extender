"""Loopback-only EVC1 browser qualification. Never contacts a physical device."""
import argparse,asyncio,json,struct,time,shutil,statistics,platform
from pathlib import Path
from aiohttp import web,WSMsgType
from playwright.async_api import async_playwright
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent

def packet(c,v,seq):
 payload=(a.native/c['name']/(v['id']+'.bin')).read_bytes();head=bytearray(32);head[:4]=b'EVC1';struct.pack_into('<BBBBIHHII',head,4,1,32,{'raw':0,'rle2':1,'szip':2,'srle2':3,'png':4}[v['kind']],0,seq,c['width'],c['height'],c['width']*c['height'],len(payload));return bytes(head)+payload

def select(rows,variants,cases):
 good={v['id']:v for v in variants if len([r for r in rows if r['variant']==v['id'] and r['exact']])==len(cases)}
 ids=['raw','rle2','szip-o0-b4259840-r1-i0','szip-o4-b4259840-r1-i0','srle2-o3-b4259840-r1-i0','srle2-o4-b4259840-r1-i0']
 # Preserve families; choose fastest and smallest on the real captured screen,
 # then aggregate full-sized corpus. Both criteria are Linux screening only.
 for kind in ('szip','srle2','png'):
  for subset in ([r for r in rows if r['case']=='retained-sprites'],[r for r in rows if next(c for c in cases if c['name']==r['case'])['width']==512]):
   if not subset:continue
   for metric in ('bytes','encode_ms'):
    candidates=[v for v in good.values() if v['kind']==kind]
    winner=min(candidates,key=lambda v:statistics.mean(r[metric] for r in subset if r['variant']==v['id']))
    ids.append(winner['id'])
 return [good[i] for i in dict.fromkeys(ids) if i in good]

async def run():
 a.out.mkdir(exist_ok=False);start=time.time();client=a.out/'client';client.mkdir();cases=json.loads((a.native/'manifest.json').read_text());variants=json.loads((a.native/'variants.json').read_text());native=json.loads((a.native/'results.json').read_text());selected=select(native,variants,cases);(a.out/'selected.json').write_text(json.dumps(selected,indent=2))
 for name in ('client.js','worker.js','decoder.js','envelope.js'):shutil.copy(root/name,client/name)
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
   c=cfg['cases'][seq%len(cfg['cases'])];data=packet(c,cfg['variant'],seq);await ws.send_bytes(data);last=time.monotonic();events.write(json.dumps(dict(at=time.time(),seq=seq,case=c['name'],variant=cfg['variant']['id'],bytes=len(data)))+'\n');events.flush();seq+=1
  return ws
 app=web.Application();app.router.add_get('/video',socket);app.router.add_get('/raw/{name}',raw);app.router.add_get('/',lambda r:web.FileResponse(client/'index.html'));app.router.add_static('/',client);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();port=site._server.sockets[0].getsockname()[1]
 try:
  async with async_playwright() as pw:
   browser=await pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader']);page=await browser.new_page();await page.goto(f'http://127.0.0.1:{port}');await page.wait_for_function('window.ready===true')
   for phase in ('exact','paced'):
    for v in selected:
     groups=[[c] for c in cases] if phase=='exact' else [[c for c in cases if c['width']==512]]
     for group in groups:
      count=8 if phase=='exact' else 90;setting.update(cases=group,variant=v,count=count,pace=0 if phase=='exact' else 30)
      samples=await page.evaluate('(c)=>window.run(c)',dict(cases=[c['name'] for c in group],count=count,verify=phase=='exact'));assert all(s['mismatch']==-1 for s in samples)
      steady=samples[2:];intervals=[b['at']-x['at'] for x,b in zip(steady,steady[1:])]
      result=dict(phase=phase,variant=v['id'],cases=[c['name'] for c in group],frames=count,exact=phase=='exact',decode_wall_ms=statistics.mean(s['decodeWallMs'] for s in steady),decode_ms=statistics.mean(s.get('decodeMs',0) for s in steady),submit_ms=statistics.mean(s['submitMs'] for s in steady),fps=1000/statistics.mean(intervals),samples=samples)
      results.append(result);(a.out/'results.json').write_text(json.dumps(results,indent=2));print(phase,v['id'],group[0]['name'],'PASS',flush=True)
   # Invalid envelope, unknown codec, malformed CmpS/PNG, recovery after each.
   c=cases[0];rawv=variants[0];valid=packet(c,rawv,0);bad=[b'x',valid[:-1]];b=bytearray(valid);b[6]=99;bad.append(bytes(b))
   for kind in ('szip','png'):
    v=next(v for v in selected if v['kind']==kind);b=bytearray(packet(c,v,0));b[32]=0;bad.append(bytes(b))
   edges=[]
   for b in bad:
    answer=await page.evaluate('(b)=>window.edge(b)',list(b));assert answer!='accepted';assert await page.evaluate('(b)=>window.edge(b)',list(valid))=='accepted';edges.append(answer)
   edges.append(await page.evaluate('(b)=>window.timeoutEdge(b)',list(packet(c,next(v for v in selected if v['kind']=='szip'),0))))
   assert await page.evaluate('(b)=>window.edge(b)',list(valid))=='accepted'
   (a.out/'edges.json').write_text(json.dumps(edges,indent=2));await page.screenshot(path=str(a.out/'last-frame.png'))
   (a.out/'complete.json').write_text(json.dumps(dict(seconds=time.time()-start,browser=browser.version,platform=platform.platform(),transport='loopback',presentation='headless Chromium WebGL2 SwiftShader; submission not physical display',selected=len(selected)),indent=2));await browser.close()
 finally:events.close();await runner.cleanup()
asyncio.run(run())
