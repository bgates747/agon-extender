#!/usr/bin/env python3
"""Static contract checks for BUILD-001's native P4 profile authority."""

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VDP = ROOT / "vdp"


class NativeP4ProfilesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((VDP / "build/p4-profiles.json").read_text())

    def test_three_accepted_profiles_only(self):
        self.assertEqual(set(self.document["profiles"]), {
            "p4-console", "p4-mos-recovery",
            "p4-port008-nonrelease-qualification",
        })

    def test_all_selected_inputs_exist_and_are_unique(self):
        for name, profile in self.document["profiles"].items():
            with self.subTest(profile=name):
                sources = profile["sources"]
                self.assertEqual(len(sources), len(set(sources)))
                self.assertTrue(set(sources).isdisjoint(profile["forbidden_sources"]))
                for item in sources + profile["forbidden_sources"] + profile["embedded_text"]:
                    self.assertFalse(Path(item).is_absolute())
                    self.assertNotIn("..", Path(item).parts)
                    self.assertTrue((VDP / item).is_file(), item)

    def test_dependency_versions_are_exact_and_baseline_wifi_is_retained(self):
        dependencies = self.document["common"]["dependencies"]
        self.assertEqual(dependencies["espressif/arduino-esp32"], "3.3.11")
        self.assertEqual(dependencies["espressif/esp_wifi_remote"], "1.6.4")
        for version in dependencies.values():
            self.assertRegex(version, r"^[0-9]+\.[0-9]+\.[0-9]+(?:~[0-9]+)?$")

    def test_console_owns_one_boot_entry_without_lcd_sources(self):
        sources = self.document["profiles"]["p4-console"]["sources"]
        self.assertEqual([item for item in sources if "/boot/" in item],
                         ["video/extender/boot/p4_console.cpp"])
        self.assertFalse(any("/display/lcd/" in item for item in sources))
        self.assertNotIn("espressif/esp_lcd_st7701",
                         self.document["common"]["dependencies"])

    def test_console_explicitly_enables_staged_webdav(self):
        definitions = self.document["profiles"]["p4-console"]["definitions"]
        self.assertIn("AGON_EXTENDER_STAGED_WEBDAV=1", definitions)

    def test_clang_translation_changes_only_known_gcc_target_flags(self):
        script = ROOT / "scripts/prepare_p4_clang_database.py"
        spec = importlib.util.spec_from_file_location("clang_db", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        entry = {
            "directory": str(ROOT), "file": str(VDP / "sample.cpp"),
            "output": "sample.o",
            "command": "riscv32-esp-elf-g++ -DKEEP=1 "
                       "-march=rv32imafc_zicsr_zifencei_xesppie "
                       "-fstrict-volatile-bitfields -fno-tree-switch-conversion "
                       "-Ikeep -c sample.cpp -o sample.o",
        }
        translated = module.translate(entry, Path("/opt/llvm"))["arguments"]
        self.assertIn("-DKEEP=1", translated)
        self.assertIn("-Ikeep", translated)
        self.assertIn("-march=rv32imafc_zicsr_zifencei", translated)
        self.assertNotIn("-fstrict-volatile-bitfields", translated)
        self.assertNotIn("-fno-tree-switch-conversion", translated)


if __name__ == "__main__":
    unittest.main()
