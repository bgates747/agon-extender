import random
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from controller_clock import bounds, map_interval


class ClockTests(unittest.TestCase):
    def test_asymmetry_drift_and_long_uptime_remain_bounded(self):
        rng = random.Random(123)
        origin = 50_000_000_000_000_000
        offset = 123_456_789
        for drift in (-100, 0, 35, 125):
            rate = 1+drift/1e6
            def clock(a):
                return origin+offset+round((a-origin)*rate)
            rows = []
            for second in range(20):
                a1 = origin+second*1_000_000_000
                forward = rng.randrange(100_000, 2_000_000)
                backward = rng.randrange(3_000_000, 7_000_000)
                process = 70_000
                rows.append([a1, clock(a1+forward), clock(a1+forward+process),
                             a1+forward+process+backward])
            model = bounds(rows, error_a_ns=1, error_b_ns=1, max_drift_ppm=500)
            self.assertLessEqual(model['rate_min'], rate)
            self.assertGreaterEqual(model['rate_max'], rate)
            for second in (-2, 0, 10, 25):
                a = origin+second*1_000_000_000
                low, high = map_interval(model, a)
                self.assertLessEqual(low, clock(a))
                self.assertGreaterEqual(high, clock(a))
            # Asymmetric paths must leave uncertainty, despite exact timers.
            self.assertGreater(model['offset_width_ns'], 100_000)

    def test_exact_zero_path_case(self):
        rows = [[0, 1000, 1010, 10], [1_000_000, 1_001_000, 1_001_010, 1_000_010]]
        model = bounds(rows, error_a_ns=0, error_b_ns=0, max_drift_ppm=100)
        self.assertEqual(model['rate_min'], 1)
        self.assertEqual(model['rate_max'], 1)
        self.assertEqual(map_interval(model, 12345), (13345, 13345))

    def test_inconsistent_or_wrapped_clocks_rejected(self):
        for rows in ([], [[10, 30, 20, 40]], [[20, 30, 40, 10]],
                     [[0, 0, 100, 1]], [[0, 1.1, 2, 3]], [[0, 1, 2]]):
            with self.assertRaises(ValueError):
                bounds(rows, error_a_ns=0, error_b_ns=0, max_drift_ppm=100)

    def test_quantized_counter_errors_are_explicit(self):
        rows = [[0, 16_000, 16_000, 1000]]
        exact = bounds(rows, error_a_ns=0, error_b_ns=0, max_drift_ppm=0)
        coarse = bounds(rows, error_a_ns=0, error_b_ns=16_667_000, max_drift_ppm=0)
        self.assertGreater(coarse['offset_width_ns'], exact['offset_width_ns']+30_000_000)


if __name__ == '__main__':
    unittest.main()
