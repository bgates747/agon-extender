// NET-008 isolated P4-PC wiring appliance; not an Extender product backend.
// Boot leaves it idle. Explicit USB Serial/JTAG CLI START runs exactly once,
// following the existing USB-minimal appliance model. No eZ80 appliance runs;
// no MOS/VDP route or peripheral is commandeered. All mainboard lanes are inputs.
#include "bandwidth.h"
#include "join_codec.h"
#include <cstdio>
#include <cstring>
#include <cctype>
#include <initializer_list>
#include <driver/gpio.h>
#include <driver/uart.h>
#include <driver/usb_serial_jtag.h>
#include <driver/usb_serial_jtag_vfs.h>
#include <esp_ldo_regulator.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

namespace {
constexpr uart_port_t modem=UART_NUM_2;
// Smith reports likely crossed wires: preserve wiring, route TX48/RX47.
constexpr gpio_num_t tx=GPIO_NUM_48,rx=GPIO_NUM_47;
esp_ldo_channel_handle_t power;
QueueHandle_t events;
bool installed=false,used=false;
void hex(const char *event,unsigned seq,const unsigned char *bytes,size_t count) {
  std::printf("NET008 {\"event\":\"%s\",\"seq\":%u,\"hex\":\"",event,seq);
  for(size_t i=0;i<count;++i)std::printf("%02x",bytes[i]);
  std::printf("\"}\n");
}
bool checked(esp_err_t error,const char *operation) {
  if(error==ESP_OK)return true;
  std::printf("NET008 {\"event\":\"error\",\"operation\":\"%s\",\"code\":%d}\n",operation,int(error));return false;
}
bool healthy() {
  uart_event_t e;
  while(xQueueReceive(events,&e,0)==pdTRUE)
    if(e.type!=UART_DATA) {
      std::printf("NET008 {\"event\":\"uart_error\",\"type\":%u}\n",unsigned(e.type));return false;
    }
  return true;
}
bool retire() {
  bool ok=true;
  if(installed) {
    ok=checked(uart_driver_delete(modem),"uart_delete");
    if(!ok)return false;
    installed=false;
    for(auto pin:{tx,rx}) {
      ok=checked(gpio_reset_pin(pin),"pin_release")&&ok;
      ok=checked(gpio_set_direction(pin,GPIO_MODE_INPUT),"pin_input")&&ok;
      ok=checked(gpio_pullup_dis(pin),"pin_no_pullup")&&ok;
      ok=checked(gpio_pulldown_dis(pin),"pin_no_pulldown")&&ok;
    }
  }
  return ok;
}
bool exchange(unsigned seq,const char *command,int milliseconds,bool identity=false) {
  unsigned char raw[2048]{};size_t n=0;
  auto start=esp_timer_get_time();
  hex("tx",seq,reinterpret_cast<const unsigned char *>(command),std::strlen(command));
  if(uart_write_bytes(modem,command,std::strlen(command))!=int(std::strlen(command)))return false;
  if(!checked(uart_wait_tx_done(modem,pdMS_TO_TICKS(100)),"tx_done"))return false;
  int terminal=0;
  while(esp_timer_get_time()-start<int64_t(milliseconds)*1000) {
    if(!healthy())return false;
    int got=uart_read_bytes(modem,raw+n,sizeof(raw)-n-1,pdMS_TO_TICKS(20));
    if(got<0)return false;
    n+=size_t(got);raw[n]=0;
    if(n==sizeof(raw)-1)break;
    // Require a complete terminal line, not OK appearing in arbitrary text.
    const char *s=reinterpret_cast<const char *>(raw);
    if(std::strstr(s,"\nERROR\r\n")){terminal=-1;break;}
    if(std::strstr(s,"\nOK\r\n")){terminal=1;break;}
  }
  hex("rx",seq,raw,n);
  bool version=!identity || std::strstr(reinterpret_cast<const char *>(raw),"AT version:");
  bool pass=terminal==1 && version && !std::memchr(raw,0,n) && healthy();
  std::printf("NET008 {\"event\":\"command_result\",\"seq\":%u,\"pass\":%s,\"terminal\":%d,\"identity\":%s,\"bytes\":%u,\"elapsed_us\":%lld}\n",
              seq,pass?"true":"false",terminal,version?"true":"false",unsigned(n),static_cast<long long>(esp_timer_get_time()-start));
  return pass;
}
void run() {
  if(used){std::puts("NET008 {\"event\":\"refused\",\"reason\":\"already_invoked\"}");return;}
  used=true;bool pass=false;
  std::printf("NET008 {\"event\":\"start\",\"build\":\"%s\",\"tx\":48,\"rx\":47,\"baud\":115200}\n",NET008_BUILD_ID);
  uart_config_t cfg{};cfg.baud_rate=115200;cfg.data_bits=UART_DATA_8_BITS;
  cfg.parity=UART_PARITY_DISABLE;cfg.stop_bits=UART_STOP_BITS_1;
  cfg.flow_ctrl=UART_HW_FLOWCTRL_DISABLE;cfg.source_clk=UART_SCLK_DEFAULT;
  if(checked(uart_param_config(modem,&cfg),"uart_config") &&
     checked(uart_driver_install(modem,4096,0,32,&events,0),"uart_install")) {
    installed=true;
    if(checked(uart_set_pin(modem,tx,rx,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE),"uart_pins")) {
      // Only receive a bounded initial window; do not discard possible evidence.
      unsigned char prelude[1024];size_t n=0;auto end=esp_timer_get_time()+250000;
      while(n<sizeof(prelude) && esp_timer_get_time()<end) {
        int got=uart_read_bytes(modem,prelude+n,sizeof(prelude)-n,pdMS_TO_TICKS(20));
        if(got<0)break;
        n+=size_t(got);
      }
      hex("prelude",0,prelude,n);
      if(n<sizeof(prelude) && healthy()) {
        pass=exchange(1,"AT\r\n",2000) && exchange(2,"AT+GMR\r\n",3000,true);
        for(unsigned i=3;pass && i<=5;++i)pass=exchange(i,"AT\r\n",2000);
      }
    }
  }
  bool retired=retire();pass=pass&&retired;
  std::printf("NET008 {\"event\":\"end\",\"pass\":%s,\"uart_retired\":%s}\n",pass?"true":"false",retired?"true":"false");
}
void join(unsigned baud) {
 uint8_t private_bytes[98]{};size_t got=0,wanted=2;auto end=esp_timer_get_time()+5000000;
 std::puts("NET008 {\"event\":\"join_input_ready\"}");
 while(got<wanted&&esp_timer_get_time()<end){
  int n=usb_serial_jtag_read_bytes(private_bytes+got,wanted-got,pdMS_TO_TICKS(20));if(n<0)break;got+=size_t(n);
  if(got==2&&wanted==2){if(private_bytes[0]<1||private_bytes[0]>32||private_bytes[1]>64)break;wanted=2+private_bytes[0]+private_bytes[1];}
 }
 if(got==wanted&&wanted>2)net008_join(baud,private_bytes+2,private_bytes[0],private_bytes+2+private_bytes[0],private_bytes[1]);
 else std::puts("NET008 {\"event\":\"join_end\",\"pass\":false,\"phase\":\"private_input\",\"ip_ready\":false,\"uart_retired\":true}");
 n8join::wipe(private_bytes,sizeof(private_bytes));
}
void status() {
  std::printf("NET008 {\"event\":\"ready\",\"build\":\"%s\",\"source\":\"%s\",\"start_required\":true,\"used\":%s}\n",NET008_BUILD_ID,NET008_SOURCE_COMMIT,used?"true":"false");
}
}
extern "C" void app_main() {
  // Keep the shared D7/modem I/O bank powered at3.3V; never borrow its SD owner.
  esp_ldo_channel_config_t ldo{};ldo.chan_id=4;ldo.voltage_mv=3300;
  ESP_ERROR_CHECK(esp_ldo_acquire_channel(&ldo,&power));
  // Release both modem pins before either can become TX. GPIO47 must remain
  // input in this swapped assignment; never drive both connected modem lines.
  for(auto pin:{tx,rx}) {
    ESP_ERROR_CHECK(gpio_reset_pin(pin));ESP_ERROR_CHECK(gpio_set_direction(pin,GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(pin));ESP_ERROR_CHECK(gpio_pulldown_dis(pin));
  }
  // Release every existing mainboard lane and handshake; do not touch USB/LED.
  for(int n:{14,15,16,17,18,19,20,32,33,36,46}) {
    auto pin=gpio_num_t(n);
    ESP_ERROR_CHECK(gpio_reset_pin(pin));ESP_ERROR_CHECK(gpio_set_direction(pin,GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(pin));ESP_ERROR_CHECK(gpio_pulldown_dis(pin));
  }
  usb_serial_jtag_driver_config_t usb{};usb.tx_buffer_size=4096;usb.rx_buffer_size=256;
  ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&usb));usb_serial_jtag_vfs_use_driver();
  std::setvbuf(stdout,nullptr,_IONBF,0);
  status();
  char line[192]{};size_t n=0;bool overflow=false;
  for(;;) {
    char c;
    if(usb_serial_jtag_read_bytes(&c,1,pdMS_TO_TICKS(20))!=1)continue;
    if(c=='\n'||c=='\r') {
      if(n&&!overflow){
        line[n]=0;unsigned old_rate=0,new_rate=0,ms=0,port=0,nonce=0;char ip[64]{};char extra=0;
        if(!std::strcmp(line,"START"))run();
        else if(!std::strcmp(line,"STATUS"))status();
        else if(std::sscanf(line,"JOIN %u %c",&old_rate,&extra)==1&&old_rate>0&&old_rate<=1152000)join(old_rate);
        else if(std::sscanf(line,"INFO %u %c",&old_rate,&extra)==1&&old_rate>0&&old_rate<=1152000)net008_info(old_rate);
        else if(std::sscanf(line,"BENCH %u %u %u %63s %u %u %c",&old_rate,&new_rate,&ms,ip,&port,&nonce,&extra)==6)net008_bench(old_rate,new_rate,ms,ip,port,nonce);
        else std::puts("NET008 {\"event\":\"refused\",\"reason\":\"command\"}");
      }
      n=0;overflow=false;
    } else if(n+1<sizeof(line) && !overflow)line[n++]=c;else overflow=true;
  }
}
