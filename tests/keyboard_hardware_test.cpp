// Real qualification state machine and Stream, faked IDF clock/pins/UART.
// The parser fake checks orchestration only; processed_keyboard_test separately
// exercises the actual retained callback/event/packet implementations.
#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include "keyboard_probe_stream.hpp"
using uart_port_t=int; using gpio_num_t=int; using QueueHandle_t=int;
constexpr int UART_NUM_1=1, GPIO_NUM_11=11, GPIO_NUM_12=12, GPIO_NUM_23=23;
constexpr int UART_PIN_NO_CHANGE=-1, GPIO_MODE_INPUT=0, GPIO_MODE_OUTPUT=1;
constexpr int UART_DATA_8_BITS=8, UART_PARITY_DISABLE=0, UART_STOP_BITS_1=1;
constexpr int UART_HW_FLOWCTRL_CTS=1, UART_SCLK_DEFAULT=0;
constexpr int UART_INTR_TX_DONE=1, UART_INTR_TXFIFO_EMPTY=2;
constexpr int ESP_OK=0, ESP_ERR_TIMEOUT=1, UART_DATA=1, pdTRUE=1;
struct uart_config_t { int baud_rate,data_bits,parity,stop_bits,flow_ctrl,source_clk; };
struct uart_event_t { int type; };
static unsigned now_ms, connects, pass_logs, fail_logs, tx_since, rx_index[2];
static unsigned sent_keys, polls, kbRegion;
static int scenario, levels[40], directions[40];
static bool tx_connected, injected_error;
static std::vector<uint8_t> pending;
struct Finished {};
static uint32_t millis() { return now_ms; }
static void delay(int) {
  // An indefinite idle before a second Agon-only reset must still work.
  if (!now_ms) now_ms=200000; else ++now_ms;
  if (now_ms>214000) throw Finished{};
}
static bool active() { return (now_ms>=200020 && now_ms<206000) ||
                                   (now_ms>=207000 && now_ms<213000); }
static int gpio_set_level(int pin,int value) { levels[pin]=value; return 0; }
static int gpio_set_direction(int pin,int value) { directions[pin]=value; return 0; }
static int gpio_reset_pin(int pin) {
  directions[pin]=GPIO_MODE_INPUT;
  if (pin==12) tx_connected=false;
  return 0;
}
static int gpio_pullup_dis(int) { return 0; }
static int gpio_pulldown_dis(int) { return 0; }
static int gpio_input_enable(int) { return 0; }
static int gpio_get_level(int pin) {
  assert(pin==23);
  // A 100 ms CTS pause mid-cycle must not rearm or drop the current key.
  return !active() || (scenario==0 && now_ms>=201080 && now_ms<201180);
}
static int uart_set_pin(int,int tx,int rx,int,int cts) {
  assert(tx==12 && rx==22 && cts==23 && levels[11]==1);
  assert(directions[11]==GPIO_MODE_OUTPUT);
  tx_connected=true; ++connects; return 0;
}
static int uart_param_config(int,uart_config_t *c) {
  assert(c->baud_rate==1152000 && c->flow_ctrl==UART_HW_FLOWCTRL_CTS); return 0;
}
static int uart_driver_install(int,int,int,int,int *,int) { return 0; }
static int uart_disable_intr_mask(int,int) { return 0; }
static void uart_ll_txfifo_rst(int) { pending.clear(); }
static int xQueueReceive(int,uart_event_t *event,int) {
  if (scenario==5 && !injected_error && now_ms>=201000) {
    injected_error=true; event->type=99; return pdTRUE;
  }
  return 0;
}
static int uart_get_buffered_data_len(int,size_t *n) {
  *n=scenario==7 && now_ms>=201000 ? 1 : 0; return 0;
}
static int uart_read_bytes(int,uint8_t *p,unsigned length,int) {
  if (!active() || gpio_get_level(23) || scenario==3) return 0;
  assert(tx_connected && directions[11]==GPIO_MODE_OUTPUT && !levels[11]);
  const uint8_t bytes[]={23,0,0x81,1,23,0,0x80,0xA7};
  auto &index=rx_index[now_ms>=207000 ? 1 : 0];
  unsigned n=0, limit=scenario==4 ? 2 : sizeof(bytes);
  while (n<length && index<limit) p[n++]=bytes[index++];
  if (scenario==1 && n) p[0]=22;
  return int(n);
}
static int uart_tx_chars(int,const char *p,int n) {
  assert(tx_connected && pending.empty() && (n==3 || n==6));
  if (scenario==6) return n-1;
  pending.assign(p,p+n); tx_since=now_ms; return n;
}
static int uart_wait_tx_done(int,int) {
  assert(!pending.empty());
  if (scenario==2 || gpio_get_level(23) || now_ms-tx_since<2) return ESP_ERR_TIMEOUT;
  if (pending.size()==3) {
    assert(pending==std::vector<uint8_t>({0x80,1,0xA7})); ++polls;
  } else {
    const auto &key=keyboardProbeEvents[sent_keys%12];
    assert(pending==std::vector<uint8_t>({0x81,4,key.keycode,key.modifiers,key.virtual_key,key.down}));
    ++sent_keys;
  }
  pending.clear(); return ESP_OK;
}
static void log_message(const char *,const char *format,...) {
  if (std::strstr(format,"KEYBOARD SENDER PASS")) ++pass_logs;
  if (std::strstr(format,"KEYBOARD FAIL")) ++fail_logs;
}
#define ESP_ERROR_CHECK(x) assert((x)==ESP_OK)
#define ESP_LOGI log_message
#define ESP_LOGE log_message
#define UART_LL_GET_HW(x) (x)
#define AGON_EXTENDER_BUILD_ID "test"
#define AGON_EXTENDER_ARTIFACT_STATUS "draft"
class VDUStreamProcessor {
 public:
  KeyboardProbeStream *stream;
  void processNext() {
    if (stream->available()) {
      assert(stream->read()==23 && stream->read()==0);
      int opcode=stream->read(), argument=stream->read();
      if (opcode==0x81) kbRegion=argument;
      else { assert(opcode==0x80); stream->write(0x80); stream->write(1); stream->write(uint8_t(argument)); }
    } else {
      agon::extender::input::ProcessedKey key;
      assert(agon::extender::input::processedKeyboard().pop(key));
      const uint8_t bytes[]={0x81,4,key.keycode,key.modifiers,key.virtual_key,key.down};
      assert(stream->write(bytes,sizeof(bytes))==sizeof(bytes));
    }
  }
};
#include "keyboard_hardware.inc"
int main(int argc,char **argv) {
  assert(argc==2); scenario=std::stoi(argv[1]);
  auto *stream=beginKeyboardQualification(); VDUStreamProcessor processor{stream};
  try { runKeyboardQualification(&processor); } catch (const Finished &) {}
  assert(!tx_connected && directions[11]==GPIO_MODE_INPUT && pending.empty());
  if (!scenario) {
    assert(connects==2 && polls==2 && sent_keys==24 && pass_logs==2 && !fail_logs);
    assert(!stream->failure && kbRegion==1);
  } else {
    assert(stream->failure && fail_logs && !pass_logs && connects==1);
    const char *expected[]={"", "unsupported or overlapping command", "UART TX timeout",
      "admission timeout", "partial command timeout", "UART error event", "UART enqueue",
      "unexpected command after admission"};
    assert(!std::strcmp(stream->failure,expected[scenario]));
  }
  delete stream;
}
