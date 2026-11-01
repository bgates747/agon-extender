"""Pinned timestamp-only derivative and actual native linkage rejection checks."""
from pathlib import Path
import importlib.util,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import validate_p4_build as validator
spec=importlib.util.spec_from_file_location('probe',ROOT/'vdp/video/extender/display/rolling/patch_fbcpy.py');probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
BASE=ROOT/'agents/build001/native-tools/esp-idf/components/esp_lcd/src/esp_async_fbcpy.c'
class ProbeTest(unittest.TestCase):
    def test_only_hooks_added_and_unreviewed_base_rejected(self):
        original=BASE.read_bytes();derived=probe.derive(original)
        stripped='\n'.join(line for line in derived.split('\n') if 'agon_scanout_copy_phase(' not in line and line!='#include "strip_probe.h"')
        # The descriptor hook also inserts one separator line; ignore blank
        # lines only when proving every original instruction/comment unchanged.
        lines=lambda text:[line for line in text.splitlines() if line.strip()]
        self.assertEqual(lines(stripped),lines(original.decode()))
        self.assertEqual(derived.count('agon_scanout_copy_phase('),4)
        with self.assertRaises(ValueError):probe.derive(original+b'\n')
    def test_exact_source_single_action_archive_and_elf_required(self):
        with tempfile.TemporaryDirectory(prefix='fbcpy-link-') as d:
            build=Path(d)/'build';source=build/'dsi-strip/esp_async_fbcpy.c';source.parent.mkdir(parents=True)
            source.write_text(probe.derive(BASE.read_bytes()))
            obj='esp-idf/esp_lcd/fbcpy.obj';archive='esp-idf/esp_lcd/libesp_lcd.a'
            actions=[{'file':str(source),'output':obj}];edge=f'build {archive}: ARCHIVE {obj}\n';elf=f'build agon_extender.elf: LINK {archive}\n'
            validator.check_rolling_fbcpy_linkage(actions,edge+elf,build)
            for selected,ninja in [([],edge+elf),(actions*2,edge+elf),([{'file':str(BASE),'output':obj}],edge+elf),(actions,elf),(actions,edge)]:
                with self.subTest(selected=selected,ninja=ninja),self.assertRaises(SystemExit):validator.check_rolling_fbcpy_linkage(selected,ninja,build)
            source.write_text(source.read_text()+'\n')
            with self.assertRaisesRegex(SystemExit,'complete pinned derivative'):validator.check_rolling_fbcpy_linkage(actions,edge+elf,build)
if __name__=='__main__':unittest.main()
