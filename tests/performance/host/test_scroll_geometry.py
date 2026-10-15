"""Check circular wrap against an independent pixel oracle, including margins."""
import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np

PATH = Path(__file__).resolve().parents[2] / 'fixtures/scroll/geometry.py'
SPEC = importlib.util.spec_from_file_location('scroll_geometry', PATH)
g = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = g
SPEC.loader.exec_module(g)


class Geometry(unittest.TestCase):
    def test_initial_regions(self):
        rows = {name: rect for name, _, _, rect in g.cases(320, 240, 32)}
        self.assertEqual(rows['partial-up'], g.Rect(32, 0, 256, 240))
        self.assertEqual(rows['partial-left'], g.Rect(0, 32, 320, 176))
        self.assertEqual(rows['full-up'], g.Rect(0, 0, 320, 240))

    def test_wrap_pixels(self):
        # Every source pixel is distinct; a full phase cycle and stationary
        # surroundings are checked on square and non-square sample grids.
        for width, height, margin in [(11, 9, 2), (23, 7, 1), (320, 240, 32)]:
            original = np.arange(width*height).reshape(height, width)
            for name, direction, partial, r in g.cases(width, height, margin):
                with self.subTest(size=(width, height), case=name):
                    screen = original.copy()
                    axis = 0 if direction in ('up', 'down') else 1
                    delta = -1 if direction in ('up', 'left') else 1
                    period = r.height if axis == 0 else r.width
                    for step in range(period+1):
                        area = screen[r.y:r.bottom+1, r.x:r.right+1]
                        # Actual scroll: shift with a deliberately wrong fill.
                        area[:] = np.roll(area, delta, axis=axis)
                        strip, (dx, dy) = g.wrap(r, direction, step)
                        area_strip = screen[strip.y:strip.bottom+1, strip.x:strip.right+1]
                        area_strip[:] = -1
                        area_strip[:] = original[strip.y-dy:strip.bottom+1-dy,
                                                 strip.x-dx:strip.right+1-dx]
                        expected = original.copy()
                        expected[r.y:r.bottom+1, r.x:r.right+1] = np.roll(
                            original[r.y:r.bottom+1, r.x:r.right+1],
                            delta*(step+1), axis=axis)
                        np.testing.assert_array_equal(screen, expected)

    def test_wire_extent_and_single_pixel(self):
        for _, direction, partial, r in g.cases(320, 240, 32):
            command = g.update(r, direction, partial, 0)
            self.assertEqual(command[9:14], bytes([23, 7, 2 if partial else 1,
                                                  g.DIRECTIONS[direction], 1]))
            self.assertEqual(command[-6:-4], bytes([25, 0xED]))

    def test_reject_invalid_geometry(self):
        for args in [(320, 240, 120), (0, 240, 32), (320, 240, -1)]:
            with self.assertRaises(ValueError):
                g.cases(*args)


if __name__ == '__main__':
    unittest.main()
