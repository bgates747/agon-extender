from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class ConsoleSessionTests(unittest.TestCase):
    def test_control_integrity_expiry_replay_and_abort(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'session'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                            '-fsanitize=address,undefined','-fno-sanitize-recover=all',
                            '-I'+str(ROOT/'vdp/video'),str(ROOT/'tests/console_session_test.cpp'),
                            '-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True)

    def test_paired_wire_headers_match(self):
        self.assertEqual((ROOT/'vdp/video/extender/transport/console_wire.h').read_bytes(),
                         (ROOT.parent/'agon-emos/src/emos_console_wire.h').read_bytes())
