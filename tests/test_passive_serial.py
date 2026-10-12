"""Model Linux/CH341 controls around the actual pyserial open sequence.

No physical serial port is opened. The original sequence is the regression
control: it enters the reset-active state before arriving at False/False.
"""
import errno
import struct
import sys
import termios
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import passive_serial
import serial


class PassiveSerialTests(unittest.TestCase):
    def open_sequence(self, joined, unsupported=False):
        controls = 0
        states = []

        def os_open(*_):
            nonlocal controls
            # tty_port_block_til_ready: the Linux nonblocking-open path
            # asserts DTR and RTS together through ch341_dtr_rts.
            controls = termios.TIOCM_DTR | termios.TIOCM_RTS
            states.append(controls)
            return 101

        def ioctl(fd, operation, data):
            nonlocal controls
            if unsupported:
                raise OSError(errno.ENOTTY, "unsupported")
            value = struct.unpack("I", data)[0]
            self.assertEqual(operation, termios.TIOCMBIC)
            controls &= ~value
            states.append(controls)

        with patch("os.open", side_effect=os_open), \
             patch("os.close"), patch("os.pipe", side_effect=[(102, 103), (104, 105)]), \
             patch("fcntl.fcntl"), patch("fcntl.ioctl", side_effect=ioctl), \
             patch.object(serial.Serial, "_reconfigure_port"), \
             patch.object(serial.Serial, "_reset_input_buffer"):
            if joined:
                port = passive_serial.open_passive_serial("mock-port")
            else:
                port = serial.Serial(port=None)
                port.dtr = False
                port.rts = False
                port.port = "mock-port"
                port.open()
            port.close()
        return states

    def test_old_opener_reproduces_reset_active_state(self):
        states = self.open_sequence(False)
        self.assertIn(termios.TIOCM_RTS, states)

    def test_joined_opener_never_has_differential_controls(self):
        self.assertEqual(self.open_sequence(True),
                         [termios.TIOCM_DTR | termios.TIOCM_RTS, 0, 0])

    def test_unsupported_joined_update_fails_instead_of_being_ignored(self):
        with self.assertRaisesRegex(serial.SerialException, "clear DTR/RTS together"):
            self.open_sequence(True, unsupported=True)


if __name__ == "__main__":
    unittest.main()
