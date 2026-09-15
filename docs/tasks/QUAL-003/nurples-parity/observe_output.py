"""Measure output with quiescent credit boundaries; no reset/keyboard/flash.

Agent-assigned diagnostic observer. Served production scripts are retained;
only outgoing frame credits are gated at window boundaries. No extra credit is
issued until the last response and its RAF presentation have drained.
"""
import argparse,hashlib,json,time
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

GATE=r'''(() => {
 const Original=window.WebSocket;
 window.__outputGate={stop:false,inflight:0,sent:0,received:0,closes:[],frames:[],socket:null};
 window.WebSocket=class extends Original {
  constructor(...args) {
   super(...args); const g=window.__outputGate;g.socket=this;
   this.addEventListener('message',e=>{
    if(!(e.data instanceof ArrayBuffer))return;
    const b=new DataView(e.data);if(b.byteLength<32 || b.getUint32(0)!==0x45564631)return;
    g.inflight--;g.received++;g.frames.push({ms:performance.now(),sequence:b.getUint32(8,true),width:b.getUint16(12,true),height:b.getUint16(14,true),bytes:b.byteLength});
   });
   this.addEventListener('close',e=>g.closes.push({code:e.code,reason:e.reason}));
  }
  send(data) {const g=window.__outputGate;if(data==='frame') {if(g.stop)return;g.inflight++;g.sent++;}return super.send(data);}
 };
})();'''

def main():
 p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=float,default=10);p.add_argument('--receive-only',action='store_true');p.add_argument('--browser-executable');a=p.parse_args()
 assert 1<=a.seconds<=60;a.output.mkdir(parents=True,exist_ok=False);url=a.url.rstrip('/');record={'scope':'quiescent snapshot/socket counter deltas; browser received FPS separately','receive_only':a.receive_only,'observer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 def read():
  with urlopen(url+'/diagnostics/video-timing',timeout=5) as r:return json.load(r)
 for name in ('index.html','app.js','frame_protocol.js','webgl2_presenter.js'):
  with urlopen(url+('/' if name=='index.html' else '/'+name),timeout=5) as r:(a.output/name).write_bytes(r.read())
 errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'],executable_path=a.browser_executable);page=browser.new_page();page.add_init_script(GATE);page.on('pageerror',lambda e:errors.append(str(e)))
  def stop():
   page.evaluate('__outputGate.stop=true');page.wait_for_function('__outputGate.inflight===0',timeout=15000)
   page.wait_for_timeout(100) # allow final RAF and suppression of its next credit
   assert page.evaluate('__outputGate.inflight')==0
  try:
   page.goto(url,wait_until='domcontentloaded')
   if a.receive_only:page.evaluate("() => {const w=new WebSocket('ws://'+location.host+'/video');w.binaryType='arraybuffer';w.onopen=()=>w.send('frame');w.onmessage=()=>w.send('frame');}")
   else:page.click('#connect')
   page.wait_for_function('__outputGate.received>=10',timeout=20000);stop();record['before']=read()
   record['start_ms']=page.evaluate('performance.now()');record['start_received']=page.evaluate('__outputGate.received')
   page.evaluate("__outputGate.stop=false;__outputGate.socket.send('frame')")
   page.wait_for_timeout(a.seconds*1000);stop();record['end_ms']=page.evaluate('performance.now()');record['after']=read()
   record['gate']=page.evaluate('({sent:__outputGate.sent,received:__outputGate.received,inflight:__outputGate.inflight,closes:__outputGate.closes,frames:__outputGate.frames})')
   assert not errors and not record['gate']['closes'] and record['gate']['inflight']==0
   for r in (record['before'],record['after']):
    assert r['totals_valid'] and not r['lost_completions'] and not r['overlapping_calls'] and not r['busy_reads'],r
   rows=[]
   for b,e in zip(record['before']['phases'],record['after']['phases']):
    assert b['name']==e['name'];n=e['count']-b['count'];units=e['units']-b['units'];us=e['total_us']-b['total_us'];assert n>0
    expected={'snapshot':512*384,'socket_send':512*384+32,'credit_to_ready':1,'ready_to_send':1}[e['name']];assert units==n*expected,(e['name'],n,units,expected)
    rows.append({'phase':e['name'],'count':n,'units':units,'mean_ms':us/n/1000})
   frames=[f for f in record['gate']['frames'] if f['ms']>=record['start_ms']];assert len(frames)>1 and all((f['width'],f['height'],f['bytes'])==(512,384,196640) for f in frames)
   record['summary']={'phases':rows,'received_fps':(len(frames)-1)*1000/(frames[-1]['ms']-frames[0]['ms']),'frames':len(frames)};record['status']='pass'
  except Exception as e:record['status']='failed';record['error']=str(e);raise
  finally:
   record['errors']=errors;(a.output/'result.json').write_text(json.dumps(record,indent=2)+'\n');browser.close()
 print(json.dumps(record['summary'],indent=2))
if __name__=='__main__':main()
