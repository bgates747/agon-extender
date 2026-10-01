#!/usr/bin/env python3
"""Structural checks for the installed-hardware performance runner."""

from __future__ import annotations

import importlib.util
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock
from urllib.error import HTTPError


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
    def test_missing_optional_video_timing_endpoint_is_not_fatal(self):
        missing = HTTPError("http://device/diagnostics/video-timing", 404,
                            "Not Found", {}, None)
        with mock.patch.object(performance, "read_json", side_effect=missing):
            self.assertEqual(
                performance.video_timing_capability("http://device"),
                (False, None))

    def test_other_video_timing_http_errors_remain_fatal(self):
        failed = HTTPError("http://device/diagnostics/video-timing", 500,
                           "Failure", {}, None)
        with mock.patch.object(performance, "read_json", side_effect=failed):
            with self.assertRaises(HTTPError):
                performance.video_timing_capability("http://device")

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

    def test_white_boundary_selects_first_post_measurement_marker(self):
        white = hashlib.sha256(bytes([63]) * 4).hexdigest()
        records = [
            {"received_monotonic": 1.0, "width": 2, "height": 2,
             "format": 2, "sha256": "not-white"},
            {"received_monotonic": 31.0, "width": 2, "height": 2,
             "format": 2, "sha256": white},
            {"received_monotonic": 32.0, "width": 2, "height": 2,
             "format": 2, "sha256": white},
        ]
        self.assertEqual(performance.white_boundary(records, (2, 2), 30.0), 31.0)

    def test_compact_pacing_parser_retains_variable_wall_time_updates(self):
        frames = 450
        header = b"GTPRT2!!" + struct.pack("<H", frames) + (3600).to_bytes(3, "little")
        row = struct.pack("<HH", 100, 200) + (2).to_bytes(3, "little")
        with tempfile.TemporaryDirectory() as folder:
            summary = performance.parse_pacing(
                header + row * frames, Path(folder) / "combined.csv")
        self.assertEqual(summary["updates"], frames)
        self.assertEqual(summary["updates_per_second"], 15.0)

    def test_nurples_parser_uses_retained_count_not_capacity(self):
        def u24(value):
            return value.to_bytes(3, "little")

        row1 = b"".join(map(u24, (100, 200, 100, 1900)))
        row2 = b"".join(map(u24, (100, 200, 1900, 3700)))
        raw = (b"GTPRN2!!" + u24(2) + row1 + row2 +
               bytes((performance.PERFORMANCE_CAPACITY - 2) * 12))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            symbols = root / "nurples.symbols"
            symbols.write_text(
                f"gt_data $40000\n"
                f"gt_data_end ${0x40000 + len(raw):X}\n")
            summary = performance.parse_nurples(
                raw, symbols, root / "combined.csv")
        self.assertEqual(summary["updates"], 2)
        self.assertEqual(summary["mos_run_ticks"], 3600)

    def test_compact_empty_is_explicit_build_option(self):
        source = (ROOT / "tests/performance/builders/controls.py").read_text()
        self.assertIn("--compact-empty", source)
        self.assertIn("gt::save_pacing(result)", source)


if __name__ == "__main__":
    unittest.main()
