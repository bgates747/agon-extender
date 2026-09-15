#!/usr/bin/env python3
"""Bounded headless observation of the production browser video path.

No keyboard, reset, serial, SD, firmware changes, or retries that evict a viewer.
Logical period, received frames and browser submissions are separate measurements.
"""
import argparse,hashlib,json,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OBSERVER=r'''(() => {
 const Original=window.WebSocket;
 window.__videoObservation={frames:[],closes:[],presentations:[],first:null,last:null,overflow:false};
 window.WebSocket=class extends Original {
  constructor(...args) {
   super(...args); const observation=window.__videoObservation;
   this.addEventListener('message',event=>{
    const b=event.data;if(!(b instanceof ArrayBuffer)||b.byteLength<32)return;
    const d=new DataView(b),a=new Uint8Array(b);
    if(String.fromCharCode(...a.slice(0,4))!=='EVF1')return;
    if(observation.frames.length>=12000){observation.overflow=true;return;}
    observation.frames.push({ms:performance.now(),version:d.getUint8(4),header:d.getUint8(5),
      format:d.getUint8(6),flags:d.getUint8(7),sequence:d.getUint32(8,true),
      width:d.getUint16(12,true),height:d.getUint16(14,true),stride:d.getUint32(16,true),
      payload:d.getUint32(20,true),period:d.getUint32(24,true),reserved:d.getUint32(28,true),bytes:b.byteLength});
    const latest=observation.frames[observation.frames.length-1];
    if(latest.format===2 && latest.width>=144 && latest.height>=68) {
      let code=0,complement=0,valid=true;
      for(let bit=0;bit<8;bit++) {
        const top=a[32+38*latest.stride+22+16*bit],bottom=a[32+62*latest.stride+22+16*bit];
        if(![0,63].includes(top)||![0,63].includes(bottom))valid=false;
        if(top===63)code|=1<<bit;if(bottom===63)complement|=1<<bit;
      }
      let decoded=code;for(let tail=code>>1;tail;tail>>=1)decoded^=tail;
      latest.marker={code,complement,decoded,valid:valid&&((code^complement)===255)};
    }
    if(!observation.first)observation.first=b;observation.last=b;
   });
   this.addEventListener('close',event=>observation.closes.push({ms:performance.now(),code:event.code,reason:event.reason}));
  }
 };
 document.addEventListener('DOMContentLoaded',()=>{
  const node=document.querySelector('#presented');if(!node)return;
  new MutationObserver(()=>window.__videoObservation.presentations.push({ms:performance.now(),count:Number(node.textContent)}))
    .observe(node,{childList:true,subtree:true,characterData:true});
 });
})();'''

def collect(url,seconds,out,label,receive_only=False,browser_executable=None,signal_ready=False):
    out=out.resolve();assert out.is_relative_to(ROOT/'agents') and not out.exists()
    out.mkdir(parents=True)
    record={'run':'PORT-003-'+datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ'),
            'label':label,'scope':'production browser receive/WebGL submission; no scanout/VDP execution timing claim',
            'receive_only':receive_only,'seconds_requested':seconds,'started_utc':datetime.now(timezone.utc).isoformat(),
            'observer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'assets':{},'status':'incomplete'}
    errors=[]
    import platform
    record['host']={'system':platform.system(),'machine':platform.machine(),'python':platform.python_version()}
    try:
        for name in ('index.html','app.js','frame_protocol.js','webgl2_presenter.js'):
            with urlopen(url+('/' if name=='index.html' else '/'+name),timeout=5) as response:data=response.read()
            (out/name).write_bytes(data)
            local=(ROOT/'vdp/video/extender/web'/name).read_bytes()
            record['assets'][name]={'sha256':hashlib.sha256(data).hexdigest(),'matches_local':data==local}
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'],executable_path=browser_executable)
            try:
                record['browser_version']=browser.version
                page=browser.new_page();page.add_init_script(OBSERVER)
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(url,wait_until='domcontentloaded',timeout=10000)
                if receive_only:
                    page.evaluate("""() => { const ws=new WebSocket('ws://'+location.host+'/video');
                        ws.binaryType='arraybuffer';ws.onopen=()=>ws.send('frame');
                        ws.onmessage=()=>ws.send('frame');window.__receiveOnly=ws; }""")
                else:page.click('#connect')
                if signal_ready:
                    page.wait_for_function('__videoObservation.frames.length>0',timeout=20000)
                    (out/'ready.json').write_text(json.dumps({
                        'first_frame_received':True,
                        'ready_at':datetime.now(timezone.utc).isoformat(),
                        'browser_ms':page.evaluate('performance.now()')},indent=2)+'\n')
                start=time.monotonic()
                while time.monotonic()-start<seconds:
                    page.wait_for_timeout(200)
                    state=page.evaluate('({n:__videoObservation.frames.length,closes:__videoObservation.closes,overflow:__videoObservation.overflow})')
                    if state['closes'] or state['overflow'] or errors:raise RuntimeError(str(state)+str(errors))
                record['observed_wall_seconds']=time.monotonic()-start
                observation=page.evaluate('({frames:__videoObservation.frames,closes:__videoObservation.closes,presentations:__videoObservation.presentations,overflow:__videoObservation.overflow})')
                record.update(observation)
                for name in ('first','last'):
                    data=bytes(page.evaluate(f'Array.from(new Uint8Array(__videoObservation.{name} || new ArrayBuffer(0)))'))
                    if data:(out/(name+'.evf')).write_bytes(data)
                page.screenshot(path=str(out/'browser.png'))
                record['ui']={key:page.locator('#'+key).inner_text() for key in ('state','surface','stride','period','received','presented','fps','gaps')}
                frames=record['frames'];assert len(frames)>=2,'No sustained frame delivery'
                for f in frames:
                    assert f['version']==1 and f['header']==32 and f['format'] in (1,2) and f['flags']&1 and not f['flags']&~3
                    assert 0<f['width']<=1024 and 0<f['height']<=768 and f['reserved']==0
                    assert f['stride']>=f['width']*(3 if f['format']==1 else 1)
                    assert f['payload']==f['stride']*f['height'] and f['payload']<=2359296 and f['bytes']==32+f['payload']
                gaps=[b['ms']-a['ms'] for a,b in zip(frames,frames[1:])]
                import statistics
                layouts=Counter((f['width'],f['height'],f['stride'],f['format']) for f in frames)
                record['summary']={'received':len(frames),'received_fps':(len(frames)-1)*1000/(frames[-1]['ms']-frames[0]['ms']),
                    'median_receive_interval_ms':statistics.median(gaps),'maximum_receive_interval_ms':max(gaps),
                    # Report actual headers, including an older retained first
                    # snapshot. A mode name/observer label is not geometry evidence.
                    'layouts':[{'width':w,'height':h,'stride':s,'format':fmt,'frames':n}
                               for (w,h,s,fmt),n in sorted(layouts.items())],
                    'observed_logical_period_us':sorted({f['period'] for f in frames}),
                    'sequence_gaps':sum(max(0,((b['sequence']-a['sequence'])&0xffffffff)-1) for a,b in zip(frames,frames[1:]))}
                record['status']='bounded video delivery observed; workload and human interpretation remain separate'
            finally:
                if 'frames' not in record:
                    try:
                        record.update(page.evaluate('({frames:__videoObservation.frames,closes:__videoObservation.closes,presentations:__videoObservation.presentations})'))
                    except Exception:pass
                browser.close()
    except Exception as error:
        record['error']=str(error);record['status']='failed; partial observations retained'
        raise
    finally:
        record['page_errors']=errors
        (out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record['summary'],indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--url',required=True)
    p.add_argument('--seconds',type=float,default=20);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--label',required=True);p.add_argument('--receive-only',action='store_true');p.add_argument('--browser-executable');p.add_argument('--signal-ready',action='store_true');a=p.parse_args()
    assert 1<=a.seconds<=180 and a.url.startswith('http://')
    collect(a.url.rstrip('/'),a.seconds,a.output,a.label,a.receive_only,a.browser_executable,a.signal_ready)
