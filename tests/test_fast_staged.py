"""Real P4 engine/queue + actual EMOS SD utility, entirely offline."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EMOS = Path(os.environ.get('AGON_EMOS_ROOT', ROOT.parent/'agon-emos'))


class FastEngineTests(unittest.TestCase):
    def test_paired_engine_and_error_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            objects = []
            for name, source in [('service', EMOS/'projects/sdserve/src/service.c'),
                                 ('filesystem', EMOS/'tests/sdserve_host/fs.c')]:
                obj = work/(name+'.o')
                subprocess.run(['cc', '-std=c17', '-Wall', '-Wextra', '-Werror',
                                '-Wno-misleading-indentation', '-g', '-fsanitize=address,undefined',
                                '-I'+str(EMOS/'tests/sdserve_host'), '-c', str(source), '-o', str(obj)], check=True)
                objects.append(str(obj))
            executable = work/'engine'
            subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                            '-Wno-misleading-indentation', '-g', '-fsanitize=address,undefined',
                            '-I'+str(ROOT/'vdp/video'), str(ROOT/'tests/storage/fast_engine_test.cpp'),
                            *objects, '-o', str(executable)], check=True)
            subprocess.run([str(executable), str(work/'disk')], check=True, timeout=30)
            http = work/'http'
            subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                            '-Wno-misleading-indentation', '-g', '-fsanitize=address,undefined',
                            '-I'+str(ROOT/'tests/storage/fast_fakes'), '-I'+str(ROOT/'vdp/video'),
                            str(ROOT/'tests/storage/fast_http_test.cpp'), *objects, '-o', str(http)], check=True)
            subprocess.run([str(http), str(work/'http-disk')], check=True, timeout=30)


if __name__ == '__main__':
    unittest.main()
