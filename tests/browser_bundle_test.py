#!/usr/bin/env python3
"""Check embedded browser bytes and negotiation, without connecting to hardware."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import hashlib
import json
import ctypes
import struct
import subprocess
import tempfile
from playwright.sync_api import sync_playwright


def codec_vectors(project):
    # Compile the same maintained headers selected by this firmware build.
    with tempfile.TemporaryDirectory() as tmp:
        source=Path(tmp)/'codec.cpp'; library=Path(tmp)/'codec.so'
        source.write_text('''#include "extender/codecs/rle2.hpp"
#include "extender/network/packed_frame.hpp"
#include "extender/network/pair_rle.hpp"
extern "C" size_t encode(int kind,const unsigned char*s,size_t n,unsigned char*d,size_t cap){
 if(kind==0){auto r=rle2::encode_auto(s,n,d,cap,true);return r?r.bytes:0;}
 if(kind==1)return packed_frame::encode(s,n,d,cap,n,true);
 return pair_rle::encode(s,n,d,cap,n);
}''')
        subprocess.run(['c++','-std=c++17','-O2','-shared','-fPIC','-I',str(project/'video'),str(source),'-o',str(library)],check=True)
        lib=ctypes.CDLL(str(library));f=lib.encode
        f.argtypes=[ctypes.c_int,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];f.restype=ctypes.c_size_t
        vectors=[]
        for width,height in ((320,240),(512,384),(641,3)):
            n=width*height
            for pattern in range(4):
                data=bytes((7 if pattern==0 else (i//2)%2 if pattern==1 else i%64 if pattern==2 else (i*37+i//31)%64) for i in range(n))
                for kind in range(4):
                    out=ctypes.create_string_buffer(n+32)
                    count=f(kind,data,n,out,len(out)) if kind<3 else 0
                    magic=(b'EVR1',b'EVP1',b'EVQ1')[kind] if count else b'EVF1'
                    payload=out.raw[:count] if count else data
                    header=struct.pack('<4sBBBBIHHIIII',magic,1,32,2,1,1,width,height,width,n,16667,0)
                    vectors.append((list(header+payload),list(data),magic.decode()))
        return vectors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--expect', choices=('raw','compressed'), default='compressed')
    args=parser.parse_args()
    project=args.bundle/'source/vdp'
    image=(project/'.pio/build/p4-console/firmware.bin').read_bytes()
    web=project/'video/extender/web'
    hashes={}
    for name in ('index.html','app.js','style.css','frame_protocol.js','webgl2_presenter.js'):
        data=(web/name).read_bytes()
        assert data+b'\0' in image, f'{name} not embedded in actual binary'
        hashes[name]=hashlib.sha256(data).hexdigest()
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*_): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(web)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
            page=browser.new_page();errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            # Record constructor URLs. No real WebSocket or reset bridge request.
            page.add_init_script('''window.urls=[]; window.WebSocket=class {
              static OPEN=1; static CLOSED=3;
              constructor(url){window.urls.push(String(url));this.readyState=0;}
              close(){this.readyState=3;} send(){} addEventListener(){}
            };''')
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            page.click('#connect')
            page.wait_for_function('window.urls.length>0')
            urls=page.evaluate('window.urls')
            expected='/video'+('?rle2=1&packed=2' if args.expect=='compressed' else '')
            assert urls[-1].endswith(expected),urls
            assert page.locator('header #reset-agon').count()==1
            assert not errors,errors
            formats=set()
            for frame, pixels, magic in codec_vectors(project):
                assert page.evaluate("""async ([bytes,expected])=>{
                    const {parseFrame}=await import('./frame_protocol.js');
                    const actual=parseFrame(new Uint8Array(bytes).buffer).pixels;
                    return actual.length===expected.length && actual.every((v,i)=>v===expected[i]);
                }""", [frame,pixels]),magic
                formats.add(magic)
            assert formats=={'EVF1','EVR1','EVP1','EVQ1'},formats
            browser.close()
    finally: server.shutdown()
    result={'outcome':'pass','expected_negotiation':args.expect,'embedded_assets':hashes,'codec_vectors':48,'formats':sorted(formats)}
    (args.bundle/'browser-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__': main()
