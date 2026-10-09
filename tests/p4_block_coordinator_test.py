"""Reuse the native leaf SDK model; link actual physical coordinator leaves."""
from pathlib import Path
from time import monotonic
import subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
def prepare_sdk(d):
 fake=(ROOT/'tests/p4_native_sdk_fake.hpp').read_text()+"""
using uart_port_t=int;using portMUX_TYPE=int;
constexpr int UART_NUM_1=1,ESP_ERR_TIMEOUT=3,GPIO_MATRIX_CONST_ONE_INPUT=0x38;
constexpr int SOC_UART_RX_PIN_IDX=0,SOC_UART_CTS_PIN_IDX=1;
#define UART_PERIPH_SIGNAL(u,p) ((u)*10+(p))
#define portMUX_INITIALIZER_UNLOCKED 0
struct uart_dev_t {};extern uart_dev_t hardware;
#define UART_LL_GET_HW(u) (&hardware)
void enterCritical(portMUX_TYPE*);void exitCritical(portMUX_TYPE*);
#define taskENTER_CRITICAL(m) enterCritical(m)
#define taskEXIT_CRITICAL(m) exitCritical(m)
int uart_wait_tx_done(int,int);int uart_get_buffered_data_len(int,std::size_t*);
int uart_set_pin(int,int,int,int,int);
void esp_rom_gpio_connect_in_signal(int,int,bool);
unsigned uart_ll_get_rxfifo_len(uart_dev_t*);bool uart_ll_is_tx_idle(uart_dev_t*);
"""
 (d/'p4_native_sdk_fake.hpp').write_text(fake)
 for name in ('driver/parlio_rx.h','driver/parlio_tx.h','driver/gpio.h',
  'driver/uart.h','esp_attr.h','esp_heap_caps.h','freertos/FreeRTOS.h',
  'esp_rom_gpio.h','hal/uart_ll.h','soc/uart_periph.h'):
  p=d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('#include "p4_native_sdk_fake.hpp"\n')

class CoordinatorTest(unittest.TestCase):
 def test_coordinator(self):
  clock=monotonic()
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp)
   prepare_sdk(d)
   prefix=(ROOT/'tests/p4_native_payload_test.cpp').read_text().split('int main(){')[0]
   # Local quote includes must resolve to this combined narrow SDK model.
   prefix=prefix.replace('static H admitted(', '[[maybe_unused]] static H admitted(')
   source=d/'coordinator.cpp';source.write_text(prefix+(ROOT/'tests/p4_block_coordinator_test.cpp').read_text())
   exe=d/'coordinator'
   subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic',
    '-fsanitize=address,undefined','-fno-sanitize-recover=all',f'-I{d}',f'-I{ROOT/"vdp/video"}',
    str(source),*[str(ROOT/'vdp/video/extender/transport'/(s+'.cpp')) for s in
     ('p4_block_coordinator','p4_native_payload','p4_uart_parking','p4_parallel_handover','p4_parallel_egress')],
    '-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True,timeout=30)
  print(f'Coordinator host compile/test: {monotonic()-clock:.6f} seconds; no electrical timing')
if __name__=='__main__':unittest.main()
