"""BENCH-005: installed-client instrumentation, injected A edge to decoded/present submission.
Run from repo root with --url; source web assets copied from installed device.
No firmware changes. Host helper common owns admitted CLI, private environment.
"""
from pathlib import Path
import queue,concurrent.futures.thread,sys,time,json,struct,argparse,urllib.request
sys.path.insert(0,'agents/qual004')
from common import cli,KB
sys.path.insert(0,'scripts')
from keyboard import packet
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--uncapped',action='store_true');p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=a.output;r.mkdir(exist_ok=True)
source=urllib.request.urlopen(a.url+'/app.js').read().decode()
if a.uncapped:source=source.replace('Math.max(0,lastCreditAt+1000/30-performance.now())','0')
marker='''const p=frame.pixels; const o=64*frame.strideBytes+16*(frame.pixelFormat===2?1:3); return p[o];'''
source=source.replace('function acceptFrame(frame, usesCredit) {','function acceptFrame(frame, usesCredit) { window.b005Decoded.push({t:performance.now(),pixel:window.b005Pixel(frame),seq:frame.sequence,w:frame.width,h:frame.height});')
source=source.replace('presenter.present(accepted.frame);','presenter.present(accepted.frame); window.b005Presented.push({t:performance.now(),pixel:window.b005Pixel(accepted.frame),seq:accepted.frame.sequence});')
assert 'window.b005Decoded.push' in source
results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader']);page=browser.new_page()
 page.add_init_script('window.b005Decoded=[];window.b005Presented=[];window.b005Pixel=frame=>{'+marker+'};')
 page.route('**/app.js',lambda route:route.fulfill(status=200,content_type='text/javascript',body=source))
 page.goto(a.url);page.click('#connect');page.wait_for_timeout(1500)
 for idx,(kind,busy) in enumerate([('char','idle')] if a.uncapped else [('char','idle'),('map','idle'),('char','busy'),('map','busy'),('block','idle')]):
  cli(('b005-uncapped-' if a.uncapped else 'b005-r2-run-')+str(idx),'EMOS EXCOM --keep-display','LOAD /test/bench005/keylat.bin','RUN . '+kind+' '+busy)
  page.wait_for_timeout(800)
  assert page.evaluate('window.b005Decoded.at(-1).w')==320
  k=KB(a.url,r/(kind+'-'+busy+'-keyboard.json'));k.open(k.status())
  records=[]
  try:
   for n in range(20):
    page.wait_for_timeout(160+(n*37)%170)
    host_before=time.perf_counter()*1000; browser_now=page.evaluate('performance.now()'); host_after=time.perf_counter()*1000
    offset=browser_now-(host_before+host_after)/2
    began=time.perf_counter()*1000;k.request(2,[(4,1)]);ended=time.perf_counter()*1000
    value={'start':began+offset,'httpEnd':ended+offset,'clock_alignment_bound_ms':(host_after-host_before)/2}
    expected=63 if n%2==0 else 0;start=value['start']
    # Keep A down until the visible response or deadline, avoiding lost keymap taps.
    try:page.wait_for_function('v=>window.b005Presented.some(x=>x.t>=v.start&&x.pixel===v.expected)',arg={'start':start,'expected':expected},timeout=3000)
    except Exception as e:value['error']=str(e)
    found=page.evaluate('v=>({decoded:window.b005Decoded.find(x=>x.t>=v.start&&x.pixel===v.expected),presented:window.b005Presented.find(x=>x.t>=v.start&&x.pixel===v.expected)})',{'start':start,'expected':expected})
    value.update(found);value.update(trial=n+1,expected=expected);records.append(value)
    k.send([(4,0)])
    if 'error' in value:break
   k.send([(41,1),(41,0)]);k.cancel()
  finally:k.lock.close()
  page.wait_for_timeout(500)
  (r/(kind+'-'+busy+'.json')).write_text(json.dumps(records,indent=2)+'\n')
  results.append({'kind':kind,'activity':busy,'trials':records});print(kind,busy,len(records),flush=True)
  if any('error' in x for x in records):raise RuntimeError('Marker timeout; preserve evidence')
 browser.close()
(r/'results.json').write_text(json.dumps(results,indent=2)+'\n')
cli('b005-uncapped-after' if a.uncapped else 'b005-r2-after','EMOS LEGACY --keep-display')
