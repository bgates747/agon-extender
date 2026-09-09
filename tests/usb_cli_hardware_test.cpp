// Maintained owner, decoder, queue and Stream; deterministic external devices.
#include <array>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include "usb_cli_stream.hpp"
using uart_port_t=int; using gpio_num_t=int; using QueueHandle_t=int;
constexpr int UART_NUM_1=1, GPIO_NUM_11=11, GPIO_NUM_12=12, GPIO_NUM_23=23;
constexpr int UART_PIN_NO_CHANGE=-1, GPIO_MODE_INPUT=0, GPIO_MODE_OUTPUT=1;
constexpr int UART_DATA_8_BITS=8, UART_PARITY_DISABLE=0, UART_STOP_BITS_1=1;
constexpr int UART_HW_FLOWCTRL_CTS=1, UART_SCLK_DEFAULT=0;
constexpr int UART_INTR_TX_DONE=1, UART_INTR_TXFIFO_EMPTY=2;
constexpr int ESP_OK=0, ESP_ERR_TIMEOUT=1, UART_DATA=1, pdTRUE=1;
struct uart_config_t { int baud_rate,data_bits,parity,stop_bits,flow_ctrl,source_clk; };
struct uart_event_t { int type; };
static unsigned now_ms, tx_since, cancelled, polls, rx_index;
static int scenario, levels[40], directions[40];
static bool tx_connected, injected_error;
static std::vector<uint8_t> pending, received;
static std::array<bool,249> held{};
struct Request {unsigned time; std::array<uint8_t,4> bytes;};
static std::vector<Request> requests;
struct Finished {};
static uint32_t millis() { return now_ms; }
static void delay(int n) { now_ms+=n; if(now_ms>=9000) throw Finished{}; }
static int gpio_set_level(int pin,int value) { levels[pin]=value; return 0; }
static int gpio_set_direction(int pin,int value) { directions[pin]=value; return 0; }
static int gpio_reset_pin(int pin) {directions[pin]=GPIO_MODE_INPUT;if(pin==12)tx_connected=false;return 0;}
static int gpio_pullup_dis(int) { return 0; }
static int gpio_pulldown_dis(int) { return 0; }
static int gpio_input_enable(int) { return 0; }
static int uart_set_pin(int,int tx,int rx,int,int cts) {
  assert(tx==12 && rx==22 && cts==23 && directions[11]==GPIO_MODE_OUTPUT);
  tx_connected=true;return 0;
}
static int uart_param_config(int,uart_config_t *c) {
  assert(c->baud_rate==1152000 && c->flow_ctrl==UART_HW_FLOWCTRL_CTS);return 0;
}
static int uart_driver_install(int,int,int,int,int *,int) { return 0; }
static int uart_disable_intr_mask(int,int) { return 0; }
static void uart_ll_txfifo_rst(int) {pending.clear();++cancelled;}
static int xQueueReceive(int,uart_event_t *event,int) {
  if(scenario==5 && !injected_error && now_ms>=100) {injected_error=true;event->type=99;return pdTRUE;}
  return 0;
}
static int uart_read_bytes(int,uint8_t *p,unsigned length,int) {
  if(rx_index>=requests.size() || now_ms<requests[rx_index].time) return 0;
  assert(tx_connected && !levels[11] && length==4);
  auto request=requests[rx_index++];unsigned n=scenario==4?2:4;
  std::memcpy(p,request.bytes.data(),n);return n;
}
static int uart_tx_chars(int,const char *p,int n) {
  assert(tx_connected && pending.empty() && (n==3 || n==6));
  if(scenario==6) return n-1;
  pending.assign(p,p+n);tx_since=now_ms;return n;
}
static int uart_wait_tx_done(int,int) {
  assert(!pending.empty());
  if(now_ms-tx_since<2 || (scenario==1 && now_ms>=100 && now_ms<500) ||
     (scenario==2 && now_ms>=100 && now_ms<5400)) return ESP_ERR_TIMEOUT;
  if(pending.size()==3) {assert(pending[0]==0x80 && pending[1]==1);++polls;}
  else {
    assert(pending[0]==0x81 && pending[1]==4 && pending[4]<held.size());
    if(!pending[5]) assert(held[pending[4]]); // Never invent a release.
    held[pending[4]]=pending[5];
    received.insert(received.end(),pending.begin(),pending.end());
  }
  pending.clear();return ESP_OK;
}
namespace agon::extender::input::usbhost {
static bool begin() {return true;}
static bool attached() {return now_ms<1200 || now_ms>=1500;}
template<class Report,class Connection,class Lost>
void pump(Report report,Connection connection,Lost lost) {
  (void)lost;
  auto key=[&](uint8_t u,uint8_t m=0) {const uint8_t p[]={m,0,u,0,0,0,0,0};report(p,8);};
  if(scenario==1) {
    if(now_ms>=100 && now_ms<300 && now_ms%2==0) key(now_ms%4==0?4:0);
    if(now_ms==600) key(5);
    if(now_ms==700) key(0);
  } else if(scenario==2) {
    if(now_ms==100) key(4);
    if(now_ms==200) key(0);
    if(now_ms==5600) key(5);
    if(now_ms==5700) key(0);
  } else if(scenario==7) {
    if(now_ms==100) key(4); // Unsupported layout must not admit this input.
    if(now_ms==200) key(0);
    if(now_ms==5600) key(5);
    if(now_ms==5700) key(0);
  } else if(!scenario) {
    if(now_ms==100) key(4);
    if(now_ms==200) key(0);
    if(now_ms==300) key(5);
    if(now_ms==1100) key(0);
    if(now_ms==1120) key(4,2);
    if(now_ms==1200) connection(false);
    if(now_ms==1500) connection(true);
    if(now_ms==1510) key(0);
    if(now_ms==1600) key(5);
    if(now_ms==1700) key(0);
    if(now_ms==1900) key(31,2);
    if(now_ms==2000) key(0);
  }
}
}
#define ESP_ERROR_CHECK(x) assert((x)==ESP_OK)
#define UART_LL_GET_HW(x) (x)
#define AGON_EXTENDER_BUILD_ID "test"
#define AGON_EXTENDER_ARTIFACT_STATUS "draft"
class VDUStreamProcessor {
 public:
  UsbCliStream *stream;
  void processNext() {
    if(stream->available()) {
      assert(stream->read()==23 && stream->read()==0);
      int opcode=stream->read(),argument=stream->read();
      if(opcode==0x80) {stream->write(0x80);stream->write(1);stream->write(uint8_t(argument));}
      else assert(opcode==0x81);
    } else {
      agon::extender::input::ProcessedKey key;
      assert(agon::extender::input::processedKeyboard().pop(key));
      const uint8_t bytes[]={0x81,4,key.keycode,key.modifiers,key.virtual_key,key.down};
      assert(stream->write(bytes,6)==6);
    }
  }
};
#include "diagnostic/usb_cli_hardware.inc"
int main(int argc,char **argv) {
  assert(argc==2);scenario=std::stoi(argv[1]);
  requests={{10,{23,0,0x81,uint8_t(scenario==7?2:1)}},{20,{23,0,0x80,0xA7}}};
  if(!scenario) {requests.push_back({1800,{23,0,0x81,0}});requests.push_back({1810,{23,0,0x80,0xA8}});}
  if(scenario==2 || scenario==7) {requests.push_back({5500,{23,0,0x81,1}});requests.push_back({5510,{23,0,0x80,0xA8}});}
  if(scenario==3) requests[0].bytes[2]=0xFF;
  if(scenario==4) requests.resize(1);
  auto *stream=beginKeyboardQualification();VDUStreamProcessor processor{stream};
  try {runKeyboardQualification(&processor);} catch(const Finished &) {}
  if(scenario>=3 && scenario<=6) {
    const char *expected[]={"","","","unsupported command","partial command timeout","UART receive error","TX enqueue"};
    assert(stream->failure && !std::strcmp(stream->failure,expected[scenario]));
    assert(levels[11]==1 && pending.empty());
  } else {
    assert(!stream->failure && pending.empty() && !levels[11]);
    for(bool down:held) assert(!down);
    assert(cancelled==unsigned(scenario==2));
    if(!scenario) {
      assert(polls==2 && received.size()==17*6);
      std::string text;
      for(unsigned i=0;i<received.size();i+=6) if(received[i+5] && received[i+2]) text+=char(received[i+2]);
      assert(text=="abbbbAb\"");
    } else if(scenario==1) assert(polls==1 && received.size()>=4*6);
    else {
      assert(polls==unsigned(scenario==2?2:1));
      assert(received==std::vector<uint8_t>({0x81,4,'b',0,23,1,0x81,4,'b',0,23,0}));
    }
  }
  delete stream;
}
