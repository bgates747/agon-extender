"""Exercise the restored page in Chromium: real EVF1/WebGL, simulated sockets.

This checks video presentation/credit and reconnect without browser key capture;
it does not contact P4 or establish physical network performance.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(
        Quiet, directory=str(ROOT/'vdp/video/extender/web')))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=['--enable-unsafe-swiftshader'])
            page = browser.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.add_init_script('''
window.sockets=[];
window.WebSocket=class extends EventTarget {
  static CONNECTING=0; static OPEN=1; static CLOSING=2; static CLOSED=3;
  constructor(url) {
    super(); this.url=url; this.readyState=0; this.sent=[];
    sockets.push(this);
    setTimeout(()=>{ this.readyState=1; this.dispatchEvent(new Event('open')); },10);
  }
  send(value) { this.sent.push(value); }
  close() { this.readyState=3; this.dispatchEvent(new Event('close')); }
};
''')
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            assert page.locator('#keyboard').count() == 0
            assert page.locator('#keyboard-state').count() == 0
            page.click('#connect')
            page.wait_for_function("sockets[0]?.sent.length === 1")
            assert page.evaluate('sockets[0].sent') == ['frame']
            page.evaluate('''async () => {
              const {makeDemoFrame}=await import('/frame_protocol.js');
              sockets[0].dispatchEvent(new MessageEvent('message',
                {data:makeDemoFrame({sequence:1})}));
            }''')
            page.wait_for_function("sockets[0].sent.length === 2")
            # Typing into the page must neither acquire a keyboard endpoint nor
            # emit key messages; the second video credit follows presentation.
            page.click('#screen')
            page.keyboard.type('Video only')
            page.wait_for_timeout(100)
            assert page.evaluate('sockets.length') == 1
            assert page.evaluate('sockets[0].sent') == ['frame', 'frame']
            assert page.evaluate('sockets[0].url.endsWith("/video")')
            page.evaluate('sockets[0].close()')
            page.click('#connect')
            page.wait_for_function("sockets[1]?.sent.length === 1")
            assert page.evaluate('sockets.length') == 2
            page.click('#demo')
            page.wait_for_timeout(500)
            assert page.evaluate('sockets[1].readyState') == 3
            assert not errors, errors
            output = ROOT/'agents/excom/video-only-review'
            output.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(output/'browser.png'))
            browser.close()
    finally:
        server.shutdown()
    print('PASS: video render/credit, reconnect, local pattern and no browser key capture')


if __name__ == '__main__':
    main()
