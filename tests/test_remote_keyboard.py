from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RemoteKeyboardTests(unittest.TestCase):
    def test_session_events_and_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / 'remote-keyboard'
            subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                            '-fsanitize=address,undefined', '-I' + str(ROOT / 'vdp/video'),
                            str(ROOT / 'tests/remote_keyboard_test.cpp'), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True, timeout=10)


if __name__ == '__main__':
    unittest.main()
