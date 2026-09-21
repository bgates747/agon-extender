"""Presentation geometry in real Chromium; no P4 connection or emulator changes."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'vdp/video/extender/web')))
Thread(target=server.serve_forever,daemon=True).start()
out=ROOT/'agents/browser-ui/review';out.mkdir(parents=True,exist_ok=True)
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
        for width,height in [(1280,900),(1920,1080),(390,844)]:
            page=browser.new_page(viewport={'width':width,'height':height});errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/?demo')
            page.wait_for_function("document.querySelector('#surface').textContent!=='—'")
            assert page.locator('canvas').count()==1
            assert page.locator('#capture-keyboard').count()==1
            assert page.locator('select').count()==0
            assert not page.locator('.stats').is_visible()
            assert page.locator('header #fps').count()==1 and page.locator('header #surface').count()==1
            button=page.locator('#connect').bounding_box();state=page.locator('#state').bounding_box()
            assert state['y']>=button['y']+button['height']
            assert abs(state['x']-button['x'])<1
            # The full mode sentence must wrap without widening a narrow page.
            page.evaluate("document.querySelector('#surface').textContent='Mode 136 320x240 64 colors 60 Hz double-buffered'")
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#screen').focus()
            assert page.evaluate("getComputedStyle(document.querySelector('#screen')).outlineStyle")=='none'
            page.screenshot(path=str(out/f'normal-{width}.png'),full_page=True)
            page.click('#fullscreen');page.wait_for_function("document.fullscreenElement?.id==='video-panel'")
            page.wait_for_timeout(200)
            canvas=page.locator('#screen').bounding_box();view=page.locator('#video-viewport').bounding_box();strip=page.locator('#keyboard-strip').bounding_box()
            expected=min(view['width'],view['height']*4/3)
            assert abs(canvas['width']-expected)<1,(width,canvas,view)
            assert canvas['width']>320 and canvas['height']>240
            assert abs(canvas['width']/canvas['height']-4/3)<.01
            assert canvas['y']+canvas['height']<=strip['y']+1
            assert canvas['x']>=0 and canvas['x']+canvas['width']<=width+1
            page.mouse.move(width/2,height/2);page.locator('#screen').focus();page.wait_for_timeout(180)
            assert page.evaluate("getComputedStyle(document.querySelector('#keyboard-strip')).opacity")=='0'
            page.screenshot(path=str(out/f'fullscreen-{width}.png'))
            page.mouse.move(width/2,height-2);page.wait_for_timeout(180)
            assert page.evaluate("getComputedStyle(document.querySelector('#keyboard-strip')).opacity")=='1'
            page.click('#fullscreen');page.wait_for_function('!document.fullscreenElement')
            assert not errors,errors
            page.close()
        browser.close()
finally:server.shutdown()
print('Layout passes: enlargement at three sizes, no cropping/outline, bottom reveal, compact controls and no manual locks')
