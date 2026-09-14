#!/usr/bin/env python3
"""Capture P4 ZDI recovery; only --restore permits the hash-bound write command.

Run on the USB host with pyserial. Does not flash or reset either board itself;
opening the board's USB console can reset it. Use only with a prepared programmer.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import zlib


def decode_dump(lines, label):
    data = bytearray()
    expected_crc = None
    for line in lines:
        parts = line.split()
        if parts[:2] == ['DATA', label]:
            if len(parts) != 4 or int(parts[2], 16) != len(data):
                raise ValueError('Missing, duplicate or out-of-order dump record')
            chunk = bytes.fromhex(parts[3])
            if len(chunk) != 256:
                raise ValueError('Wrong dump chunk size')
            data.extend(chunk)
        elif parts[:3] == ['DUMP', 'END', label]:
            expected_crc = int(parts[3], 16)
    if len(data) != 131072 or zlib.crc32(data) != expected_crc:
        raise ValueError('Incomplete dump or CRC mismatch')
    return bytes(data)


def main():
    import serial
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', type=Path, required=True)
    p.add_argument('--serial-id', required=True)
    p.add_argument('--mos', type=Path, required=True)
    p.add_argument('--mos-sha256', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    mos = a.mos.read_bytes()
    assert 1 <= len(mos) <= 131072
    assert hashlib.sha256(mos).hexdigest() == a.mos_sha256, 'Wrong MOS payload'
    expected_flash = mos.ljust(131072, b'\xff')
    props = subprocess.check_output(['udevadm','info','--query=property',
                                     '--name',str(a.port.resolve(strict=True))],text=True)
    props = dict(line.split('=',1) for line in props.splitlines() if '=' in line)
    normalize = lambda x: x.replace(':','').replace('-','').lower()
    assert normalize(props.get('ID_SERIAL_SHORT','')) == normalize(a.serial_id), 'Wrong USB device'
    a.out.mkdir(exist_ok=False, parents=True)
    result = {'restore_authorized': a.restore, 'selected_sha256': a.mos_sha256,
              'port': str(a.port), 'flash_verified': False}
    lines = []
    armed_dump = armed_restore = False
    identities = 0
    handle = serial.Serial(port=None, baudrate=115200, timeout=1, write_timeout=3)
    handle.dtr = False
    handle.rts = False
    handle.port = str(a.port)
    try:
        handle.open()
        deadline = time.monotonic() + 900
        with (a.out/'console.log').open('wb', buffering=0) as log:
            while time.monotonic() < deadline:
                raw = handle.readline()
                if not raw:
                    continue
                log.write(raw)
                line = raw.decode('ascii', errors='replace').strip()
                lines.append(line)
                if not line.startswith('DATA '):
                    print(line, flush=True)
                if any(x in line for x in ('RECOVERY REFUSED','RECOVERY STOP/FAIL','Guru Meditation','abort()','task_wdt:')):
                    raise RuntimeError('Programmer refused or faulted; no retry')
                if line.startswith('Identity '):
                    assert 'product=0007 revision=AA' in line, 'ZDI identity mismatch'
                    identities += 1
                if line == 'WAIT DUMP' and not armed_dump:
                    assert identities == 3, 'Complete identity gate was not observed'
                    handle.write(b'DUMP\n'); handle.flush()
                    armed_dump = True
                if line.startswith('DUMP END before '):
                    before = decode_dump(lines, 'before')
                    (a.out/'before-rom.bin').write_bytes(before)
                    result['before_sha256'] = hashlib.sha256(before).hexdigest()
                    result['different_bytes'] = sum(x!=y for x,y in zip(before,expected_flash))
                    print('Existing ROM differs in',result['different_bytes'],'bytes',flush=True)
                    if before == expected_flash or not a.restore:
                        result['disposition'] = 'already matches; no erase' if before == expected_flash else 'dump only'
                        break
                if line == 'WAIT RESTORE ' + a.mos_sha256 and not armed_restore:
                    assert a.restore and 'before_sha256' in result and result['different_bytes'] > 0
                    # Preserve the verified pre-erase dump durably before arming.
                    with (a.out/'before-rom.bin').open('rb') as f:
                        os.fsync(f.fileno())
                    handle.write(('RESTORE '+a.mos_sha256+'\n').encode()); handle.flush()
                    armed_restore = True
                    result['restore_command_sent'] = True
                if line == 'RECOVERY PASS':
                    after = decode_dump(lines, 'after')
                    (a.out/'after-rom.bin').write_bytes(after)
                    assert after == expected_flash, 'Host full-ROM byte comparison failed'
                    result['after_sha256'] = hashlib.sha256(after).hexdigest()
                    result['flash_verified'] = True
                    result['disposition'] = 'restored and verified; target halted'
                    break
            else:
                raise TimeoutError('Recovery console deadline; no retry')
    except BaseException as exc:
        result['error'] = str(exc)
        raise
    finally:
        if handle.is_open:
            handle.close()
        (a.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__ == '__main__':
    main()
