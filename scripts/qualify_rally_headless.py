#!/usr/bin/env python3
"""Real eZ80 Rally/EMOS with a portable P4 keyboard/telemetry peer, always silent.

Invoke only through the generated profile's ./fab-agon-emulator entry point.
--graphical is accepted for review-wrapper compatibility; SDL stays dummy.
Byte transport models no physical baud clock or ESP-IDF task scheduling.
"""
import argparse
import ctypes as C
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import socket
import struct
import subprocess
import tempfile
import threading
import time
from rally_drive import Sample,run as drive
from rally_trial import quit_game

def run(args):
    media=args.sdcard;record={'scope':__doc__,'outcome':'fail','packets':0,'packet_timing':[]}
    config=json.loads((media/'fixture.json').read_text());disk=media/'working.img'
    maximum_gap=float(config.get('maximum_gap_seconds',.3))
    if maximum_gap not in (.2,.3,.35):
        raise ValueError('Use an explicitly recorded 200/300/350ms observation bound')
    record['telemetry_limit_seconds']=maximum_gap
    record['telemetry_limit_reason']=(
        'Current physical controller bound' if maximum_gap==.3 else
        'Explicit historical diagnostic bound; not current physical acceptance')
    runtime_manifest=args.emulator.resolve().parents[2]/'runtime-inputs.json'
    runtime=json.loads(runtime_manifest.read_text())
    tx_interrupts=runtime.get('uart1_tx_interrupts',False)
    if tx_interrupts!=config.get('uart1_tx_interrupts',False):
        raise ValueError('Frozen fixture and actual runtime disagree about UART1 TX interrupts')
    record['native_runtime']=dict(uart1_tx_interrupts=tx_interrupts,
        manifest_sha256=hashlib.sha256(runtime_manifest.read_bytes()).hexdigest(),
        executable_sha256=hashlib.sha256(args.emulator.read_bytes()).hexdigest(),
        reference_commit=runtime['reference_commit'])
    record['native_uart_limit']=(
        'Opt-in TX-empty/complete demand and read-only IIR; no physical baud or ESP-IDF scheduling proof'
        if tx_interrupts else
        'No TX-empty interrupt demand; bounded VBlank/RX drains, not physical timing')
    shutil.copyfile(media/'seed.img',disk)
    lib=C.CDLL(str(media/'bench-peer.so'));lib.key_begin(42000)
    lib.key_post.argtypes=[C.c_char_p,C.c_uint,C.c_uint]
    lib.telemetry_receive.argtypes=[C.c_char_p,C.c_uint,C.c_uint]
    lock=threading.RLock();start=time.monotonic()
    now=lambda:int((time.monotonic()-start)*1000)&0xffffffff
    class HTTP(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def reply(self,code,data):
            self.send_response(code);self.send_header('Content-Length',str(len(data)))
            self.end_headers();self.wfile.write(data)
        def do_GET(self):
            out=C.create_string_buffer(500)
            with lock:
                if self.path=='/keyboard/status':lib.key_status(out,500,now())
                elif self.path=='/telemetry/latest':lib.telemetry_status(out,500,now())
                else:self.reply(404,b'{}');return
            self.reply(200,out.value)
        def do_POST(self):
            data=self.rfile.read(int(self.headers['Content-Length']));out=C.create_string_buffer(500)
            with lock:
                code=lib.key_post(data,len(data),now());lib.key_status(out,500,now())
            self.reply(code,out.value)
    server=ThreadingHTTPServer(('127.0.0.1',0),HTTP)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    finished=threading.Event();errors=[]
    def exercise():
        try:
            deadline=time.monotonic()+45
            while True:
                out=C.create_string_buffer(500)
                with lock:lib.telemetry_status(out,500,now())
                value=json.loads(out.value)
                if value['online']:break
                if time.monotonic()>deadline:raise TimeoutError('No resident telemetry from Rally')
                time.sleep(.02)
            sample=Sample.decode(value,maximum_gap*1000)
            if sample.grip!=200:raise RuntimeError('Author-requested 200% grip is not active')
            if sample.step!=config.get('steering_step',2):
                raise RuntimeError('Unexpected steering step for this frozen case')
            if config.get('observe_only',False):
                # Packet-assembly diagnosis only: no driver or keyboard session.
                # Never represent a stationary trace as passing driving evidence.
                until=time.monotonic()+config['seconds']
                while time.monotonic()<until:time.sleep(.02)
                record['outcome']='observation only; no driving acceptance'
                return
            record['driving']=drive(f'http://127.0.0.1:{server.server_port}',
                                   args.output.with_suffix('.keys.json'),
                                   args.output.with_suffix('.driving.jsonl'),config['seconds'],
                                   maximum_gap=maximum_gap)
            result=record['driving']
            if result.get('error') or result.get('release_error'):raise RuntimeError(str(result))
            # A canceled HTTP session alone does not prove that the guest has
            # consumed the key-up packets. Keep forwarding the ordinary UART
            # stream until a later game snapshot reports released driving keys.
            deadline=time.monotonic()+2
            while True:
                out=C.create_string_buffer(500)
                with lock:lib.telemetry_status(out,500,now())
                released=Sample.decode(json.loads(out.value),maximum_gap*1000)
                if not released.held:
                    record['guest_controls_released']=dict(frame=released.frame,held=released.held)
                    break
                if time.monotonic()>deadline:raise TimeoutError('Guest driving controls did not release')
                time.sleep(.02)
            exit_folder=args.output.parent/'native-exit';exit_folder.mkdir()
            record['application_exit']=quit_game(
                f'http://127.0.0.1:{server.server_port}',exit_folder,result['exit_admission'])
            out=C.create_string_buffer(500)
            with lock:lib.key_status(out,500,now())
            record['final_keyboard']=json.loads(out.value)
            if record['final_keyboard']['held'] or record['final_keyboard']['pending']:
                raise RuntimeError('Keyboard output not fully released after exit')
            if result['grass'] or result['distance']<sample.length:raise RuntimeError('No complete on-road lap')
            if result['contacts']:raise RuntimeError('Traffic contact during headless run')
            record['outcome']='pass'
        except Exception as error:errors.append(repr(error));record['error']=repr(error)
        finally:finished.set()
    process=None;peer=None;received=bytearray();received_at=[];transcript=bytearray()
    with tempfile.TemporaryDirectory(prefix='rally-telemetry-') as temporary:
        listener=socket.socket(socket.AF_UNIX);path=temporary+'/uart1'
        listener.bind(path);listener.listen(1)
        with args.output.with_suffix('.log').open('wb') as log:
            try:
                command=[str(args.emulator),'--mos',str(args.firmware),'--vdp',str(args.vdp),
                         '--sdcard-img',str(disk),'--zero','--renderer','sw','--uart1-peer',path]
                record['command']=command
                process=subprocess.Popen(command,cwd=temporary,stdin=subprocess.DEVNULL,
                    stdout=log,stderr=subprocess.STDOUT,
                    env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy'))
                worker=threading.Thread(target=exercise,daemon=True);worker.start()
                while not finished.is_set():
                    if time.monotonic()-start>config['seconds']+55:raise TimeoutError('Whole run deadline')
                    if process.poll() is not None:raise RuntimeError('Emulator exited')
                    for ready in select.select([peer or listener],[],[],.001)[0]:
                        if peer is None:peer,_=listener.accept();peer.setblocking(False)
                        else:
                            data=peer.recv(4096)
                            if not data:raise RuntimeError('UART peer disconnected')
                            received.extend(data);transcript.extend(data)
                            received_at.extend([time.monotonic()-start]*len(data))
                    while len(received)>=4:
                        if received[:2]!=b'\x17\0':raise RuntimeError('Envelope lost framing')
                        opcode,n=received[2:4]
                        if opcode in (0x80,0x81):
                            del received[:4];del received_at[:4]
                            if opcode==0x81:
                                with lock:lib.key_admit(n)
                            else:peer.sendall(bytes([0x80,1,n]))
                            continue
                        if opcode!=0xf5 or n!=140:raise RuntimeError('Unexpected UART1 command')
                        if len(received)<144:break
                        payload=bytes(received[4:144]);packet_times=received_at[:144]
                        del received[:144];del received_at[:144]
                        with lock:accepted=lib.telemetry_receive(payload,140,now())
                        if not accepted:raise RuntimeError('P4 rejected a telemetry snapshot')
                        record['packets']+=1
                        record['packet_timing'].append(dict(
                            first_host_seconds=packet_times[0],last_host_seconds=packet_times[-1],
                            assembly_ms=(packet_times[-1]-packet_times[0])*1000,
                            chunks=len(set(packet_times)),
                            frame=struct.unpack_from('<I',payload,8)[0],
                            raw_clock=struct.unpack_from('<I',payload,12)[0]))
                    if peer:
                        out=C.create_string_buffer(6)
                        with lock:n=lib.key_take(out,now())
                        if n:peer.sendall(out.raw[:n])
                worker.join(timeout=1)
                if errors:raise RuntimeError(errors[0])
            except Exception as error:record['error']=repr(error);record['outcome']='fail'
            finally:
                if process:
                    process.terminate()
                    try:process.wait(timeout=5)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
                if peer:peer.close()
                listener.close();server.shutdown();server.server_close()
                record['seconds']=time.monotonic()-start
                args.output.with_suffix('.uart').write_bytes(transcript)
                args.output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2),flush=True)
    return 0 if record['outcome'] in ('pass','observation only; no driving acceptance') else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('emulator','firmware','vdp','sdcard','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--graphical',action='store_true')
    raise SystemExit(run(parser.parse_args()))
