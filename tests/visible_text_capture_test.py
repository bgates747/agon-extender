from pathlib import Path
import runpy
import unittest
M=runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/capture_visible_text.py'))
BUILD='uart-visible-text-probe-r01-b2026-09-08-12-00-00Z'
def transcript():
    return ''.join(s+' build='+BUILD+'\n' for s in ['VISIBLE TEXT START','VISIBLE TEXT REQUEST hex=0C1F0202454D4F5320544F204544503A205541525420544558540D0A1700CA170080A6','VISIBLE TEXT PARSER reply=8001A6','VISIBLE TEXT SENT count=3','VISIBLE TEXT PASS received=35 reply=3']).encode()
class CaptureTests(unittest.TestCase):
    def test_exact_and_negative_stages(self):
        data=transcript();self.assertTrue(M['verdict'](data,BUILD)[0])
        for line in data.splitlines(keepends=True):
            self.assertFalse(M['verdict'](data.replace(line,b''),BUILD)[0])
        for bad in [data.replace(b'8001A6',b'8001A4'),data+ b'VISIBLE TEXT FAIL late byte\n',data.replace(BUILD.encode(),b'wrong'),data+data.splitlines(keepends=True)[0]]:
            self.assertFalse(M['verdict'](bad,BUILD)[0])
        self.assertFalse(M['verdict'](data+b'VISIBLE TEXT RECEIVER restarted\n',BUILD)[0])
    def test_completion_waits_for_both_conditions(self):
        f=M['capture_complete']
        self.assertFalse(f(None,90,True));self.assertFalse(f(10,14.99,True))
        self.assertFalse(f(10,90,False));self.assertTrue(f(10,15,True))
    def test_readiness_requires_selected_empty_stopped_peer(self):
        self.assertTrue(M['receiver_ready'](('VISIBLE TEXT WAIT received=0 cts=1 build='+BUILD+'\n').encode(),BUILD))
        for bad in [b'VISIBLE TEXT WAIT received=1 cts=1 build='+BUILD.encode()+b'\n',b'VISIBLE TEXT START build='+BUILD.encode()+b'\n']:
            with self.assertRaises(RuntimeError):M['receiver_ready'](bad,BUILD)
