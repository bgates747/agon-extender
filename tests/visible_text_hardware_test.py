"""Run real orchestration with faked hardware, including a second Agon request."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HardwareSequenceTests(unittest.TestCase):
    def test_repeat_after_long_idle_and_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            # The harness provides the exercised ESP-IDF declarations; these
            # empty headers satisfy the production include paths only.
            for name in ('driver/gpio.h', 'driver/uart.h', 'hal/uart_ll.h'):
                path = temp / name
                path.parent.mkdir(exist_ok=True)
                path.write_text('// Declarations supplied by the harness.\n')
            binary = temp / 'hardware-test'
            subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                            '-fsanitize=address,undefined', '-I' + str(temp),
                            '-I' + str(ROOT / 'vdp/video/extender/diagnostic'),
                            str(ROOT / 'tests/visible_text_hardware_test.cpp'),
                            '-o', str(binary)], check=True)
            for scenario in range(3):
                with self.subTest(scenario=scenario):
                    subprocess.run([str(binary), str(scenario)], check=True)


if __name__ == '__main__':
    unittest.main()
