"""Host controller semantics with synthetic evdev reports; no physical devices."""
import errno
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from controller_input import (Axis, AxisStats, State, Observer, Device, Recorder,
                              validate_capture, discover, EV_ABS, EV_KEY, EV_SYN,
                              SYN_DROPPED, SYN_REPORT)


def make_state(pressed=()):
    axes = {k: Axis(-32768, 32767) for k in (0, 1, 3, 4)}
    axes.update({k: Axis(0, 255) for k in (2, 5)})
    axes.update({k: Axis(-1, 1) for k in (16, 17)})
    values = {k: 0 for k in axes}
    return State(axes, values, pressed)


class FakeDevice:
    def __init__(self):
        self.state = make_state()
        self.axes = self.state.axes
        self.name = 'Synthetic F310'
        self.identity = dict(name=self.name, vendor=0x046d, product=0xc21d, version=1, path='synthetic')
        self.queue = []
        self.closed = False
        self.query_values = dict(self.state.values)
        self.query_pressed = set()

    def events(self):
        events, self.queue = self.queue, []
        for i, (kind, code, value) in enumerate(events):
            yield dict(kernel_ns=1000+i, type=kind, code=code, value=value)

    def query(self):
        return self.query_values, self.query_pressed

    def close(self):
        self.closed = True


class ControllerTests(unittest.TestCase):
    def test_byte_preview_endpoints_and_no_deadzone(self):
        a = Axis(-32768, 32767, flat=128)
        self.assertEqual([a.byte(v) for v in (-32768, 0, 32767)], [0, 128, 255])
        self.assertGreater(a.unit(64), 0)  # Kernel flat metadata isn't applied twice.
        self.assertEqual(a.byte(99999), 255)
        t = Axis(0, 255)
        self.assertEqual([t.byte(v, unipolar=True) for v in (0, 128, 255)], [0, 128, 255])

    def test_coherent_report_and_independent_triggers(self):
        s = make_state()
        s.feed(EV_ABS, 0, 9000, 1)
        s.feed(EV_ABS, 2, 230, 1)
        self.assertEqual((s.values[0], s.values[2]), (0, 0))
        self.assertEqual(s.feed(EV_SYN, SYN_REPORT, 0, 2), 'frame')
        self.assertEqual((s.values[0], s.values[2], s.values[5]), (9000, 230, 0))

    def test_tap_between_ui_redraws_and_repeats(self):
        s = make_state()
        for value in (1, 2, 1, 0):
            s.feed(EV_KEY, 304, value, 1)
        s.feed(EV_SYN, SYN_REPORT, 0, 2)
        self.assertNotIn(304, s.pressed)
        self.assertEqual((s.presses[304], s.releases[304]), (1, 1))
        self.assertEqual([v[2] for v in s.history], [True, False])

    def test_initial_held_button_is_not_a_new_press(self):
        s = make_state({304})
        self.assertIn(304, s.pressed)
        self.assertEqual(s.presses[304], 0)

    def test_dropped_report_discards_partial_changes(self):
        s = make_state()
        s.feed(EV_ABS, 0, 1000, 1)
        s.feed(EV_KEY, 304, 1, 1)
        self.assertEqual(s.feed(EV_SYN, SYN_DROPPED, 0, 2), 'gap')
        s.feed(EV_KEY, 305, 1, 3)
        self.assertEqual(s.feed(EV_SYN, SYN_REPORT, 0, 4), 'resync')
        values = dict(s.values, **{})
        values[0] = 9000
        s.resync(values, {305})
        self.assertEqual(s.pressed, {305})
        self.assertEqual((s.presses[304], s.presses[305]), (0, 0))
        self.assertIsNone(s.stats[0].smallest_step)
        self.assertEqual(s.dropped, 1)

    def test_observed_steps_and_range(self):
        s = AxisStats()
        for value in (128, 128, 384, 896, 640):
            s.observe(value)
        self.assertEqual(s.summary(), dict(min=128,max=896,distinct=4,
                                          smallest_observed_step=256,step_gcd=256,changes=3))

    def test_rest_is_finite_and_never_changes_native_values(self):
        s = make_state()
        s.values[0] = 128
        s.values[1] = -129
        s.start_rest(0)
        self.assertIsNone(s.sample_rest(500_000_000))
        r = s.sample_rest(2_000_000_000)
        self.assertTrue(r['accepted'])
        self.assertEqual(s.centres[1], -129)
        self.assertEqual(s.axes[1].byte(s.values[1], s.centres[1]), 128)
        self.assertEqual(s.values[1], -129)
        self.assertIsNone(s.sample_rest(3_000_000_000))

    def test_rest_end_stop_rejected_and_gap_cancels(self):
        s = make_state()
        s.values[0] = 32767
        s.start_rest(0)
        self.assertFalse(s.sample_rest(2_000_000_000)['accepted'])
        self.assertFalse(s.centres)
        s.start_rest(3_000_000_000)
        s.feed(EV_SYN, SYN_DROPPED, 0, 3_000_000_001)
        self.assertIsNone(s.rest)

    def test_disconnect_clears_and_reconnect_starts_new_session(self):
        a, b = FakeDevice(), FakeDevice()
        o = Observer()
        with patch('controller_input.discover', side_effect=[(a,''),(b,'')]):
            o.poll()
            first = o.session
            a.state.pressed.add(304)
            with patch.object(a, 'events', side_effect=OSError(errno.ENODEV, 'gone')):
                o.poll()
            self.assertIsNone(o.state)
            self.assertTrue(a.closed)
            o.next_scan = 0
            o.poll()
            self.assertNotEqual(o.session, first)
            self.assertFalse(o.state.pressed)
            self.assertEqual(o.sessions, 2)
        o.close()

    def test_ambiguous_controllers_require_selection_and_close_both(self):
        a,b = FakeDevice(),FakeDevice()
        with patch('controller_input.glob.glob', side_effect=[['a','b'],[]]), patch('controller_input.Device', side_effect=[a,b]):
            device, reason = discover()
        self.assertIsNone(device)
        self.assertIn('Multiple', reason)
        self.assertTrue(a.closed and b.closed)

    def test_record_roundtrip_short_tap_gap_and_reconnect(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'capture.jsonl'
            a,b = FakeDevice(),FakeDevice()
            o = Observer()
            o.start_recording(path)
            with patch('controller_input.discover', side_effect=[(a,''),(b,'')]):
                o.poll()
                a.queue = [(EV_KEY,304,1),(EV_KEY,304,0),(EV_ABS,2,255),(EV_SYN,0,0)]
                o.poll()
                a.query_values[5] = 200
                a.queue = [(EV_SYN,SYN_DROPPED,0),(EV_KEY,304,1),(EV_SYN,0,0),
                           (EV_ABS,0,500),(EV_SYN,0,0)]
                o.poll()
                with patch.object(a,'events',side_effect=OSError(errno.ENODEV,'gone')):
                    o.poll()
                o.next_scan = 0
                o.poll()
                b.queue = [(EV_ABS,0,-100),(EV_SYN,0,0)]
                o.poll()
            o.close()
            result = validate_capture(path)
            self.assertEqual((result['sessions'],result['frames']), (2,3))
            self.assertTrue(result['complete'])
            rows = [json.loads(x) for x in path.read_text().splitlines()]
            next(x for x in rows if x['kind']=='frame')['state']['axes']['0'] = 123
            path.write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
            with self.assertRaisesRegex(ValueError,'disagrees'):
                validate_capture(path)

    def test_record_start_mid_report_preserves_pending_state(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'capture.jsonl'
            o,a = Observer(),FakeDevice()
            with patch('controller_input.discover', return_value=(a,'')):
                o.poll()
            a.state.feed(EV_ABS,0,800,1)
            a.state.feed(EV_KEY,304,1,1)
            o.start_recording(path)
            a.queue = [(EV_SYN,0,0)]
            o.poll()
            o.close()
            self.assertEqual(validate_capture(path)['frames'],1)

    def test_record_create_new_and_incomplete_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'capture.jsonl'
            r = Recorder(path)
            r.handle.flush()
            with self.assertRaises(FileExistsError):
                Recorder(path)
            with self.assertRaisesRegex(ValueError,'Incomplete'):
                validate_capture(path)
            r.close()
            self.assertTrue(validate_capture(path)['complete'])

    def test_wrong_device_closes_fd(self):
        with patch('controller_input.os.open',return_value=123), patch('controller_input.os.close') as close:
            with patch('controller_input.read_ioctl',side_effect=[bytes(8),b'wrong\0']):
                with self.assertRaisesRegex(OSError,'XInput'):
                    Device('fake')
            close.assert_called_once_with(123)


if __name__ == '__main__':
    unittest.main()
