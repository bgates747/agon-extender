"""Exercise the shipped page's real DOM focus/events with a bounded socket fake.
No P4 socket or video consumer is opened. Chromium checks syntax and execution;
keyboard packets here are browser transport messages, not hardware evidence.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from functools import partial
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'vdp/video/extender/web')))
    Thread(target=server.serve_forever,daemon=True).start()
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
        page=browser.new_page(); errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script('''
window.messages=[]; window.stall=false;
window.WebSocket=class {
 static CONNECTING=0; static OPEN=1; static CLOSING=2; static CLOSED=3;
 constructor(url) { this.url=url; this.readyState=0; this.bufferedAmount=0;
   setTimeout(()=>{if(this.readyState===0){this.readyState=1;this.onopen?.({});}},10); }
 addEventListener(name,fn) { this["on"+name]=fn; }
 send(value) { if(this.url.endsWith('/keyboard')) {
   messages.push(Array.from(value));
   if(!stall) setTimeout(()=>this.onmessage?.({data:new Uint8Array([65]).buffer}),1);
 } }
 close() { this.readyState=3; setTimeout(()=>this.onclose?.({}),1); }
};''')
        page.goto(f'http://127.0.0.1:{server.server_port}/')
        page.click('#connect'); page.wait_for_timeout(50)
        page.click('#keyboard'); page.wait_for_function("document.querySelector('#keyboard-state').textContent.startsWith('Keyboard captured')")
        page.keyboard.press('a'); page.keyboard.press('Shift+b'); page.keyboard.press('3'); page.keyboard.press('Shift+Digit1')
        page.keyboard.press('Backspace'); page.keyboard.press('Enter')
        page.wait_for_timeout(200)
        messages=page.evaluate('messages')
        downs=[x for x in messages if len(x)==4 and x[3]==1]
        for expected in ([75,4,0,1],[75,5,2,1],[75,32,0,1],[75,30,2,1],[75,42,0,1],[75,40,0,1]):
            assert expected in downs,(expected,downs)
        page.focus('#connect'); before=page.evaluate('messages.length'); page.keyboard.press('x');page.wait_for_timeout(100)
        assert page.evaluate('messages.length')==before
        assert 'released' in page.text_content('#keyboard-state')
        page.click('#keyboard'); page.wait_for_timeout(80)
        page.keyboard.press('Tab'); page.wait_for_timeout(80)
        assert not page.evaluate("document.querySelector('#screen').classList.contains('keyboard-focus')")
        page.click('#keyboard'); page.wait_for_timeout(80)
        page.evaluate('stall=true'); page.keyboard.press('q'); page.wait_for_timeout(2100)
        assert 'timeout' in page.text_content('#keyboard-state')
        assert not errors,errors
        browser.close()
    server.shutdown()
    print('PASS: Chromium focus, US keys/modifiers, Enter/Backspace, blur, Tab and ACK timeout; no local echo')
if __name__=='__main__': main()
