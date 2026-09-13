#!/usr/bin/env python3
"""Bounded real eZ80/EMOS/FatFS run with the maintained P4 queue and host client.

Always headless, even when the canonical review wrapper supplies --graphical.
That argument is accepted solely for wrapper compatibility; no visual claim.
The peer models bytes/CTS, not physical baud, FIFO overrun or P4 scheduling.
"""
import argparse
import ctypes as C
import hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
from pathlib import Path
import random
import select
import shutil
import socket
import struct
import subprocess
import tempfile
import threading
import time
from sdcard import Client,path_payload
from qualify_sdcard import AuditedClient,error_checks,exercise as qualify_cycles

def run(a):
    media=a.sdcard.resolve();record={'outcome':'fail','scope':__doc__,'events':[]}
    config=json.loads((media/'fixture.json').read_text())
    disk=media/'working.img';shutil.copyfile(media/'seed.img',disk)
    lib=C.CDLL(str(media/'sd-peer.so'));lock=threading.RLock()
    lib.peer_post.argtypes=[C.c_char_p,C.c_uint,C.c_void_p,C.POINTER(C.c_uint),C.c_uint]
    lib.peer_take.argtypes=[C.c_void_p,C.c_uint]
    lib.peer_receive.argtypes=[C.c_char_p,C.c_uint,C.c_uint]
    start=time.monotonic()
    def now():return int((time.monotonic()-start)*1000)&0xffffffff
    class HTTP(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            with lock:
                value={'protocol':1,'online':bool(lib.peer_online(now())),
                       'pending':bool(lib.peer_pending()),'boot':lib.peer_boot()}
            b=json.dumps(value).encode();self.send_response(200);self.end_headers();self.wfile.write(b)
        def do_POST(self):
            n=int(self.headers['Content-Length']);data=self.rfile.read(n)
            out=C.create_string_buffer(240);length=C.c_uint()
            with lock:code=lib.peer_post(data,n,out,C.byref(length),now())
            self.send_response(code);self.end_headers();self.wfile.write(out.raw[:length.value])
    server=ThreadingHTTPServer(('127.0.0.1',0),HTTP)
    http_thread=threading.Thread(target=server.serve_forever,daemon=True);http_thread.start()
    finished=threading.Event();client_error=[];client_results=[]
    def exercise():
        try:
            url=f'http://127.0.0.1:{server.server_port}'
            audit=(media/'qualification-audit.jsonl').open('w')
            client=(AuditedClient(url,media/'client-state.json',audit,30)
                    if config.get('qualification_smoke') else
                    Client(url,media/'client-state.json',timeout=30))
            deadline=time.monotonic()+30
            while not client.status()['online']:
                if time.monotonic()>deadline:raise TimeoutError('No service presence')
                time.sleep(.03)
            client.connect()
            orphan=path_payload('/extender/sdtest/orphan.bin')
            if client.rpc(10,b'\0'+orphan)!=b'\x06':raise RuntimeError('Missing orphan fixture')
            if client.rpc(10,b'\x02'+orphan)!=b'\0':raise RuntimeError('Orphan recovery failed')
            record['orphan_recovery']=True
            if config.get('qualification_smoke'):
                error_checks(client,'/extender/sdtest/errors.bin')
                qualify_cycles(client,'/extender/sdtest/cycles.bin',
                               sizes=(0,1,211,212,213,256,512,1000,212,213),results=client_results)
                record['qualification_controller_smoke']=True
            for i,size in enumerate([] if config.get('qualification_smoke') else config['sizes']):
                data=random.Random(size).randbytes(size);t=time.monotonic()
                client.upload('/extender/sdtest/game.bin',data,True)
                info=client.rpc(2,path_payload('/extender/sdtest/game.bin'))
                if len(info)!=5 or struct.unpack_from('<I',info)[0]!=size:raise RuntimeError('STAT mismatch')
                listing=client.rpc(3,struct.pack('<I',0)+path_payload('/extender/sdtest'))
                if len(listing)<12 or listing[4]:raise RuntimeError('LIST omitted the uploaded file')
                client.rpc(10,b'\x03'+bytes([len('/extender/sdtest/game.bin')])+b'/extender/sdtest/game.bin')
                client_results.append({'size':size,'sha256':hashlib.sha256(data).hexdigest(),'seconds':time.monotonic()-t})
                print('Raw FAT cycle passed:',size,flush=True)
            client.rpc(11);record['service_exit_response']=True
            client.lock.close();audit.close()
        except Exception as e:client_error.append(repr(e))
        finally:finished.set()
    proc=None;peer=None;transcript=bytearray();received=bytearray();dropped=False
    with tempfile.TemporaryDirectory(prefix='sd-peer-') as tmp:
        listener=socket.socket(socket.AF_UNIX);sockpath=tmp+'/uart1';listener.bind(sockpath);listener.listen(1)
        log=(a.output.with_suffix('.log')).open('wb')
        env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        command=[str(a.emulator),'--mos',str(a.firmware),'--vdp',str(a.vdp),
                 '--sdcard-img',str(disk),'--zero','--renderer','sw','--uart1-peer',sockpath]
        record['command']=command
        try:
            proc=subprocess.Popen(command,cwd=tmp,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
            client_thread=threading.Thread(target=exercise,daemon=True);client_thread.start()
            while not finished.is_set():
                if time.monotonic()-start>600:raise TimeoutError('Whole fixture deadline')
                if proc.poll() is not None:raise RuntimeError('Emulator exited: '+str(proc.returncode))
                for ready in select.select([peer or listener],[],[],.002)[0]:
                    if peer is None:peer,_=listener.accept();peer.setblocking(False)
                    else:
                        data=peer.recv(4096)
                        if not data:raise RuntimeError('UART peer closed')
                        received.extend(data);transcript.extend(data)
                while len(received)>=4:
                    if received[:2]!=b'\x17\0':raise RuntimeError('Unexpected envelope: '+received[:20].hex())
                    op,n=received[2:4]
                    if op in (0x80,0x81):
                        del received[:4]
                        if op==0x80:
                            peer.sendall(bytes([0x80,1,n]));record['events'].append('keyboard admitted')
                        continue
                    if op!=0xf6:raise RuntimeError('Unexpected operation '+hex(op))
                    if len(received)<4+n:break
                    data=bytes(received[4:4+n]);del received[:4+n]
                    # Drop one successful WRITE response before the P4 queue
                    # sees it. The real application must replay without rewriting.
                    if not dropped and len(data)>=20 and data[3]==2 and data[12]==6:
                        dropped=True;record['events'].append('dropped one WRITE response');continue
                    with lock:lib.peer_receive(data,len(data),now())
                if peer:
                    out=C.create_string_buffer(240)
                    with lock:n=lib.peer_take(out,now())
                    if n:peer.sendall(bytes([0x8d,n])+out.raw[:n])
            client_thread.join(timeout=2)
            if client_error:raise RuntimeError(client_error[0])
            if not dropped:raise RuntimeError('Lost-response case was not exercised')
            record['outcome']='pass'
        except Exception as e:record['error']=repr(e);raise
        finally:
            if proc:
                proc.terminate()
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
            if peer:peer.close()
            listener.close();log.close();server.shutdown();server.server_close()
            record['cycles']=client_results;record['seconds']=time.monotonic()-start
            record['uart_sha256']=hashlib.sha256(transcript).hexdigest()
            a.output.with_suffix('.uart').write_bytes(transcript)
            a.output.write_text(json.dumps(record,indent=2)+'\n')
    print('PASS: headless real eZ80/FatFS, P4 queue, HTTP client and lost response. No physical claim.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('emulator','firmware','vdp','sdcard','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--graphical',action='store_true');run(p.parse_args())
