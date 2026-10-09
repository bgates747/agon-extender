"""Local browser paste correctness; an acknowledging peer, never the bench."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('keyboard_client', ROOT/'scripts/keyboard.py')
mapper=importlib.util.module_from_spec(spec);spec.loader.exec_module(mapper)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'vdp/video/extender/web')))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--enable-unsafe-swiftshader'])
        page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        locale=[0]
        page.route('**/keyboard/status',lambda route:route.fulfill(json={'ready':True,'locale':locale[0]}))
        page.add_init_script('''
window.sockets=[];window.dropAck=false;
window.WebSocket=class {
 static OPEN=1;
 constructor(){this.readyState=0;this.bufferedAmount=0;this.sent=[];sockets.push(this);setTimeout(()=>{this.readyState=1;this.onopen?.();},10);}
 send(p){if(typeof p==='string')return;this.sent.push({p:Array.from(p),t:performance.now()});
 const b=new Uint8Array(p);b[3]=0;new DataView(b.buffer).setUint32(4,7,true);
 if(!dropAck)setTimeout(()=>this.onmessage?.({data:b.buffer}),0);}
 close(){this.readyState=3;this.onclose?.();}
};''')
        page.goto(f'http://127.0.0.1:{server.server_port}')
        page.click('#paste-text')
        def observe(caps=False):
            page.evaluate("caps=>document.querySelector('#paste-content').dispatchEvent(new KeyboardEvent('keydown',{code:'KeyA',key:caps?'A':'a',modifierCapsLock:caps,bubbles:true}))",caps)
        for loc,caps,value in [(0,False,'aA£@#\\\n\t'),(1,True,'aA@#\\~')]:
            locale[0]=loc;observe(caps);page.fill('#paste-content',value);page.click('#paste-send')
            page.wait_for_function("document.querySelector('#paste-state').textContent==='Text sent to P4'",timeout=15000)
            packets=page.evaluate('sockets.at(-1).sent.filter(x=>x.p[3]===2)')
            expected=list(mapper.text_events(value,loc,caps=caps))
            assert [[x['p'][12],x['p'][13]] for x in packets]==[list(x) for x in expected], (packets,expected)
            assert all(b['t']-a['t']>=18 for a,b in zip(packets,packets[1:])),packets
            page.evaluate("window.dispatchEvent(new Event('agon-reset-request'))")
        observe();page.fill('#paste-content','valid🙂');n=page.evaluate('sockets.length');page.click('#paste-send')
        page.wait_for_function("document.querySelector('#paste-state').textContent.includes('Unsupported character')")
        assert page.evaluate('sockets.length')==n
        page.fill('#paste-content','a'*30);page.click('#paste-send');page.wait_for_timeout(200);page.click('#paste-stop')
        n=page.evaluate('sockets.at(-1).sent.length');page.wait_for_timeout(200)
        assert page.evaluate('sockets.at(-1).sent.length')==n
        assert page.evaluate('sockets.at(-1).readyState')==3
        page.fill('#paste-content','aaaa');page.click('#paste-send')
        page.wait_for_function("document.querySelector('#keyboard-state').textContent==='Keyboard captured'")
        page.evaluate('window.dropAck=true')
        page.wait_for_function("document.querySelector('#paste-state').textContent.includes('acknowledgement timed out')",timeout=3000)
        assert page.evaluate('sockets.at(-1).readyState')==3
        page.evaluate('window.dropAck=false');page.fill('#paste-content','aaaa');page.click('#paste-send')
        page.wait_for_timeout(100);page.evaluate("window.dispatchEvent(new Event('blur'))")
        assert page.evaluate('sockets.at(-1).readyState')==3
        page.evaluate('window.dropAck=true');page.fill('#paste-content','a');page.click('#paste-send')
        page.wait_for_function("document.querySelector('#paste-state').textContent.includes('admission timed out')",timeout=7000)
        assert not errors,errors
        browser.close()
finally:server.shutdown()
print('Paste locale/caps mappings, prevalidation, cadence, cancellation and admission timeout pass')
