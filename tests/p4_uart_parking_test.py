"""Exercise maintained IDF UART adapter using a scripted SDK boundary."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ParkingTests(unittest.TestCase):
    def test_real_adapter(self):
        with tempfile.TemporaryDirectory() as td:
            temp=Path(td)
            for header in ('driver/uart.h','driver/gpio.h','freertos/FreeRTOS.h',
                           'esp_rom_gpio.h','hal/uart_ll.h','soc/uart_periph.h'):
                p=temp/header;p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text('#include "p4_uart_sdk_fake.hpp"\n')
            exe=temp/'parking'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic',
                '-fsanitize=address,undefined',f'-I{temp}',f'-I{ROOT / "tests"}',
                f'-I{ROOT / "vdp/video"}',str(ROOT/'tests/p4_uart_parking_test.cpp'),
                str(ROOT/'vdp/video/extender/transport/p4_uart_parking.cpp'),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True)
if __name__=='__main__':unittest.main()
