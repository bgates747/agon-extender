"""Transport chunking and opaque payload regression over the full graphics corpus."""
import json
from pathlib import Path
import random
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from vdu_framer import Framer


class FramingTests(unittest.TestCase):
    def split(self, raw):
        f=Framer(); out=[]; rng=random.Random(37)
        while raw:
            n=rng.randrange(1,57); out+=f.feed(raw[:n]); raw=raw[n:]
        self.assertFalse(f.pending)
        return out

    def test_entire_generated_corpus(self):
        build=ROOT/'suite/build'
        streams=[p.read_bytes() for p in build.glob('shp*.vdu')]
        catalog=json.loads((build/'bitmaps-catalog.json').read_text())
        streams += [bytes.fromhex(a['hex']) for p in catalog['pages'] for s in p['stages']
                    for a in s['actions'] if a['op']=='vdu']
        streams.append((build/'bitmaps-cleanup.vdu').read_bytes())
        self.assertGreater(len(streams),150)
        for raw in streams:
            self.assertEqual(b''.join(self.split(raw)), raw)

    def test_control_bytes_inside_raw_payload_are_opaque(self):
        control=b'\x17\0\xf7'+bytes(range(16))
        payload=bytes(range(256))+control*3
        upload=b'\x17\0\xa0\x60\xea\0'+len(payload).to_bytes(2,'little')+payload
        bitmap=b'\x17\x1b\x01\x13\0\x01\0'+(control*4)
        expected=[upload,bitmap,control]
        self.assertEqual(self.split(b''.join(expected)),expected)

    def test_every_split_of_control_and_queries(self):
        raw=b'\x17\0\xf7'+bytes(range(16))+b'\x17\0\x84\x17\0\xf7\0'
        expected=Framer().feed(raw)
        for i in range(len(raw)+1):
            f=Framer(); self.assertEqual(f.feed(raw[:i])+f.feed(raw[i:]),expected)
            self.assertFalse(f.pending)

    def test_unknown_command_fails_closed(self):
        with self.assertRaises(ValueError):Framer().feed(b'\x17\0\xfe\x17\0\xf7')

if __name__=='__main__':unittest.main()
