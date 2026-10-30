from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from p4_boot_guard import check_startup

class StartupFailure(unittest.TestCase):
 def test_normal_boot_and_historical_coredump_notice(self):
  check_startup(b'ESP-ROM\nCore dump data checksum is correct\nconsole-build\nUSB KEYBOARD READY',b'console-build')
 def test_first_crash_stops_before_probe(self):
  for fault in (b'***ERROR*** A stack overflow in task httpd',b'Guru Meditation',b'assert failed: xyz',b'Backtrace:',b'Rebooting...'):
   probes=[]
   with self.assertRaises(RuntimeError):
    check_startup(b'console-build\n'+fault,b'console-build')
    probes.append('HTTP readiness')
   self.assertEqual(probes,[])
 def test_restart_without_panic_text_refused(self):
  with self.assertRaises(RuntimeError):check_startup(b'console-build\nconsole-build',b'console-build')
 def test_partial_error_is_rejected_once_completed(self):
  raw=b'console-build\n***ERR';check_startup(raw,b'console-build')
  with self.assertRaises(RuntimeError):check_startup(raw+b'OR*** stack overflow',b'console-build')
if __name__=='__main__':unittest.main()
