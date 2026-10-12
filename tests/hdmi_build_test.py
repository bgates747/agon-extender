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

    def test_ifdef_selection_rejects_ambiguous_compiler_definitions(self):
        name = "AGON_EXTENDER_BITMAP_FAST"
        self.assertTrue(validate_p4_build.selected_definition([], name, False))
        self.assertTrue(validate_p4_build.selected_definition(["-D" + name + "=1"], name, True))
        self.assertTrue(validate_p4_build.selected_definition(["-D", name + "=1"], name, True))
        for argv in (["-D" + name], ["-D" + name + "=0"],
                     ["-D" + name + "=1"] * 2,
                     ["-D" + name + "=1", "-U" + name]):
            self.assertFalse(validate_p4_build.selected_definition(argv, name, True))
            self.assertFalse(validate_p4_build.selected_definition(argv, name, False))

    def test_link_observer_cannot_enter_ordinary_or_parallel_builds(self):
        args = (self.document, "p4-console", "p4-pc", "hdmi", "normal", True, "auto", True)
        self.assertNotIn("AGON_EXTENDER_HDMI_LINK_WATCH=1",
                         build_p4.select_display_profile(*args)["definitions"])
        self.assertIn("AGON_EXTENDER_HDMI_LINK_WATCH=1",
                      build_p4.select_display_profile(*args, hdmi_link_watch=True)["definitions"])
        for choice in (dict(indexed_ppa=True), dict(parallel_boot_candidate=True)):
            with self.assertRaises(SystemExit):
                build_p4.select_display_profile(*args, hdmi_link_watch=True, **choice)
        with self.assertRaises(SystemExit):
            build_p4.select_display_profile(self.document, "p4-console", "p4-pc",
                                           "browser", hdmi_link_watch=True)

    def test_indexed_ppa_is_explicit_and_requires_full_output_lifetime(self):
        args=(self.document,"p4-console","p4-pc","hdmi","normal",True,"auto",True)
        old=build_p4.select_display_profile(*args)
        indexed=build_p4.select_display_profile(*args,indexed_ppa=True)
        self.assertNotIn("AGON_EXTENDER_INDEXED_PPA=1",old["definitions"])
        self.assertIn("AGON_EXTENDER_INDEXED_PPA=1",indexed["definitions"])
        self.assertIn("video/extender/display/hdmi_ppa_indexed.cpp",indexed["sources"])
        record=build_p4.display_input_record("hdmi","normal",True,"auto",True,indexed_ppa=True)
        self.assertEqual(record["render_storage"],"linear-physical-rgb222")
        self.assertEqual(record["logical_stride_bytes"],"logical width")
        for output,timing,rolling,direct in (("browser","auto",True,True),("hdmi","848x480",True,True),("hdmi","auto",False,True),("hdmi","auto",True,False)):
            with self.assertRaises(SystemExit):
                build_p4.select_display_profile(self.document,"p4-console","p4-pc",output,"normal",direct,timing,rolling,indexed_ppa=True)

    def test_ppa_selection_is_explicit_and_preserves_ordinary_profiles(self):
        args=(self.document,"p4-console","p4-pc","hdmi","normal",True,"auto",True)
        ordinary=build_p4.select_display_profile(*args)
        scaled=build_p4.select_display_profile(*args,ppa_scale_320=True)
        self.assertNotIn("AGON_EXTENDER_HDMI_PPA_320=1",ordinary["definitions"])
        self.assertIn("AGON_EXTENDER_HDMI_PPA_320=1",scaled["definitions"])
        self.assertIn("esp_driver_ppa",scaled["requires"])
        with self.assertRaises(SystemExit):
            build_p4.select_display_profile(self.document,"p4-console","p4-pc","hdmi",ppa_scale_320=True)
        record=build_p4.display_input_record("hdmi","normal",True,"auto",True,True)
        self.assertEqual(record["ppa_scale_320"]["carrier"],[848,480])
        self.assertNotEqual(record["presentation_copy_bytes"],0)

    def test_frame_snapshot_requires_indexed_storage_and_is_off_by_default(self):
        args=(self.document,"p4-console","p4-pc","hdmi","normal",True,"auto",True)
        ordinary=build_p4.select_display_profile(*args)
        indexed=build_p4.select_display_profile(*args,indexed_ppa=True)
        snapshot=build_p4.select_display_profile(*args,indexed_ppa=True,indexed_frame_snapshot=True)
        flag="AGON_EXTENDER_INDEXED_FRAME_SNAPSHOT=1"
        self.assertNotIn(flag,ordinary["definitions"])
        self.assertNotIn(flag,indexed["definitions"])
        self.assertIn(flag,snapshot["definitions"])
        with self.assertRaisesRegex(SystemExit,"snapshot requires"):
            build_p4.select_display_profile(*args,indexed_frame_snapshot=True)

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

    def test_smaller_hdmi_timing_is_explicit_and_recorded(self):
        default = build_p4.select_display_profile(self.document,"p4-console","p4-pc","hdmi","normal",True)
        smaller = build_p4.select_display_profile(self.document,"p4-console","p4-pc","hdmi","normal",True,"848x480")
        self.assertNotIn("AGON_EXTENDER_HDMI_848X480=1", default["definitions"])
        self.assertIn("AGON_EXTENDER_HDMI_848X480=1", smaller["definitions"])
        self.assertEqual(default["sources"], smaller["sources"])
        metadata = build_p4.display_input_record("hdmi","normal",True,"848x480")
        self.assertEqual(metadata["logical_stride_bytes"],2544)
        self.assertEqual((metadata["configuration"]["width"],metadata["configuration"]["height"]),(848,480))
        self.assertEqual(metadata["configuration"]["timing"]["h_total"],1104)
        for output,timing in (("browser","848x480"),("hdmi","692x384")):
            with self.assertRaises(SystemExit):
                build_p4.select_display_profile(self.document,"p4-console","p4-pc",output,hdmi_timing=timing)

    def test_automatic_carriers_require_the_complete_lifecycle_profile(self):
        for direct, rolling, bench in ((False,True,"normal"),(True,False,"normal"),(True,True,"off")):
            with self.assertRaises(SystemExit):
                build_p4.select_display_profile(self.document,"p4-console","p4-pc","hdmi",bench,direct,"auto",rolling)
        profile=build_p4.select_display_profile(self.document,"p4-console","p4-pc","hdmi","normal",True,"auto",True)
        self.assertIn("AGON_EXTENDER_HDMI_AUTO=1",profile["definitions"])
        record=build_p4.display_input_record("hdmi","normal",True,"auto",True)
        self.assertEqual(record["configuration"]["carriers"], [[684,384],[848,480]])
        scanout=record["scanout"]
        self.assertEqual(scanout["kind"], "mode-selected-rolling")
        self.assertEqual(scanout["blocks"],15)
        self.assertEqual(scanout["runtime_layouts"],
                         [{"geometry":[684,384],"blocks":12},
                          {"geometry":[848,480],"blocks":15}])
        self.assertEqual(scanout["sram_allocation_width"],848)
        self.assertEqual(scanout["sram_allocation_bytes"],244224)
        self.assertNotIn("full_frame_geometry",scanout)

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

    def test_rolling_scanout_is_only_selected_for_explicit_experiments(self):
        selected = build_p4.select_display_profile(self.document, "p4-console",
            "p4-pc", "hdmi", "normal", True, "848x480", True)
        self.assertIn("AGON_EXTENDER_ROLLING_SCANOUT=1", selected["definitions"])
        self.assertTrue(any(p.endswith("rolling/scene.cpp") for p in selected["sources"]))
        for direct, timing, bench in ((False,"848x480","normal"),
                (True,"720p","normal"),(True,"848x480","off")):
            with self.assertRaises(SystemExit):
                build_p4.select_display_profile(self.document,"p4-console","p4-pc",
                    "hdmi",bench,direct,timing,True)

    def test_native_active_timing_and_bounded_memory_selection(self):
        selected = build_p4.select_display_profile(self.document, "p4-console",
            "p4-pc", "hdmi", "normal", True, "512x384", True)
        self.assertIn("AGON_EXTENDER_HDMI_512X384=1", selected["definitions"])
        self.assertNotIn("AGON_EXTENDER_HDMI_848X480=1", selected["definitions"])
        metadata = build_p4.display_input_record("hdmi", "normal", True, "512x384", True)
        self.assertEqual(metadata["logical_stride_bytes"], 1536)
        self.assertEqual(metadata["scanout"]["blocks"], 12)
        self.assertEqual(metadata["scanout"]["refill_abort_us"], 1600)
        configuration = metadata["configuration"]
        self.assertEqual((configuration["width"], configuration["height"]), (512,384))
        self.assertEqual(configuration["timing"]["h_front_sync_back"], [368,112,112])
        self.assertEqual(configuration["timing"]["v_front_sync_back"], [102,8,23])
        self.assertEqual(configuration["aspect_hint"], "4:3")

    def test_wide_carrier_preserves_centered_canvas_and_dma_geometry(self):
        selected = build_p4.select_display_profile(self.document, "p4-console",
            "p4-pc", "hdmi", "normal", True, "684x384", True)
        self.assertIn("AGON_EXTENDER_HDMI_684X384=1", selected["definitions"])
        metadata = build_p4.display_input_record("hdmi", "normal", True, "684x384", True)
        self.assertEqual(metadata["logical_stride_bytes"], 2052)
        self.assertEqual(metadata["scanout"]["blocks"], 12)
        self.assertEqual(metadata["scanout"]["refill_abort_us"], 1600)
        self.assertEqual(684 * 32 * 3 * metadata["scanout"]["sram_slots"], 196992)
        self.assertEqual(metadata["configuration"]["timing"]["h_front_sync_back"], [196,112,112])
        self.assertEqual(metadata["configuration"]["aspect_hint"], "16:9")

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

    def test_bitmap_fast_path_requires_explicit_direct_rgb888(self):
        selected = build_p4.select_display_profile(self.document, "p4-console",
            "p4-pc", "hdmi", "normal", True, "auto", True, bitmap_fast=True)
        self.assertIn("AGON_EXTENDER_BITMAP_FAST=1", selected["definitions"])
        control = build_p4.select_display_profile(self.document, "p4-console",
            "p4-pc", "hdmi", "normal", True, "auto", True)
        self.assertNotIn("AGON_EXTENDER_BITMAP_FAST=1", control["definitions"])
        with self.assertRaisesRegex(SystemExit, "bitmap fast"):
            build_p4.select_display_profile(self.document, "p4-console", "p4-pc",
                "hdmi", "normal", True, "auto", True, indexed_ppa=True, bitmap_fast=True)

    def test_scroll_fast_selects_p4_kernel_only_in_explicit_rgb888_experiment(self):
        args = (self.document, "p4-console", "p4-pc", "hdmi", "normal", True, "auto", True)
        source = "video/extender/display/scroll_copy_pie.S"
        control = build_p4.select_display_profile(*args)
        selected = build_p4.select_display_profile(*args, scroll_fast=True)
        self.assertNotIn(source, control["sources"])
        self.assertIn(source, selected["sources"])
        self.assertIn("AGON_EXTENDER_SCROLL_FAST=1", selected["definitions"])
        with self.assertRaisesRegex(SystemExit, "scroll fast"):
            build_p4.select_display_profile(*args, indexed_ppa=True, scroll_fast=True)

    def test_bitmap_lut_requires_explicit_fast_rgb888_painter(self):
        args=(self.document,"p4-console","p4-pc","hdmi","normal",True,"auto",True)
        control=build_p4.select_display_profile(*args,bitmap_fast=True)
        candidate=build_p4.select_display_profile(*args,bitmap_fast=True,bitmap_lut=True)
        flag="AGON_EXTENDER_BITMAP_LUT=1"
        self.assertNotIn(flag,control["definitions"])
        self.assertIn(flag,candidate["definitions"])
        with self.assertRaisesRegex(SystemExit,"LUT requires"):
            build_p4.select_display_profile(*args,bitmap_lut=True)
        with self.assertRaises(SystemExit):
            build_p4.select_display_profile(*args,indexed_ppa=True,bitmap_fast=True,bitmap_lut=True)


    def test_direct_bgr_overlay_is_explicit_and_accepts_both_storage_backends(self):
        args=(self.document,"p4-console","p4-pc","hdmi","normal",True,"auto",True)
        flag="AGON_EXTENDER_OVERLAY_BGR=1"
        for choices in ({}, {"indexed_ppa":True},
                        {"indexed_ppa":True,"indexed_frame_snapshot":True},
                        {"bitmap_fast":True,"bitmap_lut":True},
                        {"scroll_fast":True}, {"hdmi_link_watch":True},
                        {"ppa_scale_320":True}, {"parallel_boot_candidate":True},
                        {"parallel_boot_candidate":True,"exext_stream":True},
                        {"parallel_boot_candidate":True,"parallel_data_check":True}):
            control=build_p4.select_display_profile(*args,**choices)
            candidate=build_p4.select_display_profile(*args,overlay_bgr=True,**choices)
            self.assertNotIn(flag,control["definitions"])
            self.assertIn(flag,candidate["definitions"])
            self.assertEqual(control["sources"],candidate["sources"])
            self.assertEqual(candidate["definitions"],
                             [*control["definitions"][:len(self.document["profiles"]["p4-console"]["definitions"])],
                              flag,*control["definitions"][len(self.document["profiles"]["p4-console"]["definitions"]):]])
        for timing in ("848x480","512x384","684x384"):
            self.assertIn(flag,build_p4.select_display_profile(
                self.document,"p4-console","p4-pc","hdmi","normal",True,timing,True,
                overlay_bgr=True)["definitions"])
        for output,rolling in (("hdmi",False),("browser",True)):
            with self.assertRaisesRegex(SystemExit,"BGR overlay"):
                build_p4.select_display_profile(self.document,"p4-console","p4-pc",
                    output,"normal",True,"848x480" if output=="hdmi" else "1280x720",rolling,overlay_bgr=True)

    def test_direct_bgr_definition_applies_to_the_whole_generated_component(self):
        args=(self.document,"p4-console","p4-pc","hdmi","normal",True,"auto",True)
        for storage in ({},{"indexed_ppa":True,"indexed_frame_snapshot":True}):
            for selected in (False,True):
                profile=build_p4.select_display_profile(*args,overlay_bgr=selected,**storage)
                with tempfile.TemporaryDirectory() as tmp:
                    generated=Path(tmp)
                    build_p4.render_component(profile,self.document["common"],generated,{})
                    cmake=(generated/"CMakeLists.txt").read_text()
                    definition_block=cmake.split("target_compile_definitions(${COMPONENT_LIB} PRIVATE",1)[1].split(")",1)[0]
                    self.assertEqual("AGON_EXTENDER_OVERLAY_BGR=1" in definition_block,selected)
                    self.assertEqual(cmake.count("AGON_EXTENDER_OVERLAY_BGR=1"),int(selected))
                    self.assertIn("rolling/scene.cpp",cmake)
                    self.assertIn("hdmi_output.cpp",cmake)

    def test_direct_bgr_numeric_compile_binding_is_value_aware_and_unambiguous(self):
        name="AGON_EXTENDER_OVERLAY_BGR"
        check=lambda argv,on: validate_p4_build.selected_definition(
            argv,name,on,value_aware=True)
        self.assertTrue(check([],False))
        self.assertTrue(check(["-D"+name+"=0"],False))
        self.assertTrue(check(["-D",name+"=0"],False))
        self.assertTrue(check(["-D"+name+"=1"],True))
        for argv in (["-D"+name], ["-D"+name+"=2"],
                     ["-D"+name+"=0"]*2, ["-D"+name+"=1"]*2,
                     ["-D"+name+"=1","-U"+name],
                     ["-D"+name+"=1","-U",name],
                     ["-D"+name+"=0","-D"+name+"=1"]):
            self.assertFalse(check(argv,True))
            self.assertFalse(check(argv,False))
        self.assertFalse(check(["-D"+name+"=0"],True))
        self.assertFalse(check(["-D"+name+"=1"],False))


if __name__ == "__main__":
    unittest.main()
