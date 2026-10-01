#!/usr/bin/env python3
"""Structural checks for the installed-hardware performance runner."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


def load():
    spec = importlib.util.spec_from_file_location(
        "qualification_performance", ROOT / "qualification/performance.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


performance = load()


class PerformanceQualificationTests(unittest.TestCase):
    def test_all_modes_have_observer_on_and_off_controls(self):
        matrix = {(case["mode"], case["kind"], case["video_hz"])
                  for case in performance.cases()}
        for mode in (0, 8, 20):
            self.assertIn((mode, "empty", None), matrix)
            self.assertIn((mode, "empty", 60), matrix)
        self.assertIn((20, "nurples", None), matrix)
        self.assertIn((20, "nurples", 30), matrix)
        self.assertIn((20, "nurples", 60), matrix)
        self.assertEqual(len(matrix), 9)

    def test_startup_owns_mode_before_fixture(self):
        case = {"mode": 20, "kind": "nurples", "workdir": "/test/nurples"}
        startup = performance.build_startup(
            case, "/extender/fixtures/nur.bin",
            "/agents/extender/results/nur.raw", 0x123456, 1448).decode("ascii")
        self.assertLess(startup.index("EMOS KEYINPUT extender"),
                        startup.index("EMOS EXCOM"))
        self.assertLess(startup.index("EMOS EXCOM"), startup.index("VDU 22 20"))
        self.assertLess(startup.index("VDU 22 20"), startup.index("LOAD "))
        self.assertNotIn("KEYINPUT mainboard", startup)
        self.assertTrue(startup.endswith("EMOS sdserve --fast /\r\n"))

    def test_empty_result_is_supplied_as_run_argument(self):
        case = {"mode": 8, "kind": "empty", "workdir": None}
        startup = performance.build_startup(
            case, "/extender/fixtures/empty.bin",
            "/agents/extender/results/empty.csv").decode("ascii")
        self.assertIn("RUN . /agents/extender/results/empty.csv\r\n", startup)

    def test_nurples_builder_suppresses_fixture_mode_switches(self):
        source = (ROOT / "tests/performance/builders/nurples.py").read_text()
        self.assertIn("Startup/CLI owns video mode", source)
        self.assertIn("Startup owns mode20", source)
        self.assertIn("'ntiming0.bin' if args.no_markers", source)

    def test_video_session_supports_nonretained_measurement(self):
        source = (ROOT / "qualification/video.py").read_text()
        self.assertIn("def next_frame(self):", source)
        self.assertIn("return decode_evf(raw)", source)

    def test_video_summary_filters_geometry_and_uses_receive_clock(self):
        records = [
            {"received_monotonic": 1.0, "width": 320, "height": 240,
             "sequence": 7},
            {"received_monotonic": 2.0, "width": 512, "height": 384,
             "sequence": 10},
            {"received_monotonic": 2.5, "width": 512, "height": 384,
             "sequence": 13},
            {"received_monotonic": 4.0, "width": 512, "height": 384,
             "sequence": 20},
        ]
        summary = performance.summarize_video(
            records, 1.5, 3.0, (512, 384), 30)
        self.assertEqual(summary["matching_frames"], 2)
        self.assertEqual(summary["request_cap_hz"], 30)
        self.assertEqual(summary["delivered_frames_per_second"], 2.0)
        self.assertEqual(summary["source_sequence_per_second"], 6.0)


if __name__ == "__main__":
    unittest.main()
