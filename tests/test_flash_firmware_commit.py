#!/usr/bin/env python3
"""Host-only contract tests for commit-pinned flash completion behavior."""

from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "flash_firmware_commit", ROOT / "scripts/flash_firmware_commit.py")
assert SPEC and SPEC.loader
FLASH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FLASH)


def verified_receipt() -> dict:
    return {
        "schema": 1,
        "status": "verified",
        "target": "p4",
        "component_commit": "a" * 40,
        "build_id": "test-build",
        "write_verified": True,
        "boot_identity_observed": True,
    }


class FinishP4InstallTests(unittest.TestCase):
    def test_verified_flash_resets_agon_then_requires_new_ready_epoch(self) -> None:
        events: list[str] = []
        with tempfile.TemporaryDirectory() as temporary:
            reset_config = Path(temporary) / "reset.json"
            reset_config.write_text("{}\n")
            config = {"extender_url": "http://p4.invalid",
                      "reset_config": str(reset_config)}

            def status(_url: str) -> dict:
                events.append("status")
                return {"boot": 17, "ready": False}

            def reset(*_args, **_kwargs):
                events.append("reset")
                return mock.Mock(returncode=0)

            def wait(_url: str, *, old_boot: int, timeout: float) -> dict:
                self.assertEqual(old_boot, 17)
                self.assertEqual(timeout, 60)
                events.append("wait")
                return {"boot": 18, "ready": True}

            with (mock.patch.object(FLASH, "keyboard_status", side_effect=status),
                  mock.patch.object(FLASH.subprocess, "run", side_effect=reset),
                  mock.patch.object(FLASH, "wait_keyboard", side_effect=wait)):
                receipt = FLASH.finish_p4_install(config, verified_receipt(),
                                                  reset_agon=True)

        self.assertEqual(events, ["status", "reset", "wait"])
        self.assertTrue(receipt["agon_reset_performed"])
        self.assertTrue(receipt["agon_connection_verified"])
        self.assertEqual(receipt["agon_boot_before"], 17)
        self.assertEqual(receipt["agon_boot_after"], 18)

    def test_no_reset_flag_skips_reset_and_connectivity_probe(self) -> None:
        with (mock.patch.object(FLASH, "keyboard_status") as status,
              mock.patch.object(FLASH.subprocess, "run") as reset,
              mock.patch.object(FLASH, "wait_keyboard") as wait):
            receipt = FLASH.finish_p4_install({}, verified_receipt(),
                                              reset_agon=False)
        status.assert_not_called()
        reset.assert_not_called()
        wait.assert_not_called()
        self.assertFalse(receipt["agon_reset_performed"])
        self.assertFalse(receipt["agon_connection_verified"])

    def test_unverified_p4_never_resets_agon(self) -> None:
        receipt = verified_receipt()
        receipt["write_verified"] = False
        with mock.patch.object(FLASH.subprocess, "run") as reset:
            with self.assertRaisesRegex(RuntimeError, "before verified P4 write and boot"):
                FLASH.finish_p4_install({}, receipt, reset_agon=True)
        reset.assert_not_called()

    def test_connectivity_failure_prevents_success_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            reset_config = Path(temporary) / "reset.json"
            reset_config.write_text("{}\n")
            config = {"extender_url": "http://p4.invalid",
                      "reset_config": str(reset_config)}
            with (mock.patch.object(FLASH, "keyboard_status",
                                    return_value={"boot": 20, "ready": False}),
                  mock.patch.object(FLASH.subprocess, "run"),
                  mock.patch.object(FLASH, "wait_keyboard",
                                    side_effect=TimeoutError("not connected"))):
                with self.assertRaisesRegex(TimeoutError, "not connected"):
                    FLASH.finish_p4_install(config, verified_receipt(),
                                            reset_agon=True)

    def test_success_output_is_plain_english_without_json_dump(self) -> None:
        receipt = verified_receipt()
        receipt.update(agon_reset_performed=True,
                       agon_connection_verified=True)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            FLASH.print_success(receipt, Path("/tmp/receipt.json"))
        text = output.getvalue()
        self.assertIn("P4 FLASH WORKFLOW SUCCEEDED", text)
        self.assertIn("EMOS-to-P4 connectivity: verified", text)
        self.assertIn("Receipt: /tmp/receipt.json", text)
        self.assertNotIn('{"', text)


if __name__ == "__main__":
    unittest.main()
