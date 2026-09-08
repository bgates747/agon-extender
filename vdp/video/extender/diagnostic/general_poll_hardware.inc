// PORT-013 boot-TU-only hardware orchestration around the retained parser.
// Deliberately admits one fixed poll; not an activation protocol or public UART
// transport. Parser-produced reply bytes are buffered before hardware enqueue.
#include <driver/gpio.h>
#include <driver/uart.h>
#include <hal/uart_ll.h>
namespace {
constexpr uart_port_t gp_port = UART_NUM_1;
GeneralPollStream *gp_stream;
QueueHandle_t gp_events;
bool gp_released;
void gp_release() {
  if (gp_released) return;
  // ESP-IDF 5.5.5 has RX-only uart_flush. Disconnect TX before cancelling any
  // pending FIFO bytes, just as the proven flow fixture does. Remove this LL
  // workaround when the pinned public driver supplies bounded TX cancellation.
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_12));
  ESP_ERROR_CHECK(uart_disable_intr_mask(gp_port, UART_INTR_TX_DONE | UART_INTR_TXFIFO_EMPTY));
  uart_ll_txfifo_rst(UART_LL_GET_HW(gp_port));
  ESP_ERROR_CHECK(gpio_reset_pin(GPIO_NUM_11));
  for (int pin : {11,12}) {
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  gp_released=true;
}
}
void rejectGeneralPollDuplexChange() {
  if (gp_stream) gp_stream->transaction.fail("unsupported duplex change");
}
GeneralPollStream *beginGeneralPollQualification() {
  for (int pin : {9,10,11,12,13,14,15,17,20,21,22,23,32,33}) {
    ESP_ERROR_CHECK(gpio_reset_pin(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_set_direction(gpio_num_t(pin), GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,1));
  ESP_ERROR_CHECK(gpio_set_direction(GPIO_NUM_11,GPIO_MODE_OUTPUT));
  uart_config_t cfg={}; cfg.baud_rate=1152000; cfg.data_bits=UART_DATA_8_BITS;
  cfg.parity=UART_PARITY_DISABLE; cfg.stop_bits=UART_STOP_BITS_1;
  cfg.flow_ctrl=UART_HW_FLOWCTRL_CTS; cfg.source_clk=UART_SCLK_DEFAULT;
  ESP_ERROR_CHECK(uart_param_config(gp_port,&cfg));
  ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_12,1));
  ESP_ERROR_CHECK(uart_set_pin(gp_port,12,22,UART_PIN_NO_CHANGE,23));
  ESP_ERROR_CHECK(gpio_input_enable(GPIO_NUM_23));
  ESP_ERROR_CHECK(uart_driver_install(gp_port,1024,0,16,&gp_events,0));
  gp_stream=new GeneralPollStream;
  ESP_LOGI("general-poll","GENERAL POLL RECEIVER %s (%s)",AGON_EXTENDER_BUILD_ID,AGON_EXTENDER_ARTIFACT_STATUS);
  ESP_LOGI("general-poll","RX=22 TX=12 CTS=23 RTS=11 baud=1152000 8N1");
  return gp_stream;
}
void runGeneralPollQualification(VDUStreamProcessor *processor) {
  enum class Stage { waiting, receiving, sending, quiet, pass, fail };
  Stage stage=Stage::waiting;
  uint32_t since=millis(), report=since-1000;
  auto &t=gp_stream->transaction;
  for (;;) {
    const auto now=millis();
    uart_event_t ev;
    while (xQueueReceive(gp_events,&ev,0)==pdTRUE)
      if (ev.type!=UART_DATA) t.fail("UART error event");
    uint8_t bytes[32]; const int n=uart_read_bytes(gp_port,bytes,sizeof(bytes),0);
    if (n<0) t.fail("UART receive error");
    for (int i=0;i<n;++i) {
      if (stage!=Stage::receiving) t.fail("out-of-phase request bytes");
      else t.receive(bytes[i]);
    }
    const bool stopped=gpio_get_level(GPIO_NUM_23)!=0;
    if (stage==Stage::waiting && !stopped && !t.failure) {
      stage=Stage::receiving; since=now;
      ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,0));
      ESP_LOGI("general-poll","GENERAL POLL START build=%s",AGON_EXTENDER_BUILD_ID);
    }
    if (stage==Stage::receiving && t.received==4 && !t.failure) {
      ESP_ERROR_CHECK(gpio_set_level(GPIO_NUM_11,1));
      ESP_LOGI("general-poll","GENERAL POLL REQUEST hex=170080A5 build=%s",AGON_EXTENDER_BUILD_ID);
      if (!t.begin()) t.fail("parser admission failed");
      else {
        processor->processNext(); // Real VDU dispatch -> sendGeneralPoll -> send_packet.
        if (t.finish()) {
          ESP_LOGI("general-poll","GENERAL POLL PARSER reply=8001A5 build=%s",AGON_EXTENDER_BUILD_ID);
          if (uart_tx_chars(gp_port,reinterpret_cast<const char *>(t.output),3)!=3)
            t.fail("reply enqueue failed");
          else { stage=Stage::sending; since=now; }
        }
      }
    }
    if (stage==Stage::sending && !t.failure) {
      const auto tx=uart_wait_tx_done(gp_port,0);
      if (tx==ESP_OK) {
        ESP_LOGI("general-poll","GENERAL POLL SENT count=3 build=%s",AGON_EXTENDER_BUILD_ID);
        gp_release(); stage=Stage::quiet; since=now;
      } else if (tx!=ESP_ERR_TIMEOUT) t.fail("UART TX completion error");
    }
    if (stage==Stage::quiet && now-since>=250 && !t.failure) stage=Stage::pass;
    if (stage==Stage::waiting && now-since>=180000) t.fail("no EMOS start edge");
    if ((stage==Stage::receiving || stage==Stage::sending) && now-since>=5000)
      t.fail("transaction timeout");
    if (t.failure) { gp_release(); stage=Stage::fail; }
    if (now-report>=1000) {
      if (stage==Stage::waiting)
        ESP_LOGI("general-poll","GENERAL POLL WAIT received=0 cts=%d build=%s",stopped,AGON_EXTENDER_BUILD_ID);
      else if (stage==Stage::pass)
        ESP_LOGI("general-poll","GENERAL POLL PASS received=4 reply=3 build=%s",AGON_EXTENDER_BUILD_ID);
      else if (stage==Stage::fail)
        ESP_LOGE("general-poll","GENERAL POLL FAIL reason=%s build=%s",t.failure,AGON_EXTENDER_BUILD_ID);
      report=now;
    }
    delay(1);
  }
}
