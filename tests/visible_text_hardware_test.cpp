// Exercise the maintained hardware orchestration with deterministic UART/GPIO
// fakes. This proves rearm/timeout sequencing, not electrical or parser behavior.
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdarg>
#include <string>
#include "visible_text_transaction.hpp"
using uart_port_t=int; using gpio_num_t=int; using QueueHandle_t=int;
constexpr int UART_NUM_1=1, GPIO_NUM_11=11, GPIO_NUM_12=12, GPIO_NUM_23=23;
constexpr int UART_PIN_NO_CHANGE=-1, GPIO_MODE_INPUT=0, GPIO_MODE_OUTPUT=1;
constexpr int UART_DATA_8_BITS=8, UART_PARITY_DISABLE=0, UART_STOP_BITS_1=1;
constexpr int UART_HW_FLOWCTRL_CTS=1, UART_SCLK_DEFAULT=0;
constexpr int UART_INTR_TX_DONE=1, UART_INTR_TXFIFO_EMPTY=2;
constexpr int ESP_OK=0, ESP_ERR_TIMEOUT=1, UART_DATA=1, pdTRUE=1;
struct uart_config_t { int baud_rate,data_bits,parity,stop_bits,flow_ctrl,source_clk; };
struct uart_event_t { int type; };
struct VisibleTextStream { VisibleTextTransaction transaction; };
static unsigned now_ms, connects, replies, parses, pass_logs, fail_logs;
static unsigned received[2];
static constexpr uint8_t first[]={12,'F','I','R','S','T',13,10,23,0,0xCA,23,0,0x80,0xA7};
static constexpr uint8_t second[]={12,31,2,2,'2',13,10,23,0,0xCA,23,0,0x80,0xA7};
static constexpr uint8_t ack[]={0x80,1,0xA7};
static int scenario, levels[40], directions[40];
static bool tx_connected;
struct Finished {};
static uint32_t millis() { return now_ms; }
static void delay(int) {
  if (!now_ms) now_ms=200001; else ++now_ms; // idle longer than old 180s limit
  if (now_ms>(scenario==2 ? 207000u : 201100u)) throw Finished{};
}
static int gpio_set_level(int pin,int value) { levels[pin]=value; return 0; }
static int gpio_set_direction(int pin,int value) { directions[pin]=value; return 0; }
static int gpio_reset_pin(int pin) {
  directions[pin]=GPIO_MODE_INPUT;
  if(pin==12)tx_connected=false;
  return 0;
}
static int gpio_pullup_dis(int) { return 0; }
static int gpio_pulldown_dis(int) { return 0; }
static int gpio_input_enable(int) { return 0; }
static int gpio_get_level(int pin) {
  assert(pin==23);
  return !((now_ms>=200020 && now_ms<200550) ||
           (now_ms>=200700 && now_ms<201050));
}
static int uart_set_pin(int,int tx,int rx,int,int cts) {
  assert(tx==12 && rx==22 && cts==23);
  assert(directions[11]==GPIO_MODE_OUTPUT && levels[11]==1);
  tx_connected=true; ++connects; return 0;
}
static int uart_param_config(int,uart_config_t *c) { assert(c->baud_rate==1152000); return 0; }
static int uart_driver_install(int,int,int,int,int *,int) { return 0; }
static int uart_disable_intr_mask(int,int) { return 0; }
static void uart_ll_txfifo_rst(int) {}
static int xQueueReceive(int,uart_event_t *,int) { return 0; }
static int uart_read_bytes(int,uint8_t *p,unsigned length,int) {
  if(directions[11]!=GPIO_MODE_OUTPUT || levels[11] || gpio_get_level(23)) return 0;
  unsigned cycle=now_ms>=200700 ? 1 : 0, n=0;
  const auto *request=cycle ? second : first;
  const auto size=cycle ? sizeof(second) : sizeof(first);
  while(n<length && received[cycle]<size) p[n++]=request[received[cycle]++];
  if(scenario==1 && n) p[0]=22;
  return int(n);
}
static int uart_tx_chars(int,const char *p,int n) {
  assert(tx_connected && n==3 && !std::memcmp(p,ack,3));
  ++replies; return n;
}
static int uart_wait_tx_done(int,int) { return scenario==2 ? ESP_ERR_TIMEOUT : ESP_OK; }
static void log_message(const char *,const char *fmt,...) {
  if(std::strstr(fmt,"VISIBLE TEXT PASS"))++pass_logs;
  if(std::strstr(fmt,"VISIBLE TEXT FAIL"))++fail_logs;
}
#define ESP_ERROR_CHECK(x) assert((x)==ESP_OK)
#define ESP_LOGI log_message
#define ESP_LOGE log_message
#define UART_LL_GET_HW(x) (x)
#define AGON_EXTENDER_BUILD_ID "test"
#define AGON_EXTENDER_ARTIFACT_STATUS "draft"
class VDUStreamProcessor {
 public:
  VisibleTextStream *stream;
  void processNext() {
    ++parses;
    const auto *expected=parses==1 ? first : second;
    const auto size=parses==1 ? sizeof(first) : sizeof(second);
    for(unsigned i=0;i<size;++i) assert(stream->transaction.read()==expected[i]);
    for(auto b:ack) assert(stream->transaction.write(b)==1);
  }
};
#include "visible_text_hardware.inc"
int main(int argc,char **argv) {
  assert(argc==2); scenario=std::stoi(argv[1]);
  auto *stream=beginVisibleTextQualification(); VDUStreamProcessor processor{stream};
  try { runVisibleTextQualification(&processor); } catch(const Finished &) {}
  assert(!tx_connected && directions[11]==GPIO_MODE_INPUT);
  if(!scenario) {
    assert(connects==2 && replies==2 && parses==2 && pass_logs==2 && !fail_logs);
    assert(!stream->transaction.failure && stream->transaction.received==0);
  } else {
    assert(fail_logs && !pass_logs && connects==1 && stream->transaction.failure);
    assert(replies==(scenario==2 ? 1u : 0u));
  }
  delete stream;
}
