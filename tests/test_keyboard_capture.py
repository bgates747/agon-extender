"""Require exact ordered sender evidence; acquisition and Agon remain separate."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('capture_keyboard',
    Path(__file__).resolve().parents[1]/'scripts/capture_keyboard.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
BUILD = 'uart-keyboard-probe-r01-b2026-09-09-00-00-00Z'
SUFFIX = ' build='+BUILD


def stages():
    return ['KEYBOARD START cycle=1'+SUFFIX, 'KEYBOARD LOCALE 1'+SUFFIX,
            'KEYBOARD POLL token=1'+SUFFIX,
            *['KEYBOARD EVENT '+str(i)+' SENT'+SUFFIX for i in range(1,13)],
            'KEYBOARD SENDER PASS events=12 key_bytes=72'+SUFFIX]


def data(lines):
    return ('\r\n'.join('\x1b[0;32mI (100) keyboard: '+s+'\x1b[0m' for s in lines)+'\r\n').encode()


class VerdictTests(unittest.TestCase):
    def test_ready_is_idle_and_exact(self):
        wait='KEYBOARD WAIT cts=1'+SUFFIX
        self.assertTrue(module.receiver_ready(data([wait]),BUILD))
        self.assertFalse(module.receiver_ready(b'ordinary boot',BUILD))
        for line in (wait.replace('cts=1','cts=0'), wait.replace(BUILD,'other'),
                     stages()[0], stages()[-1], 'KEYBOARD FAIL reason=test'+SUFFIX):
            with self.subTest(line=line), self.assertRaises(RuntimeError):
                module.receiver_ready(data([line]),BUILD)

    def test_exact_stages_and_quiet_wait(self):
        lines=['KEYBOARD SENDER '+BUILD+' (candidate)', 'KEYBOARD WAIT cts=1'+SUFFIX]
        lines+=stages()+['KEYBOARD WAIT cts=1'+SUFFIX]
        self.assertTrue(module.verdict(data(lines),BUILD)[0])
        for token in (0,255):
            self.assertTrue(module.verdict(data([s.replace('token=1','token='+str(token)) for s in stages()]),BUILD)[0])

    def test_reject_partial_malformed_reordered_and_late(self):
        good=stages()
        cases=[good[:i]+good[i+1:] for i in range(len(good))]
        cases += [good[:4]+good[5:6]+good[4:5]+good[6:],good+[good[-1]],
                  [s.replace('token=1','token=256') for s in good],
                  [s.replace('cycle=1','cycle=2') for s in good],
                  [s.replace('EVENT 5 SENT','EVENT 5 QUEUED') for s in good],
                  [s.replace('LOCALE 1','LOCALE 2') for s in good],
                  [s.replace(BUILD,'other') for s in good]]
        cases += [good+[line] for line in ('KEYBOARD FAIL reason=UART error'+SUFFIX,
                  'KEYBOARD SENDER '+BUILD+' (candidate)', 'KEYBOARD START cycle=2'+SUFFIX,
                  'KEYBOARD WAIT cts=1 build=other','KEYBOARD UNKNOWN'+SUFFIX)]
        for i,case in enumerate(cases):
            with self.subTest(case=i): self.assertFalse(module.verdict(data(case),BUILD)[0])

    def test_wait_for_both_acquisition_and_clean_tail(self):
        self.assertFalse(module.capture_complete(None,100,True))
        self.assertFalse(module.capture_complete(1,5.9,True))
        self.assertFalse(module.capture_complete(1,6,False))
        self.assertTrue(module.capture_complete(1,6,True))


if __name__=='__main__': unittest.main()
