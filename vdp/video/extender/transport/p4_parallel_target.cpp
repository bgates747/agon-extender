#include "extender/transport/p4_parallel_target.hpp"

#include <algorithm>
#include <climits>
#include <cstdlib>
#include <cstring>
#include <limits>

#include <driver/gpio.h>
#include <esp32-hal-periman.h>
#include <esp_err.h>
#include <esp_heap_caps.h>
#include <esp_memory_utils.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

namespace agon::extender::transport {
namespace {

constexpr std::uint64_t pinBit(int pin) noexcept {
  return UINT64_C(1) << static_cast<unsigned>(pin);
}

constexpr std::uint64_t parallelInputMask() noexcept {
  std::uint64_t mask = pinBit(P4ParallelTargetConfig::kClockPin) |
                       pinBit(P4ParallelTargetConfig::kValidPin);
  for (int const pin : P4ParallelTargetConfig::kDataPins) mask |= pinBit(pin);
  return mask;
}

constexpr std::uint64_t sharedUartOutputMask() noexcept {
  return pinBit(P4ParallelTargetConfig::kDataPins[1]) |
         pinBit(P4ParallelTargetConfig::kDataPins[3]);
}

gpio_num_t gpioNumber(int pin) noexcept {
  return static_cast<gpio_num_t>(pin);
}

}  // namespace

bool EspP4EpochHardware::configureInputs(std::uint64_t pin_mask) noexcept {
  gpio_config_t config{};
  config.pin_bit_mask = pin_mask;
  config.mode = GPIO_MODE_INPUT;
  config.pull_up_en = GPIO_PULLUP_DISABLE;
  config.pull_down_en = GPIO_PULLDOWN_DISABLE;
  config.intr_type = GPIO_INTR_DISABLE;
  return gpio_config(&config) == ESP_OK;
}

bool EspP4EpochHardware::configureReleasedOpenDrain(int pin) noexcept {
  gpio_num_t const gpio = gpioNumber(pin);
  // Preload the output latch high before the mux enables GPIO open drain.  A
  // logical high on GPIO_MODE_INPUT_OUTPUT_OD is high-impedance release, never
  // a push-pull drive into the circuit's control pull-up.
  bool const preloaded = gpio_set_level(gpio, 1) == ESP_OK;
  gpio_config_t config{};
  config.pin_bit_mask = pinBit(pin);
  config.mode = GPIO_MODE_INPUT_OUTPUT_OD;
  config.pull_up_en = GPIO_PULLUP_DISABLE;
  config.pull_down_en = GPIO_PULLDOWN_DISABLE;
  config.intr_type = GPIO_INTR_DISABLE;
  bool const configured = gpio_config(&config) == ESP_OK;
  bool const released = gpio_set_level(gpio, 1) == ESP_OK;
  return preloaded && configured && released;
}

bool EspP4EpochHardware::releaseControl(int pin) noexcept {
  return configureReleasedOpenDrain(pin);
}

bool EspP4EpochHardware::assertControl(int pin) noexcept {
  return gpio_set_level(gpioNumber(pin), 0) == ESP_OK;
}

bool EspP4EpochHardware::releaseReady() noexcept {
  return releaseControl(P4ParallelTargetConfig::kReadyPin);
}

bool EspP4EpochHardware::releaseParallelForwardBanks() noexcept {
  bool const bank_a =
      releaseControl(P4ParallelTargetConfig::kForwardBankAEnablePin);
  bool const bank_b =
      releaseControl(P4ParallelTargetConfig::kForwardBankBEnablePin);
  return bank_a && bank_b;
}

bool EspP4EpochHardware::releaseReturnBank() noexcept {
  return releaseControl(P4ParallelTargetConfig::kReturnBankEnablePin);
}

bool EspP4EpochHardware::disableSharedUartOutputs() noexcept {
  // Arduino's peripheral manager invokes the registered UART deinitializer
  // before changing ownership to INIT.  Both calls are attempted: GPIO12 is
  // UART TX and GPIO11 is UART RTS in the retained pin plan, and either output
  // would contend with an admitted forward-parallel sender.
  bool const tx_released = perimanClearPinBus(
      static_cast<std::uint8_t>(P4ParallelTargetConfig::kDataPins[1]));
  bool const rts_released = perimanClearPinBus(
      static_cast<std::uint8_t>(P4ParallelTargetConfig::kDataPins[3]));
  bool const inputs = configureInputs(sharedUartOutputMask());
  return tx_released && rts_released && inputs;
}

bool EspP4EpochHardware::configureParallelInputPads() noexcept {
  return configureInputs(parallelInputMask());
}

bool EspP4EpochHardware::releaseParallelInputPads() noexcept {
  // The PARLIO owner has already disabled/deleted its unit before this call.
  // Leave every shared pad as an unpulled GPIO input, with no output owner.
  return configureInputs(parallelInputMask());
}

bool EspP4EpochHardware::enableParallelForwardBanks() noexcept {
  bool const bank_a =
      assertControl(P4ParallelTargetConfig::kForwardBankAEnablePin);
  bool const bank_b =
      assertControl(P4ParallelTargetConfig::kForwardBankBEnablePin);
  if (bank_a && bank_b) return true;
  (void)releaseParallelForwardBanks();
  return false;
}

bool EspP4EpochHardware::assertReady() noexcept {
  return assertControl(P4ParallelTargetConfig::kReadyPin);
}

static_assert(std::atomic<std::size_t>::is_always_lock_free,
              "PARLIO ISR publication requires lock-free size_t atomics");
static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
              "PARLIO ISR publication requires lock-free generation atomics");

bool IRAM_ATTR EspP4ParlioBackend::receiveDone(
    parlio_rx_unit_handle_t, parlio_rx_event_data_t const *event,
    void *user_data) noexcept {
  auto *backend = static_cast<EspP4ParlioBackend *>(user_data);
  backend->completed_bytes_.store(event->recv_bytes,
                                  std::memory_order_relaxed);
  // Pinned ESP-IDF 5.5.5 calls this user callback from
  // parlio_rx_default_eof_callback() before it clears the transaction and
  // gives trans_sem.  The release increment publishes recv_bytes; wait()
  // performs an acquire load after parlio_rx_unit_wait_all_done().  Correctness
  // therefore does not depend on a volatile field or on undocumented task/ISR
  // compiler ordering around the driver's semaphore.
  backend->completion_generation_.fetch_add(1, std::memory_order_release);
  return false;
}

void EspP4ParlioBackend::clearCompletion() noexcept {
  completed_bytes_.store(0, std::memory_order_relaxed);
  armed_generation_ = completion_generation_.load(std::memory_order_acquire);
}

bool EspP4ParlioBackend::acquire(std::uint8_t *record_storage,
                                 std::size_t capacity) noexcept {
  if (record_storage == nullptr || capacity == 0 ||
      capacity == std::numeric_limits<std::size_t>::max() || unit_ != nullptr ||
      delimiter_ != nullptr || dma_buffer_ != nullptr) {
    return false;
  }

  record_storage_ = record_storage;
  capacity_ = capacity;
  // One target-owned sentinel byte makes maximum-length records and overlong
  // records unambiguous.  A legitimate capacity-byte record completes only
  // when VALID_N releases; a sender that clocks one more byte fills the DMA
  // transaction at capacity+1 and is rejected without publishing a truncated
  // record to the parser.
  dma_capacity_ = capacity_ + 1;
  dma_buffer_ = static_cast<std::uint8_t *>(heap_caps_aligned_calloc(
      64, 1, dma_capacity_,
      MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT));
  if (dma_buffer_ == nullptr || !esp_ptr_dma_capable(dma_buffer_)) {
    (void)release();
    return false;
  }

  parlio_rx_unit_config_t unit_config{};
  unit_config.trans_queue_depth = 1;
  unit_config.max_recv_size = dma_capacity_;
  unit_config.dma_burst_size = 64;
  unit_config.data_width = P4ParallelTargetConfig::kDataPins.size();
  unit_config.clk_src = PARLIO_CLK_SRC_EXTERNAL;
  unit_config.ext_clk_freq_hz =
      P4ParallelTargetConfig::kConfiguredExternalClockHz;
  unit_config.exp_clk_freq_hz =
      P4ParallelTargetConfig::kConfiguredExternalClockHz;
  unit_config.clk_in_gpio_num =
      gpioNumber(P4ParallelTargetConfig::kClockPin);
  unit_config.clk_out_gpio_num = GPIO_NUM_NC;
  unit_config.valid_gpio_num =
      gpioNumber(P4ParallelTargetConfig::kValidPin);
  for (std::size_t index = 0;
       index < P4ParallelTargetConfig::kDataPins.size(); ++index) {
    unit_config.data_gpio_nums[index] =
        gpioNumber(P4ParallelTargetConfig::kDataPins[index]);
  }
  // CLOCK is transaction-gated by the eZ80 sender (the ESP-IDF documentation
  // calls SPI the corresponding non-free-running case).  In this mode the
  // unit remains started while enabled, preserving alignment when CLOCK stops
  // idle; cancellation resets that state by disable/re-enable.
  unit_config.flags.free_clk = false;
  unit_config.flags.clk_gate_en = false;

  if (parlio_new_rx_unit(&unit_config, &unit_) != ESP_OK) {
    (void)release();
    return false;
  }

  parlio_rx_level_delimiter_config_t delimiter_config{};
  delimiter_config.valid_sig_line_id = PARLIO_RX_UNIT_MAX_DATA_WIDTH - 1;
  delimiter_config.sample_edge = PARLIO_SAMPLE_EDGE_NEG;
  delimiter_config.bit_pack_order = PARLIO_BIT_PACK_ORDER_LSB;
  delimiter_config.eof_data_len = 0;
  // ESP-IDF's level-delimiter timeout starts only while VALID is inactive; it
  // cannot detect a stopped CLOCK with VALID stuck active.  The task-level
  // bounded millisecond wait below owns both stopped-CLOCK recovery and prompt
  // cancellation instead.
  delimiter_config.timeout_ticks = 0;
  delimiter_config.flags.active_low_en = true;
  if (parlio_new_rx_level_delimiter(&delimiter_config, &delimiter_) != ESP_OK) {
    (void)release();
    return false;
  }

  parlio_rx_event_callbacks_t callbacks{};
  callbacks.on_receive_done = receiveDone;
  if (parlio_rx_unit_register_event_callbacks(unit_, &callbacks, this) !=
      ESP_OK) {
    (void)release();
    return false;
  }
  clearCompletion();
  return true;
}

bool EspP4ParlioBackend::enable() noexcept {
  if (unit_ == nullptr || delimiter_ == nullptr || dma_buffer_ == nullptr ||
      enabled_) {
    return false;
  }
  if (parlio_rx_unit_enable(unit_, true) != ESP_OK) return false;
  enabled_ = true;
  armed_ = false;
  clearCompletion();
  return true;
}

bool EspP4ParlioBackend::arm() noexcept {
  if (!enabled_ || armed_ || unit_ == nullptr || delimiter_ == nullptr ||
      dma_buffer_ == nullptr) {
    return false;
  }
  clearCompletion();
  parlio_receive_config_t receive_config{};
  receive_config.delimiter = delimiter_;
  receive_config.flags.partial_rx_en = false;
  receive_config.flags.indirect_mount = false;
  if (parlio_rx_unit_receive(unit_, dma_buffer_, dma_capacity_,
                             &receive_config) != ESP_OK) {
    return false;
  }
  armed_ = true;
  return true;
}

bool EspP4ParlioBackend::validReleasedWithin(
    std::uint32_t bound_ms,
    std::atomic<bool> const &cancel_requested) const noexcept {
  std::int64_t const deadline_us =
      esp_timer_get_time() + static_cast<std::int64_t>(bound_ms) * 1000;
  do {
    if (cancel_requested.load(std::memory_order_acquire)) return false;
    if (gpio_get_level(gpioNumber(P4ParallelTargetConfig::kValidPin)) != 0) {
      return true;
    }
    // One scheduler tick is guaranteed to yield; pdMS_TO_TICKS(1) is allowed
    // to round to zero when a future configuration lowers the tick rate.
    vTaskDelay(1);
  } while (esp_timer_get_time() < deadline_us);
  return gpio_get_level(gpioNumber(P4ParallelTargetConfig::kValidPin)) != 0;
}

ReceiveCompletion EspP4ParlioBackend::wait(
    ReceiveWaitPolicy policy,
    std::atomic<bool> const &cancel_requested) noexcept {
  if (!enabled_ || !armed_ || !policy.valid()) {
    return {ReceiveStatus::kError, 0};
  }

  std::int64_t const timeout_us =
      static_cast<std::int64_t>(policy.completion_timeout_ms) * 1000;
  std::int64_t deadline_us = esp_timer_get_time() + timeout_us;
  // Idle is not a failed record.  Start a fresh completion deadline only once
  // VALID_N proves that a sender began one; an already-active/stuck VALID_N at
  // entry is therefore bounded by the normal fatal completion timeout.
  bool record_started =
      gpio_get_level(gpioNumber(P4ParallelTargetConfig::kValidPin)) == 0;
  for (;;) {
    if (cancel_requested.load(std::memory_order_acquire)) {
      return {ReceiveStatus::kCancelled, 0};
    }
    std::int64_t const now_us = esp_timer_get_time();
    if (!record_started &&
        gpio_get_level(gpioNumber(P4ParallelTargetConfig::kValidPin)) == 0) {
      record_started = true;
      deadline_us = now_us + timeout_us;
    }
    if (now_us >= deadline_us) {
      if (record_started) return {ReceiveStatus::kTimeout, 0};
      // READY_N already advertised this armed transaction.  Do not release it
      // merely because the sender is idle: EMOS could observe that assertion
      // immediately before a return/re-arm boundary and begin into teardown.
      // Roll the observation window while continuing bounded cancellation
      // polls; only VALID-active completion receives a fatal deadline.
      deadline_us = now_us + timeout_us;
      continue;
    }

    std::uint64_t const remaining_us =
        static_cast<std::uint64_t>(deadline_us - now_us);
    std::uint64_t const remaining_ms = (remaining_us + 999) / 1000;
    std::uint64_t const slice_ms = std::min<std::uint64_t>(
        {remaining_ms, policy.cancellation_poll_ms,
         static_cast<std::uint64_t>(INT_MAX)});
    esp_err_t const result =
        parlio_rx_unit_wait_all_done(unit_, static_cast<int>(slice_ms));
    if (result == ESP_ERR_TIMEOUT) continue;
    if (result != ESP_OK) return {ReceiveStatus::kError, 0};
    if (cancel_requested.load(std::memory_order_acquire)) {
      return {ReceiveStatus::kCancelled, 0};
    }

    std::uint32_t const completed_generation =
        completion_generation_.load(std::memory_order_acquire);
    if (completed_generation == armed_generation_) {
      return {ReceiveStatus::kError, 0};
    }
    std::size_t const bytes =
        completed_bytes_.load(std::memory_order_relaxed);
    if (bytes == 0 || bytes > capacity_) {
      return {ReceiveStatus::kOverflow, bytes};
    }
    // DMA-full completion can precede the sender's VALID_N release by a small
    // scheduling interval.  Permit one cancellation slice for that release;
    // a line still active after the bound is a stuck-VALID/overflow fault.
    if (!validReleasedWithin(policy.cancellation_poll_ms, cancel_requested)) {
      return cancel_requested.load(std::memory_order_acquire)
                 ? ReceiveCompletion{ReceiveStatus::kCancelled, 0}
                 : ReceiveCompletion{ReceiveStatus::kOverflow, bytes};
    }
    std::memcpy(record_storage_, dma_buffer_, bytes);
    armed_ = false;
    return {ReceiveStatus::kComplete, bytes};
  }
}

bool EspP4ParlioBackend::cancel() noexcept {
  if (unit_ == nullptr) return false;
  // ESP-IDF exposes no per-transaction cancel API.  In pinned IDF 5.5.5,
  // parlio_rx_unit_disable() stops GDMA, clears curr_trans, and signals the
  // transaction semaphore; parlio_rx_unit_enable(reset_queue=true) drops any
  // queued transactions.  This adapter deliberately relies on that inspected
  // implementation contract to establish a fresh retry epoch.
  if (enabled_) {
    if (parlio_rx_unit_disable(unit_) != ESP_OK) return false;
    enabled_ = false;
    armed_ = false;
  }
  if (parlio_rx_unit_enable(unit_, true) != ESP_OK) return false;
  enabled_ = true;
  armed_ = false;
  clearCompletion();
  return true;
}

bool EspP4ParlioBackend::disable() noexcept {
  if (unit_ == nullptr) return false;
  if (!enabled_) return true;
  if (parlio_rx_unit_disable(unit_) != ESP_OK) return false;
  enabled_ = false;
  armed_ = false;
  return true;
}

bool EspP4ParlioBackend::release() noexcept {
  bool ok = true;
  if (enabled_) ok = disable() && ok;
  if (enabled_) return false;

  if (delimiter_ != nullptr) {
    bool const deleted = parlio_del_rx_delimiter(delimiter_) == ESP_OK;
    if (deleted) delimiter_ = nullptr;
    ok = deleted && ok;
  }
  if (unit_ != nullptr) {
    bool const deleted = parlio_del_rx_unit(unit_) == ESP_OK;
    if (deleted) unit_ = nullptr;
    ok = deleted && ok;
  }
  if (unit_ == nullptr && delimiter_ == nullptr && dma_buffer_ != nullptr) {
    std::free(dma_buffer_);
    dma_buffer_ = nullptr;
  }
  if (unit_ == nullptr && delimiter_ == nullptr && dma_buffer_ == nullptr) {
    record_storage_ = nullptr;
    capacity_ = 0;
    dma_capacity_ = 0;
    armed_ = false;
    clearCompletion();
  }
  return ok && unit_ == nullptr && delimiter_ == nullptr &&
         dma_buffer_ == nullptr;
}

}  // namespace agon::extender::transport
