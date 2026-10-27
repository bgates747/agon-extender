"""Portable native USB decoder/source lifecycle, without a bench or emulator."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UsbController(unittest.TestCase):
    def test_decoder_and_source_lifecycle(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'usb-f310'
            subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                            '-fsanitize=address,undefined', '-I'+str(ROOT/'vdp/video'),
                            str(ROOT/'tests/controller/usb_f310.cpp'), '-o', str(target)], check=True)
            subprocess.run([str(target)], check=True)
