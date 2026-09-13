// Maintained console owner; only physical drivers and the VDU producer are mocked.
#include <cassert>
#include <deque>
#include <vector>
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <string>
#include "transport/console_stream.hpp"
using gpio_num_t=int;using QueueHandle_t=int;
constexpr int GPIO_NUM_12=12,GPIO_MODE_INPUT=0;
constexpr int UART_DATA_8_BITS=8,UART_PARITY_DISABLE=0,UART_STOP_BITS_1=1;
constexpr int UART_HW_FLOWCTRL_CTS_RTS=3,UART_HW_FLOWCTRL_CTS=1,UART_SCLK_DEFAULT=0;
constexpr int UART_INTR_TX_DONE=1,UART_INTR_TXFIFO_EMPTY=2;
constexpr int ESP_OK=0,ESP_ERR_TIMEOUT=1,pdTRUE=1;
constexpr int UART_FIFO_OVF=3,UART_FRAME_ERR=4,UART_PARITY_ERR=5,COMMS_TIMEOUT=200;
struct uart_config_t{int baud_rate,data_bits,parity,stop_bits,flow_ctrl,rx_flow_ctrl_thresh,source_clk;};
struct uart_event_t{int type;};
static unsigned now_ms,cancelled,refills,submitted_at,complete_at;
static int scenario;static bool produced,expect_refill,read_started,expect_serial_reply;
static unsigned last_byte_at,max_packet_gap;
static std::deque<uint8_t> fifo;
static std::vector<uint8_t> received,expected;
struct Finished{};
static unsigned millis(){return now_ms;}
static unsigned esp_random(){return 42;}
static void delay(int n){
 for(int i=0;i<n;++i){
  ++now_ms;
  bool blocked=(scenario==1 && now_ms>=3 && now_ms<603)||(scenario==2 && now_ms<5300);
  if(!blocked)for(unsigned k=0;k<100 && !fifo.empty();++k){if(received.size()%18)max_packet_gap=std::max(max_packet_gap,now_ms-last_byte_at);
   last_byte_at=now_ms;received.push_back(fifo.front());fifo.pop_front();}
  if(!complete_at && produced && received==expected)complete_at=now_ms;
  if(now_ms>=6200)throw Finished{};
 }
}
static int gpio_reset_pin(int){return 0;}
static int gpio_set_level(int,int){return 0;}
static int gpio_set_direction(int,int){return 0;}
static int gpio_pullup_dis(int){return 0;}
static int gpio_pulldown_dis(int){return 0;}
static int uart_set_pin(int,int tx,int rx,int rts,int cts){assert(tx==12 && rx==22 && rts==11 && cts==23);return 0;}
static int uart_param_config(int,uart_config_t*c){assert(c->baud_rate==1152000 && c->rx_flow_ctrl_thresh==64);return 0;}
static int uart_driver_install(int,int rx,int tx,int,QueueHandle_t*,int){assert(rx==4096 && tx==0);return 0;}
static int uart_set_rx_timeout(int,unsigned){return 0;}
static int uart_disable_intr_mask(int,int){return 0;}
static int uart_set_hw_flow_ctrl(int,int,int){return 0;}
static int uart_set_rts(int,int){return 0;}
static void uart_ll_txfifo_rst(int){fifo.clear();++cancelled;}
static int xQueueReceive(int,uart_event_t*,int){return 0;}
int uart_get_buffered_data_len(int,size_t*n){*n=(scenario==3 && produced && !read_started)?1:0;return 0;}
int uart_read_bytes(int,void*,uint32_t,unsigned){return 0;}
static int uart_wait_tx_done(int,int){return fifo.empty()?ESP_OK:ESP_ERR_TIMEOUT;}
static int uart_tx_chars(int,const char*p,unsigned n){
 unsigned count=std::min<unsigned>(n,128-fifo.size());
 if(count && !fifo.empty())++refills;
 for(unsigned i=0;i<count;++i)fifo.push_back(uint8_t(p[i]));
 return int(count);
}
namespace agon::extender::input::usbhost{
static bool begin(){return true;}
template<class R,class C,class L> void pump(R,C,L){}
}
#define ESP_ERROR_CHECK(x) assert((x)==ESP_OK)
#define UART_LL_GET_HW(x) (x)
#define AGON_EXTENDER_BUILD_ID "host-owner-test"
#define AGON_EXTENDER_ARTIFACT_STATUS "experimental"
class VDUStreamProcessor{public:void processNext();void vdu_mode(int){}};
#include "transport/console_hardware.inc"
void VDUStreamProcessor::processNext(){
 if(!produced && console_stream->session.active()){
  // Fixed packet sequence crosses the reply ring wrap and UART FIFO boundaries.
  expected.resize(4626);for(unsigned i=0;i<expected.size();++i)expected[i]=uint8_t(i*37+13);
  console_stream->read_pos=8100;
  assert(console_stream->write(expected.data(),expected.size())==expected.size());
  submitted_at=now_ms;produced=true;console_admit_pending=true;return;
 }
 if(produced && scenario==3 && !read_started) {
  read_started=true;delay(400); // Blocking next upload cannot pump queued reply bytes.
 }
 if(produced && !console_admit_pending)assert(fifo.empty() && console_stream->count==0);
}
static void admit(ConsoleStream&s){
 uint8_t p[CONSOLE_SIZE]={'E','X',1,CONSOLE_PREPARE,1},reply[CONSOLE_SIZE];p[12]=1;console_seal(p);
 assert(s.session.request(p,now_ms,42,reply));std::memcpy(p+8,reply+8,4);p[3]=CONSOLE_COMMIT;console_seal(p);
 assert(s.session.request(p,now_ms,42,reply));
}
int main(int argc,char**argv){
 assert(argc==4);scenario=std::stoi(argv[1]);expect_refill=std::stoi(argv[2]);expect_serial_reply=std::stoi(argv[3]);
 auto*s=beginConsole();admit(*s);VDUStreamProcessor processor;
 try{runConsole(&processor);}catch(const Finished&){}
 assert(!s->failure && s->count==0 && fifo.empty());
 if(scenario==2){
  assert(cancelled==1 && received.empty() && !s->session.active());
  admit(*s);assert(s->session.active()); // stale tail absent before new lease
 }else{
  assert(cancelled==0 && received==expected && complete_at>submitted_at && !console_admit_pending);
  assert((refills>0)==expect_refill);
  if(scenario==3)assert(read_started && (max_packet_gap<250)==expect_serial_reply);
 }
 std::printf("scenario=%d bytes=%zu completion_ms=%u refills=%u cancellations=%u max_packet_gap_ms=%u\n",scenario,received.size(),complete_at-submitted_at,refills,cancelled,max_packet_gap);
 delete s;
}
