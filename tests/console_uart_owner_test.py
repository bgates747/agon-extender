"""Verify owner-core driver installation and its maintained startup call site."""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ConsoleUartOwnerTests(unittest.TestCase):
    def test_actual_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            (d/'driver').mkdir();(d/'freertos').mkdir()
            (d/'driver/uart.h').write_text('''#pragma once
#include <cstdint>
using esp_err_t=int;using uart_port_t=int;using QueueHandle_t=void*;
constexpr int ESP_OK=0,ESP_FAIL=1,ESP_ERR_INVALID_STATE=2,UART_NUM_1=1;
esp_err_t uart_driver_install(uart_port_t,int,int,int,QueueHandle_t*,int);
esp_err_t uart_set_rx_timeout(uart_port_t,uint8_t);
''')
            (d/'freertos/FreeRTOS.h').write_text('#pragma once\nint xPortGetCoreID();\n')
            exe=d/'owner'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic',
                            '-fsanitize=address,undefined','-fno-sanitize-recover=all',
                            f'-I{d}',f'-I{ROOT/"vdp/video"}',str(ROOT/'tests/console_uart_owner_test.cpp'),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True)
    def test_real_owner_is_the_installing_task(self):
        hardware=(ROOT/'vdp/video/extender/transport/console_hardware.inc').read_text()
        begin=hardware.split('ConsoleStream *beginConsole() {',1)[1].split('void runConsole(',1)[0]
        run=hardware.split('void runConsole(VDUStreamProcessor *processor) {',1)[1]
        self.assertNotIn('uart_driver_install',begin)
        self.assertNotIn('startConsoleUart',begin)
        self.assertTrue(run.lstrip().startswith('// First driver operation'))
        self.assertLess(run.index('startConsoleUart(&console_events)'),run.index('for(;;)'))
        ino=(ROOT/'vdp/video/video.ino').read_text()
        task=ino.split('auto processTaskResult = xTaskCreatePinnedToCore(',1)[1].split(');',1)[0]
        self.assertIn('processLoop',task)
        self.assertIn('agon::extender::transport::consoleUartOwnerCore',task)
        self.assertIn('runConsole(processor)',ino)
if __name__=='__main__':unittest.main()
