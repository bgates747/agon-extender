// Focused browser typing around the retained VDU parser and key serializer.
// One process task owns UART RX/TX; the HTTP task only queues browser events.
#include <driver/gpio.h>
#include <driver/uart.h>
#include <hal/uart_ll.h>
namespace {
constexpr uart_port_t key_port=UART_NUM_1;
BrowserTypingStream *key_stream;
QueueHandle_t key_events;
bool key_released;
uint32_t typing_tx_id{},typing_command_id{};
using agon::extender::diagnostic::trace;
uint32_t packTrace(const uint8_t *p,unsigned n) {
  uint32_t v=0; for(unsigned i=0;i<n && i<4;++i) v|=uint32_t(p[i])<<(8*i); return v;
}
void key_connect() {
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,1));
  ESP_ERROR_CHECK(gpio_set_direction(GPIO_NUM_11,GPIO_MODE_OUTPUT));
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_12,1));
  ESP_ERROR_CHECK(uart_set_pin(key_port,12,22,UART_PIN_NO_CHANGE,23));
  ESP_ERROR_CHECK(gpio_input_enable(GPIO_NUM_23));
  key_released=false;
}
void key_release() {
  if (key_released) return;
  // ESP-IDF 5.5.5 uart_flush is RX-only. Disconnect TX before cancelling its
  // FIFO, as in the accepted UART fixtures. Remove when public bounded TX
  // cancellation exists in the selected driver.
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_12));
  ESP_ERROR_CHECK(uart_disable_intr_mask(key_port,UART_INTR_TX_DONE|UART_INTR_TXFIFO_EMPTY));
  uart_ll_txfifo_rst(UART_LL_GET_HW(key_port));
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_11));
  for (int pin : {11,12}) {
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  key_released=true;
}
bool key_transmit() {
  const auto n=key_stream->produced;
  ++typing_tx_id;
  trace("uart_submit",typing_tx_id,n,packTrace(key_stream->output,n),n>4?packTrace(key_stream->output+4,n-4):0);
  if (!n || uart_tx_chars(key_port,reinterpret_cast<const char *>(key_stream->output),n)!=int(n)) {
    key_stream->fail("UART enqueue"); return false;
  }
  return true;
}
}
void rejectBrowserTypingDuplex() {
  if (key_stream) key_stream->fail("unsupported duplex change");
}
BrowserTypingStream *beginBrowserTyping() {
  agon::extender::diagnostic::browserTrace().begin();
  trace("typing_start");
  for (int pin : {9,10,11,12,13,14,15,17,20,21,22,23,32,33}) {
    ESP_ERROR_CHECK(gpio_reset_pin(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_set_direction(gpio_num_t(pin),GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  uart_config_t cfg={}; cfg.baud_rate=1152000; cfg.data_bits=UART_DATA_8_BITS;
  cfg.parity=UART_PARITY_DISABLE; cfg.stop_bits=UART_STOP_BITS_1;
  cfg.flow_ctrl=UART_HW_FLOWCTRL_CTS; cfg.source_clk=UART_SCLK_DEFAULT;
  ESP_ERROR_CHECK(uart_param_config(key_port,&cfg));
  key_connect();
  ESP_ERROR_CHECK(uart_driver_install(key_port,1024,0,16,&key_events,0));
  key_stream=new BrowserTypingStream;
  ESP_LOGI("keyboard","BROWSER TYPING %s (%s)",AGON_EXTENDER_BUILD_ID,AGON_EXTENDER_ARTIFACT_STATUS);
  ESP_LOGI("keyboard","RX=22 TX=12 CTS=23 RTS=11 baud=1152000 8N1");
  return key_stream;
}
void runBrowserTyping(VDUStreamProcessor *processor) {
  auto &stream=*key_stream;
  auto &browser=agon::extender::input::browserKeyboard();
  auto &input=agon::extender::input::processedKeyboard();
  bool active=false, layout_seen=false, admitted=false, transmitting=false, rx_paused=false;
  uint8_t command[4]{}; unsigned used=0, needed=1;
  uint32_t partial_at=0, tx_at=0, stopped_at=millis();
  for (;;) {
    const auto now=millis();
    browser.expire(now); // lease revocation also runs while UART TX is paused
    const bool stopped=gpio_get_level(GPIO_NUM_23)!=0;
    if (!stopped) stopped_at=now;
    uart_event_t event;
    while (xQueueReceive(key_events,&event,0)==pdTRUE)
      if (event.type!=UART_DATA) stream.fail("UART error event");
    // Long CTS stop terminates this bounded session. Ordinary receive-ISR
    // CTS pulses are much shorter and never imply keyboard revocation.
    if ((active || stream.failure) && stopped && now-stopped_at>=1000) {
      trace("uart_session_stop",0,now-stopped_at);
      browser.ready(false); key_release(); input.reset(); stream=BrowserTypingStream{};
      uart_flush_input(key_port); xQueueReset(key_events);
      active=layout_seen=admitted=transmitting=false; used=0; needed=1;
    }
    if (!active && !stopped && !stream.failure) {
      if (key_released) key_connect();
      gpio_set_level(GPIO_NUM_11,0); rx_paused=false; active=true;
      ESP_LOGI("typing","TYPING UART READY build=%s",AGON_EXTENDER_BUILD_ID);
    }
    if (active && !stream.failure) {
      size_t buffered=0;
      ESP_ERROR_CHECK(uart_get_buffered_data_len(key_port,&buffered));
      if ((!rx_paused && buffered>=512) || (rx_paused && buffered<=256)) {
        rx_paused=!rx_paused;
        ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,rx_paused?1:0));
      }
    }
    if (transmitting && !stream.failure) {
      auto result=uart_wait_tx_done(key_port,0);
      if (result==ESP_OK) { trace("uart_done_observed",typing_tx_id); transmitting=false; stream.produced=0; }
      else if (result!=ESP_ERR_TIMEOUT || now-tx_at>=5000) stream.fail("TX timeout");
    }
    if (active && !transmitting && !stream.failure) {
      // Consume at most one complete VDU unit. Parameter reads never wait for
      // arbitrary future bytes inside the retained parser.
      uint8_t byte;
      while (used<needed && uart_read_bytes(key_port,&byte,1,0)==1) {
        if (!used) partial_at=now;
        command[used++]=byte;
        if (used==1) {
          if (byte==23 || byte==31) needed=3;
          else if (!((byte>=32&&byte<=126)||(byte>=8&&byte<=13)||byte==30)) stream.fail("unsupported VDU unit");
        }
        if (used==3 && command[0]==23) {
          if (command[1] || (command[2]!=0x80 && command[2]!=0x81 && command[2]!=0xCA)) stream.fail("unsupported system command");
          if (command[2]!=0xCA) needed=4;
        }
        if (stream.failure) break;
      }
      if (used && used==needed && !stream.failure) {
        ++typing_command_id;
        trace("vdu_received",typing_command_id,packTrace(command,needed),needed);
        if (!layout_seen && !(needed==4&&command[0]==23&&command[2]==0x81&&command[3]==1)) stream.fail("expected US locale admission");
        if (stream.command(command,needed) && !stream.failure) {
          processor->processNext();
          trace(command[0]==23 && command[2]==0xCA ? "draw_flush_done" : "vdu_parser_return",typing_command_id);
          if (stream.available()) stream.fail("parser consumption");
          if (command[0]==23 && command[2]==0x81) {
            if (kbRegion!=1) stream.fail("typing probe requires US locale");
            else layout_seen=true;
          }
          if (layout_seen && command[0]==23 && command[2]==0x80 && !admitted) {
            admitted=true; browser.ready(true);
            ESP_LOGI("typing","TYPING READY: browser focus may supply keys build=%s",AGON_EXTENDER_BUILD_ID);
          }
        }
        used=0; needed=1;
      }
      if (used && now-partial_at>=250) stream.fail("partial VDU timeout");
      if (!stream.produced && admitted && !stream.failure) {
        agon::extender::input::ProcessedKey key;
        if (browser.pop(key,now)) {
          trace("key_pop",0,key.keycode,key.down,key.modifiers);
          if (!input.push(key)) stream.fail("processed queue overflow");
          else processor->processNext();
        }
      }
      if (stream.produced && !stream.failure && key_transmit()) { transmitting=true; tx_at=now; }
    }
    if (stream.failure) {
      browser.ready(false); key_release();
      if (active) trace("uart_failure");
      if (active) trace(stream.failure);
      if (active) ESP_LOGE("typing","TYPING FAIL %s build=%s",stream.failure,AGON_EXTENDER_BUILD_ID);
      active=false;
    }
    delay(1);
  }
}
