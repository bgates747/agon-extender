"""Run the maintained USB CLI owner against deterministic UART/USB boundaries.

Only external driver calls and the retained parser are faked. The separate
processed-keyboard test exercises the actual retained packet methods.
"""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UsbCliHardwareTests(unittest.TestCase):
    def test_admission_editing_backpressure_loss_and_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            diagnostic = temp/'diagnostic'
            diagnostic.mkdir()
            source = ROOT/'vdp/video/extender'
            # Compile the maintained owner bytes unchanged. Its relative USB
            # boundary include resolves to this fake; decoder/queue are real.
            (diagnostic/'usb_cli_hardware.inc').write_bytes((source/'diagnostic/usb_cli_hardware.inc').read_bytes())
            (temp/'input').mkdir()
            (temp/'input/p4_usb_host.hpp').write_text('// Fake host is declared by the harness.\n')
            for name in ('usb_cli_keyboard.hpp', 'usb_key_queue.hpp'):
                (temp/'input'/name).symlink_to(source/'input'/name)
            for name in ('driver/gpio.h', 'driver/uart.h', 'hal/uart_ll.h'):
                path = temp/name
                path.parent.mkdir(exist_ok=True)
                path.write_text('// Driver declarations are supplied by the harness.\n')
            (temp/'Stream.h').write_text('''#pragma once
#include <cstddef>
#include <cstdint>
class Stream { public:
  virtual ~Stream() = default;
  virtual int available()=0, read()=0, peek()=0;
  virtual void flush()=0;
  virtual size_t write(uint8_t)=0;
  virtual size_t write(const uint8_t *, size_t)=0;
};
''')
            binary = temp/'usb-cli-test'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                            '-fsanitize=address,undefined','-fno-sanitize-recover=all',
                            '-I'+str(temp),'-I'+str(source/'diagnostic'),'-I'+str(source/'input'),
                            str(ROOT/'tests/usb_cli_hardware_test.cpp'),'-o',str(binary)], check=True)
            for scenario in range(8):
                with self.subTest(scenario=scenario):
                    subprocess.run([str(binary),str(scenario)], check=True)


if __name__ == '__main__':
    unittest.main()
