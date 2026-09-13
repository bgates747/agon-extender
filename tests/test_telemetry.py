from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class TelemetryTests(unittest.TestCase):
    def test_latest(self):
        with tempfile.TemporaryDirectory() as directory:
            exe=Path(directory)/'telemetry'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                            '-fsanitize=address,undefined','-I'+str(ROOT/'vdp/video'),
                            str(ROOT/'tests/telemetry_test.cpp'),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True)

if __name__=='__main__': unittest.main()
