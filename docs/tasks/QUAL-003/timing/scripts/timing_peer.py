#!/usr/bin/env python3
"""Actual EMOS + two native VDP diagnostic modules + FAT SD image.
Native timing is functional evidence only, never device performance evidence.
"""
import argparse,ctypes as c,json,os,pty,re,select,shutil,socket,subprocess,tempfile,time
from pathlib import Path
from console_peer import NativeVdp
from vdu_framer import Framer

def run(args):
    media=args.sdcard.resolve();cfg=json.loads((media/'review.json').read_text())
    native=NativeVdp(media/'peer-native.so')
    session=c.CDLL(str(media/'console-session.so'))
    session.console_peer_request.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32,c.c_void_p]
    session.console_peer_request.restype=c.c_bool;session.console_peer_active.restype=c.c_bool
    transcript=bytearray();ordinary=bytearray();started=time.monotonic();peer=None;debug='';last_vblank=0
    record=dict(outcome='fail',scope=__doc__,controls=[],diagnostic_requests=0,rejection_cases=[])
    native_rx=bytearray();delivery=[];injected=False
    cases=json.loads((media/'corpus.json').read_text())['cases']
    with tempfile.TemporaryDirectory(prefix='graphics-timing-') as temp:
        temp=Path(temp);sock=temp/'uart1';server=socket.socket(socket.AF_UNIX);server.bind(str(sock));server.listen(1)
        image=temp/'sd.img';shutil.copy2(media/'initial.img',image)
        master,slave=pty.openpty()
        env=dict(os.environ,LD_PRELOAD=str(media/'sdl-review.so'),
                 PAIRED_REVIEW_TITLE='Visual validation — screenshot requested: '+cfg['build_id'],
                 SHAPES_REVIEW_KEYS=str(temp/'keys'),SHAPES_REVIEW_CAPTURE=str(temp/'capture'))
        (temp/'keys').write_bytes(b'')
        if not cfg['human']:env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        command=[str(args.emulator.resolve()),'--mos',str(args.firmware.resolve()),'--vdp',str(media/'mainboard-native.so'),
                 '--sdcard-img',str(image),'--renderer','sw','--zero','--uart1-peer',str(sock),
                 '--debugger','--breakpoint',hex(cfg['done'])]
        process=subprocess.Popen(command,cwd=temp,env=env,stdin=slave,stdout=slave,stderr=slave);os.close(slave)
        framer=Framer()
        def pump():
            nonlocal peer,debug,last_vblank,injected
            now=time.monotonic()
            if now-last_vblank>=1/60:native.lib.signal_vblank();native.scanout();last_vblank=now
            for ready in select.select([master,peer or server],[],[],.002)[0]:
                if ready==master:
                    data=os.read(master,65536);transcript.extend(data);debug+=data.decode(errors='replace')
                elif peer is None:peer,_=server.accept();peer.setblocking(False)
                else:
                    incoming=peer.recv(65536)
                    if not incoming:raise RuntimeError('UART1 closed')
                    for packet in framer.feed(incoming):
                        if packet[:3]==b'\x17\0\xf7':
                            control=packet[3:];record['controls'].append(control.hex());reply=(c.c_ubyte*16)()
                            if session.console_peer_request(control,int((now-started)*1000),0x51737acd,reply):
                                if control[3]==1:native.send(b'\x16\0')
                                peer.sendall(b'\xff\x10'+bytes(reply))
                        else:
                            bootstrap=packet[:3] in (b'\x17\0\x80',b'\x17\0\x81')
                            if not bootstrap and not session.console_peer_active():raise RuntimeError('VDU outside committed route')
                            native.send(packet);ordinary.extend(packet)
                            if packet[:3]==b'\x17\0\xef':record['diagnostic_requests']+=1
            native_rx.extend(native.receive())
            while len(native_rx)>=2 and len(native_rx)>=2+native_rx[1]:
                frame=bytes(native_rx[:2+native_rx[1]]);del native_rx[:len(frame)]
                if frame[:6]==b'\x8c\x10QTG\xa1':
                    token=int.from_bytes(frame[6:8],'little');metric=frame[8]
                    if metric==0 and not injected:
                        injected=True
                        # Space corrupt/stale admissions so a host burst cannot
                        # manufacture UART overrun. The real reply comes last.
                        faults=[]
                        faults.append(('short',b'\x8c\x0f'+frame[2:-1]))
                        for name,index,value in [('magic',2,0),('version',5,0xa2),('source',9,0),('stale-token',6,(token-1)&255)]:
                            bad=bytearray(frame);bad[index]=value;faults.append((name,bytes(bad)))
                        for i,(name,bad) in enumerate(faults):
                            delivery.append((now+i*.02,bad));record['rejection_cases'].append(name)
                        delivery.append((now+len(faults)*.02,frame));continue
                    if metric==1 and token%2==0:
                        case=cases[((token-1)%(len(cases)*2))//2]['name']
                        if case.startswith(('BSP22_','BSP26_','BSP29_')):
                            frames=args.output.parent/'frames';frames.mkdir(exist_ok=True)
                            native.capture(frames/(case.lower()+'.bmp'))
                delivery.append((now,frame))
            if peer and delivery and now>=delivery[0][0]:
                peer.sendall(delivery.pop(0)[1])
            if process.poll() is not None:raise RuntimeError(f'Fab exited with status {process.returncode}')
        def prompt():
            nonlocal debug
            while '>> ' not in debug:
                if time.monotonic()-started>360:raise TimeoutError('Review exceeded six minutes')
                pump()
            value,debug=debug.split('>> ',1);return value
        try:
            record['stop']=prompt()
            os.write(master,f'mem {hex(cfg["status"])} 3\n'.encode());record['status_dump']=prompt()
            dest=args.output.with_suffix('.csv')
            subprocess.run([cfg['mcopy'],'-o','-i',str(image),'::/extender/gqt/GQT001.CSV',str(dest)],check=True)
            text=dest.read_text();record['terminal']=text.splitlines()[-1]
            if '# terminal,status=0,saved=256,' not in text:raise RuntimeError('Incomplete native paired benchmark: '+record['terminal'])
            if not re.search(r': 00 00 00',record['status_dump']):raise RuntimeError('Fixture final route/exit check failed')
            record['outcome']='pass';print('Paired native graphics timing review passed; 256 intervals saved.',flush=True)
            args.output.write_text(json.dumps(record,indent=2)+'\n')
            if cfg['human']:
                os.write(master,b'continue\n')
                # Keep the completed console available for the Author's screenshot.
                while process.poll() is None:
                    try:pump()
                    except (OSError,RuntimeError):
                        if process.poll() is None:raise
        finally:
            record['process_exit']=process.poll()
            if process.poll() is not None:
                while select.select([master],[],[],0)[0]:
                    try: data=os.read(master,65536)
                    except OSError: break
                    if not data: break
                    transcript.extend(data)
            # Preserve the durable prefix even if the emulator exits before the
            # fixture's final breakpoint; it identifies the unfinished case.
            subprocess.run([cfg['mcopy'],'-o','-i',str(image),'::/extender/gqt/GQT001.CSV',str(args.output.with_suffix('.csv'))],
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            args.output.write_text(json.dumps(record,indent=2)+'\n');args.output.with_suffix('.log').write_bytes(transcript)
            args.output.with_suffix('.uart').write_bytes(ordinary)
            if process.poll() is None:process.terminate();process.wait(timeout=5)
            os.close(master)
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('emulator','firmware','vdp','sdcard','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--graphical',action='store_true');run(p.parse_args())
