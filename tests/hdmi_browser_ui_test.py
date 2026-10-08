#!/usr/bin/env python3
"""HDMI page disables video/WebGL while independent keyboard capture works.

The Pi's Chromium supplies the browser; sockets are simulated and no hardware
endpoint receives traffic. Both reset controls and keyboard ownership remain
the existing browser mechanisms.
"""
from functools import partial
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "vdp/video/extender/web"


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hdmi848', action='store_true')
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(WEB)))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            options = {"headless": True}
            if executable := shutil.which("chromium"):
                options["executable_path"] = executable
            browser = playwright.chromium.launch(**options)
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            html = (WEB / "index.html").read_text().replace(
                'name="agon-video-output" content="browser"',
                'name="agon-video-output" content="hdmi"')
            if args.hdmi848:
                html = html.replace('content="1280x720 60 Hz"', 'content="848x480 60.07 Hz"')
            page.route("**/?demo", lambda route: route.fulfill(
                content_type="text/html", body=html))
            page.add_init_script("""
window.sockets = [];
HTMLCanvasElement.prototype.getContext = () => { throw Error('WebGL must remain unused'); };
window.WebSocket = class extends EventTarget {
  static OPEN = 1;
  constructor(url) {
    super(); this.url = url; this.readyState = 0; this.bufferedAmount = 0; this.sent = [];
    sockets.push(this);
    setTimeout(() => {
      this.readyState = 1;
      const event = new Event('open'); this.dispatchEvent(event); this.onopen?.(event);
    }, 10);
  }
  send(value) {
    this.sent.push(Array.from(value));
    const bytes = new Uint8Array(value); bytes[3] = 0;
    new DataView(bytes.buffer).setUint32(4, 7, true);
    setTimeout(() => this.onmessage?.(new MessageEvent('message', {data:bytes.buffer})), 0);
  }
  close() {
    this.readyState = 3;
    const event = new Event('close'); this.dispatchEvent(event); this.onclose?.(event);
  }
};
""")
            page.goto(f"http://127.0.0.1:{server.server_port}/?demo")
            page.wait_for_function("document.querySelector('#state').textContent === 'HDMI output'")
            assert page.locator("#surface").inner_text() == ("HDMI 848x480 60.07 Hz" if args.hdmi848 else "HDMI 1280x720 60 Hz")
            for selector in ("#video-viewport", "#connect", "#demo", "#fullscreen", ".diagnostics"):
                assert not page.locator(selector).is_visible(), selector
            assert page.locator("#hdmi-output").is_visible()
            assert page.locator("#capture-keyboard").is_visible()
            assert page.evaluate("sockets.length") == 0
            assert page.locator("header #reset-agon").count() == 1

            page.click("#capture-keyboard")
            page.wait_for_function("document.querySelector('#keyboard-state').textContent === 'Keyboard captured'")
            assert page.evaluate("document.activeElement.id") == "hdmi-output"
            page.keyboard.type("az")
            page.keyboard.press("Tab")
            events = page.evaluate("sockets[0].sent.filter(p=>p[3]===2).map(p=>[p[12],p[13]])")
            assert events == [[4, 1], [4, 0], [29, 1], [29, 0], [43, 1], [43, 0]], events
            assert page.evaluate("sockets.length") == 1
            assert page.evaluate("new URL(sockets[0].url).pathname") == "/keyboard/browser"
            page.click("header h1")
            assert page.locator("#capture-keyboard").inner_text() == "Capture keyboard"
            assert page.evaluate("sockets[0].readyState") == 3
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
    print("PASS: HDMI UI suppresses video/WebGL and preserves independent browser keyboard capture")


if __name__ == "__main__":
    main()
