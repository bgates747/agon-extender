"""Matched installed-client benchmark; URL/private output passed by caller.
Headless Chromium presentation submissions, not physical monitor refresh.
"""
from pathlib import Path
import argparse,json,time,urllib.request,statistics
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=float,default=5);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
source=urllib.request.urlopen(a.url+'/app.js',timeout=10).read().decode()
source=source.replace('acceptFrame(parseFrame(event.data), true);','''const before=performance.now();const f=parseFrame(event.data);const after=performance.now();
window.samples.push({t:after,decode_ms:after-before,bytes:event.data.byteLength,magic:String.fromCharCode(...new Uint8Array(event.data,0,4)),seq:f.sequence,w:f.width,h:f.height,signature:[0,1,2,3,4,5,6,7].map(i=>f.pixels[Math.floor(f.height/2)*f.strideBytes+Math.floor((i+.5)*f.width/8)]).join(",")});
window.lastPixels=Array.from(f.pixels);acceptFrame(f,true);''')
# Array.from is only for correctness frame retrieval, omit from timed stream.
source=source.replace('window.lastPixels=Array.from(f.pixels);','window.lastFrame=f;')
source=source.replace('presenter.present(accepted.frame);','presenter.present(accepted.frame);window.presented.push({t:performance.now(),seq:accepted.frame.sequence});')
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
 for label,query in [('raw',''),('rle2','?rle2=1'),('packed','?packed=1'),('auto','?rle2=1&packed=1')]:
  page=b.new_page();page.add_init_script('window.samples=[];window.presented=[];window.lastFrame=null;')
  src=source.replace('?rle2=1&packed=1',query)
  page.route('**/app.js',lambda route,request,src=src:route.fulfill(status=200,content_type='text/javascript',body=src))
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  before_counters=json.loads(urllib.request.urlopen(a.url+'/diagnostics/video-timing',timeout=10).read())
  page.goto(a.url);page.click('#connect');page.wait_for_timeout(1000)
  page.evaluate('window.samples=[];window.presented=[];');page.wait_for_timeout(a.seconds*1000)
  data=page.evaluate('({samples:window.samples,presented:window.presented,pixels:window.lastFrame?Array.from(window.lastFrame.pixels):null})')
  pixels=data.pop('pixels');assert pixels is not None,(label,errors)
  (a.output/(label+'.rgb222')).write_bytes(bytes(pixels))
  samples=data['samples'];pr=data['presented'];assert len(samples)>1,(label,errors)
  gaps=[pr[i]['t']-pr[i-1]['t'] for i in range(1,len(pr))]
  data.update(label=label,errors=errors,frames=len(pr),fps=(len(pr)-1)*1000/(pr[-1]['t']-pr[0]['t']) if len(pr)>1 else 0,mean_bytes=statistics.mean(s['bytes'] for s in samples),decode_ms=statistics.mean(s['decode_ms'] for s in samples),interval_p95_ms=sorted(gaps)[int(.95*(len(gaps)-1))] if gaps else None)
  page.close()
  after_counters=json.loads(urllib.request.urlopen(a.url+'/diagnostics/video-timing',timeout=10).read())
  data.update(before_counters=before_counters,after_counters=after_counters)
  results.append(data)
 b.close()
(a.output/'samples.json').write_text(json.dumps(results,indent=2)+'\n')
print([(r['label'],round(r['fps'],2),round(r['mean_bytes'])) for r in results],flush=True)
