"""Cross-component software path; no bench, emulator or physical timing claim."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
EMOS=Path(os.environ.get('AGON_EMOS_ROOT',ROOT.parent/'agon-emos'))
HOST=ROOT.parent/'agon-emos/tests/host'

class Pipeline(unittest.TestCase):
    def test_standalone_public_header(self):
        with tempfile.TemporaryDirectory() as temp:
            binary=Path(temp)/'public-header'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                            '-fsanitize=address,undefined','-no-pie','-I'+str(ROOT/'include'),
                            str(ROOT/'tests/controller/public_header.cpp'),'-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True)

    def test_p4_to_resident_service_to_actual_application_client(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            wire=ROOT/'vdp/video/extender/input/controller/appliance_wire.h'
            self.assertEqual(wire.read_bytes(),(EMOS/'src/emos_controller_wire.h').read_bytes())
            (out/'controller_wire.h').write_bytes(wire.read_bytes())
            (out/'ff.h').write_text('enum {FR_OK=0,FR_TIMEOUT=15,FR_INVALID_PARAMETER=19};\n')
            (out/'ez80f92.h').write_text('/* No register I/O in this endpoint. */\n')
            flags=['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-endif-labels',
                            '-Wno-pointer-to-int-cast','-Wno-int-to-pointer-cast',
                            '-fsanitize=address,undefined','-no-pie','-DMOS_DEFINES_H',
                            '-DMOS_AGONDEV_LOWERCASE_EZ80_H=1',
                            '-DEMOS_BUSY=31','-DEMOS_UNSAFE_CALLER=32','-DEMOS_UNAVAILABLE=35',
                            '-include',str(HOST/'defines.h'),'-I'+temp,
                            '-I'+str(HOST),'-I'+str(EMOS/'src')]
            units=['emos_controller']
            if os.environ.get('AGON_NETWORK_PARALLEL'):
                flags+=['-DEMOS_NETWORK_PARALLEL=1'];units+=['emos_app_span']
            objects=[]
            for unit in units:
                obj=out/(unit+'.o');objects.append(str(obj))
                subprocess.run([*flags,'-c',str(EMOS/'src'/(unit+'.c')),'-o',str(obj)],check=True)
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                            '-fsanitize=address,undefined','-no-pie','-I'+temp,'-I'+str(ROOT/'vdp/video'),'-I'+str(ROOT/'include'),
                            str(ROOT/'tests/controller/pipeline.cpp'),*objects,
                            '-o',str(out/'pipeline')],check=True)
            subprocess.run([str(out/'pipeline')],check=True)

if __name__=='__main__':unittest.main()
