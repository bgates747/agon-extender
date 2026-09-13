#!/usr/bin/env python3
"""Bounded keyboard/foreground-restart test for the already commissioned SD service.

The Author presses Escape during WRITE traffic, then types RUN . /extender/sdtest
at MOS. This observer never injects keys, executes commands, resets or flashes.
Only a fresh test target is modified. Human confirmation of the input action is
separate evidence; a changed service incarnation alone cannot prove keystrokes.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import struct
import subprocess
import time
import zlib

from sdcard import Client, path_payload

ROOT = Path(__file__).resolve().parents[1]


def require(value, message):
    if not value:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--window', type=float, default=180, help='Seconds allowed for each human action')
    args = parser.parse_args()
    require(10 <= args.window <= 600, 'Human-action window must be 10..600 seconds')
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    now = datetime.now(timezone.utc)
    target = '/extender/sdtest/p17-key-'+now.strftime('%Y%m%d-%H%M%S')+'.bin'
    name = path_payload(target)
    result = {'started_at': now.isoformat(), 'outcome': 'fail', 'target': target,
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_sha256': {n: hashlib.sha256((Path(__file__).parent/Path(n).name).read_bytes()).hexdigest()
                                for n in ('scripts/qualify_sd_keyboard.py', 'scripts/sdcard.py')},
              'human_keyboard_confirmation': 'pending',
              'limitation': 'A changed incarnation may also follow a reset; require Author confirmation of Escape and typed RUN.'}
    client = None
    def checkpoint(**fields):
        result.update(fields)
        (output/'progress.json').write_text(json.dumps(result, indent=2)+'\n')
    try:
        client = Client(args.url, output/'before-client.json', timeout=10)
        client.connect()
        boot = client.state['boot']
        require(client.rpc(10, b'\0'+name) == b'\0', 'Refusing an existing test target')
        old = b'PORT-017 previous target must survive Escape.\r\n'
        client.upload(target, old, True)
        data = bytes(range(256))*4096
        tid = secrets.randbelow(0xffffffff)+1
        require(client.rpc(5, struct.pack('<III', tid, len(data), zlib.crc32(data))+name) ==
                struct.pack('<II', tid, 0), 'Unexpected BEGIN identity')
        offset = 0
        # Only publish readiness once a real binary chunk has been written.
        acknowledgement = client.rpc(6, struct.pack('<II', tid, offset)+data[:212])
        require(acknowledgement == struct.pack('<II', tid, 212), 'Unexpected first WRITE identity')
        offset = 212
        checkpoint(phase='ready_for_escape', initial_boot=boot, transfer=tid, acknowledged=offset)
        print('Ready: press Escape during traffic, then type RUN . /extender/sdtest at MOS.', flush=True)
        deadline = time.monotonic()+args.window
        while time.monotonic() < deadline:
            try:
                status = client.status()
                if not status['online'] or status['boot'] != boot:
                    checkpoint(interruption_status=status)
                    break
                require(offset < len(data), 'Test completed before the requested interruption')
                chunk = data[offset:offset+212]
                acknowledgement = client.rpc(6, struct.pack('<II', tid, offset)+chunk)
                require(acknowledgement == struct.pack('<II', tid, offset+len(chunk)), 'WRITE identity differs')
                offset += len(chunk)
                checkpoint(acknowledged=offset)
            except Exception as error:
                # The in-flight request may have committed before Escape.
                # Preserve its state; never guess whether it executed.
                checkpoint(interruption_error=repr(error))
                break
        else:
            client.rpc(9, struct.pack('<I', tid))
            checkpoint(phase='timed_out_without_interruption', outcome='partial')
            return
        checkpoint(phase='waiting_for_typed_restart', acknowledged=offset)
        deadline = time.monotonic()+args.window
        while time.monotonic() < deadline:
            try:
                status = client.status()
                if status['online'] and status['boot'] != boot:
                    break
            except OSError:
                pass
            time.sleep(.25)
        else:
            checkpoint(phase='restart_not_observed', outcome='partial')
            return
        client.lock.close()
        client = Client(args.url, output/'after-client.json', timeout=30)
        client.connect()
        checkpoint(phase='verifying_recovery', restarted_boot=client.state['boot'])
        require(client.rpc(10, b'\0'+name) == b'\x07', 'Interrupted stage/journal was not preserved')
        require(client.download(target) == old, 'Escape/restart damaged the previous target')
        partial = client.download(target+'.p17part')
        require(0 < len(partial) < len(data) and partial == data[:len(partial)], 'Interrupted stage is not an exact prefix')
        require(len(partial) >= offset, 'Acknowledged bytes were lost after Escape/close')
        checkpoint(partial_size=len(partial), partial_sha256=hashlib.sha256(partial).hexdigest())
        require(client.rpc(10, b'\x02'+name) == b'\x01', 'Explicit interrupted-stage abandonment failed')
        client.upload(target, b'Network write after keyboard exit/restart\r\n', True)
        require(client.download(target+'.p17bak') == old, 'Recovery activation lost the previous target')
        require(client.rpc(10, b'\x03'+name) == b'\x01', 'Verified backup cleanup failed')
        checkpoint(phase='recovery_pass', outcome='pass')
        print('Restart/recovery PASS. Human keyboard-action confirmation remains separate.', flush=True)
    except Exception as error:
        checkpoint(error=repr(error))
        raise
    finally:
        if client:
            client.lock.close()
        result['ended_at'] = datetime.now(timezone.utc).isoformat()
        (output/'result.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
