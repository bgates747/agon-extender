// Single retained-parser owner for ordinary VDU, USB events and stock replies.
// USB callbacks only queue reports. Neither ISR nor network task writes UART1.
#include <driver/gpio.h>
#include <hal/uart_ll.h>
#include <esp_random.h>
#include "../input/p4_usb_host.hpp"
#include "../input/usb_cli_keyboard.hpp"
#include "../input/usb_key_queue.hpp"
namespace {
ConsoleStream *console_stream;
QueueHandle_t console_events;
agon::extender::input::UsbCliKeyboard console_keyboard;
agon::extender::input::UsbKeyQueue console_keys;
bool console_locale_pending{},console_admit_pending{},console_overload{};
void console_cancel_tx() {
  // IDF 5.5.5 flush is RX-only; inherited bounded TX cancellation from PORT-015.
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_12));
  ESP_ERROR_CHECK(uart_disable_intr_mask(UART_NUM_1,UART_INTR_TX_DONE|UART_INTR_TXFIFO_EMPTY));
  uart_ll_txfifo_rst(UART_LL_GET_HW(UART_NUM_1));
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_12,1));
  ESP_ERROR_CHECK(uart_set_pin(UART_NUM_1,12,22,11,23));
}
}
void consoleLayout(int region) {
  if (!console_keys.releaseAll()) console_stream->fail("layout release capacity");
  console_keyboard.admissionBoundary();
  console_keyboard.locale=region;
  console_locale_pending=region>=0 && region<=1;
}
void consolePoll() { if(console_locale_pending) console_admit_pending=true; }
void consoleControl(VDUStreamProcessor *processor, const uint8_t *p) {
  uint8_t reply[CONSOLE_SIZE];
  if (!console_stream->session.request(p,millis(),esp_random(),reply)) return;
  if(p[3]==CONSOLE_PREPARE) {
    // PORT-008 N002: raw changeMode() replaces Canvas with no selected font.
    // Skipping retained vdu_mode() context reset crashed on EMOS's first
    // VDU 26 (cursorHome -> getFont()->width). Use the complete stock lifecycle,
    // including drain, context/font reset and mode reply, before acknowledging
    // preparation. EMOS ignores that pre-commit mode reply in Legacy; its
    // post-commit queries still own publication. USB acquisition is separate.
    processor->vdu_mode(0);
  }
  // QUAL-003: PREPARE_KEEP deliberately leaves Canvas, contexts and resource
  // buffers intact. Its fresh lease is still required before ordinary output.
  console_stream->write(CONSOLE_REPLY);console_stream->write(CONSOLE_SIZE);
  console_stream->write(reply,sizeof(reply));
  printf("ExCom control op=%u active=%u\n",p[3],console_stream->session.active());
}
ConsoleStream *beginConsole() {
  for(int pin:{9,10,11,12,13,14,15,17,20,21,22,23,32,33}) {
    ESP_ERROR_CHECK(gpio_reset_pin(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_set_direction(gpio_num_t(pin),GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  uart_config_t cfg{};cfg.baud_rate=1152000;cfg.data_bits=UART_DATA_8_BITS;
  cfg.parity=UART_PARITY_DISABLE;cfg.stop_bits=UART_STOP_BITS_1;
  cfg.flow_ctrl=UART_HW_FLOWCTRL_CTS_RTS;cfg.rx_flow_ctrl_thresh=64;cfg.source_clk=UART_SCLK_DEFAULT;
  ESP_ERROR_CHECK(uart_param_config(UART_NUM_1,&cfg));
  ESP_ERROR_CHECK(uart_set_pin(UART_NUM_1,12,22,11,23));
  ESP_ERROR_CHECK(uart_driver_install(UART_NUM_1,4096,0,32,&console_events,0));
  console_stream=new ConsoleStream;
  if(!agon::extender::input::usbhost::begin()) console_stream->fail("USB host startup");
  printf("ExCom console %s (%s), UART1 1152000 8N1 RTS/CTS\n",AGON_EXTENDER_BUILD_ID,AGON_EXTENDER_ARTIFACT_STATUS);
  return console_stream;
}
void runConsole(VDUStreamProcessor *processor) {
  auto &s=*console_stream;
  auto &keyboard=console_keyboard;
  auto emit=[](agon::extender::input::ProcessedKey k){if(!console_keys.push(k))console_overload=true;};
  uint8_t incoming[3+CONSOLE_SIZE]{};
  unsigned used=0,need=3;
  uint32_t partial_at=0,tx_at=0;
  bool transmitting=false;
  for(;;) {
    const uint32_t now=millis();s.session.expire(now);
    agon::extender::input::usbhost::pump(
      [&](const uint8_t *p,size_t n){keyboard.report(p,n,now,emit);},
      [&](bool attached){if(!attached)keyboard.disconnect(emit);},
      [&](){keyboard.lost(emit);});
    if(console_overload) {
      if(!console_keys.releaseAll())s.fail("key release capacity");
      keyboard.lost([](agon::extender::input::ProcessedKey){});console_overload=false;
    }
    uart_event_t event;
    while(xQueueReceive(console_events,&event,0)==pdTRUE)
      if(event.type==UART_FIFO_OVF || event.type==UART_FRAME_ERR || event.type==UART_PARITY_ERR)
        s.fail("UART receive corruption");
    if(transmitting) {
      auto result=uart_wait_tx_done(UART_NUM_1,0);
      if(result==ESP_OK)transmitting=false;
      else if(result!=ESP_ERR_TIMEOUT)s.fail("TX completion");
      else if(now-tx_at>=5000) {
        console_cancel_tx();s.count=0;transmitting=false;s.session.cancel();
        console_keys.reset();keyboard.admissionBoundary();
        console_locale_pending=console_admit_pending=false;
        printf("ExCom UART blocked; awaiting fresh admission\n");
      }
    }
    if(!transmitting && s.count) {
      unsigned n=std::min<unsigned>(128,std::min<unsigned>(s.count,sizeof(s.output)-s.read_pos));
      int sent=uart_tx_chars(UART_NUM_1,reinterpret_cast<const char *>(s.output+s.read_pos),n);
      if(sent<0)s.fail("TX enqueue");
      else if(sent) {s.read_pos=(s.read_pos+sent)%sizeof(s.output);s.count-=sent;transmitting=true;tx_at=now;}
    }
    if(console_admit_pending && !s.count && !transmitting) {
      keyboard.admit();console_admit_pending=console_locale_pending=false;
      printf("ExCom native keyboard admitted\n");
    }
    // Leave enough reply capacity for one bounded stock parser invocation.
    // Parser reads may wait for continuation, but driver RTS protects its RX.
    if(s.count<4096) {
      agon::extender::input::ProcessedKey key;
      if(console_keys.pop(key)) {
        if(!agon::extender::input::processedKeyboard().push(key))s.fail("processed key queue");
        processor->processNext();
      } else if(s.session.active()) {
        unsigned budget=64;
        do {processor->processNext();} while(s.session.active() && s.available() && s.count<4096 && --budget);
      }
      else {
        uint8_t b;
        // Minimal preactivation recognizer: stock keyboard setup/poll exception
        // and fixed control envelope only. No ordinary VDU is reachable here.
        for(unsigned budget=0;budget<32 && uart_read_bytes(UART_NUM_1,&b,1,0)==1;++budget) {
          if(!used) {if(b!=23)continue;partial_at=now;need=3;}
          incoming[used++]=b;
          if(used==2 && b!=0){used=0;continue;}
          if(used==3) {
            if(b==CONSOLE_OPCODE)need=3+CONSOLE_SIZE;
            else if(b==0x80 || b==0x81)need=4;
            else {used=0;continue;}
          }
          if(used==need) {
            if(incoming[2]==CONSOLE_OPCODE)consoleControl(processor,incoming+3);
            else {s.feed(incoming);processor->processNext();}
            used=0;break;
          }
        }
        if(used && uint32_t(now-partial_at)>=250)used=0;
        // Cursor/event housekeeping still belongs to the retained processor.
        if(!used)processor->processNext();
      }
    }
    keyboard.tick(now,emit);
    if(s.failure) {
      keyboard.pause();console_cancel_tx();
      ESP_ERROR_CHECK(uart_set_hw_flow_ctrl(UART_NUM_1,UART_HW_FLOWCTRL_CTS,0));
      ESP_ERROR_CHECK(uart_set_rts(UART_NUM_1,1));
      printf("ExCom fault: %s; reset P4 before retry\n",s.failure);
      for(;;)delay(1000);
    }
    delay(1);
  }
}
