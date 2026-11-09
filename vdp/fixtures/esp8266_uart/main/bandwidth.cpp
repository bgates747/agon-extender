// Isolated NET-008 modem torture appliance. CRC32 is the explicit Author test
// exception for P4/Pi5 transfer integrity, never an EMOS transport change.
// Ordinary P4 services are deliberately absent in this development image.
#include "bandwidth.h"
#include "bw_codec.h"
#include <cstdio>
#include <cstring>
#include <cctype>
#include <initializer_list>
#include <atomic>
#include <driver/uart.h>
#include <driver/gpio.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
namespace {
constexpr auto u=UART_NUM_2;
QueueHandle_t queue;
bool installed=false;
std::atomic<bool> stop{false},tx_done{false};
std::atomic<unsigned> tx_count{0};
unsigned faults=0,crc_errors=0,frame_errors=0,rx_seen=0;
bool data_active=false;int64_t progress_at=0,data_start=0;
size_t last_exact=0;const char *rx_failure="none";
int64_t tx_first=0,tx_last=0,tx_deadline=0;
unsigned duration=0;
uint8_t tx_wire[n8bw::max_frame],tx_data[n8bw::payload_size];
uint8_t rx_wire[n8bw::max_frame],expected[n8bw::payload_size];
bool health() {
 uart_event_t e;bool current_ok=true;
 while(xQueueReceive(queue,&e,0)==pdTRUE)if(e.type!=UART_DATA){current_ok=false;++faults;stop=true;std::printf("NET008 {\"event\":\"bw_uart_error\",\"type\":%u}\n",unsigned(e.type));}
 return current_ok;
}
bool ok(esp_err_t e){if(e==ESP_OK)return true;std::printf("NET008 {\"event\":\"bw_driver_error\",\"code\":%d}\n",int(e));stop=true;return false;}
bool init(unsigned baud) {
 uart_config_t c{};c.baud_rate=int(baud);c.data_bits=UART_DATA_8_BITS;c.parity=UART_PARITY_DISABLE;c.stop_bits=UART_STOP_BITS_1;c.flow_ctrl=UART_HW_FLOWCTRL_DISABLE;c.source_clk=UART_SCLK_DEFAULT;
 stop=false;tx_first=tx_last=0;faults=0;crc_errors=0;frame_errors=0;tx_done=false;tx_count=0;data_active=false;rx_seen=0;
 for(auto p:{GPIO_NUM_47,GPIO_NUM_48}){if(!ok(gpio_reset_pin(p))||!ok(gpio_set_direction(p,GPIO_MODE_INPUT)))return false;}
 if(!ok(uart_param_config(u,&c))||!ok(uart_driver_install(u,32768,4096,128,&queue,0)))return false;
 installed=true;return ok(uart_set_pin(u,48,47,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE));
}
bool retire() {
 if(installed){if(!ok(uart_driver_delete(u)))return false;installed=false;}
 bool pass=true;
 for(auto p:{GPIO_NUM_47,GPIO_NUM_48})pass=ok(gpio_reset_pin(p))&&ok(gpio_set_direction(p,GPIO_MODE_INPUT))&&ok(gpio_pullup_dis(p))&&ok(gpio_pulldown_dis(p))&&pass;
 return pass;
}
void hex(const char *kind,const uint8_t *data,size_t n) {
 std::printf("NET008 {\"event\":\"%s\",\"hex\":\"",kind);
 for(size_t i=0;i<n;++i)std::printf("%02x",data[i]);
 std::puts("\"}");
}
bool write(const void *data,size_t n){return uart_write_bytes(u,data,n)==int(n);}
bool command(const char *s,unsigned milliseconds,bool prompt=false,bool report=false) {
 uint8_t b[2048]{};size_t n=0;auto end=esp_timer_get_time()+int64_t(milliseconds)*1000;
 if(!write(s,std::strlen(s))||!ok(uart_wait_tx_done(u,pdMS_TO_TICKS(500))))return false;
 bool pass=false;
 while(esp_timer_get_time()<end&&n+1<sizeof(b)) {
  if(!health())break;
  int got=uart_read_bytes(u,b+n,sizeof(b)-n-1,pdMS_TO_TICKS(10));if(got<0)break;n+=size_t(got);b[n]=0;
  if(std::strstr(reinterpret_cast<char *>(b),"\nERROR\r\n")||std::strstr(reinterpret_cast<char *>(b),"FAIL\r\n"))break;
  if(prompt?std::strchr(reinterpret_cast<char *>(b),'>')!=nullptr:std::strstr(reinterpret_cast<char *>(b),"\nOK\r\n")!=nullptr){pass=true;break;}
 }
 if(report||!pass)hex("bw_at_reply",b,n);
 return pass;
}
bool exact(uint8_t *out,size_t n,int64_t deadline) {
 size_t got=0;last_exact=0;
 while(got<n&&esp_timer_get_time()<deadline&&!stop) {
  if(!health())return false;
  int k=uart_read_bytes(u,out+got,n-got,pdMS_TO_TICKS(20));if(k<0)return false;got+=size_t(k);last_exact=got;
  auto now=esp_timer_get_time();
  if(data_active&&now-progress_at>=1000000){progress_at=now;std::printf("NET008 {\"event\":\"bw_progress\",\"elapsed_us\":%lld,\"tx_frames\":%u,\"rx_frames\":%u,\"uart_errors\":%u}\n",static_cast<long long>(now-data_start),unsigned(tx_count),rx_seen,faults);}
 }
 return got==n;
}
bool read_frame(int64_t deadline,size_t &n) {
 n=0;rx_failure="none";
 if(!exact(rx_wire,16,deadline)){n=last_exact;rx_failure="header_timeout_or_uart";return false;}n=16;
 if(std::memcmp(rx_wire,"N8BW",4)||n8bw::get(rx_wire+8)>n8bw::payload_size){++frame_errors;rx_failure="header_framing";return false;}
 size_t len=n8bw::get(rx_wire+8);
 if(!exact(rx_wire+16,len,deadline)){n+=last_exact;rx_failure="payload_timeout_or_uart";return false;}
 n+=len;if(!n8bw::valid(rx_wire,n)){++crc_errors;rx_failure="crc_mismatch";return false;}return true;
}
void tx_task(void *) {
 unsigned seq=1;tx_first=esp_timer_get_time();tx_deadline=tx_first+int64_t(duration)*1000;
 while(!stop&&esp_timer_get_time()<tx_deadline) {
  n8bw::pattern(tx_data,sizeof(tx_data),seq,n8bw::up_salt);size_t n=n8bw::frame(tx_wire,seq,tx_data,sizeof(tx_data));
  if(!write(tx_wire,n)){stop=true;break;}tx_count=seq++;
 }
 if(!write(tx_wire,n8bw::frame(tx_wire,seq,nullptr,0))||uart_wait_tx_done(u,pdMS_TO_TICKS(3000))!=ESP_OK)stop=true;
 tx_last=esp_timer_get_time();tx_done=true;vTaskDelete(nullptr);
}
}
void net008_info(unsigned baud) {
 bool pass=init(baud);
 if(pass)pass=command("AT\r\n",2000)&&command("ATE0\r\n",2000)&&command("AT+CIPSTATUS\r\n",2000,false,true)&&command("AT+CIFSR\r\n",2000,false,true);
 bool retired=retire();std::printf("NET008 {\"event\":\"bw_info_end\",\"pass\":%s,\"baud\":%u,\"uart_retired\":%s}\n",pass?"true":"false",baud,retired?"true":"false");
}
void net008_bench(unsigned old_baud,unsigned new_baud,unsigned milliseconds,const char *ip,unsigned port,unsigned nonce) {
 bool pass=false,connected=false,transparent=false;const char *phase="arguments";unsigned rx_count=0;int64_t rx_first=0,rx_last=0;uint32_t actual_baud=0;
 if(milliseconds<1000||milliseconds>62000||new_baud>1152000||old_baud>1152000||!new_baud||!old_baud||!port||port>65535||std::strlen(ip)>15){std::puts("NET008 {\"event\":\"bw_refused\"}");return;}
 for(const char *p=ip;*p;++p)if(!std::isdigit(unsigned(*p))&&*p!='.'){std::puts("NET008 {\"event\":\"bw_refused\"}");return;}
 phase="uart_init";if(!init(old_baud))goto finish;
 phase="old_baud_AT";if(!command("AT\r\n",2000)||!command("ATE0\r\n",2000))goto finish;
 if(old_baud!=new_baud) {
  char change[80];std::snprintf(change,sizeof(change),"AT+UART_CUR=%u,8,1,0,0\r\n",new_baud);
  // Older modem may emit OK on either side of the transition. Record it;
  // the positive AT at the new rate, not this optional old-rate ACK, is proof.
  command(change,300);if(!ok(uart_set_baudrate(u,new_baud)))goto finish;
  vTaskDelay(pdMS_TO_TICKS(100));uart_flush_input(u);
  std::printf("NET008 {\"event\":\"bw_transition\",\"old_rate_ack_faults\":%u}\n",unsigned(faults));
  xQueueReset(queue);faults=0;stop=false;
 }
 phase="new_baud_AT";if(!command("AT\r\n",2000))goto finish;
 uart_get_baudrate(u,&actual_baud);
 std::printf("NET008 {\"event\":\"bw_baud\",\"requested\":%u,\"actual_p4\":%u}\n",new_baud,unsigned(actual_baud));
 phase="tcp_setup";if(!command("AT+CIPMUX=0\r\n",2000)||!command("AT+CIPMODE=1\r\n",2000))goto finish;
 {
  char start[100];std::snprintf(start,sizeof(start),"AT+CIPSTART=\"TCP\",\"%s\",%u\r\n",ip,port);
  if(!command(start,10000))goto finish;
  connected=true;
 }
 phase="transparent_start";if(!command("AT+CIPSEND\r\n",3000,true))goto finish;
 transparent=true;
 vTaskDelay(pdMS_TO_TICKS(50));uart_flush_input(u);
 {
  uint8_t hello[16];n8bw::put(hello,nonce);n8bw::put(hello+4,new_baud);n8bw::put(hello+8,milliseconds);n8bw::put(hello+12,1024);
  phase="peer_GO";size_t n=n8bw::frame(tx_wire,0,hello,sizeof(hello));if(!write(tx_wire,n)||!read_frame(esp_timer_get_time()+10000000,n)||n8bw::get(rx_wire+4)!=0||n!=18||std::memcmp(rx_wire+16,"GO",2))goto finish;
 }
 {
  phase="data";duration=milliseconds;stop=false;tx_done=false;tx_count=0;tx_first=0;tx_last=0;
  auto run_start=esp_timer_get_time();auto deadline=run_start+int64_t(milliseconds+20000)*1000;data_start=run_start;progress_at=run_start;data_active=true;
  if(xTaskCreate(tx_task,"n8bw_tx",4096,nullptr,5,nullptr)!=pdPASS)goto finish;
  unsigned wanted=1;bool eos=false;
  while(!stop&&esp_timer_get_time()<deadline) {
   size_t n=0;
   if(!read_frame(deadline,n)){phase=rx_failure;hex("bw_bad_frame",rx_wire,n);stop=true;break;}
   if(n8bw::get(rx_wire+4)!=wanted++){phase="rx_sequence";stop=true;break;}
   size_t len=n8bw::get(rx_wire+8);
   if(!len){eos=true;break;}
   n8bw::pattern(expected,len,wanted-1,n8bw::down_salt);
   if(std::memcmp(expected,rx_wire+16,len)){phase="rx_payload";stop=true;break;}
   ++rx_count;rx_seen=rx_count;auto now=esp_timer_get_time();if(!rx_first)rx_first=now;rx_last=now;

  }
  data_active=false;if(!eos)stop=true;
  auto join_until=esp_timer_get_time()+10000000;
  while(!tx_done&&esp_timer_get_time()<join_until)vTaskDelay(pdMS_TO_TICKS(5));
  // Never delete a live UART driver under its TX task. Retain for explicit
  // recovery if a task cannot join; no data/firmware replay follows.
  if(!tx_done){std::puts("NET008 {\"event\":\"bw_task_unjoined\"}");return;}
  pass=eos&&!stop&&faults==0&&health();if(pass)phase="complete";
 }
 finish:
 data_active=false;
 bool clean=true;
 if(transparent) {
  // Producers are stopped and joined before guarded transparent escape.
  vTaskDelay(pdMS_TO_TICKS(1100));clean=write("+++",3)&&clean;clean=uart_wait_tx_done(u,pdMS_TO_TICKS(500))==ESP_OK&&clean;vTaskDelay(pdMS_TO_TICKS(1100));
 }
 if(connected){bool closed=command("AT+CIPCLOSE\r\n",3000);clean=closed&&clean;}
 if(installed){bool at=command("AT\r\n",2000);clean=at&&clean;}
 bool retired=retire();
 std::printf("NET008 {\"event\":\"bw_end\",\"pass\":%s,\"phase\":\"%s\",\"baud\":%u,\"actual_p4_baud\":%u,\"duration_ms\":%u,\"nonce\":%u,\"tx_frames\":%u,\"rx_frames\":%u,\"tx_bytes\":%u,\"rx_bytes\":%u,\"tx_elapsed_us\":%lld,\"rx_elapsed_us\":%lld,\"uart_errors\":%u,\"crc_errors\":%u,\"frame_errors\":%u,\"cleanup\":%s,\"uart_retired\":%s}\n",pass&&clean&&retired?"true":"false",phase,new_baud,unsigned(actual_baud),milliseconds,nonce,unsigned(tx_count),rx_count,unsigned(tx_count)*1024,rx_count*1024,static_cast<long long>(tx_last-tx_first),static_cast<long long>(rx_last-rx_first),unsigned(faults),crc_errors,frame_errors,clean?"true":"false",retired?"true":"false");
}
