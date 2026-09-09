"""Exercise the maintained keyboard UART orchestration with deterministic fakes."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HardwareSequenceTests(unittest.TestCase):
    def test_repeat_backpressure_timeouts_and_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            for name in ('driver/gpio.h', 'driver/uart.h', 'hal/uart_ll.h'):
                path = temp/name
                path.parent.mkdir(exist_ok=True)
                path.write_text('// Declarations supplied by the harness.\n')
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
            binary = temp/'hardware-test'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                            '-fsanitize=address,undefined','-fno-sanitize-recover=all',
                            '-I'+str(temp),'-I'+str(ROOT/'vdp/video/extender/diagnostic'),
                            str(ROOT/'tests/keyboard_hardware_test.cpp'),'-o',str(binary)], check=True)
            for scenario in range(8):
                with self.subTest(scenario=scenario):
                    subprocess.run([str(binary),str(scenario)], check=True)


if __name__ == '__main__':
    unittest.main()
