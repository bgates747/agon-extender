#include "extender/transport/forward_parallel_stream.hpp"

#include <cstring>

#include <driver/gpio.h>
#include <esp_heap_caps.h>
#include <esp_log.h>
#include <hal/cache_hal.h>
#include <hal/cache_ll.h>

#ifndef CONFIG_IDF_TARGET_ESP32P4
#error "PORT-008 forward parallel transport requires ESP32-P4"
#endif

namespace agon::extender::transport {
namespace {

constexpr char kTag[] = "extender_forward";
constexpr gpio_num_t kReadyPin = GPIO_NUM_20;
constexpr gpio_num_t kClockPin = GPIO_NUM_14;
constexpr gpio_num_t kValidPin = GPIO_NUM_13;
constexpr gpio_num_t kDataPins[] = {
    GPIO_NUM_22, GPIO_NUM_12, GPIO_NUM_23, GPIO_NUM_11,
    GPIO_NUM_32, GPIO_NUM_10, GPIO_NUM_33, GPIO_NUM_9,
};
constexpr std::uint32_t kExpectedExternalClockHz = 10'000'000;
constexpr std::uint32_t kValidSignalLine = PARLIO_RX_UNIT_MAX_DATA_WIDTH - 1;

std::size_t alignUp(std::size_t value, std::size_t alignment) {
  return (value + alignment - 1) & ~(alignment - 1);
}

}  // namespace

bool IRAM_ATTR ForwardParallelStream::receiveDone(
    parlio_rx_unit_handle_t, parlio_rx_event_data_t const *event,
    void *user_data) {
  auto *state = static_cast<ReceiveState *>(user_data);
  state->received = event->recv_bytes;
  return false;
}

bool ForwardParallelStream::releaseReady() {
  // READY_N is open drain: writing one releases the line to the external
  // pull-up; writing zero admits one sender transaction.
  return gpio_set_level(kReadyPin, 1) == ESP_OK;
}

bool ForwardParallelStream::configureHardware() {
  // Preload the released output latch before enabling open-drain output so
  // boot cannot briefly advertise readiness before PARLIO DMA is armed.
  if (gpio_set_level(kReadyPin, 1) != ESP_OK) return false;
  gpio_config_t const ready_config = {
      .pin_bit_mask = UINT64_C(1) << kReadyPin,
      .mode = GPIO_MODE_INPUT_OUTPUT_OD,
      .pull_up_en = GPIO_PULLUP_DISABLE,
      .pull_down_en = GPIO_PULLDOWN_DISABLE,
      .intr_type = GPIO_INTR_DISABLE,
  };
  if (gpio_config(&ready_config) != ESP_OK || !releaseReady()) return false;

  parlio_rx_unit_config_t const unit_config = {
      .trans_queue_depth = 2,
      .max_recv_size = kMaximumRecordBytes,
      .dma_burst_size = 64,
      .data_width = 8,
      .clk_src = PARLIO_CLK_SRC_EXTERNAL,
      .ext_clk_freq_hz = kExpectedExternalClockHz,
      .exp_clk_freq_hz = kExpectedExternalClockHz,
      .clk_in_gpio_num = kClockPin,
      .clk_out_gpio_num = GPIO_NUM_NC,
      .valid_gpio_num = kValidPin,
      .data_gpio_nums = {
          kDataPins[0], kDataPins[1], kDataPins[2], kDataPins[3],
          kDataPins[4], kDataPins[5], kDataPins[6], kDataPins[7],
      },
      .flags = {
          .free_clk = true,
          .clk_gate_en = false,
      },
  };
  parlio_rx_level_delimiter_config_t const delimiter_config = {
      .valid_sig_line_id = kValidSignalLine,
      .sample_edge = PARLIO_SAMPLE_EDGE_NEG,
      .bit_pack_order = PARLIO_BIT_PACK_ORDER_LSB,
      // ESP-IDF 5.5.5 defines zero as EOF on VALID_N deassertion. This is the
      // key reason raw variable-length VDU streams need no length prefix.
      .eof_data_len = 0,
      .timeout_ticks = 0,
      .flags = {
          .active_low_en = true,
      },
  };

  if (parlio_new_rx_level_delimiter(&delimiter_config, &delimiter_) != ESP_OK)
    return false;
  if (parlio_new_rx_unit(&unit_config, &rx_unit_) != ESP_OK) return false;
  parlio_rx_event_callbacks_t const callbacks = {
      .on_receive_done = receiveDone,
  };
  if (parlio_rx_unit_register_event_callbacks(rx_unit_, &callbacks,
                                               &receive_state_) != ESP_OK)
    return false;
  if (parlio_rx_unit_enable(rx_unit_, true) != ESP_OK) return false;

  std::uint32_t alignment =
      cache_hal_get_cache_line_size(CACHE_LL_LEVEL_INT_MEM, CACHE_TYPE_DATA);
  if (alignment < 4) alignment = 4;
  dma_buffer_ = static_cast<std::uint8_t *>(heap_caps_aligned_calloc(
      alignment, 1, alignUp(kMaximumRecordBytes, alignment),
      MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));
  return dma_buffer_ != nullptr;
}

bool ForwardParallelStream::begin() {
  if (stream_buffer_ != nullptr) return true;
  stream_buffer_ = xStreamBufferCreate(kStreamCapacityBytes, 1);
  if (stream_buffer_ == nullptr || !configureHardware()) {
    (void)releaseReady();
    ESP_LOGE(kTag, "forward transport setup failed; READY_N released");
    return false;
  }
  if (xTaskCreate(receiverTaskEntry, "forwardRx", 4096, this, 4,
                  &receiver_task_) != pdPASS) {
    (void)releaseReady();
    ESP_LOGE(kTag, "forward receiver task creation failed; READY_N released");
    return false;
  }
  ESP_LOGI(kTag,
           "r01 receiver started D=22,12,23,11,32,10,33,9 CLK=14 "
           "VALID_N=13 READY_N=20 return=discard-only");
  return true;
}

void ForwardParallelStream::receiverTaskEntry(void *parameter) {
  static_cast<ForwardParallelStream *>(parameter)->receiverTask();
}

void ForwardParallelStream::receiverTask() {
  parlio_receive_config_t const receive_config = {
      .delimiter = delimiter_,
      .flags = {
          .partial_rx_en = false,
          .indirect_mount = false,
      },
  };

  for (;;) {
    // Never admit a record unless the complete maximum transaction can be
    // queued without truncation. READY_N is the physical backpressure owner.
    while (xStreamBufferSpacesAvailable(stream_buffer_) <
           kMaximumRecordBytes) {
      vTaskDelay(pdMS_TO_TICKS(1));
    }

    receive_state_.received = 0;
    esp_err_t result = parlio_rx_unit_receive(
        rx_unit_, dma_buffer_, kMaximumRecordBytes, &receive_config);
    if (result == ESP_OK) result = gpio_set_level(kReadyPin, 0);
    if (result == ESP_OK) result = parlio_rx_unit_wait_all_done(rx_unit_, -1);
    bool const released = releaseReady();
    if (result != ESP_OK || !released || receive_state_.received == 0 ||
        receive_state_.received > kMaximumRecordBytes) {
      receive_failures_.fetch_add(1, std::memory_order_relaxed);
      ESP_LOGE(kTag, "receive failed error=%s bytes=%u released=%u",
               esp_err_to_name(result),
               static_cast<unsigned>(receive_state_.received),
               static_cast<unsigned>(released));
      vTaskDelete(nullptr);
    }

    std::size_t const written = xStreamBufferSend(
        stream_buffer_, dma_buffer_, receive_state_.received, 0);
    if (written != receive_state_.received) {
      // The pre-arm space gate and single producer make this unreachable. Stop
      // instead of exposing a truncated VDU command to the retained parser.
      receive_failures_.fetch_add(1, std::memory_order_relaxed);
      ESP_LOGE(kTag, "stream enqueue truncated expected=%u actual=%u",
               static_cast<unsigned>(receive_state_.received),
               static_cast<unsigned>(written));
      vTaskDelete(nullptr);
    }
    records_received_.fetch_add(1, std::memory_order_relaxed);
    bytes_received_.fetch_add(written, std::memory_order_relaxed);
  }
}

int ForwardParallelStream::available() {
  if (stream_buffer_ == nullptr) return peeked_ >= 0 ? 1 : 0;
  return static_cast<int>(xStreamBufferBytesAvailable(stream_buffer_)) +
         (peeked_ >= 0 ? 1 : 0);
}

int ForwardParallelStream::read() {
  if (peeked_ >= 0) {
    int const value = peeked_;
    peeked_ = -1;
    return value;
  }
  std::uint8_t value{};
  if (stream_buffer_ == nullptr ||
      xStreamBufferReceive(stream_buffer_, &value, 1, 0) != 1)
    return -1;
  return value;
}

int ForwardParallelStream::peek() {
  if (peeked_ < 0) peeked_ = read();
  return peeked_;
}

void ForwardParallelStream::flush() {}

std::size_t ForwardParallelStream::write(std::uint8_t) {
  discarded_return_bytes_.fetch_add(1, std::memory_order_relaxed);
  return 1;
}

std::size_t ForwardParallelStream::write(std::uint8_t const *,
                                         std::size_t size) {
  discarded_return_bytes_.fetch_add(size, std::memory_order_relaxed);
  return size;
}

ForwardParallelMetrics ForwardParallelStream::metrics() const noexcept {
  return {
      .records_received =
          records_received_.load(std::memory_order_relaxed),
      .bytes_received = bytes_received_.load(std::memory_order_relaxed),
      .discarded_return_bytes =
          discarded_return_bytes_.load(std::memory_order_relaxed),
      .receive_failures = receive_failures_.load(std::memory_order_relaxed),
  };
}

}  // namespace agon::extender::transport
