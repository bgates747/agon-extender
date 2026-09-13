#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Exercise the pinned, caller-supplied TRS-NET server without serial hardware.

The upstream script is executed unchanged with a simulated pyserial module,
scripted setup input and a temporary synthetic volume. Only read/control
commands are sent. This is a host interoperability probe, not a guest driver.
"""
import argparse
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
from types import ModuleType
from unittest.mock import patch
import zipfile

ARCHIVE_BYTES = 1770983
ARCHIVE_SHA256 = '52d8f5f0683f6a409c01484283722f4be4296fcd075a6033f29f0e1c727b6f48'
SOURCE_SHA256 = 'f45b34e0b9899b06d04ed67c045ccc9d624c8a5a4f60c5ef712ce555a8d1665b'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_source(archive):
    require(archive.stat().st_size == ARCHIVE_BYTES,
            'Archive size differs from the pinned TRS-NET.zip; no code executed.')
    data = archive.read_bytes()
    require(hashlib.sha256(data).hexdigest() == ARCHIVE_SHA256,
            'Archive SHA-256 differs from the pinned version; no code executed.')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        source = z.read('TRS-NET.py')
    require(hashlib.sha256(source).hexdigest() == SOURCE_SHA256,
            'TRS-NET.py SHA-256 mismatch; no code executed.')
    return source


class FixtureComplete(Exception):
    """Stop the upstream infinite service loop once all requests are consumed."""


class Port:
    def __iter__(self):
        return iter(('LAB00', 'synthetic serial peer', 'fixture'))

    def __str__(self):
        # The pinned server takes the first five characters of this string.
        return 'LAB00 - synthetic serial peer'


class SerialPeer:
    def __init__(self, requests):
        self.requests = io.BytesIO(requests)
        self.sent = bytearray()
        self.portstr = 'LAB00'
        self.settings = None

    def open(self, port, **settings):
        require(port == self.portstr, 'Unexpected serial endpoint')
        self.settings = settings
        return self

    @property
    def in_waiting(self):
        remaining = len(self.requests.getbuffer()) - self.requests.tell()
        if not remaining:
            raise FixtureComplete()
        return remaining

    def read(self, size=1):
        value = self.requests.read(size)
        require(len(value) == size, 'Server requested bytes beyond the fixture')
        return value

    def readline(self):
        value = self.requests.readline()
        require(value.endswith(b'\n'), 'Server requested an incomplete command')
        return value

    def write(self, data):
        self.sent.extend(data)
        return len(data)


def probe(source):
    # Deliberately not a bootable TRSDOS volume: only known byte patterns.
    header = b'TRS-80-002 synthetic header'.ljust(256, b'\0')
    sector0 = bytes(range(256))
    sector1 = b'\x5a' * 256
    echo = bytes(reversed(range(256)))
    commands = b'@ping\n@bind\n<00000\n<00001\n\\00001\n@echo\n' + echo
    peer = SerialPeer(commands)
    serial = ModuleType('serial')
    serial.Serial = peer.open
    serial.EIGHTBITS = 8
    serial.STOPBITS_ONE = 1
    serial.tools = ModuleType('serial.tools')
    serial.tools.list_ports = ModuleType('serial.tools.list_ports')
    serial.tools.list_ports.comports = lambda: [Port()]
    modules = {module.__name__: module for module in
               (serial, serial.tools, serial.tools.list_ports)}

    transcript = io.StringIO()
    namespace = {'__name__': '__main__', '__file__': 'TRS-NET.zip/TRS-NET.py'}
    with tempfile.TemporaryDirectory(prefix='trs-net-probe-') as temp:
        volume = Path(temp) / 'synthetic.dsk'
        volume.write_bytes(header + sector0 + sector1)
        answers = iter((temp + os.sep, volume.name, '', '1'))
        try:
            with patch.dict(sys.modules, modules), \
                 patch('builtins.input', side_effect=lambda _: next(answers)), \
                 patch('os.system', return_value=0), redirect_stdout(transcript):
                try:
                    exec(compile(source, namespace['__file__'], 'exec'), namespace)
                except FixtureComplete:
                    pass
        finally:
            if 'vol0' in namespace:
                namespace['vol0'].close()
        require(volume.read_bytes() == header + sector0 + sector1,
                'Read/control probe unexpectedly changed its synthetic volume')

    # Relay the upstream banner, preserving its displayed attribution/notice.
    notice = []
    for line in transcript.getvalue().splitlines():
        if any(text in line for text in ('Copyright', 'rights reserved',
                                        'copy & distribute', 'danielpaulmartin.com')):
            notice.append(line)
            if len(notice) == 4:
                break
    print('\n'.join(notice))
    expected = [('ping', b'@pong\n'), ('bind/header', b'@bound\n' + header)]
    for name, data in (('read sector 0', sector0), ('read sector 1', sector1),
                       ('reread sector 1', sector1)):
        expected.append((name, data + struct.pack('>I', sum(data) % 256)))
    expected.append(('echo', echo))
    received = bytes(peer.sent)
    offset = 0
    results = []
    for name, data in expected:
        require(received[offset:offset + len(data)] == data,
                f'{name}: reply differs from the expected byte sequence')
        offset += len(data)
        results.append({'operation': name, 'reply_bytes': len(data), 'status': 'pass'})
    require(offset == len(received), 'Server emitted unexpected trailing bytes')
    require(namespace['gets'] == 2 and namespace['rd_retry'] == 1
            and namespace['echos'] == 1, 'Unexpected upstream operation counters')
    require(peer.settings == {'baudrate': '115200', 'rtscts': True, 'bytesize': 8,
                              'timeout': 1, 'stopbits': 1},
            'Unexpected upstream serial configuration request')
    return {'status': 'pass', 'source_sha256': SOURCE_SHA256,
            'serial': 'simulated; no timing or electrical qualification',
            'volume_unchanged': True, 'checks': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True,
                        help='Caller-supplied, pinned upstream TRS-NET.zip')
    args = parser.parse_args()
    try:
        result = probe(load_source(args.archive))
    except (OSError, ValueError, zipfile.BadZipFile, KeyError) as error:
        parser.exit(1, f'FAIL: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
