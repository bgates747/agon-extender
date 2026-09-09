// Native USB CLI candidate: one process owner serializes stock packets.
// Dedicated input composition, no browser acquisition or ordinary VDU routing.
#include <driver/gpio.h>
#include <driver/uart.h>
#include <hal/uart_ll.h>
#include "../input/p4_usb_host.hpp"
#include "../input/usb_cli_keyboard.hpp"
#include "../input/usb_key_queue.hpp"
namespace {
constexpr uart_port_t usb_cli_port=UART_NUM_1;
UsbCliStream *usb_cli_stream;
QueueHandle_t usb_cli_uart_events;
agon::extender::input::UsbCliKeyboard usb_cli_keyboard;
agon::extender::input::UsbKeyQueue usb_cli_keys;
void usb_cli_cancel_tx() {
  // IDF 5.5.5 uart_flush is RX-only. Disconnect TX before cancelling its FIFO,
  // as in the accepted UART fixtures; replace when public bounded cancellation exists.
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_12));
  ESP_ERROR_CHECK(uart_disable_intr_mask(usb_cli_port,UART_INTR_TX_DONE|UART_INTR_TXFIFO_EMPTY));
  uart_ll_txfifo_rst(UART_LL_GET_HW(usb_cli_port));
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_12,1));
  ESP_ERROR_CHECK(uart_set_pin(usb_cli_port,12,22,UART_PIN_NO_CHANGE,23));
}
}
void rejectKeyboardDuplexChange() { if (usb_cli_stream) usb_cli_stream->fail("duplex change"); }
UsbCliStream *beginKeyboardQualification() {
  for (int pin:{9,10,11,12,13,14,15,17,20,21,22,23,32,33}) {
    ESP_ERROR_CHECK(gpio_reset_pin(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_set_direction(gpio_num_t(pin),GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin))); ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  uart_config_t cfg{};cfg.baud_rate=1152000;cfg.data_bits=UART_DATA_8_BITS;
  cfg.parity=UART_PARITY_DISABLE;cfg.stop_bits=UART_STOP_BITS_1;
  cfg.flow_ctrl=UART_HW_FLOWCTRL_CTS;cfg.source_clk=UART_SCLK_DEFAULT;
  ESP_ERROR_CHECK(uart_param_config(usb_cli_port,&cfg));
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,1));
  ESP_ERROR_CHECK(gpio_set_direction(GPIO_NUM_11,GPIO_MODE_OUTPUT));
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_12,1));
  ESP_ERROR_CHECK(uart_set_pin(usb_cli_port,12,22,UART_PIN_NO_CHANGE,23));
  ESP_ERROR_CHECK(gpio_input_enable(GPIO_NUM_23));
  ESP_ERROR_CHECK(uart_driver_install(usb_cli_port,1024,0,16,&usb_cli_uart_events,0));
  usb_cli_stream=new UsbCliStream;
  if (!agon::extender::input::usbhost::begin()) usb_cli_stream->fail("USB host startup");
  printf("USB CLI %s (%s) RX=22 TX=12 CTS=23 RTS=11 baud=1152000 8N1\n",AGON_EXTENDER_BUILD_ID,AGON_EXTENDER_ARTIFACT_STATUS);
  return usb_cli_stream;
}
void runKeyboardQualification(VDUStreamProcessor *processor) {
  auto &stream=*usb_cli_stream;auto &keyboard=usb_cli_keyboard;auto &keys=usb_cli_keys;
  auto &processed=agon::extender::input::processedKeyboard();
  uint8_t command[4]{};unsigned used=0,sent=0;
  uint32_t partial_at=0,tx_at=0,status_at=0;
  bool transmitting=false,poll_tx=false,admitted=false,locale_seen=false,overload=false,boundary=false;
  auto emit=[&](agon::extender::input::ProcessedKey key) { if (!keys.push(key)) overload=true; };
  auto queue_output=[&]() {
    if (!stream.produced) return;
    if (uart_tx_chars(usb_cli_port,reinterpret_cast<const char *>(stream.output),stream.produced)!=int(stream.produced)) stream.fail("TX enqueue");
    else { transmitting=true;tx_at=millis(); }
  };
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,0));
  for (;;) {
    const uint32_t now=millis();
    // No cached timestamp crosses a concurrent input owner: USB callbacks only
    // queue reports; this task alone advances decode/repeat and UART state.
    agon::extender::input::usbhost::pump(
      [&](const uint8_t *p,size_t n){keyboard.report(p,n,now,emit);},
      [&](bool attached){if(!attached) keyboard.disconnect(emit);},
      [&](){keyboard.lost(emit);});
    if (overload) {
      if (!keys.releaseAll()) stream.fail("release capacity");
      keyboard.lost([](agon::extender::input::ProcessedKey){});overload=false;
      printf("USB CLI input backlog: held keys released; release physical keys\n");
    }
    uart_event_t event;
    while(xQueueReceive(usb_cli_uart_events,&event,0)==pdTRUE)
      if(event.type!=UART_DATA) stream.fail("UART receive error");
    if (used<4) {
      int n=uart_read_bytes(usb_cli_port,command+used,4-used,0);
      if(n<0) stream.fail("UART read");
      else if(n) { if(!used) partial_at=now;used+=unsigned(n); }
    }
    if (used && used<4 && now-partial_at>=250) stream.fail("partial command timeout");
    if (used==4 && !boundary) {
      ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,1));
      if(command[0]!=23 || command[1]!=0 || (command[2]!=0x81 && command[2]!=0x80)) stream.fail("unsupported command");
      // Old accepted frames/releases precede the reply. EMOS discards old
      // keyboard frames while preparing and commits only the matching poll.
      if(!keys.releaseAll()) stream.fail("admission release capacity");
      keyboard.admissionBoundary();admitted=false;boundary=true;
    }
    if(transmitting) {
      auto result=uart_wait_tx_done(usb_cli_port,0);
      if(result==ESP_OK) {
        transmitting=false;stream.produced=0;
        if(poll_tx) { poll_tx=false;admitted=true;keyboard.admit();printf("USB CLI READY: native keyboard admitted\n"); }
      } else if(result!=ESP_ERR_TIMEOUT) stream.fail("TX completion");
      else if(now-tx_at>=5000) {
        // Stock UART has no exit packet: source return/reset can leave CTS
        // blocked. Cancel stale bytes and require a new locale/poll admission.
        usb_cli_cancel_tx();transmitting=poll_tx=admitted=locale_seen=false;
        stream.produced=0;keys.reset();keyboard.admissionBoundary();
        printf("USB CLI WAIT: blocked TX cancelled; awaiting EMOS admission\n");
      }
    }
    if(!transmitting && !stream.failure) {
      agon::extender::input::ProcessedKey key;
      if(keys.pop(key)) {
        if(!processed.push(key)) stream.fail("processed queue");
        else {
          processor->processNext();
          const uint8_t expected[]={0x81,4,key.keycode,key.modifiers,key.virtual_key,key.down};
          if(processed.size() || stream.produced!=6 || std::memcmp(stream.output,expected,6)) stream.fail("key serializer");
          else { queue_output();++sent; }
        }
      } else if(used==4) {
        if(command[2]==0x81) {
          locale_seen=command[3]<=1;
          keyboard.locale=command[3];
          if(!locale_seen) printf("USB CLI unsupported keyboard layout %u (UK=0, US=1)\n",command[3]);
        }
        if(command[2]==0x81 || locale_seen) {
          if(stream.command(command)) {processor->processNext();stream.commandDone();}
          if(command[2]==0x80 && !stream.failure) {
            const uint8_t expected[]={0x80,1,command[3]};
            if(stream.produced!=3 || std::memcmp(stream.output,expected,3)) stream.fail("poll serializer");
            else {poll_tx=true;queue_output();}
          }
        }
        used=0;boundary=false;ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,0));
      } else if(admitted) keyboard.tick(now,emit);
    }
    if(stream.failure) {
      keyboard.pause();ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,1));usb_cli_cancel_tx();
      printf("USB CLI FAULT: %s; reset P4 before retry\n",stream.failure);
      for(;;) delay(1000);
    }
    if(now-status_at>=5000) {
      printf("USB CLI STATUS admitted=%u attached=%u keys_sent=%u\n",admitted,agon::extender::input::usbhost::attached(),sent);status_at=now;
    }
    delay(1);
  }
}
