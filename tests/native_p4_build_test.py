#!/usr/bin/env python3
"""Static contract checks for BUILD-001's native P4 profile authority."""

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

    def test_console_owns_one_boot_entry_and_lcd_sources(self):
        sources = self.document["profiles"]["p4-console"]["sources"]
        self.assertEqual([item for item in sources if "/boot/" in item],
                         ["video/extender/boot/p4_console.cpp"])
        self.assertIn("video/extender/display/lcd/output.cpp", sources)
        self.assertIn("video/extender/display/lcd/panel.c", sources)


if __name__ == "__main__":
    unittest.main()
