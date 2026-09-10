"""Synthetic wire evidence tests: framing, exact coverage and CTS accounting."""
from pathlib import Path
import tempfile
import unittest
import zipfile
import numpy as np
from analyze_trace import (BIT, MARKER, TARGET, PAYLOAD, analyze, boundaries, decode,
                           gap_metrics, independent_decode, overlap)
from capture_trace import metadata


def waveform():
    raw = np.full(9_000_000, 0x42, dtype=np.uint8) # UART idle high, both CTS low.
    def send(data, start, pin):
        for value in data:
            levels=[0]+[(value>>i)&1 for i in range(8)]+[1]
            for i,level in enumerate(levels):
                a,b=round(start+i*BIT),round(start+(i+1)*BIT)
                if level: raw[a:b] |= 1 << pin
                else: raw[a:b] &= 255 ^ (1 << pin)
            start += 220  # explicit inter-byte idle for verifiable partition.
        return start
    marker_end=send(MARKER,1000,1)
    reply_end=send(bytes([132,4,0,0,0,0]),marker_end+1000,6)
    begin=reply_end+1000
    end=send(PAYLOAD,begin,1)
    query_end=send(TARGET,end+1000,1)
    final=send(bytes([132,4,255,255,255,15]),query_end+10000,6)
    raw[begin+200:begin+1800] |= 16 # CTS rises while a byte is already in flight.
    return raw[:final+1000]


class TraceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=waveform()
        cls.result,cls.forward,cls.reverse,cls.begin,cls.end=analyze(cls.raw)

    def test_complete(self):
        self.assertEqual(self.result['forward_payload_bytes'],32768)
        self.assertGreater(self.result['payload']['idle_cts_high_seconds'],0)
        self.assertGreater(self.result['payload']['idle_cts_low_seconds'],0)
        self.assertTrue(self.result['coverage_pass'])

    def test_missing_extra_corrupt(self):
        for kind in ('missing','extra','corrupt','duplicate_marker'):
            with self.subTest(kind=kind):
                frames=[dict(f) for f in self.forward]
                if kind=='missing':del frames[25]
                if kind=='extra':frames.insert(25,dict(frames[25]))
                if kind=='corrupt':frames[25]['byte']^=1
                if kind=='duplicate_marker':frames += frames[:7]
                with self.assertRaises(ValueError):boundaries(frames,self.reverse)

    def test_missing_wrong_reply(self):
        with self.assertRaises(ValueError):boundaries(self.forward,self.reverse[:-1])
        bad=[dict(f) for f in self.reverse];bad[-1]['byte']=0
        with self.assertRaises(ValueError):boundaries(self.forward,bad)

    def test_framing(self):
        raw=self.raw.copy(); start=self.forward[10]['start']
        raw[round(start+9*BIT):round(start+10*BIT)] &= 253
        with self.assertRaises(ValueError):analyze(raw)

    def test_partition(self):
        frames=[dict(start=0,end=10),dict(start=30,end=40),dict(start=60,end=70)]
        result=gap_metrics(frames,[(0,15),(25,50)])
        self.assertAlmostEqual(result['idle_cts_high_fraction'],.5)
        self.assertEqual(overlap([(10,30),(40,60)],[(0,15),(25,50)]),20)
        self.assertEqual(overlap([(0,10)],[(10,20)]),0)

    def test_reverse_permission_before_reply(self):
        raw=self.raw.copy()
        # Receiver blocks the response before its first start bit. This delay
        # must not be assigned to the P4 renderer merely because no byte arrives.
        _,_,_,query,reply=boundaries(self.forward,self.reverse)
        a=int(query[-1]['end'])+100; b=reply[0]['start']-100
        raw[a:b] |= 8
        result,*_=analyze(raw)
        self.assertAlmostEqual(result['final_query_to_first_reply_agon_rts_high_seconds'],
                               (b-a)/24_000_000)

    def test_chunk_mapping_and_independent_decoder(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);path=out/'logic.sr'
            with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr('version','2')
                z.writestr('metadata','[global]\nsigrok version=0.5.2\n[device 1]\ncapturefile=logic-1\n'
                            'total probes=8\nunitsize=1\nsamplerate=24 MHz\n'
                            'probe2=D1\nprobe4=D3\nprobe5=D4\nprobe7=D6\n')
                z.writestr('logic-1-1',self.raw.tobytes())
            with zipfile.ZipFile(path) as z:self.assertEqual(metadata(z)[1],len(self.raw))
            for pin,frames in ((1,self.forward),(6,self.reverse)):
                independent_decode(path,out,pin,frames,self.begin,self.end)


if __name__=='__main__':unittest.main()
