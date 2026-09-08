#!/usr/bin/env python3
"""Review SD sample output and the real EMOS gateway without physical UART peers."""
import argparse
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import time
import yaml
from prepare_visible_text import sha


def checked_output(bundle, record, role):
    item = next(o for o in record['outputs'] if o['role'] == role)
    path = bundle / item['filename']
    if sha(path) != item['sha256']:
        raise ValueError('Bundle hash mismatch: ' + str(path))
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emos-bundle', required=True, type=Path)
    parser.add_argument('--sample-bundle', required=True, type=Path)
    parser.add_argument('--fab-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--emos-root', type=Path, default=Path(__file__).resolve().parents[2] / 'agon-emos')
    args = parser.parse_args()
    sys.path.insert(0, str(args.emos_root / 'scripts'))
    from review_boot import make_profile
    output = args.output.absolute()
    output.mkdir(parents=True)
    emos = args.emos_bundle.resolve(strict=True)
    sample = args.sample_bundle.resolve(strict=True)
    firmware_record = yaml.safe_load((emos / 'build-manifest.yaml').read_text())
    sample_record = yaml.safe_load((sample / 'build-manifest.yaml').read_text())
    firmware = output / 'MOS.bin'
    mos_map = output / 'MOS.map'
    shutil.copyfile(checked_output(emos, firmware_record, 'firmware'), firmware)
    shutil.copyfile(checked_output(emos, firmware_record, 'firmware_map'), mos_map)
    media = output / 'sdcard'
    (media / 'bin').mkdir(parents=True)
    (media / 'emos-boot').mkdir()
    shutil.copyfile(checked_output(emos, firmware_record, 'smoke_program'), media / 'bin/EMBOOT.BIN')
    shutil.copyfile(checked_output(sample, sample_record, 'bin'), media / 'bin/VTEXT.BIN')
    (media / 'emos-boot/check.txt').write_bytes(b'EMOS SD CHECK\r\n')
    commands = ['VDU 22 3', 'LOAD /bin/VTEXT.BIN', 'RUN . check', 'RUN . preview',
                'LOAD /bin/EMBOOT.BIN', 'RUN', 'LOAD /bin/VTEXT.BIN', 'RUN']
    (media / 'autoexec.txt').write_bytes(('\r\n'.join(commands) + '\r\n').encode())
    fab = args.fab_root.resolve(strict=True)
    process = subprocess.Popen([str(fab / 'target/release/agon-cli-emulator'),
                                '--mos', str(firmware), '--sdcard', str(media), '--zero'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    data = bytearray()
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if select.select([process.stdout], [], [], 0.2)[0]:
                block = os.read(process.stdout.fileno(), 65536)
                if not block: break
                data.extend(block)
            if b'VDP TEXT SAMPLE FAIL:' in data and data.rstrip().endswith(b'/ *'):
                break
    finally:
        process.terminate()
        process.communicate(timeout=5)
    (output / 'review.log').write_bytes(data)
    required = [b'TEXT GATEWAY CHECK PASS', b'EMOS TO EDP: UART TEXT',
                b'TEXT SAMPLE PREVIEW: onboard VDU only', b'BOOT SMOKE SD PASS',
                b'BOOT SMOKE CLOCK PASS', b'BOOT SMOKE PASS - returning to MOS',
                b'VDP TEXT SAMPLE FAIL: EMOS status 15']
    normalized = bytes(data).replace(b'\r', b'')
    if any(marker not in data for marker in required) or b'1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n' not in normalized:
        raise SystemExit('FAIL: sample/gateway/smoke review; see review.log')
    failures = (b'VDP TEXT FAIL: transmit timeout', b'VDP TEXT FAIL: no reply from EDP')
    if sum(reason in data for reason in failures) != 1 or not data.rstrip().endswith(b'/ *'):
        raise SystemExit('FAIL: expected bounded UART no-peer failure and MOS prompt')
    if b'VDP TEXT SAMPLE PASS:' in data or b'TEXT GATEWAY CHECK FAIL' in data:
        raise SystemExit('FAIL: unexpected gateway outcome')
    make_profile(output / 'profile', firmware, mos_map, media, fab)
    print('PASS: SD sample count, real gateway rejection/no-peer return, and SD/CLOCK smoke')
    print('Graphical profile: ' + str(output / 'profile'))


if __name__ == '__main__':
    main()
