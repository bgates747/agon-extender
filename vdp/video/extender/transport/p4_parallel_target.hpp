// ESP32-P4 production adapters for the platform-neutral parallel data plane.
// A target compile/link proves API closure only.  Stopped-CLOCK, stuck-VALID,
// GPIO electrical behavior, timing, and recovery still require separately
// authorized physical evidence on the applicable circuit.
#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>

#include <driver/parlio_rx.h>
#include <esp_attr.h>

#include "extender/transport/p4_parallel_data_plane.hpp"
#include "extender/transport/p4_parallel_target_config.hpp"

#ifndef CONFIG_IDF_TARGET_ESP32P4
#error "The production forward-parallel target adapters require ESP32-P4"
#endif

namespace agon::extender::transport {

class EspP4EpochHardware final : public P4EpochHardware {
 public:
  bool releaseReady() noexcept override;
  bool releaseParallelForwardBanks() noexcept override;
  bool releaseReturnBank() noexcept override;
  bool disableSharedUartOutputs() noexcept override;
  bool configureParallelInputPads() noexcept override;
  bool releaseParallelInputPads() noexcept override;
  bool enableParallelForwardBanks() noexcept override;
  bool assertReady() noexcept override;

 private:
  static bool configureReleasedOpenDrain(int pin) noexcept;
  static bool releaseControl(int pin) noexcept;
  static bool assertControl(int pin) noexcept;
  static bool configureInputs(std::uint64_t pin_mask) noexcept;
};

class EspP4ParlioBackend final : public ParlioReceiveBackend {
 public:
  bool acquire(std::uint8_t *record_storage,
               std::size_t capacity) noexcept override;
  bool enable() noexcept override;
  bool arm() noexcept override;
  ReceiveCompletion wait(
      ReceiveWaitPolicy policy,
      std::atomic<bool> const &cancel_requested) noexcept override;
  bool cancel() noexcept override;
  bool disable() noexcept override;
  bool release() noexcept override;

 private:
  static bool IRAM_ATTR receiveDone(
      parlio_rx_unit_handle_t unit,
      parlio_rx_event_data_t const *event,
      void *user_data) noexcept;
  bool validReleasedWithin(
      std::uint32_t bound_ms,
      std::atomic<bool> const &cancel_requested) const noexcept;
  void clearCompletion() noexcept;

  parlio_rx_unit_handle_t unit_{};
  parlio_rx_delimiter_handle_t delimiter_{};
  std::uint8_t *dma_buffer_{};
  std::uint8_t *record_storage_{};
  std::size_t capacity_{};
  std::size_t dma_capacity_{};
  std::atomic<std::size_t> completed_bytes_{};
  std::atomic<std::uint32_t> completion_generation_{};
  std::uint32_t armed_generation_{};
  bool enabled_{};
  bool armed_{};
};

}  // namespace agon::extender::transport
