// PORT-014 boot-TU-only hardware orchestration around the retained parser.
// Admits repeated fixed text/flush/poll transactions; not product activation.
// Parser-produced replies are buffered before hardware enqueue. After success,
// wait for EMOS to release RTS before accepting a fresh request. Keep the
// framebuffer and parser alive so opening the browser later still works.
#include <driver/gpio.h>
#include <driver/uart.h>
#include <hal/uart_ll.h>
namespace {
constexpr uart_port_t vt_port = UART_NUM_1;
VisibleTextStream *vt_stream;
QueueHandle_t vt_events;
bool vt_released;
void vt_connect() {
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,1));
  ESP_ERROR_CHECK(gpio_set_direction(GPIO_NUM_11,GPIO_MODE_OUTPUT));
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_12,1));
  ESP_ERROR_CHECK(uart_set_pin(vt_port,12,22,UART_PIN_NO_CHANGE,23));
  ESP_ERROR_CHECK(gpio_input_enable(GPIO_NUM_23));
  vt_released=false;
}
void vt_release() {
  if (vt_released) return;
  // ESP-IDF 5.5.5 has RX-only uart_flush. Disconnect TX before cancelling any
  // pending FIFO bytes, just as the proven flow fixture does. Remove this LL
  // workaround when the pinned public driver supplies bounded TX cancellation.
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_12));
  ESP_ERROR_CHECK(uart_disable_intr_mask(vt_port, UART_INTR_TX_DONE | UART_INTR_TXFIFO_EMPTY));
  uart_ll_txfifo_rst(UART_LL_GET_HW(vt_port));
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_11));
  for (int pin : {11,12}) {
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  vt_released=true;
}
}
void rejectVisibleTextDuplexChange() {
  if (vt_stream) vt_stream->transaction.fail("unsupported duplex change");
}
VisibleTextStream *beginVisibleTextQualification() {
  for (int pin : {9,10,11,12,13,14,15,17,20,21,22,23,32,33}) {
    ESP_ERROR_CHECK(gpio_reset_pin(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_set_direction(gpio_num_t(pin), GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  uart_config_t cfg={}; cfg.baud_rate=1152000; cfg.data_bits=UART_DATA_8_BITS;
  cfg.parity=UART_PARITY_DISABLE; cfg.stop_bits=UART_STOP_BITS_1;
  cfg.flow_ctrl=UART_HW_FLOWCTRL_CTS; cfg.source_clk=UART_SCLK_DEFAULT;
  ESP_ERROR_CHECK(uart_param_config(vt_port,&cfg));
  vt_connect();
  ESP_ERROR_CHECK(uart_driver_install(vt_port,1024,0,16,&vt_events,0));
  vt_stream=new VisibleTextStream;
  ESP_LOGI("visible-text","VISIBLE TEXT RECEIVER %s (%s)",AGON_EXTENDER_BUILD_ID,AGON_EXTENDER_ARTIFACT_STATUS);
  ESP_LOGI("visible-text","RX=22 TX=12 CTS=23 RTS=11 baud=1152000 8N1");
  return vt_stream;
}
void runVisibleTextQualification(VDUStreamProcessor *processor) {
  enum class Stage { waiting, receiving, sending, quiet, pass, fail };
  Stage stage=Stage::waiting;
  uint32_t since=millis(), report=since-1000;
  auto &t=vt_stream->transaction;
  unsigned cycle=0;
  for (;;) {
    const auto now=millis();
    uart_event_t ev;
    while (xQueueReceive(vt_events,&ev,0)==pdTRUE)
      if (ev.type!=UART_DATA) t.fail("UART error event");
    uint8_t bytes[32]; const int n=uart_read_bytes(vt_port,bytes,sizeof(bytes),0);
    if (n<0) t.fail("UART receive error");
    for (int i=0;i<n;++i) {
      if (stage!=Stage::receiving) t.fail("out-of-phase request bytes");
      else t.receive(bytes[i]);
    }
    const bool stopped=gpio_get_level(GPIO_NUM_23)!=0;
    if (stage==Stage::waiting && !stopped && !t.failure) {
      if (vt_released) vt_connect();
      stage=Stage::receiving; since=now;
      ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,0));
      ESP_LOGI("visible-text","VISIBLE TEXT CYCLE %u build=%s",++cycle,AGON_EXTENDER_BUILD_ID);
      ESP_LOGI("visible-text","VISIBLE TEXT START build=%s",AGON_EXTENDER_BUILD_ID);
    }
    if (stage==Stage::receiving && t.received==sizeof(t.input) && !t.failure) {
      ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,1));
      ESP_LOGI("visible-text","VISIBLE TEXT REQUEST hex=0C1F0202454D4F5320544F204544503A205541525420544558540D0A1700CA170080A6 build=%s",AGON_EXTENDER_BUILD_ID);
      if (!t.begin()) t.fail("parser admission failed");
      else {
        // Every command is dispatched by the retained parser. A complete fixed
        // request prevents waiting on partial command parameters; require
        // forward progress for each parser call. Flush precedes the real GP.
        while (t.available() && !t.failure) {
          const auto consumed=t.consumed;
          processor->processNext();
          if (t.consumed<=consumed) t.fail("retained parser made no progress");
          if (millis()-since>=5000) t.fail("retained parser deadline");
        }
        if (t.finish()) {
          ESP_LOGI("visible-text","VISIBLE TEXT PARSER reply=8001A6 build=%s",AGON_EXTENDER_BUILD_ID);
          if (uart_tx_chars(vt_port,reinterpret_cast<const char *>(t.output),3)!=3)
            t.fail("reply enqueue failed");
          else { stage=Stage::sending; since=now; }
        }
      }
    }
    if (stage==Stage::sending && !t.failure) {
      const auto tx=uart_wait_tx_done(vt_port,0);
      if (tx==ESP_OK) {
        ESP_LOGI("visible-text","VISIBLE TEXT SENT count=3 build=%s",AGON_EXTENDER_BUILD_ID);
        vt_release(); stage=Stage::quiet; since=now;
      } else if (tx!=ESP_ERR_TIMEOUT) t.fail("UART TX completion error");
    }
    if (stage==Stage::quiet && now-since>=250 && !t.failure) {
      stage=Stage::pass;
      ESP_LOGI("visible-text","VISIBLE TEXT PASS received=35 reply=3 build=%s",AGON_EXTENDER_BUILD_ID);
    }
    // A stopped peer marks the end of EMOS's receive/quiet interval. Never
    // replay a reply or treat the still-active request as a new transaction.
    // Idle waiting has no expiry; only active exchanges have deadlines.
    if (stage==Stage::pass && stopped && !t.failure) {
      t=VisibleTextTransaction{};
      stage=Stage::waiting; since=now; report=now-1000;
    }
    if ((stage==Stage::receiving || stage==Stage::sending) && now-since>=5000)
      t.fail("transaction timeout");
    if (t.failure) { vt_release(); stage=Stage::fail; }
    if (now-report>=1000) {
      if (stage==Stage::waiting)
        ESP_LOGI("visible-text","VISIBLE TEXT WAIT received=0 cts=%d build=%s",stopped,AGON_EXTENDER_BUILD_ID);
      else if (stage==Stage::fail)
        ESP_LOGE("visible-text","VISIBLE TEXT FAIL reason=%s build=%s",t.failure,AGON_EXTENDER_BUILD_ID);
      report=now;
    }
    delay(1);
  }
}
