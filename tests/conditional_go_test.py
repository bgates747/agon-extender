"""Actual host gate checks; temporary files and fake callbacks, no target/service."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from conditional_go import (accepted_delivery, require_fields, validate_window,
                            wait_once)


class GateTests(unittest.TestCase):
    def setUp(self):
        silent = patch('builtins.print'); silent.start(); self.addCleanup(silent.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.marker, self.output = self.root/'go.json', self.root/'out'
        self.now, self.calls = 0, []

    def clock(self):
        return self.now

    def pause(self, seconds):
        self.now += seconds
        if not self.marker.exists():
            self.marker.write_text('{"request":"selected"}')

    def validate(self, marker):
        require_fields(marker, {'request': 'selected'}, 'Selection')
        return {'accepted_request': marker['request']}

    def invoke(self, marker):
        self.assertTrue((self.output/'dispatch.json').exists())
        self.calls.append(marker)
        return {'exit': 0}

    def run_gate(self, **kw):
        defaults = dict(validate=self.validate, invoke=self.invoke,
                        clock=self.clock, pause=self.pause)
        defaults.update(kw)
        return wait_once(self.marker, self.output, 1, **defaults)

    def test_delayed_valid_marker_dispatches_once_after_claim(self):
        self.assertEqual(self.run_gate(), {'exit': 0})
        self.assertEqual(len(self.calls), 1)
        self.assertTrue((self.output/'armed.json').exists())
        self.assertTrue((self.output/'result.json').exists())

    def test_marker_before_arm_never_dispatches(self):
        self.marker.write_text('{}')
        with self.assertRaises(ValueError): self.run_gate()
        self.assertEqual(self.calls, [])

    def test_wrong_request_never_dispatches(self):
        def wrong(seconds):
            self.now += seconds
            self.marker.write_text('{"request":"other"}')
        with self.assertRaises(ValueError): self.run_gate(pause=wrong)
        self.assertEqual(self.calls, [])
        self.assertFalse(json.loads((self.output/'failure.json').read_text())['invocation_attempted'])

    def test_timeout_is_terminal_and_output_cannot_be_rearmed(self):
        def no_marker(seconds): self.now += seconds
        with self.assertRaises(TimeoutError): self.run_gate(pause=no_marker)
        with self.assertRaises(FileExistsError): self.run_gate()
        self.assertEqual(self.calls, [])

    def test_cancellation_never_dispatches(self):
        with self.assertRaises(InterruptedError): self.run_gate(cancelled=lambda: True)
        self.assertEqual(self.calls, [])

    def test_cancellation_after_validation_never_dispatches(self):
        cancel = [False]
        def validator(marker):
            cancel[0] = True
            return self.validate(marker)
        with self.assertRaises(InterruptedError):
            self.run_gate(validate=validator, cancelled=lambda: cancel[0])
        self.assertEqual(self.calls, [])

    def test_slow_validation_cannot_extend_window(self):
        def slow(marker):
            self.now += 2
            return self.validate(marker)
        with self.assertRaises(TimeoutError): self.run_gate(validate=slow)
        self.assertEqual(self.calls, [])
        self.assertFalse((self.output/'dispatch.json').exists())

    def test_invocation_failure_is_not_retried(self):
        def fail(marker):
            self.invoke(marker)
            raise RuntimeError('uncertain target')
        with self.assertRaises(RuntimeError): self.run_gate(invoke=fail)
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(json.loads((self.output/'failure.json').read_text())['invocation_attempted'])
        with self.assertRaises(ValueError): self.run_gate(invoke=fail)
        self.assertEqual(len(self.calls), 1)

    def test_oversized_marker_never_dispatches(self):
        def oversized(seconds):
            self.now += seconds
            self.marker.write_text(' '*8193)
        with self.assertRaises(ValueError): self.run_gate(pause=oversized)
        self.assertEqual(self.calls, [])

    def test_invalid_window_is_refused_before_arm(self):
        for duration in (0, 181, float('nan')):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                wait_once(self.marker, self.output, duration, self.validate, self.invoke)
        self.assertFalse(self.output.exists())


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.ready = dict(epoch=1000, monotonic_ns=100_000_000_000,
                          bridge_pid=10, controller_pid=11,
                          registration_deadline_monotonic_ns=180_000_000_000)
        self.marker = dict(ready_epoch=1000, ready_monotonic_ns=100_000_000_000,
                           bridge_pid=10, controller_pid=11,
                           registration_deadline_monotonic_ns=180_000_000_000,
                           issued_epoch=1001, issued_monotonic_ns=101_000_000_000)

    def check(self, marker=None, ready=None, **kw):
        defaults = dict(epoch=1002, monotonic_ns=102_000_000_000)
        defaults.update(kw)
        validate_window(marker or self.marker, ready or self.ready, **defaults)

    def test_exact_original_deadline_accepts_fresh_marker(self): self.check()

    def test_restamped_ready_or_recomputed_deadline_is_refused(self):
        for key in ('ready_epoch', 'ready_monotonic_ns',
                    'registration_deadline_monotonic_ns', 'bridge_pid', 'controller_pid'):
            marker = copy.deepcopy(self.marker);marker[key] += 1
            with self.subTest(key=key), self.assertRaises(ValueError): self.check(marker)

    def test_expired_or_insufficient_original_budget_is_refused(self):
        for now in (166_000_000_000, 181_000_000_000):
            marker = dict(self.marker, issued_monotonic_ns=now-1_000_000_000,
                          issued_epoch=1065)
            with self.subTest(now=now), self.assertRaises(ValueError):
                self.check(marker, monotonic_ns=now, epoch=1066)

    def test_stale_future_or_inconsistent_issue_time_is_refused(self):
        for key, value in [('issued_epoch', 990), ('issued_epoch', 1003),
                           ('issued_monotonic_ns', 90_000_000_000),
                           ('issued_monotonic_ns', 103_000_000_000)]:
            marker = copy.deepcopy(self.marker);marker[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError): self.check(marker)

    def test_accepted_canonical_receipt_requires_exact_bytes_and_endpoints(self):
        message = b'mail waiting\n'
        receipt = dict(phase='accepted', source='sender', target='owner',
            delivery_id='selected', transport='pi-unix-app-server', method='turn/steer',
            read_confirmed=False, message_sha256=hashlib.sha256(message).hexdigest())
        args = dict(source='sender', target='owner', delivery_id='selected')
        accepted_delivery(receipt, message, **args)
        for key, value in [('phase', 'queued'), ('target', 'other'),
                           ('delivery_id', 'other'), ('method', 'turn/queue')]:
            wrong = dict(receipt, **{key: value})
            with self.subTest(key=key), self.assertRaises(ValueError):
                accepted_delivery(wrong, message, **args)
        with self.assertRaises(ValueError): accepted_delivery(receipt, message[:-1], **args)


if __name__ == '__main__': unittest.main()
