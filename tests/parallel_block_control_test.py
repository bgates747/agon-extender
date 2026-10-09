"""Run maintained EMOS UART/ISR and P4 block owner with modeled adapter proof."""
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
import os
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
EMOS = Path(os.environ.get('AGON_EMOS_ROOT', ROOT.parent / 'agon-emos'))
class BlockControlTests(unittest.TestCase):
    def test_owners(self):
        start=datetime.now(timezone.utc).isoformat(); clock=monotonic()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                d=Path(tmp); objects=[]
                flags=['-Wall','-Wextra','-Werror','-Wno-endif-labels',
                       '-ffunction-sections','-fdata-sections',
                       '-fsanitize=address,undefined','-fno-sanitize-recover=all']
                inc=[f'-I{EMOS/"tests/host"}',f'-I{EMOS/"src"}',f'-I{ROOT/"vdp/video"}']
                for name in ('emos_console','emos_parallel_handover'):
                    obj=d/(name+'.o'); objects.append(str(obj))
                    subprocess.run(['cc','-std=c17',*flags,*inc,'-c',
                                    str(EMOS/'src'/(name+'.c')),'-o',str(obj)],check=True)
                exe=d/'blocks'
                subprocess.run(['c++','-std=c++17',*flags,*inc,*objects,
                    str(ROOT/'tests/parallel_block_control_test.cpp'),
                    str(ROOT/'vdp/video/extender/transport/p4_parallel_handover.cpp'),
                    '-Wl,--gc-sections','-o',str(exe)],check=True)
                subprocess.run([str(exe)],check=True,timeout=30)
        finally:
            print(f'Block control: start={start}, end={datetime.now(timezone.utc).isoformat()}, elapsed={monotonic()-clock:.6f} s')
if __name__=='__main__':unittest.main()
