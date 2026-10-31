#!/usr/bin/env python3
"""Structural tests for commit-pinned flash and hardware regression tools."""

from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path
import tempfile
import unittest
import struct
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


shared = load("hardware_validation", ROOT / "scripts/hardware_validation.py")
runner = load("firmware_qualification", ROOT / "qualification/run.py")
notifier = load("qualification_notify", ROOT / "qualification/notify.py")
video = load("qualification_video", ROOT / "qualification/video.py")


class HardwareValidationTests(unittest.TestCase):
    def test_repair_manifest_is_explicit_and_valid(self):
        document = json.loads((ROOT / "qualification/manifests/hardware.json").read_text())
        runner.validate_repair_manifest(document)
        self.assertEqual([case["id"] for case in document["cases"]],
                         ["installed-p4-integrated-smoke", "a10-rp06-mode-transaction",
                          "a10-rp04-raw-sd-write"])
        self.assertFalse(document["cases"][0]["destructive"])
        self.assertFalse(document["cases"][1]["destructive"])
        self.assertTrue(document["cases"][2]["destructive"])
        self.assertTrue(all(case["acceptance_required"] for case in document["cases"]))
        self.assertEqual([case["receipt_target"] for case in document["cases"]],
                         ["p4", "p4", "emos"])
        self.assertEqual(document["cases"][2]["depends_on"],
                         ["installed-p4-integrated-smoke", "a10-rp06-mode-transaction"])
        self.assertEqual(sum(case["required_checks"] for case in document["cases"]), 25)

    def test_manifest_rejects_unknown_self_or_duplicate_dependency(self):
        document = json.loads((ROOT / "qualification/manifests/hardware.json").read_text())
        document["cases"][2]["depends_on"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "depends_on"):
            runner.validate_repair_manifest(document)
        document["cases"][2]["depends_on"] = [document["cases"][2]["id"]]
        with self.assertRaisesRegex(ValueError, "depends_on"):
            runner.validate_repair_manifest(document)
        dependency = document["cases"][0]["id"]
        document["cases"][2]["depends_on"] = [dependency, dependency]
        with self.assertRaisesRegex(ValueError, "depends_on"):
            runner.validate_repair_manifest(document)

    def test_failed_prerequisite_blocks_dependent_case(self):
        case = {"depends_on": ["first"]}
        self.assertEqual(runner.unmet_dependencies(case, {}), ["first"])
        self.assertEqual(
            runner.unmet_dependencies(case, {"first": {"status": "test-failure"}}),
            ["first"],
        )
        self.assertEqual(
            runner.unmet_dependencies(case, {"first": {"status": "pass"}}),
            [],
        )

    def test_unsafe_foreground_blocks_keyboard_notification(self):
        results = [
            {"id": "safe", "status": "pass"},
            {"id": "raw", "status": "infrastructure-error",
             "foreground_unsafe": True},
        ]
        self.assertEqual(runner.notification_blockers(results), ["raw"])
        self.assertEqual(runner.notification_blockers(results[:1]), [])

    def test_video_decoder_accepts_exact_rgb222_frame(self):
        pixels = bytes((0, 1, 62, 63))
        raw = (b"EVF1" + bytes((1, 32, 2, 1)) +
               struct.pack("<IHHIIII", 7, 2, 2, 2, 4, 16667, 0) + pixels)
        record = video.decode_evf(raw)
        self.assertEqual((record["sequence"], record["width"], record["height"]),
                         (7, 2, 2))
        with self.assertRaisesRegex(ValueError, "RGB222"):
            video.decode_evf(raw[:-1] + b"\x40")

    def test_video_geometry_wait_discards_transition_frame(self):
        records = [
            {"sequence": 1, "width": 320, "height": 240},
            {"sequence": 2, "width": 640, "height": 480},
        ]

        class Session:
            def frame(self, path):
                Path(path).write_bytes(b"frame")
                return records.pop(0)

        with tempfile.TemporaryDirectory() as folder, \
                mock.patch.object(runner.time, "sleep"):
            result = runner.wait_video_geometry(
                Session(), Path(folder), "expected", 640, 480, timeout=1)
            attempts = sorted(Path(folder).glob("expected-*.evf"))
        self.assertEqual(result["sequence"], 2)
        self.assertEqual(len(attempts), 2)

    def test_physical_result_requires_complete_restore_oracle(self):
        record = (
            b"schema=1\ncase=a10-rp04-raw-sd-write\nstatus=pass\nsector=2\n"
            b"test_rc=0\nrestore_rc=0\nrestore_verify_rc=0\n"
            b"before_crc32=12345678\npattern_crc32=87654321\n"
            b"observed_crc32=87654321\nrestored_crc32=12345678\n"
            b"detail=completed\nfirst_partition_lba=8192\nwrite_attempted=1\n"
            b"token=0123456789ABCDEF\n"
        )
        self.assertEqual(runner.parse_result(record)["status"], "pass")
        with self.assertRaisesRegex(ValueError, "wrong schema"):
            runner.parse_result(record.replace(b"restore_rc=0\n", b""))

    def test_bench_startup_requires_extender_and_rejects_mainboard(self):
        runner.require_extender_startup(
            b"SET KEYBOARD 1\r\nEMOS KEYINPUT extender\r\n")
        with self.assertRaisesRegex(ValueError, "must select"):
            runner.require_extender_startup(b"SET KEYBOARD 1\r\n")
        with self.assertRaisesRegex(ValueError, "must select"):
            runner.require_extender_startup(
                b"EMOS KEYINPUT extender\r\nEMOS KEYINPUT mainboard\r\n")

    def test_bridge_reset_requires_a_new_boot_and_records_it(self):
        status={"boot":12,"ready":True,"physical_neutral":True}
        with tempfile.TemporaryDirectory() as folder, \
                mock.patch.object(runner,"wait_keyboard",side_effect=[{"boot":11},status]) as wait, \
                mock.patch.object(runner,"urlopen") as opened:
            opened.return_value.__enter__.return_value.read.return_value=b'{"pulse":"released"}'
            result=runner.bridge_reset({"reset_url":"http://bridge/reset"},"http://device",Path(folder))
            self.assertEqual(wait.call_args.kwargs["old_boot"],11)
            self.assertEqual(result["boot"],12)
            saved=json.loads((Path(folder)/"browser-reset.json").read_text())
            self.assertEqual(saved["new_boot"],12)

    def test_raw_sd_fixture_requires_token_and_prompt_without_unsafe_reset(self):
        source = inspect.getsource(runner.run_fwbug008)
        self.assertEqual(runner.RP04_COMPLETION_TIMEOUT, 20)
        self.assertIn("completion_token", source)
        self.assertIn("marker_followed_by_prompt", source)
        self.assertIn("host-owned result listener", source)
        self.assertIn("Agon was not reset", source)
        self.assertNotIn("reset_and_wait", source)
        self.assertNotIn("restore_startup(", source)
        self.assertNotIn("fixture-owned completion service", source)

    def test_run_marker_requires_marker_then_prompt(self):
        marker = "A10-RP04 COMPLETE 0123456789ABCDEF"
        self.assertFalse(runner.marker_followed_by_prompt("/ *\n" + marker, marker))
        self.assertFalse(runner.marker_followed_by_prompt(marker + "\nnot a prompt", marker))
        self.assertTrue(runner.marker_followed_by_prompt(
            marker + "                                           ?\n"
            "/ *                                                   ?\n", marker))

    def test_bare_or_pre_marker_prompt_is_not_a_safe_boundary(self):
        marker = "A10-RP04 START 0123456789ABCDEF"
        self.assertFalse(runner.marker_followed_by_prompt("/ *\n", marker))
        self.assertFalse(runner.marker_followed_by_prompt("/ *\n" + marker, marker))

    def test_normal_startup_allows_loaded_but_uninvoked_application(self):
        runner.require_extender_startup(
            b"SET KEYBOARD 1\r\nEMOS KEYINPUT extender\r\nCD /game\r\nLOAD flight.bin &040000\r\n")
        for command in (b"RUN", b"EXEC /suite.txt", b"IFTHERE a THEN RUN", b"SET Alias$go RUN"):
            with self.subTest(command=command), self.assertRaises(ValueError):
                runner.require_extender_startup(b"EMOS KEYINPUT extender\r\n" + command)

    def test_startup_verification_never_uploads_or_repairs(self):
        client = mock.Mock()
        client.download.return_value = b"normal"
        with tempfile.TemporaryDirectory() as folder:
            runner.unchanged_startup(client, b"normal", Path(folder))
            client.upload.assert_not_called()
            client.download.return_value = b"changed"
            with self.assertRaises(runner.UnsafeMainboardState):
                runner.unchanged_startup(client, b"normal", Path(folder))
        client.upload.assert_not_called()

    def test_config_requires_exact_p4_identity_even_for_shared_tool(self):
        document = json.loads((ROOT / "qualification/config.example.json").read_text())
        document["p4"].pop("usb_serial")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text(json.dumps(document))
            with self.assertRaisesRegex(ValueError, "p4.usb_serial"):
                shared.load_config(path)

    def test_commit_resolution_returns_full_identity(self):
        commit = shared.resolve_commit(ROOT, "HEAD")
        self.assertEqual(len(commit), 40)
        self.assertTrue(all(character in "0123456789abcdef" for character in commit))

    def test_notification_exits_attention_listener_before_verdict(self):
        calls = []

        class Lock:
            def close(self):
                calls.append("close")

        class Client:
            def __init__(self, url, state):
                calls.append((url, state.name))
                self.lock = Lock()

            def status(self):
                return {"online": True}

            def connect(self, *, require_fast):
                assert require_fast
                calls.append("connect")

            def rpc(self, operation):
                calls.append(("rpc", operation))

        original = notifier.SdClient
        notifier.SdClient = Client
        try:
            notifier.exit_attention_service("http://device", Path("state.json"),
                                             timeout=0.1)
        finally:
            notifier.SdClient = original
        self.assertIn(("rpc", 11), calls)
        self.assertEqual(calls[-1], "close")

    def test_screen_gate_retries_fresh_captures_until_observable(self):
        captures = iter(("old", "old", "marker"))
        original = runner.capture_text
        runner.capture_text = lambda url, timeout=30: next(captures)
        try:
            with tempfile.TemporaryDirectory() as folder:
                output = Path(folder) / "captures"
                result = runner.wait_screen(
                    "http://device", lambda text: text == "marker",
                    "contain marker", output, timeout=2)
                self.assertEqual(result, "marker")
                self.assertEqual(
                    [path.read_text() for path in sorted(output.iterdir())],
                    ["old", "old", "marker"])
        finally:
            runner.capture_text = original

    def test_video_gate_retries_until_new_mode_geometry_is_published(self):
        class Session:
            def __init__(self):
                self.frames = iter(((320, 240), (512, 384)))

            def frame(self, path):
                width, height = next(self.frames)
                return {"width": width, "height": height, "sequence": width}

        with tempfile.TemporaryDirectory() as folder:
            result = runner.wait_video_geometry(
                Session(), Path(folder), "mode20", 512, 384, timeout=1)
        self.assertEqual((result["width"], result["height"]), (512, 384))


if __name__ == "__main__":
    unittest.main()
