"""Real Chromium events with an acknowledging input peer; no hardware traffic."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'vdp/video/extender/web')))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
        page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script('''
window.sockets=[];
window.WebSocket=class extends EventTarget {
 static OPEN=1;
 constructor(url){super();this.url=url;this.readyState=0;this.bufferedAmount=0;this.sent=[];sockets.push(this);
 setTimeout(()=>{this.readyState=1;const e=new Event('open');this.dispatchEvent(e);this.onopen?.(e);},10);}
 send(value){this.sent.push(typeof value==='string'?value:Array.from(value));
 if(typeof value!=='string'){const b=new Uint8Array(value);b[3]=0;new DataView(b.buffer).setUint32(4,7,true);
 setTimeout(()=>this.onmessage?.(new MessageEvent('message',{data:b.buffer})),0);}}
 close(){this.readyState=3;const e=new Event('close');this.dispatchEvent(e);this.onclose?.(e);}
};
''')
        page.goto(f'http://127.0.0.1:{server.server_port}')
        assert page.evaluate('sockets.length')==0
        page.click('#capture-keyboard');page.wait_for_function("document.querySelector('#keyboard-state').textContent==='Keyboard captured'")
        page.keyboard.type('az')
        page.keyboard.press('Tab');page.keyboard.press('Escape')
        page.wait_for_timeout(50)
        events=page.evaluate('sockets[0].sent.filter(p=>p[3]===2).map(p=>[p[12],p[13]])')
        assert events==[[4,1],[4,0],[29,1],[29,0],[43,1],[43,0],[41,1],[41,0]],events
        # DOM repeat is not forwarded; P4 owns repeat timing.
        page.evaluate("document.querySelector('#screen').dispatchEvent(new KeyboardEvent('keydown',{code:'KeyA',key:'a',repeat:true,bubbles:true,cancelable:true}))")
        assert len(page.evaluate('sockets[0].sent.filter(p=>p[3]===2)'))==8
        # No capture coupling to video. Start/stop a video socket without focus change.
        page.evaluate("const s=new WebSocket('/video');s.close()")
        assert page.locator('#keyboard-state').inner_text()=='Keyboard captured'
        # Focus outside panel releases; reconnect is never automatic.
        page.click('header h1');assert page.locator('#capture-keyboard').inner_text()=='Capture keyboard'
        page.click('#capture-keyboard');page.wait_for_function("document.querySelector('#keyboard-state').textContent==='Keyboard captured'")
        page.keyboard.down('Shift');page.keyboard.down('a')
        page.evaluate("window.dispatchEvent(new Event('blur'))")
        assert page.evaluate('sockets.at(-1).readyState')==3
        page.evaluate("window.dispatchEvent(new Event('focus'))")
        assert page.locator('#capture-keyboard').inner_text()=='Capture keyboard'
        # Unknown state is not guessed or replaced by manual controls.
        assert page.locator('select').count()==0
        page.click('#capture-keyboard');page.wait_for_function("document.querySelector('#keyboard-state').textContent==='Keyboard captured'")
        page.evaluate("document.querySelector('#screen').dispatchEvent(new KeyboardEvent('keydown',{code:'Numpad1',key:'1',bubbles:true,cancelable:true}))")
        assert 'unavailable' in page.locator('#keyboard-state').inner_text()
        assert page.evaluate('sockets.at(-1).sent.filter(p=>p[3]===2).length')==0
        page.evaluate("document.querySelector('#screen').dispatchEvent(new KeyboardEvent('keydown',{code:'Numpad1',key:'1',modifierNumLock:true,bubbles:true,cancelable:true}))")
        packet=page.evaluate('sockets.at(-1).sent.at(-1)');assert packet[12:16]==[89,1,32,32],packet
        # Caps follows host reports both on and off, with no override widget.
        page.evaluate("document.querySelector('#screen').dispatchEvent(new KeyboardEvent('keydown',{code:'KeyA',key:'A',modifierCapsLock:true,bubbles:true,cancelable:true}))")
        assert page.evaluate('sockets.at(-1).sent.at(-1)[15] & 16')==16
        page.evaluate("document.querySelector('#screen').dispatchEvent(new KeyboardEvent('keyup',{code:'KeyA',key:'a',bubbles:true,cancelable:true}))")
        assert page.evaluate('sockets.at(-1).sent.at(-1)[15] & 16')==0
        assert page.evaluate("getComputedStyle(document.querySelector('#screen')).outlineStyle")=='none'
        # Enter fullscreen while already captured; keep the same input session.
        input_count=page.evaluate('sockets.length')
        page.click('#fullscreen')
        page.wait_for_function("document.fullscreenElement?.id==='video-panel'")
        page.locator('#keyboard-strip').hover()
        assert page.locator('#keyboard-state').inner_text()=='Keyboard captured'
        assert page.evaluate('sockets.length')==input_count
        assert page.evaluate('sockets.at(-1).readyState')==1
        page.locator('#keyboard-strip').hover()
        assert page.locator('#keyboard-state').inner_text()=='Keyboard captured'
        canvas_box=page.locator('#screen').bounding_box();strip_box=page.locator('#keyboard-strip').bounding_box()
        assert canvas_box['y']+canvas_box['height']<=strip_box['y']+1
        page.click('#fullscreen');page.wait_for_function('!document.fullscreenElement')
        assert page.locator('#keyboard-state').inner_text()=='Keyboard captured'
        assert page.evaluate('sockets.length')==input_count
        assert page.evaluate('sockets.at(-1).readyState')==1
        page.click('#capture-keyboard')
        assert page.locator('#capture-keyboard').inner_text()=='Capture keyboard'
        assert not errors,errors
        browser.close()
finally: server.shutdown()
print('Browser capture: explicit ownership, key transitions, repeat suppression, focus loss, video independence and host-only locks pass')
