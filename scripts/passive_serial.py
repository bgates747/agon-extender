"""Open a POSIX serial reader without separate DTR/RTS transitions.

BENCH-010: Linux raises both modem controls at open. Pyserial's ordinary
False/False setup then clears DTR before RTS, pulsing the Agon Light2 Rev B
shared reset circuit. Clear both controls in a single driver operation instead.
This is a host adaptation, not an EMOS/VDP protocol change. Qualification is
specific to the recorded host/USB adapter; no universal glitch-free claim.
"""

import fcntl
import os
import struct
import termios

import serial


class _PassiveSerial(serial.Serial):
    def _clear_controls(self):
        if self._dtr_state or self._rts_state:
            raise serial.SerialException("Passive capture requires DTR and RTS both false")
        try:
            fcntl.ioctl(self.fd, termios.TIOCMBIC,
                        struct.pack("I", termios.TIOCM_DTR | termios.TIOCM_RTS))
        except OSError as error:
            # Serial.open ignores EINVAL/ENOTTY from normal control updates.
            # Here those mean our joined update is unsupported: fail closed.
            raise serial.SerialException(
                f"Cannot clear DTR/RTS together for passive capture: {error}") from error

    def _update_dtr_state(self):
        self._clear_controls()

    def _update_rts_state(self):
        self._clear_controls()


def open_passive_serial(port, *, baudrate=115200, timeout=0.25):
    """Return an open, exclusively locked reader; caller owns close/lifecycle.

    No bytes are written and no reset is requested. The caller must establish
    device identity and bench ownership before calling. This deliberately
    exposes no RTS/CTS, DSR/DTR, or control-line toggling options.
    """
    if os.name != "posix":
        raise serial.SerialException("Passive joined-control capture requires POSIX")
    handle = _PassiveSerial(port=None, baudrate=baudrate, timeout=timeout,
                            rtscts=False, dsrdtr=False, exclusive=True)
    handle.dtr = False
    handle.rts = False
    handle.port = str(port)
    handle.open()
    return handle
