#!/usr/bin/env python3
"""Browser reset controls against mocked bridge requests; no hardware access."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1];web=root/'vdp/video/extender/web'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(web)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium')
  page=browser.new_page();seen=[];errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('dialog',lambda d:d.accept())
  page.route('**/index.html',lambda route:route.fulfill(content_type='text/html',body=(web/'index.html').read_text().replace('name="agon-reset-url" content=""','name="agon-reset-url" content="http://bridge.test/reset"')))
  def reset(route):
   r=route.request;seen.append((r.url,r.method,r.headers.get('x-agon-reset'),json.loads(r.post_data)))
   route.fulfill(status=200,content_type='application/json',body='{"pulse":"released"}')
  page.route('http://bridge.test/**',reset)
  page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
  page.click('#reset-p4');page.wait_for_function("!document.querySelector('#reset-p4').disabled")
  page.click('#reset-agon');page.wait_for_function("!document.querySelector('#reset-agon').disabled")
  assert [x[0] for x in seen]==['http://bridge.test/reset-p4','http://bridge.test/reset'],seen
  assert all(x[1:3]==('POST','1') for x in seen)
  assert seen[0][3]['id']!=seen[1][3]['id']
  page.unroute('**/index.html');page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
  assert page.locator('#reset-p4').is_disabled() and page.locator('#reset-agon').is_disabled()
  assert not errors,errors
  browser.close()
 print('PASS: distinct targets, POST/header/IDs, disabled unconfigured controls; no hardware calls')
finally:server.shutdown();server.server_close()
