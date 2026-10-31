"""Actuator failures must not select another device or leave reset asserted."""
from contextlib import contextmanager
import importlib.util
from pathlib import Path
import struct
import sys
import termios
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("reset_agon_usb", ROOT / "scripts/reset_agon_usb.py")
RESET = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RESET)


class UsbResetTests(unittest.TestCase):
    def test_wrong_adapter_is_never_opened(self):
        config = {"stable_port": "/dev/serial/by-id/expected", "udev": {
            "ID_VENDOR_ID": "1234", "ID_MODEL_ID": "5678", "ID_PATH": "required-path"}}
        with (mock.patch.object(RESET.Path, "resolve", return_value=Path("/dev/ttyUSB99")),
              mock.patch.object(RESET.subprocess, "check_output", return_value="ID_VENDOR_ID=wrong\n"),
              mock.patch.object(RESET, "open_passive_serial") as opened):
            with self.assertRaisesRegex(ValueError, "identity differs"):
                RESET.pulse(config)
        opened.assert_not_called()

    def exercise(self, failure=None):
        state = 0
        transitions = []

        def ioctl(_fd, action, payload):
            nonlocal state
            if action == termios.TIOCMGET:
                return struct.pack("I", state)
            bits = struct.unpack("I", payload)[0]
            if action == termios.TIOCMBIS:
                state |= bits
            elif action == termios.TIOCMBIC:
                state &= ~bits
            transitions.append(state)

        @contextmanager
        def opened(*_args, **_kwargs):
            yield mock.Mock(fd=42)

        with (mock.patch.object(RESET, "identity", return_value=Path("/dev/selected")),
              mock.patch.object(RESET, "open_passive_serial", opened),
              mock.patch.object(RESET.fcntl, "ioctl", side_effect=ioctl),
              mock.patch.object(RESET.time, "sleep", side_effect=failure) as sleep):
            if failure is None:
                RESET.pulse({})
            else:
                with self.assertRaises(type(failure)):
                    RESET.pulse({})
            sleep.assert_called_once_with(0.1)
        self.assertEqual(transitions, [termios.TIOCM_RTS, 0])
        self.assertEqual(state, 0)

    def test_success_releases_both_controls_together(self):
        self.exercise()

    def test_interrupted_pulse_releases_both_controls(self):
        self.exercise(SystemExit(143))


if __name__ == "__main__":
    unittest.main()
