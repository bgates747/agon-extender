"""Fail-closed HDMI selection, source identity and actual linkage checks."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_p4
import validate_p4_build


class HdmiBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((ROOT / "vdp/build/p4-profiles.json").read_text())

    def test_unsupported_board_or_profile_rejected_before_output_creation(self):
        for board, profile in (("p4-devkit", "p4-console"),
                               ("p4-pc", "p4-mos-recovery")):
            with self.subTest(board=board, profile=profile), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "uncreated"
                result = subprocess.run([
                    str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/build_p4.py"),
                    "--profile", profile, "--board", board,
                    "--display-output", "hdmi", "--output", str(output),
                ], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("HDMI output requires p4-pc / p4-console", result.stderr)
                self.assertFalse(output.exists())

    def test_sink_selection_preserves_the_rendering_owner_and_original_profile(self):
        original = deepcopy(self.document)
        browser = build_p4.select_display_profile(self.document, "p4-console", "p4-devkit", "browser")
        hdmi = build_p4.select_display_profile(self.document, "p4-console", "p4-pc", "hdmi")
        self.assertEqual(self.document, original)
        base = original["profiles"]["p4-console"]
        self.assertEqual(browser["sources"], base["sources"])
        self.assertEqual(browser["definitions"], base["definitions"])
        self.assertEqual(hdmi["sources"], [*base["sources"], build_p4.HDMI_SOURCE])
        self.assertEqual(hdmi["display_family"], "stock-shaped")
        self.assertIn("AGON_EXTENDER_HDMI=1", hdmi["definitions"])

    def test_conversion_without_scanout_is_distinct_from_drawing_only_off(self):
        before = deepcopy(self.document)
        off = build_p4.select_display_profile(self.document, "p4-console", "p4-pc", "hdmi", "off")
        convert = build_p4.select_display_profile(self.document, "p4-console", "p4-pc", "hdmi", "convert-off")
        self.assertEqual(self.document, before)
        self.assertEqual(off["sources"], convert["sources"])
        self.assertIn("AGON_EXTENDER_BENCH_OFF=1", off["definitions"])
        self.assertNotIn("AGON_EXTENDER_BENCH_CONVERT_OFF=1", off["definitions"])
        self.assertEqual(convert["definitions"], [*off["definitions"], "AGON_EXTENDER_BENCH_CONVERT_OFF=1"])

    def test_direct_rgb888_is_explicit_and_native_build_excludes_it(self):
        normal = build_p4.select_display_profile(self.document, "p4-console", "p4-pc", "hdmi", "normal")
        direct = build_p4.select_display_profile(self.document, "p4-console", "p4-pc", "hdmi", "normal", True)
        self.assertIn(build_p4.RGB888_SOURCE, normal["forbidden_sources"])
        self.assertNotIn(build_p4.RGB888_SOURCE, normal["sources"])
        self.assertIn(build_p4.RGB888_SOURCE, direct["sources"])
        self.assertIn("AGON_EXTENDER_DIRECT_RGB888=1", direct["definitions"])
        build_p4.check_build_identity("rgb-001-r01-b2026-10-05-23-15-00Z", True, True,
                                      "p4-console", "p4-pc", "hdmi", "normal", True)
        for output,benchmark in (("browser","normal"),("hdmi",None)):
            with self.assertRaises(SystemExit):
                build_p4.select_display_profile(self.document,"p4-console","p4-pc",output,benchmark,True)

    def test_bridge_copy_or_missing_link_is_rejected(self):
        bridge = ROOT / "vdp/components/esp_lcd_lt8912b/esp_lcd_lt8912b.c"
        obj = "esp-idf/esp_lcd_lt8912b/CMakeFiles/__idf_esp_lcd_lt8912b.dir/esp_lcd_lt8912b.c.obj"
        archive = "esp-idf/esp_lcd_lt8912b/libesp_lcd_lt8912b.a"
        commands = [{"file": str(bridge), "output": obj},
                    {"file": str(ROOT / "agents/build001/native-tools/esp-idf/components/esp_lcd/dsi/esp_lcd_panel_dpi.c")}]
        ninja = f"build {archive}: archive {obj}\nbuild agon_extender.elf: link {archive}\n"
        validate_p4_build.check_hdmi_linkage(commands, ninja, "hdmi")
        stale = deepcopy(commands)
        stale[0]["file"] = "/tmp/stale-copy/esp_lcd_lt8912b.c"
        with self.assertRaisesRegex(SystemExit, "compile source differs"):
            validate_p4_build.check_hdmi_linkage(stale, ninja, "hdmi")
        with self.assertRaisesRegex(SystemExit, "absent from the bridge archive"):
            validate_p4_build.check_hdmi_linkage(commands, ninja.replace(obj, "unrelated.obj"), "hdmi")
        with self.assertRaisesRegex(SystemExit, "absent from the ELF link"):
            validate_p4_build.check_hdmi_linkage(commands, ninja.replace(f"link {archive}", "link unrelated.a"), "hdmi")
        with self.assertRaisesRegex(SystemExit, "browser build compiled"):
            validate_p4_build.check_hdmi_linkage(commands, ninja, "browser")

    def test_dirty_experimental_permission_does_not_waive_normal_identity_guard(self):
        identity = "hdmi-001-r01-b2026-10-05-01-23-45Z"
        with self.assertRaisesRegex(SystemExit, "clean committed inputs"):
            build_p4.check_build_identity(identity, True, False, "p4-console", "p4-pc", "hdmi")
        build_p4.check_build_identity(identity, True, True, "p4-console", "p4-pc", "hdmi")
        for build_id, board, sink in (("release-r01", "p4-pc", "hdmi"),
                                      (identity, "p4-devkit", "hdmi"),
                                      (identity, "p4-pc", "browser")):
            with self.subTest(build_id=build_id, board=board, sink=sink):
                with self.assertRaisesRegex(SystemExit, "dirty experimental builds require"):
                    build_p4.check_build_identity(build_id, True, True, "p4-console", board, sink)
        with self.assertRaisesRegex(SystemExit, "invalid UTC timestamp"):
            build_p4.check_build_identity("hdmi-001-r01-b2026-13-05-01-23-45Z", True, True,
                                          "p4-console", "p4-pc", "hdmi")

    def test_experimental_source_snapshot_retains_exact_bytes_and_detects_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            source = work / "source.cpp"
            source.write_bytes(b"// exact experimental bytes\n")
            output = work / "output"
            output.mkdir()
            with patch.object(build_p4, "ROOT", work), patch.object(build_p4, "source_paths", return_value=[source]):
                record = build_p4.freeze_source_inputs(output)
                with tarfile.open(output / "source.tar.gz", "r:gz") as archive:
                    data = archive.extractfile("source.cpp").read()
                self.assertEqual(data, source.read_bytes())
                self.assertEqual(record["files"][0]["sha256"], hashlib.sha256(data).hexdigest())
                source.write_bytes(b"// changed while building\n")
                self.assertNotEqual(build_p4.source_input_record(), record)


if __name__ == "__main__":
    unittest.main()
