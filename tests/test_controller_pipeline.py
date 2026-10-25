"""Cross-component software path; no bench, emulator or physical timing claim."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
EMOS=ROOT.parent/'agon-emos'

class Pipeline(unittest.TestCase):
    def test_p4_to_resident_service_to_actual_application_client(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            wire=ROOT/'vdp/video/extender/input/controller/appliance_wire.h'
            self.assertEqual(wire.read_bytes(),(EMOS/'src/emos_controller_wire.h').read_bytes())
            (out/'controller_wire.h').write_bytes(wire.read_bytes())
            (out/'ff.h').write_text('enum {FR_OK=0,FR_TIMEOUT=15,FR_INVALID_PARAMETER=19};\n')
            subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-endif-labels',
                            '-Wno-pointer-to-int-cast','-Wno-int-to-pointer-cast',
                            '-fsanitize=address,undefined','-DMOS_DEFINES_H',
                            '-DEMOS_BUSY=31','-DEMOS_UNSAFE_CALLER=32','-DEMOS_UNAVAILABLE=35',
                            '-include',str(EMOS/'tests/host/defines.h'),'-I'+temp,
                            '-I'+str(EMOS/'tests/host'),'-I'+str(EMOS/'src'),
                            '-c',str(EMOS/'src/emos_controller.c'),'-o',str(out/'emos.o')],check=True)
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                            '-fsanitize=address,undefined','-I'+temp,'-I'+str(ROOT/'vdp/video'),
                            str(ROOT/'tests/controller/pipeline.cpp'),str(out/'emos.o'),
                            '-o',str(out/'pipeline')],check=True)
            subprocess.run([str(out/'pipeline')],check=True)

if __name__=='__main__':unittest.main()
