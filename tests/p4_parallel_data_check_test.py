"""Private retained-data endpoint: independent source and exact byte attribution.

No electrical, DMA timing or performance claim. Actual owner lifecycle is used;
only the physical completion signals are modeled by the C++ fixture.
"""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DataCheckTests(unittest.TestCase):
    def test_independent_directions(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / 'endpoint'
            subprocess.run([
                'c++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pedantic',
                '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                f'-I{ROOT / "vdp/video"}',
                str(ROOT / 'tests/p4_parallel_data_check_test.cpp'),
                str(ROOT / 'vdp/video/extender/transport/p4_parallel_handover.cpp'),
                '-o', str(exe),
            ], check=True)
            subprocess.run([str(exe)], check=True, timeout=20,
                           env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0'))

if __name__ == '__main__':
    unittest.main()
