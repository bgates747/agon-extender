from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SdServiceTests(unittest.TestCase):
    def test_queue_retry_cache_and_lifecycle(self):
        with tempfile.TemporaryDirectory() as temp:
            exe = Path(temp)/'service'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                            '-fsanitize=address,undefined','-I'+str(ROOT/'vdp/video'),
                            str(ROOT/'tests/sd_service_test.cpp'),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True,timeout=10)


if __name__ == '__main__':
    unittest.main()
