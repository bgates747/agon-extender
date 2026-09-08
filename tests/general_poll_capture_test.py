from pathlib import Path
import runpy
import unittest
M=runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/capture_general_poll.py'))
BUILD='uart-general-poll-probe-r01-b2026-09-08-12-00-00Z'
def transcript():
    return ''.join(s+' build='+BUILD+'\n' for s in ['GENERAL POLL START','GENERAL POLL REQUEST hex=170080A5','GENERAL POLL PARSER reply=8001A5','GENERAL POLL SENT count=3','GENERAL POLL PASS received=4 reply=3']).encode()
class CaptureTests(unittest.TestCase):
    def test_exact_and_negative_stages(self):
        data=transcript();self.assertTrue(M['verdict'](data,BUILD)[0])
        for line in data.splitlines(keepends=True):
            self.assertFalse(M['verdict'](data.replace(line,b''),BUILD)[0])
        for bad in [data.replace(b'8001A5',b'8001A4'),data+ b'GENERAL POLL FAIL late byte\n',data.replace(BUILD.encode(),b'wrong'),data+data.splitlines(keepends=True)[0]]:
            self.assertFalse(M['verdict'](bad,BUILD)[0])
        self.assertFalse(M['verdict'](data+b'GENERAL POLL RECEIVER restarted\n',BUILD)[0])
    def test_completion_waits_for_both_conditions(self):
        f=M['capture_complete']
        self.assertFalse(f(None,90,True));self.assertFalse(f(10,14.99,True))
        self.assertFalse(f(10,90,False));self.assertTrue(f(10,15,True))
    def test_readiness_requires_selected_empty_stopped_peer(self):
        self.assertTrue(M['receiver_ready'](('GENERAL POLL WAIT received=0 cts=1 build='+BUILD+'\n').encode(),BUILD))
        for bad in [b'GENERAL POLL WAIT received=1 cts=1 build='+BUILD.encode()+b'\n',b'GENERAL POLL START build='+BUILD.encode()+b'\n']:
            with self.assertRaises(RuntimeError):M['receiver_ready'](bad,BUILD)
