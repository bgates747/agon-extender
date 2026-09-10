#!/usr/bin/env python3
"""Real EMOS + two native stock VDPs, with the maintained P4 control/key mapper.

This bounded review checks paired routing, independent probes, image retention
and exit. It does not emulate ESP-IDF, P4 rendering, Ethernet or physical UART.
Only the task's generated VDU corpus is admitted by the command-length framer.
"""
import sys
sys.dont_write_bytecode=True
import argparse
import ctypes as c
import json
from datetime import datetime,timezone
import os
from pathlib import Path
import pty
import re
import select
import socket
import subprocess
import tempfile
import time
import traceback
from PIL import Image
from console_peer import NativeVdp
from vdu_framer import Framer


def run(args):
    media=args.sdcard.resolve(strict=True)
    config=json.loads((media/'review.json').read_text())
    symbols=json.loads((media/'symbols.json').read_text())
    output=args.output.parent; output.mkdir(parents=True,exist_ok=True)
    record={'outcome':'fail','scope':__doc__,'controls':[],'stages':[],
            'run_id':'QUAL-003-'+datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ'),
            'capture_scale_override':os.environ.get('PAIRED_REVIEW_WINDOW_SCALE')}
    native=NativeVdp(args.vdp)
    session=c.CDLL(str(media/'console-session.so'))
    session.console_peer_request.argtypes=[c.c_void_p,c.c_uint32,c.c_uint32,c.c_void_p]
    session.console_peer_request.restype=c.c_bool
    session.console_peer_active.restype=c.c_bool
    session.console_peer_key.argtypes=[c.c_ubyte,c.c_void_p]
    session.console_peer_key.restype=c.c_bool
    framer=Framer(); transcript=bytearray(); ordinary=bytearray()
    started=time.monotonic(); last_vblank=0; peer=None; debug=''; keys=[]
    process=None
    with tempfile.TemporaryDirectory(prefix='paired-graphics-') as tmp:
        tmp=Path(tmp); sock=tmp/'uart1'; server=socket.socket(socket.AF_UNIX)
        server.bind(str(sock)); server.listen(1)
        master,slave=pty.openpty()
        capture=tmp/'capture-request'; keyfile=tmp/'keys'; keyfile.write_bytes(b'')
        env=dict(os.environ)
        env.update(LD_PRELOAD=str(media/'sdl-review.so'),SHAPES_REVIEW_KEYS=str(keyfile),
                   SHAPES_REVIEW_CAPTURE=str(capture),
                   PAIRED_REVIEW_TITLE='Visual validation — screenshot requested: paired graphics')
        if not config['human']:
            env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
        command=[str(args.emulator.resolve()),'--mos',str(args.firmware.resolve()),
                 '--sdcard',str(media),'--vdp',str(args.vdp.resolve()),'--renderer','sw',
                 '--scale','integer','--zero','--uart1-peer',str(sock),'--debugger',
                 '--breakpoint',hex(symbols['waitKeypress']),
                 '--breakpoint',hex(symbols[config['app']+'_review_done']),
                 '--breakpoint',hex(symbols['paired_failure'])]
        process=subprocess.Popen(command,cwd=tmp,env=env,stdin=slave,stdout=slave,stderr=slave)
        os.close(slave)

        def pump():
            nonlocal peer,debug,last_vblank
            now=time.monotonic()
            if now-last_vblank>=1/60:
                native.lib.signal_vblank(); native.scanout(); last_vblank=now
            for ready in select.select([master,peer or server],[],[],.003)[0]:
                if ready==master:
                    data=os.read(master,65536);transcript.extend(data)
                    debug+=data.decode(errors='replace')
                elif peer is None:
                    peer,_=server.accept();peer.setblocking(False)
                else:
                    data=peer.recv(65536)
                    if not data:raise RuntimeError('Emulator UART1 closed')
                    for packet in framer.feed(data):
                        if packet[:3]==b'\x17\0\xf7':
                            control=packet[3:];record['controls'].append(control.hex())
                            reply=(c.c_ubyte*16)()
                            if session.console_peer_request(control,int((now-started)*1000),0x729ad041,reply):
                                # Complete retained mode initialization for fresh entry.
                                if control[3]==1:native.send(b'\x16\0')
                                peer.sendall(b'\xff\x10'+bytes(reply))
                        else:
                            bootstrap=packet[:3] in (b'\x17\0\x80',b'\x17\0\x81')
                            if not bootstrap and not session.console_peer_active():
                                raise RuntimeError('VDU outside committed route: '+packet.hex())
                            native.send(packet);ordinary.extend(packet)
            replies=native.receive()
            if peer and replies:peer.sendall(replies)
            while keys and keys[0][0]<=now:
                _,packet=keys.pop(0);peer.sendall(packet)
            if process.poll() is not None:raise RuntimeError('Emulator exited')

        def delay(seconds):
            end=time.monotonic()+seconds
            while time.monotonic()<end:pump()

        def receive(timeout=50):
            nonlocal debug
            deadline=time.monotonic()+timeout
            while '>> ' not in debug:
                if time.monotonic()>deadline:raise TimeoutError('Debugger: '+debug[-1200:])
                pump()
            text,debug=debug.split('>> ',1)
            return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]','',text)

        def command(text):
            os.write(master,(text+'\n').encode());return receive()

        def memory(address,size):
            text=command(f'mem {hex(address)} {hex(size)}');data=[]
            for line in text.splitlines():
                match=re.match(r'^[0-9a-f]{6}: ((?:[0-9a-f]{2} ?)+) \|',line)
                if match:data.extend(int(v,16) for v in match[1].split())
            if len(data)!=size:raise ValueError('Unexpected memory dump '+text)
            return data

        def byte(name):return memory(symbols[name],1)[0]

        def type_key(character):
            packet=(c.c_ubyte*6)()
            if not session.console_peer_key(character,packet):raise ValueError('Unmapped key')
            now=time.monotonic();down=bytes(packet)
            keys.extend([(now+.2,down),(now+.35,down[:5]+b'\0')])

        def shot(index):
            main=output/f'{index:03}-mainboard.bmp';edp=output/f'{index:03}-edp.png'
            main.unlink(missing_ok=True)
            delay(.15)
            request=tmp/'request.tmp';request.write_text(str(main)+'\n');request.replace(capture)
            deadline=time.monotonic()+8
            while not main.exists() or capture.exists():
                if time.monotonic()>deadline:raise TimeoutError('Mainboard frame capture')
                pump()
            # Normalize the actual integer-scaled SDL capture for comparison;
            # RGB conversion discards SDL's non-display alpha channel.
            frame=Image.open(main).convert('RGB')
            if frame.width%512 or frame.height%384 or frame.width//512!=frame.height//384:
                raise RuntimeError('Unexpected mainboard capture dimensions')
            frame.resize((512,384),Image.Resampling.NEAREST).save(main)
            native.capture(edp)
            return main,edp

        try:
            receive()
            for index in range(config['stages']):
                state=command('state')
                if f'{symbols["waitKeypress"]:06x}:' not in state:
                    raise RuntimeError('Fixture did not reach paired pause: '+state)
                if config.get('asset_fault'):
                    error=byte('load_error')
                    if error not in (1,2):raise RuntimeError('Missing asset error status')
                    record['stages'].append(dict(asset_error=error))
                    shot(index)
                    os.write(master,b'continue\n');type_key(27);receive()
                    break
                page=byte('current_page')
                stage=byte('current_stage') if config['app']=='bitmaps' else 1
                row=(byte('paired_stage_index') if config['app']=='bitmaps' else page-1)*4
                main=memory(symbols['results']+row,4); edp=memory(symbols['results_edp']+row,4)
                if byte('paired_target')!=1 or byte('paired_status') or not session.console_peer_active():
                    raise RuntimeError('Pause did not retain the EDP route')
                if main[3] or edp[3] or main!=edp or main[1]+main[2]!=main[0]:
                    raise RuntimeError(f'Paired probe mismatch/timeout: {main} {edp}')
                observed={name:memory(symbols[name],(main[1]+main[2])*3)
                          for name in ('observed_pixels','observed_pixels_edp')}
                if observed['observed_pixels']!=observed['observed_pixels_edp']:
                    raise RuntimeError('Independent renderer samples differ')
                paths=shot(index)
                record['stages'].append(dict(page=page,stage=stage,mainboard=main,edp=edp,
                    observed=observed,images=[p.name for p in paths]))
                print(f'{config["app"]} {page}.{stage}: both {main[1]}/{main[0]}, {main[3]} timeouts',flush=True)
                if config['human'] and index+1==config['stages']:
                    # The ready review stays at the paired pause. Frame pixels come
                    # from the actual two VDPs; labels do not modify either scene.
                    from PIL import ImageDraw
                    pair=Image.new('RGB',(1024,414),'#202020')
                    draw=ImageDraw.Draw(pair)
                    draw.text((8,6),'Mainboard VDP',fill='white')
                    draw.text((520,6),'UART1 native VDP reference (P4 substitute)',fill='white')
                    pair.paste(Image.open(paths[0]).convert('RGB'),(0,30))
                    pair.paste(Image.open(paths[1]).convert('RGB'),(512,30))
                    target=output/'paired-review.png';pair.save(target)
                    subprocess.Popen(['xdg-open',str(target)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                    record['outcome']='awaiting-human-review'
                    args.output.write_text(json.dumps(record,indent=2)+'\n')
                    print('Visual validation — screenshot requested: compare the two images.',flush=True)
                    while True:pump()
                os.write(master,b'continue\n')
                type_key(27 if config['escape'] and index+1==config['stages'] else 32)
                receive()
            state=command('state')
            if f'{symbols[config["app"]+"_review_done"]:06x}:' not in state or ('HL:000001' if config.get('asset_fault') else 'HL:000000') not in state:
                raise RuntimeError('Fixture did not return success: '+state)
            if not session.console_peer_active():raise RuntimeError('Exit lost ExCom')
            os.write(master,b'continue\n');delay(.8)
            if b'/extender *' not in ordinary[-100:]:
                raise RuntimeError('ExCom MOS prompt missing after exit: '+repr(ordinary[-180:]))
            record['exit']='ExCom MOS prompt; expected HL='+str(1 if config.get('asset_fault') else 0)
            record['outcome']='pass'
        except RuntimeError:
            if record['outcome']!='awaiting-human-review':raise
        finally:
            if process.poll() is None:process.terminate()
            process.wait(timeout=5);os.close(master);server.close()
            if peer:peer.close()
            args.output.write_text(json.dumps(record,indent=2)+'\n')
            args.output.with_suffix('.log').write_bytes(transcript)
            args.output.with_suffix('.uart').write_bytes(ordinary)
            native.lib.vdp_shutdown()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('emulator','firmware','sdcard','output','vdp'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--graphical',action='store_true')
    args=p.parse_args()
    try:run(args)
    except BaseException:traceback.print_exc();os._exit(1)
    os._exit(0)
