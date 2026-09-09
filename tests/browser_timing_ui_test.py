"""Real Chromium/WebSockets with video and a controlled shared-server stall.

This validates measurement sensitivity under combined traffic, not ESP-IDF or
physical network performance. The peer deliberately models one serialized
video/key executor and supplies synthetic pixels; it never contacts the bench.
"""
import base64
import hashlib
import json
import socket
import struct
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
lock=threading.Lock()
stall=threading.Event()
video_blocked=threading.Event()
class Peer(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        route=self.path.split('?')[0]
        if route=='/diagnostics':
            data=b'ok' if '?' in self.path else b'# controlled peer; not P4 evidence\n'
            self.send_response(200);self.end_headers();self.wfile.write(data);return
        if route not in ('/video','/keyboard'): return super().do_GET()
        self.send_response(101);self.send_header('Upgrade','websocket');self.send_header('Connection','Upgrade')
        key=self.headers['Sec-WebSocket-Key']+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        self.send_header('Sec-WebSocket-Accept',base64.b64encode(hashlib.sha1(key.encode()).digest()).decode());self.end_headers()
        sequence=0
        def send(data):
            size=len(data)
            self.wfile.write(bytes([0x82, size if size<126 else 127])+(b'' if size<126 else struct.pack('!Q',size))+data)
            self.wfile.flush()
        try:
            while True:
                header=self.rfile.read(2)
                if len(header)!=2 or header[0]&15==8: break
                length=header[1]&127
                if length==126: length=struct.unpack('!H',self.rfile.read(2))[0]
                if length==127: length=struct.unpack('!Q',self.rfile.read(8))[0]
                mask=self.rfile.read(4);raw=self.rfile.read(length)
                if len(raw)!=length: break
                payload=bytes(v^mask[i%4] for i,v in enumerate(raw))
                with lock:
                    if route=='/keyboard':
                        assert len(payload) in (1,4)
                        send(b'A')
                    else:
                        assert payload==b'frame'
                        if stall.is_set():
                            stall.clear();video_blocked.set();time.sleep(2.2)
                        time.sleep(.03)
                        sequence+=1
                        frame=struct.pack('<4sBBBBIHHIIII',b'EVF1',1,32,1,3,sequence,640,480,1920,921600,16667,0)
                        send(frame+bytes([sequence%256])*921600)
        except (BrokenPipeError,ConnectionResetError,socket.timeout): pass

def main():
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Peer,directory=str(ROOT/'vdp/video/extender/web')))
    server.daemon_threads=True
    threading.Thread(target=server.serve_forever,daemon=True).start()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
        page=browser.new_page(accept_downloads=True);errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/?timing=on')
        page.click('#connect');page.wait_for_function("Number(document.querySelector('#presented').textContent)>2")
        page.click('#keyboard');page.wait_for_function("document.querySelector('#keyboard-state').textContent.startsWith('Keyboard captured')")
        page.keyboard.press('a');page.wait_for_timeout(300)
        before=int(page.text_content('#presented'));assert before>2
        stall.set();assert video_blocked.wait(3)
        page.keyboard.press('b')
        page.wait_for_function("document.querySelector('#keyboard-state').textContent.includes('timeout')")
        page.wait_for_timeout(500)
        page.click('#keyboard');page.wait_for_function("document.querySelector('#keyboard-state').textContent.startsWith('Keyboard captured')")
        page.keyboard.press('c');page.wait_for_timeout(200)
        with page.expect_download() as result: page.click('#timing-download')
        report=json.loads(Path(result.value.path()).read_text());rows=report['rows']
        assert any(r['event']=='key_release_local' and 'timeout' in r['reason'] for r in rows)
        assert any(r['event']=='key_close' and 'code' in r for r in rows)
        assert any(r['event']=='frame_received' for r in rows)
        assert any(r['event']=='frame_submitted' for r in rows)
        sends={(r['sid'],r['ordinal']):r for r in rows if r['event']=='key_send'}
        acks=[r for r in rows if r['event']=='key_ack']
        assert acks and all((r['sid'],r['ordinal']) in sends for r in acks)
        assert len({r['sid'] for r in acks})>=2
        assert any(r['event']=='key_event' and r['physical']==6 for r in rows)
        assert not errors,errors
        print('PASS: actual browser sockets carry 640x480 frames and keys; injected shared-server stall records ACK timeout/close; recapture and combined export work')
        browser.close()
    server.shutdown()
if __name__=='__main__':main()
