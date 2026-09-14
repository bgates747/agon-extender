"""Fail-closed payload preparation and independent recovery dump verification."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zlib
import hashlib

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'scripts'/f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RecoveryTests(unittest.TestCase):
    def test_payload_rejects_wrong_hash_and_size(self):
        checked = load('prepare_mos_recovery').checked
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'mos.bin'; p.write_bytes(b'example')
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(checked(p,digest,1,131072),b'example')
            with self.assertRaises(ValueError): checked(p,'0'*64,1,131072)
            with self.assertRaises(ValueError): checked(p,digest,90,90)
            p.write_bytes(b'x'*131073)
            with self.assertRaises(ValueError): checked(p,hashlib.sha256(p.read_bytes()).hexdigest(),1,131072)

    def test_dump_integrity_and_order(self):
        decode = load('mos_recovery_console').decode_dump
        data = bytes(range(256))*512
        lines = [f'DATA before {i:06X} {data[i:i+256].hex()}' for i in range(0,len(data),256)]
        lines += [f'DUMP END before {zlib.crc32(data):08X}']
        self.assertEqual(decode(lines,'before'), data)
        for damaged in (lines[1:], lines[:10]+lines[11:], lines[:10]+lines[9:],
                        lines[:-1]+['DUMP END before 00000000']):
            with self.assertRaises(ValueError): decode(damaged,'before')

    def test_inherited_zdi_and_target_initialization_unchanged(self):
        old=(ROOT/'vdp/video/extender/diagnostic/p4_zdi_mos_recovery.cpp').read_text()
        new=(ROOT/'vdp/video/extender/recovery/mos_recovery.cpp').read_text()
        for start,end in [('class Zdi {','\nZdi zdi;'),('void initializeEz80() {','\nvoid upload(')]:
            self.assertEqual(old[old.index(start):old.index(end)],new[new.index(start):new.index(end)])


if __name__ == '__main__':
    unittest.main()
