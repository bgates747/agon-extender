"""Private admission gates: real owner sources, target-independent boundaries."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EMOS = Path(os.environ.get('AGON_EMOS_ROOT', ROOT.parent / 'agon-emos'))

class ParallelAdmissionTests(unittest.TestCase):
    def test_mirrored_headers(self):
        for edp, emos in [('parallel_wire.h','emos_parallel_wire.h'),
                          ('control_crc.h','control_crc.h'),
                          ('console_wire.h','emos_console_wire.h')]:
            self.assertEqual((ROOT/'vdp/video/extender/transport'/edp).read_bytes(),
                             (EMOS/'src'/emos).read_bytes())

    def test_real_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            # Stock ZDS uart.h uses '#endif UART_H'; retain upstream spelling.
            flags=['-Wall','-Wextra','-Werror','-Wno-endif-labels','-ffunction-sections','-fdata-sections',
                   '-fsanitize=address,undefined','-fno-sanitize-recover=all']
            inc=[f'-I{EMOS / "tests/host"}', f'-I{EMOS / "src"}', f'-I{ROOT / "vdp/video"}']
            objects=[]
            for name in ['emos_console','emos_parallel_handover']:
                obj=out/f'{name}.o';objects.append(str(obj))
                subprocess.run(['cc','-std=c17',*flags,*inc,'-c',str(EMOS/'src'/f'{name}.c'),'-o',str(obj)],check=True)
            exe=out/'test'
            subprocess.run(['c++','-std=c++17',*flags,*inc,*objects,
                            str(ROOT/'tests/parallel_admission_test.cpp'),
                            str(ROOT/'vdp/video/extender/transport/p4_parallel_handover.cpp'),
                            '-Wl,--gc-sections','-o',str(exe)],check=True)
            args=[str(exe)]
            if os.environ.get('ADMISSION_VECTORS'):args.append(os.environ['ADMISSION_VECTORS'])
            subprocess.run(args,check=True)

if __name__=='__main__':unittest.main()
