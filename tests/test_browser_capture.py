"""Bounded browser/agent/physical arbitration under sanitizers."""
from pathlib import Path
import subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
class BrowserCaptureTests(unittest.TestCase):
    def test_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe=Path(tmp)/'capture'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                '-fsanitize=address,undefined','-I'+str(ROOT/'vdp/video'),
                str(ROOT/'tests/browser_capture_test.cpp'),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True,timeout=10)
if __name__=='__main__': unittest.main()
