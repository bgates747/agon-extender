"""COMMS-001 fixture records/journal; no device access or production protocol."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import struct
import zlib

HEADER = struct.Struct('<4s4B6I2BH2BH')
MAX_PAYLOAD = 84
MAX_WIRE = 128
MAX_LOGICAL = 16 * 1024 * 1024


class ProtocolError(ValueError):
    pass


class CrcError(ProtocolError):
    pass


def pattern_byte(pattern, seed, offset):
    if not 0 <= pattern <= 5 or not 0 <= seed <= 0xffffffff or not 0 <= offset <= 0xffffffff:
        raise ProtocolError('Pattern range')
    if pattern == 0:
        return 0
    if pattern == 1:
        return 255
    if pattern == 2:
        return 255 if offset & 1 else 0
    if pattern == 3:
        return 1 << ((offset + seed) & 7)
    if pattern == 4:
        return (offset + seed) & 255
    value = seed ^ offset ^ 0x9e3779b9
    value ^= value >> 16
    value = value * 0x7feb352d & 0xffffffff
    value ^= value >> 15
    value = value * 0x846ca68b & 0xffffffff
    value ^= value >> 16
    return value & 255


@dataclass(frozen=True)
class Frame:
    kind: int
    tx: int
    rx: int
    pattern: int
    run: int
    case: int
    sequence: int
    seed: int
    total: int
    offset: int
    attempt: int = 1
    direction: int = 0
    status: int = 0
    flags: int = 0
    payload: bytes = b''

    def validate(self):
        if any(type(getattr(self, name)) is not int for name in (
                'kind', 'tx', 'rx', 'pattern', 'run', 'case', 'sequence', 'seed',
                'total', 'offset', 'attempt', 'direction', 'status', 'flags')):
            raise ProtocolError('Integer fields required, not booleans/coercions')
        for name in ('run', 'case', 'sequence'):
            if not 1 <= getattr(self, name) <= 0xffffffff:
                raise ProtocolError('Nonzero uint32 identity required')
        if (self.kind not in (1, 2, 3, 4) or self.tx not in (1, 2) or self.rx not in (1, 2)
                or not 0 <= self.pattern <= 5 or not 0 <= self.seed <= 0xffffffff
                or not 0 <= self.total <= MAX_LOGICAL or not 0 <= self.offset <= self.total
                or not 1 <= self.attempt <= 5 or self.direction not in (0, 1)
                or not 0 <= self.status <= 5 or self.flags not in (0, 1)
                or not isinstance(self.payload, bytes) or len(self.payload) > MAX_PAYLOAD):
            raise ProtocolError('Invalid record fields')
        if self.kind in (1, 2):
            good = self.status == 0 and len(self.payload) <= self.total - self.offset
        elif self.kind == 3:
            good = self.status != 0 and len(self.payload) == 8
        else:
            good = self.status == 0 and not self.payload and self.flags == 1
        if not good:
            raise ProtocolError('Invalid kind/status/span')

    def encode(self):
        self.validate()
        body = HEADER.pack(b'CA01', self.kind, self.tx, self.rx, self.pattern,
                           self.run, self.case, self.sequence, self.seed, self.total, self.offset,
                           self.attempt, self.direction, len(self.payload), self.status, self.flags, 0)
        body += self.payload
        return body + struct.pack('<I', zlib.crc32(body))

    @classmethod
    def decode(cls, packet):
        if not 44 <= len(packet) <= MAX_WIRE:
            raise ProtocolError('Record length')
        if zlib.crc32(packet[:-4]) != struct.unpack('<I', packet[-4:])[0]:
            raise CrcError('CRC mismatch; header untrusted')
        f = HEADER.unpack(packet[:HEADER.size])
        if f[0] != b'CA01' or f[-1] or f[-4] != len(packet) - 44:
            raise ProtocolError('Record magic/reserved/length')
        result = cls(*f[1:11], attempt=f[11], direction=f[12], status=f[14], flags=f[15],
                     payload=packet[HEADER.size:-4])
        result.validate()
        return result

    def pattern_matches(self):
        return self.kind in (1, 2) and all(
            value == pattern_byte(self.pattern, self.seed, self.offset + i)
            for i, value in enumerate(self.payload))


def case_frames(plan, chunk=MAX_PAYLOAD):
    """Generate one fixed attempt from a trusted plan, not received metadata."""
    if not 1 <= chunk <= MAX_PAYLOAD:
        raise ProtocolError('Chunk size')
    total = plan['total']
    if type(total) is not int or not 0 <= total <= MAX_LOGICAL:
        raise ProtocolError('Logical size')
    for sequence, offset in enumerate(range(0, max(1, total), chunk), 1):
        n = min(chunk, total - offset)
        f = Frame(kind=1, tx=plan['tx'], rx=plan['rx'], pattern=plan['pattern'],
                  run=plan['run'], case=plan['case'], sequence=sequence, seed=plan['seed'],
                  total=total, offset=offset, attempt=plan.get('attempt', 1),
                  payload=bytes(pattern_byte(plan['pattern'], plan['seed'], offset + i) for i in range(n)))
        f.validate()
        yield f


class Journal:
    """Exclusive append-only host witness. No resume or truncated-tail repair.

    A checked complete write plus fsync is a host durability checkpoint, not a
    promise that Agon's eventual FAT implementation has the same power-loss scope.
    """
    def __init__(self, path):
        self.file = Path(path).open('xb', buffering=0)
        self.failed = False

    def append(self, event):
        if self.failed:
            raise OSError('Journal previously failed; dispatch must stop')
        try:
            raw = (json.dumps(event, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
            if len(raw) > 4096:
                raise ValueError('Journal record too large')
            if self.file.write(raw) != len(raw):
                raise OSError('Short journal write; retain partial tail')
            os.fsync(self.file.fileno())
        except BaseException:
            self.failed = True
            raise

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def inspect_journal(path):
    """Read bounded lines, retaining an interrupted last line as incomplete."""
    records, partial = [], False
    with Path(path).open('rb') as file:
        while True:
            raw = file.readline(4097)
            if not raw:
                break
            if len(raw) > 4096:
                raise ProtocolError('Oversized journal line')
            if not raw.endswith(b'\n'):
                partial = True
                break
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ProtocolError('Journal object required')
            records.append(value)
    if not records or records[0].get('event') != 'run':
        raise ProtocolError('Run header missing')
    pending = set()
    seen = set()
    for record in records:
        if record.get('event') in ('intent', 'outcome'):
            key = (record['case'], record['attempt'])
            if record['event'] == 'intent':
                if key in seen:
                    raise ProtocolError('Repeated journal intent')
                seen.add(key)
                pending.add(key)
            else:
                if key not in pending:
                    raise ProtocolError('Outcome without outstanding intent')
                pending.remove(key)
    complete = not partial and not pending and records[-1].get('event') == 'stop'
    return dict(records=records, incomplete_tail=partial, pending=sorted(pending), complete=complete)
