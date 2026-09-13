"""Cross-check the production C codec against Python's independent CRC codec."""
import ctypes
from pathlib import Path
import random
import struct
import subprocess
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]


class SdWire(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        work = Path(cls.tmp.name)
        (work / 'codec.c').write_text('''#include "extender/storage/sd_wire.h"
unsigned crc(const unsigned char *p, unsigned n) { return sd_crc(p,n); }
int valid(const unsigned char *p, unsigned n) { return sd_valid(p,n); }
void seal(unsigned char *p) { sd_seal(p); }
''')
        subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-shared',
                        '-fPIC', '-I'+str(ROOT/'vdp/video'), str(work/'codec.c'),
                        '-o', str(work/'codec.so')], check=True)
        cls.lib = ctypes.CDLL(str(work/'codec.so'))
        cls.lib.crc.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def record(self, payload):
        h = b'SD\x01\x01'+struct.pack('<IIBBH', 0x91827364, 9, 6, 0, len(payload))
        return h+struct.pack('<I', zlib.crc32(h+payload))+payload

    def test_crc_known_vector(self):
        self.assertEqual(self.lib.crc(b'123456789', 9), 0xCBF43926)

    def test_every_payload_size_and_binary_start(self):
        rng = random.Random(17)
        for n in range(221):
            data = bytes(rng.randrange(256) for _ in range(n))
            frame = self.record(data)
            self.assertEqual(self.lib.valid(frame, len(frame)), 1)
            buf = ctypes.create_string_buffer(frame)
            buf[16:20] = b'\0'*4
            self.lib.seal(buf)
            self.assertEqual(buf.raw[:len(frame)], frame)
        for first in range(256):
            frame = self.record(bytes([first])+bytes(range(200)))
            self.assertEqual(self.lib.valid(frame, len(frame)), 1)

    def test_every_single_bit_corruption(self):
        frame = self.record(bytes(range(220)))
        for index in range(len(frame)):
            for bit in range(8):
                bad = bytearray(frame); bad[index] ^= 1 << bit
                self.assertEqual(self.lib.valid(bytes(bad), len(bad)), 0)

    def test_framing_bounds(self):
        frame = self.record(bytes(range(220)))
        for n in range(len(frame)):
            self.assertEqual(self.lib.valid(frame[:n], n), 0)
        self.assertEqual(self.lib.valid(frame+b'\0', 241), 0)
        for index, value in [(0, 0), (2, 2), (3, 0), (3, 4)]:
            bad = bytearray(frame);bad[index] = value
            bad[16:20] = struct.pack('<I', zlib.crc32(bad[:16]+bad[20:]))
            self.assertEqual(self.lib.valid(bytes(bad), len(bad)), 0)
        bad = bytearray(frame);bad[4:8] = b'\0'*4
        bad[16:20] = struct.pack('<I', zlib.crc32(bad[:16]+bad[20:]))
        self.assertEqual(self.lib.valid(bytes(bad), len(bad)), 0)


if __name__ == '__main__':
    unittest.main()
