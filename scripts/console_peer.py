#!/usr/bin/env python3
"""Bounded real-EMOS console review using native stock VDP as the UART1 peer.

The lease and key mapper are compiled from maintained P4 headers. Stock native
VDP renders the ordinary stream and generates actual display replies. This is
not ESP-IDF, electrical, browser-video or complete VDU compatibility evidence.
Automated PASS covers control/byte-stream/prompt assertions, not pixel equality.
The selected native VDP can omit glyphs despite consuming the complete stream;
PORT-008 records a native-only timed replay and its complete VDP echo. Do not
hide that rendering issue with byte pacing or treat these images as P4 proof.
The control separator is ONLY for this scripted text/query corpus: it cannot
replace the production retained parser's command-boundary control hook.
"""
import argparse
import ctypes as c
import hashlib
import json
import os
from pathlib import Path
import select
import socket
import subprocess
import tempfile
import threading
import time
import traceback
from PIL import Image


class NativeVdp:
    def __init__(self, library):
        self.lib=c.CDLL(str(library))
        self.lib.z80_send_to_vdp.argtypes=[c.c_ubyte]
        self.lib.z80_recv_from_vdp.argtypes=[c.POINTER(c.c_ubyte)]
        self.lib.z80_recv_from_vdp.restype=c.c_bool
        self.lib.z80_uart0_is_cts.restype=c.c_bool
        self.lib.setVdpDebugLogging(False)
        self.cts_waits=0
        self.width,self.height,self.hz=c.c_uint(),c.c_uint(),c.c_float()
        self.frame=(c.c_ubyte*(1024*768*3))()
        def boot():
            self.lib.vdp_setup()
            self.lib.vdp_loop()
        threading.Thread(target=boot,daemon=True).start()

    def send(self, data):
        # Fab's native serial queue drops writes above its hard threshold.
        # Obey its CTS just as Fab's mainboard UART bridge does; the socket
        # runtime's constant UART1 CTS does not protect this second queue.
        for b in data:
            deadline=time.monotonic()+5
            while not self.lib.z80_uart0_is_cts():
                self.cts_waits+=1
                if time.monotonic()>deadline:raise RuntimeError('Native VDP CTS timeout')
                self.lib.signal_vblank()
                time.sleep(.0001)
            self.lib.z80_send_to_vdp(b)

    def receive(self):
        out=bytearray();b=c.c_ubyte()
        while self.lib.z80_recv_from_vdp(c.byref(b)):out.append(b.value)
        return out

    def scanout(self):
        # Match Fab's regular framebuffer scanout as well as its VBlank signal.
        self.lib.copyVgaFramebuffer(c.byref(self.width),c.byref(self.height),self.frame,c.byref(self.hz))

    def capture(self,path):
        self.scanout()
        Image.frombytes('RGB',(self.width.value,self.height.value),
                        bytes(self.frame)[:self.width.value*self.height.value*3]).save(path)


def run(args):
    media=args.sdcard.resolve(strict=True)
    native=NativeVdp(args.vdp or media/'vdp-reference.so')
    session=c.CDLL(str(media/'console-session.so'))
    session.console_peer_request.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32,c.c_void_p]
    session.console_peer_request.restype=c.c_bool
    session.console_peer_active.restype=c.c_bool
    session.console_peer_key.argtypes=[c.c_ubyte,c.c_void_p]
    session.console_peer_key.restype=c.c_bool
    record={'outcome':'fail','scope':__doc__,'controls':[],'keys_sent':0,'stages':[],
            'pixel_validation':'not asserted; native reference rendering issue remains open',
            'withhold_activation':args.withhold_activation}
    transcript=bytearray();ordinary=bytearray()
    started=time.monotonic();scheduled=[];key_end=started;stage=0;stage_at=started
    finished=None;admitted=False;peer=None;incoming=bytearray();last_vblank=0
    reply_buffer=bytearray();barriers={}
    def save():
        record['native_vdp_cts_waits']=native.cts_waits
        args.output.write_text(json.dumps(record,indent=2)+'\n')
        args.output.with_suffix('.log').write_bytes(transcript)
        args.output.with_suffix('.uart').write_bytes(ordinary)
    def type_line(text):
        nonlocal key_end
        begin=max(time.monotonic()+0.1,key_end+0.1)
        for i,b in enumerate(text.encode('ascii')+b'\r'):
            packet=(c.c_ubyte*6)()
            if not session.console_peer_key(b,packet):raise ValueError('Unmapped review key '+repr(chr(b)))
            down=bytes(packet);up=down[:5]+b'\0'
            scheduled.extend([(begin+i*.05,down),(begin+i*.05+.02,up)])
        key_end=begin+len(text)*.05+.02
    with tempfile.TemporaryDirectory(prefix='excom-peer-') as tmp:
        server=socket.socket(socket.AF_UNIX);path=tmp+'/uart1';server.bind(path);server.listen(1)
        command=[str(args.emulator.resolve()),'--mos',str(args.firmware.resolve()),
                 '--sdcard',str(media),'--zero','--uart1-peer',path]
        if args.graphical:command+=['--vdp',str(args.vdp.resolve()),'--renderer','sw','--verbose']
        env=dict(os.environ);env['LD_LIBRARY_PATH']=str(Path.home()/'.local/lib')+os.pathsep+env.get('LD_LIBRARY_PATH','')
        process=subprocess.Popen(command,cwd=tmp,env=env,stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        try:
            while True:
                now=time.monotonic()
                if now-last_vblank>=1/60:
                    native.lib.signal_vblank();native.scanout();last_vblank=now
                if finished is None and now-started>70:raise RuntimeError('Console review deadline, stage '+str(stage))
                for ready in select.select([process.stdout,peer or server],[],[],.003)[0]:
                    if ready is process.stdout:transcript.extend(os.read(ready.fileno(),65536))
                    elif peer is None:peer,_=server.accept();peer.setblocking(False)
                    else:
                        data=peer.recv(4096)
                        if not data and finished is None:raise RuntimeError('UART peer closed')
                        incoming.extend(data)
                while incoming:
                    if incoming[0]==23:
                        if len(incoming)<3:break
                        if incoming[:3]==bytes([23,0,0xF7]):
                            if len(incoming)<19:break
                            control=bytes(incoming[3:19]);del incoming[:19]
                            record['controls'].append(control.hex())
                            reply=(c.c_ubyte*16)()
                            if not args.withhold_activation and session.console_peer_request(control,int((now-started)*1000),0x729AD041,reply):
                                if control[3]==1:native.send(b'\x0c')
                                peer.sendall(b'\xff\x10'+bytes(reply))
                            continue
                        if incoming[:3] in (bytes([23,0,0x80]),bytes([23,0,0x81])):
                            if len(incoming)<4:break
                            data=bytes(incoming[:4]);del incoming[:4];native.send(data)
                            if data[2]==0x80 and not admitted:admitted=True;stage_at=now
                            ordinary.extend(data);continue
                        data=bytes(incoming[:3]);del incoming[:3]
                    else:data=bytes([incoming.pop(0)])
                    if not session.console_peer_active():raise RuntimeError('Ordinary VDU before activation: '+data.hex())
                    native.send(data);ordinary.extend(data)
                replies=native.receive()
                reply_buffer.extend(replies)
                while len(reply_buffer)>=2 and len(reply_buffer)>=reply_buffer[1]+2:
                    packet=bytes(reply_buffer[:reply_buffer[1]+2]);del reply_buffer[:len(packet)]
                    if packet[:2]==b'\x80\x01':barriers[packet[2]]=now
                if peer and replies:peer.sendall(replies)
                while scheduled and scheduled[0][0]<=now:
                    _,packet=scheduled.pop(0);peer.sendall(packet);record['keys_sent']+=1
                if stage==0 and admitted and now-stage_at>.8:
                    type_line('echo Legacy input');type_line('eMoS ExCoM');stage=1
                active=bool(session.console_peer_active())
                if args.withhold_activation:
                    if stage==1 and b'display switch failed' in transcript and not scheduled:
                        type_line('echo Failed entry recovered');type_line('emos keyinput');stage=8
                else:
                    if stage==1 and active and not scheduled and now>key_end+.6:
                        type_line('echo ExCom one');type_line('emos keyinput');type_line('VDU 23 0 202 23 0 128 90');stage=2
                    elif stage==2 and 90 in barriers and now>barriers[90]+.5 and not scheduled:
                        native.capture(args.output.with_name('excom-first.png'))
                        type_line('EMOS LEGACY');stage=3
                    elif stage==3 and not active and not scheduled and now>key_end+.5:
                        type_line('echo Legacy return');type_line('EMOS EXCOM');stage=4
                    elif stage==4 and active and not scheduled and now>key_end+.6:
                        type_line('echo ExCom two');type_line('emos keyinput');type_line('VDU 23 0 202 23 0 128 91');stage=5
                    elif stage==5 and 91 in barriers and now>barriers[91]+.5 and not scheduled:
                        native.capture(args.output.with_name('excom-second.png'))
                        type_line('eMoS LeGaCy');stage=6
                    elif stage==6 and not active and not scheduled and now>key_end+.5:
                        type_line('echo Visual validation - screenshot requested');type_line('echo ExCom review complete');type_line('emos keyinput');stage=8
                if stage==8 and not scheduled and now>key_end+.6:
                    if not args.graphical:
                        expected=b'Failed entry recovered' if args.withhold_activation else b'ExCom review complete'
                        if expected not in transcript or b'Keyboard input: extender' not in transcript or not transcript.rstrip().endswith(b'/ *'):
                            raise RuntimeError('Final Legacy text/source/prompt missing')
                    if not args.withhold_activation:
                        for expected in (b'ExCom one',b'ExCom two',b'Keyboard input: extender'):
                            if expected not in ordinary:raise RuntimeError('Missing EDP output '+repr(expected))
                        if [bytes.fromhex(p)[3] for p in record['controls']]!=[1,2,3,1,2,3]:
                            raise RuntimeError('Unexpected control sequence')
                    record['outcome']='awaiting-human-review' if args.graphical else 'pass'
                    finished=now;stage=9;save()
                    print('ExCom review complete: inspect native EDP images and final mainboard prompt.',flush=True)
                    if not args.graphical:break
                if process.poll() is not None:
                    if finished is None:raise RuntimeError('Emulator exited before review completion')
                    break
        except Exception as error:
            record['error']=str(error);raise
        finally:
            process.terminate()
            try:rest,_=process.communicate(timeout=3)
            except subprocess.TimeoutExpired:process.kill();rest,_=process.communicate()
            transcript.extend(rest)
            if peer:peer.close()
            server.close();save();native.lib.vdp_shutdown()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('emulator','firmware','sdcard','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--vdp',type=Path);p.add_argument('--graphical',action='store_true')
    p.add_argument('--withhold-activation',action='store_true')
    a=p.parse_args()
    try:run(a)
    except BaseException:traceback.print_exc();os._exit(1)
    # Native VDP owns C++ threads; never unload the library underneath them.
    os._exit(0)
