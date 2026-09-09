// PORT-005 controlled-event qualification around the normal processed input
// helper, retained parser and serializer. All UART/parsing/emission has one
// process-task owner. No per-key request/ACK; no browser or mode activation.
#include <driver/gpio.h>
#include <driver/uart.h>
#include <hal/uart_ll.h>
namespace {
constexpr uart_port_t key_port=UART_NUM_1;
KeyboardProbeStream *key_stream;
QueueHandle_t key_events;
bool key_released;
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
  if (!n || uart_tx_chars(key_port,reinterpret_cast<const char *>(key_stream->output),n)!=int(n)) {
    key_stream->fail("UART enqueue"); return false;
  }
  return true;
}
}
void rejectKeyboardDuplexChange() {
  if (key_stream) key_stream->fail("unsupported duplex change");
}
KeyboardProbeStream *beginKeyboardQualification() {
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
  key_stream=new KeyboardProbeStream;
  ESP_LOGI("keyboard","KEYBOARD SENDER %s (%s)",AGON_EXTENDER_BUILD_ID,AGON_EXTENDER_ARTIFACT_STATUS);
  ESP_LOGI("keyboard","RX=22 TX=12 CTS=23 RTS=11 baud=1152000 8N1");
  return key_stream;
}
void runKeyboardQualification(VDUStreamProcessor *processor) {
  enum class Stage { waiting, command, poll_tx, keys, key_tx, complete, fail };
  Stage stage=Stage::waiting;
  uint32_t since=millis(), report=since-1000, partial_at=since;
  uint8_t command[4]{}; unsigned used=0, index=0, cycle=0;
  bool layout_seen=false, pass_logged=false;
  auto &stream=*key_stream;
  auto &input=agon::extender::input::processedKeyboard();
  for (;;) {
    const auto now=millis();
    const bool stopped=gpio_get_level(GPIO_NUM_23)!=0;
    uart_event_t event;
    while (xQueueReceive(key_events,&event,0)==pdTRUE)
      if (event.type!=UART_DATA) stream.fail("UART error event");
    // This fixture admits commands only during readiness. Unexpected bytes
    // after admission must not survive to impersonate the next test cycle.
    if (stage!=Stage::waiting && stage!=Stage::command && stage!=Stage::fail) {
      size_t buffered=0;
      ESP_ERROR_CHECK(uart_get_buffered_data_len(key_port,&buffered));
      if (buffered) stream.fail("unexpected command after admission");
    }
    if (stage==Stage::waiting && !stopped && !stream.failure) {
      if (key_released) key_connect();
      ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,0));
      input.reset(); stage=Stage::command; since=now;
      layout_seen=pass_logged=false; used=index=0;
      ESP_LOGI("keyboard","KEYBOARD START cycle=%u build=%s",++cycle,AGON_EXTENDER_BUILD_ID);
    }
    if (stage==Stage::command && !stream.failure) {
      const int n=uart_read_bytes(key_port,command+used,sizeof(command)-used,0);
      if (n<0) stream.fail("UART read");
      else if (n) { if (!used) partial_at=now; used+=unsigned(n); }
      if (used==4) {
        if (!layout_seen && command[2]!=0x81) stream.fail("missing locale before poll");
        if (stream.command(command) && !stream.failure) {
          processor->processNext();
          if (stream.commandDone()) {
            if (command[2]==0x81) {
              if (stream.produced) stream.fail("unexpected locale reply");
              layout_seen=true;
              ESP_LOGI("keyboard","KEYBOARD LOCALE %u build=%s",unsigned(kbRegion),AGON_EXTENDER_BUILD_ID);
            } else {
              const uint8_t expected[]={0x80,1,command[3]};
              if (stream.produced!=3 || std::memcmp(stream.output,expected,3)) stream.fail("poll serializer");
              else if (key_transmit()) {
                stage=Stage::poll_tx; since=now;
                ESP_LOGI("keyboard","KEYBOARD POLL token=%u build=%s",unsigned(command[3]),AGON_EXTENDER_BUILD_ID);
              }
            }
          }
        }
        used=0;
      }
      if (used && now-partial_at>=250) stream.fail("partial command timeout");
      if (now-since>=5000) stream.fail("admission timeout");
    }
    if ((stage==Stage::poll_tx || stage==Stage::key_tx) && !stream.failure) {
      const auto result=uart_wait_tx_done(key_port,0);
      if (result==ESP_OK) {
        stream.produced=0;
        if (stage==Stage::key_tx) {
          ESP_LOGI("keyboard","KEYBOARD EVENT %u SENT build=%s",index,AGON_EXTENDER_BUILD_ID);
        }
        if (index==std::size(keyboardProbeEvents)) stage=Stage::complete;
        else stage=Stage::keys;
        since=now;
      } else if (result!=ESP_ERR_TIMEOUT) stream.fail("UART TX completion");
      else if (now-since>=5000) stream.fail("UART TX timeout");
    }
    if (stage==Stage::keys && !stream.failure && now-since>=(index ? 250u : 500u)) {
      const auto &key=keyboardProbeEvents[index];
      if (!input.push(key)) stream.fail("processed input rejected");
      else {
        processor->processNext(); // Normal acquisition/callback/event/serializer path.
        const uint8_t expected[]={0x81,4,key.keycode,key.modifiers,key.virtual_key,key.down};
        if (input.size() || stream.produced!=6 || std::memcmp(stream.output,expected,6)) stream.fail("key serializer");
        else if (key_transmit()) { ++index; stage=Stage::key_tx; since=now; }
      }
    }
    if (stage==Stage::complete && !stream.failure && now-since>=250) {
      if (!pass_logged) {
        ESP_LOGI("keyboard","KEYBOARD SENDER PASS events=12 key_bytes=72 build=%s",AGON_EXTENDER_BUILD_ID);
        pass_logged=true;
      }
      // Rearm only after successful completion and EMOS source release. CTS
      // pulses during active ISR service are NOT admission/exit messages.
      if (stopped) {
        key_release(); stage=Stage::waiting; report=now-1000;
      }
    }
    if (stream.failure) { key_release(); stage=Stage::fail; }
    if (now-report>=1000) {
      if (stage==Stage::waiting)
        ESP_LOGI("keyboard","KEYBOARD WAIT cts=%d build=%s",stopped,AGON_EXTENDER_BUILD_ID);
      else if (stage==Stage::fail)
        ESP_LOGE("keyboard","KEYBOARD FAIL reason=%s build=%s",stream.failure,AGON_EXTENDER_BUILD_ID);
      report=now;
    }
    delay(1);
  }
}
