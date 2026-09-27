"""Host-only WebDAV checks: no listener socket, board connection or emulator.

Optional AGON_P4_CXX points at the P4 cross compiler for object compilation.
Real-engine tests use the component-owner agon-emos checkout, not vendored code.
"""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'vdp/video/extender/storage/webdav'
EMOS = Path(os.environ.get('AGON_EMOS_ROOT', ROOT.parent / 'agon-emos'))


class WebdavTests(unittest.TestCase):
    def test_protocol_and_actual_spool(self):
        with tempfile.TemporaryDirectory() as directory:
            exe = Path(directory) / 'adapter'
            subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                            '-fsanitize=address,undefined', '-g', '-I'+str(ROOT/'vdp/video'),
                            str(ROOT/'tests/storage/webdav/adapter_test.cpp'),
                            str(SOURCE/'adapter.cpp'), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True, timeout=30)

    def test_wire_to_real_emos_engine(self):
        if not (EMOS/'projects/sdserve/src/service.c').is_file():
            self.skipTest('Real-engine test requires component-owner agon-emos checkout')
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            for source, name in [(EMOS/'projects/sdserve/src/service.c', 'service'),
                                 (EMOS/'tests/sdserve_host/fs.c', 'fs')]:
                subprocess.run(['cc', '-std=c11', '-g', '-fsanitize=address,undefined',
                                '-I'+str(EMOS/'tests/sdserve_host'), '-c', str(source),
                                '-o', str(work/(name+'.o'))], check=True)
            exe = work/'wire'
            subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                            '-fsanitize=address,undefined', '-g', '-I'+str(ROOT/'vdp/video'),
                            str(ROOT/'tests/storage/webdav/wire_test.cpp'),
                            *(str(SOURCE/f) for f in ('adapter.cpp', 'wire_backend.cpp', 'connection.cpp')),
                            str(work/'service.o'), str(work/'fs.o'), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True, timeout=30)

    @unittest.skipUnless(os.environ.get('AGON_P4_CXX'), 'Set AGON_P4_CXX for target object compilation')
    def test_target_objects(self):
        with tempfile.TemporaryDirectory() as directory:
            for source in ('adapter.cpp', 'wire_backend.cpp', 'connection.cpp'):
                subprocess.run([os.environ['AGON_P4_CXX'], '-std=gnu++17', '-Os',
                                '-Wall', '-Wextra', '-Werror', '-fstack-usage',
                                '-I'+str(ROOT/'vdp/video'), '-c', str(SOURCE/source),
                                '-o', str(Path(directory)/(source+'.o'))], check=True)


if __name__ == '__main__':
    unittest.main()
