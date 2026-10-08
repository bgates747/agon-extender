"""Offline ranking contract: malformed EDID, timing limits and evidence identity."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import hdmi_candidates as hc


def checksum(block):
    block[127] = (-sum(block[:127])) & 255
    return bytes(block)


def edid(revision=3, offsets=0):
    b = bytearray(128)
    b[:8] = bytes.fromhex('00ffffffffffff00')
    b[18:20] = bytes((1, revision))
    b[35] = 32  # established640x480@60
    b[38:54] = b'\x01\x01'*8
    # Standard1080p60 DTD:148.5MHz,2200x1125 totals. No unique-device data.
    b[54:72] = bytes.fromhex('023a801871382d40582c450000000000001e')
    b[72:90] = bytes.fromhex('000000fd0030641e5518000a202020202020')
    b[76] = offsets
    b[90:108] = b'\0\0\0\xfc\0' + b'Synthetic\n   '
    return checksum(b)


class CandidateTest(unittest.TestCase):
    def setUp(self):
        self.monitor = hc.parse_edid(edid())
        self.observations = json.loads(hc.DEFAULT_OBSERVATIONS.read_text())
        # Synthetic EDID deliberately owns these fixture observations only.
        self.observations['monitor_edid_sha256'] = self.monitor['sha256']
        self.base = hc.normalized(self.observations['observations'][0]['timing'])

    def errors(self, t):
        return hc.check(t, self.monitor, (320, 240), 60, .15, 31)[0]

    def test_known_descriptor_and_no_unique_identifiers(self):
        self.assertEqual(self.monitor['model'], 'Synthetic')
        self.assertEqual(self.monitor['ranges'], dict(v_min_hz=48, v_max_hz=100,
            h_min_khz=30, h_max_khz=85, pixel_max_hz=240000000))
        self.assertEqual(self.monitor['detailed_timings'][0]['refresh_hz'], 60)
        self.assertIn([640, 480, 60], self.monitor['geometry_hints'])
        self.assertNotIn('serial', self.monitor)

    def test_corrupt_truncated_and_malformed_cta_rejected(self):
        corrupt = bytearray(edid()); corrupt[50] ^= 1
        for bad in (bytes(corrupt), edid()[:-1], b'\0'*128):
            with self.assertRaises(ValueError):
                hc.parse_edid(bad)
        base = bytearray(edid()); base[126] = 1
        with self.assertRaises(ValueError):
            hc.parse_edid(checksum(base))
        extension = bytearray(128); extension[:5] = bytes((2, 3, 5, 0, 0x42))
        with self.assertRaisesRegex(ValueError, 'crosses'):
            hc.parse_edid(checksum(base)+checksum(extension))

    def test_cta_ids_retained_and_unhandled_explicit(self):
        base = bytearray(edid()); base[126] = 1
        extension = bytearray(128); extension[:8] = bytes((2, 3, 8, 0, 0x43, 0x90, 1, 193))
        m = hc.parse_edid(checksum(base)+checksum(extension))
        self.assertEqual(m['cta_vics'], [16, 1, 193])
        self.assertTrue(any('not expanded' in w for w in m['warnings']))

    def test_v14_range_offsets_and_missing_range(self):
        r = hc.parse_edid(edid(4, 15))['ranges']
        self.assertEqual((r['v_min_hz'], r['v_max_hz'], r['h_min_khz'], r['h_max_khz']),
                         (303, 355, 285, 340))
        b = bytearray(edid()); b[72:90] = bytes(18)
        m = hc.parse_edid(checksum(b))
        self.assertIsNone(m['ranges'])
        self.assertTrue(any('unknown' in w for w in m['warnings']))

    def test_unspecified_pixel_clock_and_cvt_refinement(self):
        for value in (0, 255):
            b = bytearray(edid()); b[81] = value
            self.assertIsNone(hc.parse_edid(checksum(b))['ranges']['pixel_max_hz'])
        b = bytearray(edid(4)); b[82] = 4; b[84] = 8
        self.assertEqual(hc.parse_edid(checksum(b))['ranges']['pixel_max_hz'], 239500000)

    def test_timing_arithmetic_and_transport_constraints(self):
        self.assertEqual(self.errors(self.base), [])
        for changes, expected in [
            ({'hs': 256, 'htotal': 1248}, '8-bit'),
            ({'hfp': 197, 'htotal': 1105}, 'rounding'),
            ({'htotal': 4096}, '12-bit'),
            ({'vbp': 1024}, '10-bit'),
            ({'htotal': 1000}, 'totals'),
            ({'lanes': 1}, 'packet'),
            ({'divider': 0}, 'positive')]:
            with self.subTest(changes=changes):
                self.assertTrue(any(expected in e for e in self.errors({**self.base, **changes})))

    def test_independent_sizes_offsets_and_rates(self):
        t = next(hc.candidates([288]))
        errors, m = hc.check(t, self.monitor, (320, 240), 60, .15, 31)
        self.assertEqual(errors, [])
        self.assertEqual((t['width'], t['height']), (512, 288))
        self.assertEqual(m['rgb888_bytes'], 442368)
        self.assertEqual(m['source_offset'], [96, 24])
        self.assertAlmostEqual(m['refresh_hz'], 60.06944027295553)
        # Rounding480 lines produces852, never the measured848-wide control.
        self.assertEqual(next(hc.candidates([480]))['width'], 852)

    def test_monitor_limits_are_filters_not_pass_evidence(self):
        m = deepcopy(self.monitor); m['ranges']['h_max_khz'] = 30
        self.assertTrue(any('horizontal' in e for e in
            hc.check(self.base, m, (320, 240), 60, .15, 0)[0]))
        report = hc.rank(self.monitor, self.observations, [256, 288, 384, 400, 480])
        by_size = {(r['timing']['width'], r['timing']['height']): r for r in report['ranked']}
        self.assertEqual(by_size[(684, 384)]['tier'], 0)
        self.assertEqual(by_size[(848, 480)]['tier'], 0)
        self.assertNotEqual(by_size[(852, 480)]['tier'], 0)
        self.assertEqual(by_size[(712, 400)]['tier'], 1)
        self.assertEqual(by_size[(512, 288)]['tier'], 2)
        self.assertTrue(any(r['tier'] == 4 for r in report['ranked']))
        self.assertTrue(any('cadence' in ' '.join(r['reasons']) for r in report['excluded']))

    def test_wrong_monitor_never_inherits_visual_pass(self):
        wrong = {**self.observations, 'monitor_edid_sha256': 'different'}
        r = hc.rank(self.monitor, wrong, [240, 384, 480])
        self.assertTrue(all(c['tier'] == 2 for c in r['ranked']))
        self.assertTrue(any('ignored' in w for w in r['warnings']))

    def test_porch_change_is_not_exact_pass(self):
        obs = deepcopy(self.observations)
        obs['observations'][0]['timing']['hfp'] -= 4
        obs['observations'][0]['timing']['hbp'] += 4
        report = hc.rank(self.monitor, obs, [384])
        original = next(r for r in report['ranked'] if hc.timing_key(r['timing']) == hc.timing_key(self.base))
        self.assertNotEqual(original['tier'], 0)


if __name__ == '__main__':
    unittest.main()
