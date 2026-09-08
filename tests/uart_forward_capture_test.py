"""Reject misleading UART bench logs without accessing a serial device."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "uart_capture", ROOT / "docs/tasks/PORT-009/capture_on_pi.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
BUILD = "uart-forward-probe-r01-b2026-09-08-00-00-00Z"
PASS = ("UART FORWARD PASS received=18 expected=18 "
        "hex=454D4F53205541525431202D3E2050340D0A reason=none build="
        + BUILD + "\r\n").encode()
BANNER = ("UART FORWARD RECEIVER " + BUILD + " (candidate)\r\n").encode()


class CaptureVerdictTests(unittest.TestCase):
    def test_exact_repeated_pass_with_console_formatting(self):
        log = BANNER + b"\x1b[0;32mI (1200) uart-forward: " + PASS + b"\x1b[0m" + PASS
        self.assertTrue(capture.verdict(log, BUILD)[0])

    def test_no_pass_and_truncated_pass(self):
        for log in (b"", BANNER, PASS[:80]):
            with self.subTest(log=log):
                self.assertFalse(capture.verdict(log, BUILD)[0])

    def test_failure_before_or_after_success_is_sticky(self):
        for failure in (b"UART FORWARD FAIL received=19\n", b"UART event type=3\n"):
            for log in (failure + PASS, PASS + failure):
                with self.subTest(log=log):
                    self.assertFalse(capture.verdict(log, BUILD)[0])

    def test_wrong_build_count_or_bytes(self):
        for bad in (PASS.replace(b"received=18", b"received=17"),
                    PASS.replace(b"expected=18", b"expected=19"),
                    PASS.replace(b"454D", b"004D"),
                    PASS.replace(b"r01-b", b"r02-b")):
            with self.subTest(log=bad):
                self.assertFalse(capture.verdict(PASS + bad, BUILD)[0])

    def test_reset_after_pass_even_when_initial_banner_was_missed(self):
        for log in (PASS + BANNER, BANNER + PASS + BANNER,
                    BANNER + BANNER + PASS):
            with self.subTest(log=log):
                self.assertFalse(capture.verdict(log, BUILD)[0])

    def test_malformed_pass_after_valid_pass(self):
        self.assertFalse(capture.verdict(PASS + b"UART FORWARD PASS broken\n", BUILD)[0])


if __name__ == "__main__":
    unittest.main()
