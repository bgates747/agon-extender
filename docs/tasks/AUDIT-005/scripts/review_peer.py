#!/usr/bin/env python3
"""Run the actual SD benchmark with EMOS and two native VDP references.

Only console control is supplied by the maintained P4 session helper. Native
VDP consumes and replies to ordinary UART1 bytes; it is not a P4 performance
model. Results created by MOS exercise its real SD API. No keyboard injection.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import ctypes as c
import hashlib
import json
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
from console_peer import NativeVdp
from benchmark_framer import Framer
from analyze import read_results


def run(args):
    media = args.sdcard.resolve()
    config = json.loads((media/'review.json').read_text())
    image=media/'sd.img'
    for path,expected in ((image,config['image_sha256']),(Path(config['mcopy']),config['mcopy_sha256'])):
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise RuntimeError('Changed review input: '+str(path))
    record = dict(outcome='fail', scope=__doc__, controls=[], output_bytes=0)
    native = NativeVdp(args.vdp)
    session = c.CDLL(str(media/'console-session.so'))
    session.console_peer_request.argtypes = [c.c_void_p,c.c_uint32,c.c_uint32,c.c_void_p]
    session.console_peer_request.restype = c.c_bool
    framer = Framer()
    transcript = bytearray()
    uart = bytearray()
    debug = ''
    peer = None
    started = time.monotonic()
    last_tick = started
    delayed=[]
    withheld=False
    pixel_number=0
    with tempfile.TemporaryDirectory(prefix='uart-benchmark-review-') as tmp:
        tmp = Path(tmp)
        server = socket.socket(socket.AF_UNIX)
        server.bind(str(tmp/'uart1')); server.listen(1)
        master, slave = pty.openpty()
        env = dict(os.environ)
        env.update(SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
        process = subprocess.Popen([
            str(args.emulator), '--mos',str(args.firmware),'--sdcard-img',str(image),
            '--vdp',str(args.vdp),'--renderer','sw','--zero','--uart1-peer',str(tmp/'uart1'),
            '--debugger','--breakpoint',hex(config['done'])],cwd=tmp,env=env,
            stdin=slave,stdout=slave,stderr=slave)
        os.close(slave)

        def pump():
            nonlocal peer, debug, last_tick, withheld, pixel_number
            now = time.monotonic()
            if now-last_tick >= 1/60:
                native.lib.signal_vblank(); native.scanout(); last_tick=now
            for ready in select.select([master, peer or server],[],[],.002)[0]:
                if ready==master:
                    data=os.read(master,65536); transcript.extend(data)
                    debug+=data.decode(errors='replace')
                elif peer is None:
                    peer,_=server.accept(); peer.setblocking(False)
                else:
                    data=peer.recv(4096)
                    if not data: raise RuntimeError('UART peer closed')
                    for packet in framer.feed(data):
                        if packet[:3]==b'\x17\0\xf7':
                            control=packet[3:]; record['controls'].append(control.hex())
                            if not config.get('absent'):
                                reply=(c.c_ubyte*16)()
                                if session.console_peer_request(control,int((now-started)*1000),0x729ad041,reply):
                                    if control[3]==1: native.send(b'\x16\0')
                                    peer.sendall(b'\xff\x10'+bytes(reply))
                        else:
                            uart.extend(packet)
                            # Controlled test of the SD observer only. Withhold
                            # its first ExCom pixel request, retaining the real
                            # native reply for late mode. This is not a model
                            # or diagnosis of physical P4 scheduling.
                            fault=config.get('probe_response','normal')
                            if packet[:3]==b'\x17\0\x84': pixel_number+=1
                            if fault!='normal' and packet[:3]==b'\x17\0\x84' and not withheld and pixel_number==config.get('fault_pixel_number',1):
                                withheld=True
                                if fault=='late': delayed.append((now+1.5,packet))
                            else: native.send(packet)
            while delayed and delayed[0][0]<=time.monotonic():
                native.send(delayed.pop(0)[1])
            reply=native.receive()
            if peer and reply: peer.sendall(reply)
            if process.poll() is not None: raise RuntimeError('Emulator exited early')

        def receive():
            nonlocal debug
            # The CLI/parser rows are deliberately much slower than raw output.
            # A complete 48-row run reached row 47 at the old 240-second bound.
            end=time.monotonic()+600
            while '>> ' not in debug:
                if time.monotonic()>end: raise TimeoutError('Fixture did not finish: '+debug[-1200:])
                pump()
            result,debug=debug.split('>> ',1)
            return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]','',result)

        def command(text):
            os.write(master,(text+'\n').encode())
            return receive()

        try:
            # EMBOOT uses the same application RAM before UPBENCH is loaded.
            # Reject address-only breakpoint attribution to that earlier app.
            for attempt in range(32):
                receive()
                state=command('state')
                if f'{config["done"]:06x}:' not in state:
                    raise RuntimeError('Wrong debugger stop: '+state)
                dump=command(f'mem {hex(config["done"])} 20')
                octets=[]
                for match in re.finditer(r'^[0-9a-f]{6}: ((?:[0-9a-f]{2} ?)+) \|',dump,re.M):
                    octets.extend(int(x,16) for x in match[1].split())
                if bytes(octets).hex()==config['done_bytes']: break
                os.write(master,b'continue\n')
            else: raise RuntimeError('Benchmark never replaced the earlier smoke application')
            status_dump=command(f'mem {hex(config["status"])} 3')
            record['status_dump']=status_dump
            fault=config.get('probe_response','normal')
            expected_status=15 if fault=='absent' or (config.get('probe') and fault=='late') else 0
            if not re.search(fr': {expected_status:02x} 00 00\s',status_dump):
                raise RuntimeError('Benchmark returned failure: '+status_dump)
            # Extract only after the application's real FatFS sync and close.
            results=args.output.parent/'results'
            results.mkdir()
            for name in ('00000001.CSV','00000002.CSV'):
                subprocess.run([config['mcopy'],'-i',str(image),
                    '::/extender/uartbench/results/'+name,str(results/name)],check=True)
            result=results/'00000002.CSV'
            if config.get('filesystem_probe'):
                fs_result=results/'filesystem-result.txt'
                subprocess.run([config['mcopy'],'-i',str(image),
                    '::/extender/fscheck/R00001/RESULT.TXT',str(fs_result)],check=True)
                if 'Filesystem probe PASS' not in fs_result.read_text():
                    raise RuntimeError('Preceding filesystem probe failed')
                record['filesystem_probe']='pass'
            if config.get('probe'):
                text=result.read_text()
                queries=[dict(item.split('=',1) for item in s.split(';')[1:])
                         for s in text.splitlines() if s.startswith('# query;')]
                fault=config.get('probe_response','normal')
                expected_phases=['route-mode-query','initial-pixel-query','cleared-pixel-value','white-pixel-query']
                expected=[(route,phase) for route in ('legacy','excom') for phase in expected_phases]
                if fault!='normal': expected=expected[:6]
                if [(q['route'],q['phase']) for q in queries]!=expected:
                    raise RuntimeError('Missing or unexpected probe phases: '+text)
                for i,q in enumerate(queries):
                    failed=fault!='normal' and i==len(queries)-1
                    first='15' if failed else '0'
                    final='15' if failed and fault=='absent' else '0'
                    if (q['send_status'],q['first_status'],q['final_status'],q['status'])!=('0',first,final,first):
                        raise RuntimeError('Incorrect early/late observation: '+str(q))
                    if not failed and q['phase'] in ('cleared-pixel-value','white-pixel-query'):
                        rgb='0/0/0' if q['phase']=='cleared-pixel-value' else '255/255/255'
                        if q['rgb']!=rgb: raise RuntimeError('Wrong diagnostic pixel')
                footer=f'# {"failed" if expected_status else "complete"};rows=0;status={expected_status};legacy_return=0'
                if text.splitlines()[-1]!=footer: raise RuntimeError('Wrong probe footer')
                record['queries']=queries
                rows=[]
            elif fault=='absent':
                text=result.read_text()
                queries=[dict(item.split('=',1) for item in s.split(';')[1:])
                         for s in text.splitlines() if s.startswith('# query;')]
                if not queries or queries[-1]['first_status']!='15' or queries[-1]['final_status']!='15':
                    raise RuntimeError('Missing unreplied-query failure')
                if not text.rstrip().endswith('status=15;legacy_return=0'):
                    raise RuntimeError('Missing bounded failure and recovery')
                # Run this case using --trace so failure is before any workload.
                if '# mode=trace;' not in text or ';rows=0;' not in text:
                    raise RuntimeError('Absent-response review must be a trace preflight')
                record['queries']=queries
                rows=[]
            else:
                rows=read_results(result)
                if fault=='late' and not any(r.get('setup_first_status')=='15' or r.get('first_reply_status')=='15' for r in rows):
                    raise RuntimeError('Late response was not durably recorded')
                if fault=='late' and config.get('fault_pixel_number')==3 and '# mode=trace;' in result.read_text():
                    if rows[0]['first_reply_status']!='15' or int(rows[0]['reply_wait_ticks'])<120:
                        raise RuntimeError('Delayed completion is missing from measured tail')
            marker=bytes([23,0,132,64,0,24,0])
            trace_marker=bytes([23,0,132,200,0,144,1])
            windows=[part.removeprefix(trace_marker) for part in bytes(uart).split(marker)]
            windows=[part for part in windows if len(part)==32768]
            excom_rows=[r for r in rows if r['route']=='excom']
            if len(windows)!=len(excom_rows):
                raise RuntimeError('Missing complete UART payload windows')
            for window,row in zip(windows,excom_rows):
                chunk=(b''.join(bytes([25,69,x,0,24,0,0,0]) for x in range(8,65,8))
                       if row['payload']=='points' else bytes(64))
                if window!=chunk*512: raise RuntimeError('UART payload differs from declared case')
            record['exact_uart_payloads']=len(windows)
            # Initial result is deliberately present to exercise no-overwrite.
            if (result.parent/'00000001.CSV').read_text()!='Prior result must survive.\n':
                raise RuntimeError('Prior result was overwritten')
            record['rows']=len(rows)
            record['cases']=[(r['route'],r['entry'],r['payload']) for r in rows]
            # Continue beyond the completed fixture's final hook to the MOS CLI.
            os.write(master,b'continue\n')
            end=time.monotonic()+1
            while time.monotonic()<end: pump()
            record['outcome']='pass'
            result_label=(f'{len(record["queries"])} query observations ({config["probe_response"]})'
                          if config.get('probe') else f'{len(rows)} saved rows')
            print(f'Functional emulator PASS: {result_label}; prior file preserved; Legacy return.',flush=True)
        finally:
            record['output_bytes']=len(uart)
            record['native_cts_waits']=native.cts_waits
            if process.poll() is None: process.terminate()
            process.wait(timeout=5)
            os.close(master); server.close()
            if peer: peer.close()
            args.output.write_text(json.dumps(record,indent=2)+'\n')
            args.output.with_suffix('.log').write_bytes(transcript)
            args.output.with_suffix('.uart').write_bytes(uart)
            native.lib.vdp_shutdown()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('emulator','firmware','sdcard','output','vdp'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--graphical',action='store_true')
    try:
        run(parser.parse_args())
    except BaseException:
        traceback.print_exc(); os._exit(1)
    os._exit(0)
