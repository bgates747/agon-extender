"""Prepare routed command65 fixtures locally; never deploy or select a mode."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--reference', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
a.out.mkdir(exist_ok=False)
u = lambda n: struct.pack('<H', n)
buf = lambda n, cmd: bytes([23, 0, 160]) + u(n) + bytes([cmd])

def upload(n, data, fragmented=False):
    chunks = [data[:2], data[2:13], data[13:15], data[15:]] if fragmented else [data]
    return buf(n, 2) + b''.join(buf(n, 0) + u(len(c)) + c for c in chunks if c)

raw = bytes((0 if (x//8+y//8)%5 == 0 else 192) | ((x//8)&3) |
            (((y//8)&3)<<2) | ((((x+y)//16)&3)<<4)
            for y in range(64) for x in range(64))
rle = bytearray(b'Cmpr' + struct.pack('<I', len(raw)) + b'RLE2\1\0')
i = 0
while i < len(raw):
    j = i + 1
    while j < len(raw) and j-i < 130 and raw[j] == raw[i]:
        j += 1
    n, v = j-i, raw[i]
    rle.extend([n-3, v] if n >= 3 else [128 | (v&63) | (64 if v&192 == 192 else 0)]*n)
    i = j
(a.out/'rle2.bin').write_bytes(rle)
subprocess.run([str(a.reference.resolve()), '-b41o3', str((a.out/'rle2.bin').resolve()),
                str((a.out/'srle2.bin').resolve())], check=True)
subprocess.run([str(a.reference.resolve()), '-d', str((a.out/'srle2.bin').resolve()),
                str((a.out/'decoded.bin').resolve())], check=True)
assert (a.out/'decoded.bin').read_bytes() == rle
packed = (a.out/'srle2.bin').read_bytes()
bad = bytearray(packed)
bad[13] = 127
unpack = buf(3002, 65)+u(3001)+buf(3000, 65)+u(3002)
cases = {
    'raw': upload(3000, raw),
    'srle': upload(3001, packed)+unpack,
    'fragmented': upload(3001, packed, True)+unpack,
    'inplace': upload(3000, packed)+(buf(3000, 65)+u(3000))*2,
    # Rejecting the outer layer must preserve the pre-existing bitmap bytes.
    'invalid_version': upload(3000, raw)+upload(3001, bad)+buf(3000, 65)+u(3001),
    'truncated': upload(3000, raw)+upload(3001, packed[:-1])+buf(3000, 65)+u(3001),
}
start = bytes([23,0,202,4,26,23,1,0,23,0,192,0,23,27,7,0,23,27,17,17,128,12])
plot = bytes([23,27,32])+u(3000)+bytes([23,27,33])+u(64)+u(64)+bytes([1,23,27,3])+u(80)+u(64)+bytes([23,0,202])
rows = []
for name, commands in cases.items():
    data = start+commands+plot
    (a.out/(name+'.vdu')).write_bytes(data)
    (a.out/(name+'.vdu.bar')).write_bytes(b'Q4B1'+len(data).to_bytes(3, 'little')+b'\0\0')
    rows.append(dict(name=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
(a.out/'expected.rgba2222').write_bytes(raw)
(a.out/'manifest.json').write_text(json.dumps(dict(cases=rows, source='deterministic alpha checker',
    reference_sha256=hashlib.sha256(a.reference.read_bytes()).hexdigest()), indent=2)+'\n')
