#!/usr/bin/env python3
"""Static contract checks for BUILD-001's native P4 profile authority."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
from copy import deepcopy


ROOT = Path(__file__).resolve().parents[1]
VDP = ROOT / "vdp"
sys.path.insert(0, str(ROOT / "scripts"))


class NativeP4ProfilesTest(unittest.TestCase):
    def test_ordinary_exext_is_explicit_and_excludes_diagnostics(self):
        from build_p4 import check_parallel_qualification_identity as check, select_display_profile
        identity='port-008-stream-r01-b2026-10-11-10-50-00Z'
        self.assertTrue(check(identity,True,True,False,'p4-console','p4-pc','hdmi',False,True))
        with self.assertRaises(SystemExit):
            check('extender-vdp-v1.0.0',True,True,False,'p4-console','p4-pc','hdmi',False,True)
        profile=select_display_profile(self.document,'p4-console','p4-pc','browser',parallel_boot_candidate=True,exext_stream=True)
        self.assertIn('AGON_EXTENDER_EXEXT_STREAM=1',profile['definitions'])
        self.assertNotIn('esp_driver_pcnt',profile['requires'])
        with self.assertRaises(SystemExit):
            select_display_profile(self.document,'p4-console','p4-pc','browser',exext_stream=True)
        with self.assertRaises(SystemExit):
            select_display_profile(self.document,'p4-console','p4-pc','browser',parallel_boot_candidate=True,parallel_data_check=True,exext_stream=True)

    def test_devkit_data_comparison_keeps_private_identity_and_boot_owner(self):
        from build_p4 import check_parallel_qualification_identity as check
        good = "port-008-data-r17-b2026-10-11-07-35-00Z"
        self.assertTrue(check(good, True, True, False, "p4-console", "p4-devkit", "browser", True))
        for identity, boot, probe, output in (
            ("extender-vdp-v1.0.0", True, False, "browser"),
            (good, False, False, "browser"),
            (good, True, True, "browser"),
            (good, True, False, "hdmi"),
        ):
            with self.subTest(identity=identity, boot=boot, probe=probe, output=output), self.assertRaises(SystemExit):
                check(identity, True, boot, probe, "p4-console", "p4-devkit", output, True)
        from build_p4 import select_display_profile
        profile = select_display_profile(self.document, "p4-console", "p4-devkit", "browser",
                                         parallel_boot_candidate=True, parallel_data_check=True)
        self.assertIn("AGON_EXTENDER_PARALLEL_DATA_CHECK=1", profile["definitions"])
        self.assertIn("esp_driver_parlio", profile["requires"])
        self.assertNotIn("esp_driver_pcnt", profile["requires"])

    def test_devkit_control_cannot_select_pc_diagnostics_or_release_identity(self):
        from build_p4 import check_parallel_qualification_identity as check
        good = "port-008-devkit-r01-b2026-10-10-06-00-00Z"
        self.assertTrue(check(good, True, True, False, "p4-console", "p4-devkit", "browser"))
        for identity, boot, probe, board, output, data in (
            ("extender-vdp-v1.0.0", True, False, "p4-devkit", "browser", False),
            (good, False, False, "p4-devkit", "browser", False),
            (good, True, True, "p4-devkit", "browser", False),
            (good, True, False, "p4-pc", "browser", False),
            (good, True, False, "p4-devkit", "hdmi", False),
            (good, True, False, "p4-devkit", "browser", True),
        ):
            with self.subTest(identity=identity, board=board, output=output), self.assertRaises(SystemExit):
                check(identity, True, boot, probe, "p4-console", board, output, data)

    def test_parallel_install_identity_is_explicit_and_nonrelease(self):
        from build_p4 import check_parallel_qualification_identity as check
        good="port-008-probe-r01-b2026-10-09-21-00-00Z"
        self.assertTrue(check(good,True,True,True,"p4-console","p4-pc","browser"))
        self.assertFalse(check(good,False,True,True,"p4-console","p4-pc","browser"))
        for args in (("extender-vdp-v1.0.0",True,True,True,"p4-console","p4-pc","browser"),
                     (good,True,False,True,"p4-console","p4-pc","browser"),
                     (good,True,True,False,"p4-console","p4-pc","browser"),
                     (good,True,True,True,"p4-console","devkit","browser"),
                     (good,True,True,True,"p4-console","p4-pc","hdmi"),
                     (good.replace("10-09","99-99"),True,True,True,"p4-console","p4-pc","browser")):
            with self.assertRaises(SystemExit):check(*args)

    @classmethod
    def setUpClass(cls):
        cls.document = json.loads((VDP / "build/p4-profiles.json").read_text())

    def test_parallel_startup_is_explicit_private_selection(self):
        from build_p4 import select_display_profile
        ordinary = select_display_profile(self.document, "p4-console", "p4-pc", "browser")
        candidate = select_display_profile(self.document, "p4-console", "p4-pc", "browser", parallel_boot_candidate=True)
        flag = "AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE=1"
        self.assertNotIn(flag, ordinary["definitions"])
        self.assertIn(flag, candidate["definitions"])
        native = "video/extender/transport/p4_native_payload.cpp"
        self.assertNotIn(native, ordinary["sources"])
        self.assertEqual(ordinary["sources"] + [native,"video/extender/transport/p4_block_coordinator.cpp"], candidate["sources"])
        self.assertIn("esp_driver_parlio", candidate["requires"])
        devkit = select_display_profile(self.document, "p4-console", "p4-devkit", "browser", parallel_boot_candidate=True)
        self.assertIn(flag, devkit["definitions"])
        with self.assertRaises(SystemExit):
            select_display_profile(self.document, "p4-console", "devkit", "browser", parallel_boot_candidate=True)
        with self.assertRaises(SystemExit):
            select_display_profile(self.document, "p4-mos-recovery", "p4-pc", "browser", parallel_boot_candidate=True)

    def test_private_probe_requires_native_owner(self):
        from build_p4 import select_display_profile
        args=(self.document,"p4-console","p4-pc","browser")
        with self.assertRaises(SystemExit):
            select_display_profile(*args,parallel_probe_candidate=True)
        ordinary=select_display_profile(*args,parallel_boot_candidate=True)
        probe=select_display_profile(*args,parallel_boot_candidate=True,parallel_probe_candidate=True)
        self.assertEqual(ordinary["sources"],probe["sources"])
        self.assertEqual(ordinary["definitions"]+["AGON_EXTENDER_PARALLEL_PROBE=1"],probe["definitions"])

    def test_three_accepted_profiles_only(self):
        self.assertEqual(self.document["schema_version"], 2)
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

    def test_exactly_one_product_display_owner_and_isolated_families(self):
        script = ROOT / "scripts/build_p4.py"
        spec = importlib.util.spec_from_file_location("build_p4_display", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.checked_display_ownership(self.document)

        families = self.document["display_families"]
        self.assertEqual(
            [name for name, family in families.items() if family["product_owner"]],
            ["stock-shaped"],
        )
        owners = [name for name, profile in self.document["profiles"].items()
                  if profile["product_display_role"] == "product-owner"]
        self.assertEqual(owners, ["p4-console"])
        self.assertEqual(
            self.document["profiles"]["p4-port008-nonrelease-qualification"]
                         ["product_display_role"],
            "bounded-qualification",
        )
        self.assertEqual(
            families["port008-parallel-nonrelease"]["bounded_owner"],
            "PORT-008",
        )
        self.assertEqual(
            families["port008-parallel-nonrelease"]["retirement_conditions"],
            ["PORT-008-2.e", "PORT-008-2.f", "A10-RP02-O03"],
        )

    def test_display_ownership_rejects_mixed_or_unbounded_profiles(self):
        script = ROOT / "scripts/build_p4.py"
        spec = importlib.util.spec_from_file_location("build_p4_display_failures", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        document = deepcopy(self.document)
        document["profiles"]["p4-console"]["sources"].append(
            "video/extender/display/p4_display_controller.cpp")
        with self.assertRaisesRegex(SystemExit, "mixes display families"):
            module.checked_display_ownership(document)

        document = deepcopy(self.document)
        document["display_families"]["port008-parallel-nonrelease"].pop(
            "retirement_conditions")
        with self.assertRaisesRegex(SystemExit, "lacks a retirement contract"):
            module.checked_display_ownership(document)

    def test_console_definition_policy_is_explicit_and_minimal(self):
        profile = self.document["profiles"]["p4-console"]
        self.assertEqual(profile["definitions"], [
            "AGON_EXTENDER_P4_BOOT=1",
            "AGON_EXTENDER_STOCK_RUNTIME=1",
            "AGON_EXTENDER_SD_SERVICE=1",
            "AGON_EXTENDER_STAGED_WEBDAV=1",
            "AGON_EXTENDER_REMOTE_KEYBOARD=1",
            "AGON_EXTENDER_TELEMETRY=1",
            "AGON_EXTENDER_VIDEO_POLL_MS=1",
            "AGON_EXTENDER_SNAPSHOT_MUTEX=1",
            "AGON_EXTENDER_SNAPSHOT_LOOKAHEAD=1",
            "AGON_EXTENDER_PACKED_ROW=1",
        ])
        self.assertEqual(profile["definition_policy"], {
            "diagnostic": [
                "AGON_EXTENDER_VIDEO_TIMING=1",
                "AGON_EXTENDER_REFRESH_TRACE=1",
                "AGON_EXTENDER_VIDEO_DISPATCH_TIMING=1",
            ],
            "rejected": [
                "AGON_EXTENDER_CANARY=1",
                "AGON_EXTENDER_INTERNAL_POOLS=1",
                "AGON_EXTENDER_DRAW_FOUR=1",
                "AGON_EXTENDER_DRAW_TWICE=1",
                "AGON_EXTENDER_OUTPUT_ROW_PAIR=1",
                "AGON_EXTENDER_INTERNAL_GAME_MODE=1",
                "AGON_EXTENDER_INTERNAL_FRAMEBUFFER=1",
                "AGON_EXTENDER_OUTPUT_BELOW_PARSER=1",
            ],
        })

    def test_build_rejects_overlapping_definition_policy(self):
        script = ROOT / "scripts/build_p4.py"
        spec = importlib.util.spec_from_file_location("build_p4_policy", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        profile = deepcopy(self.document["profiles"]["p4-console"])
        profile["definition_policy"]["rejected"].append(profile["definitions"][0])
        with self.assertRaisesRegex(SystemExit, "classified as both"):
            module.checked_definition_groups(profile)
        profile = deepcopy(self.document["profiles"]["p4-console"])
        profile["definitions"].append("AGON_EXTENDER_BAD=1;COMMAND")
        with self.assertRaisesRegex(SystemExit, "unsafe required definition"):
            module.checked_definition_groups(profile)

    def test_console_source_asset_has_one_reset_url_marker(self):
        page = (VDP / "video/extender/web/index.html").read_text()
        self.assertEqual(page.count('name="agon-reset-url" content=""'), 1)

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

    def test_factory_image_uses_idf_flash_offsets(self):
        script = ROOT / "scripts/build_p4.py"
        spec = importlib.util.spec_from_file_location("build_p4", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            build = Path(temporary)
            (build / "boot").mkdir()
            (build / "boot/boot.bin").write_bytes(b"BOOT")
            (build / "app.bin").write_bytes(b"APP")
            (build / "flasher_args.json").write_text(json.dumps({
                "flash_files": {"0x2": "boot/boot.bin", "0x9": "app.bin"}
            }))
            factory = module.assemble_factory_image(build)
            self.assertEqual(factory.read_bytes(), b"\xff\xffBOOT\xff\xff\xffAPP")


if __name__ == "__main__":
    unittest.main()
