#!/usr/bin/env python3
"""Contract tests for reset completion verification."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("reset_agon", ROOT / "scripts/reset_agon.py")
assert SPEC and SPEC.loader
RESET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RESET)


class ResetVerificationTests(unittest.TestCase):
    def test_wait_requires_new_ready_neutral_epoch(self):
        states = iter((
            {"boot": 10, "ready": False, "physical_neutral": True,
             "pending": 0, "held": 0},
            {"boot": 11, "ready": False, "physical_neutral": True,
             "pending": 0, "held": 0},
            {"boot": 11, "ready": True, "physical_neutral": True,
             "pending": 0, "held": 0},
        ))
        with (mock.patch.object(RESET, "status", side_effect=lambda _url: next(states)),
              mock.patch.object(RESET.time, "sleep")):
            result = RESET.wait_boot("http://device", 10, 1)
        self.assertEqual(result["boot"], 11)

    def test_wait_rejects_same_epoch_even_when_ready(self):
        with (mock.patch.object(RESET, "status", return_value={
                  "boot": 10, "ready": True, "physical_neutral": True,
                  "pending": 0, "held": 0}),
              mock.patch.object(RESET.time, "monotonic", side_effect=(0, 0, 2)),
              mock.patch.object(RESET.time, "sleep")):
            with self.assertRaisesRegex(TimeoutError, "deadline exceeded"):
                RESET.wait_boot("http://device", 10, 1)


if __name__ == "__main__":
    unittest.main()
