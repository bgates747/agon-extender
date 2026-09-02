// REJECTED/SUPERSEDED PORT-008 r01 forward-only transport adapter.
//
// Historical evidence only: no current source selection may compile or deploy
// this boot-active, discard-success predecessor.  The maintained production
// data plane is p4_parallel_data_plane plus extender_vdp_stream.
//
// This file originally existed because the ESP32-P4 does not provide the stock VDP's
// HardwareSerial binding. It preserves the upstream Arduino Stream boundary:
// bytes admitted by the r01 parallel circuit are presented unchanged to the
// retained VDUStreamProcessor. The reverse side intentionally remains a
// discard-only sink until PORT-008's separately reviewed UART tranche.
#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>

#include <Stream.h>
#include <driver/parlio_rx.h>
#include <freertos/FreeRTOS.h>
#include <freertos/stream_buffer.h>
#include <freertos/task.h>

namespace agon::extender::transport {

struct ForwardParallelMetrics {
  std::uint64_t records_received{};
  std::uint64_t bytes_received{};
  std::uint64_t discarded_return_bytes{};
  std::uint32_t receive_failures{};
};

class ForwardParallelStream final : public Stream {
 public:
  bool begin();

  int available() override;
  int read() override;
  int peek() override;
  void flush() override;
  std::size_t write(std::uint8_t byte) override;
  std::size_t write(std::uint8_t const *buffer, std::size_t size) override;

  ForwardParallelMetrics metrics() const noexcept;

 private:
  struct ReceiveState {
    volatile std::size_t received{};
  };

  static bool IRAM_ATTR receiveDone(parlio_rx_unit_handle_t unit,
                                    parlio_rx_event_data_t const *event,
                                    void *user_data);
  static void receiverTaskEntry(void *parameter);
  void receiverTask();
  bool configureDirectionControl();
  bool configureHardware();
  bool releaseDirections();
  bool releaseReady();
  bool selectForwardDirection();

  static constexpr std::size_t kMaximumRecordBytes = 4096;
  static constexpr std::size_t kStreamCapacityBytes = 8192;

  StreamBufferHandle_t stream_buffer_{};
  parlio_rx_unit_handle_t rx_unit_{};
  parlio_rx_delimiter_handle_t delimiter_{};
  TaskHandle_t receiver_task_{};
  std::uint8_t *dma_buffer_{};
  ReceiveState receive_state_{};
  int peeked_{-1};

  std::atomic<std::uint64_t> records_received_{};
  std::atomic<std::uint64_t> bytes_received_{};
  std::atomic<std::uint64_t> discarded_return_bytes_{};
  std::atomic<std::uint32_t> receive_failures_{};
};

}  // namespace agon::extender::transport

// The official VDP variable surface can request UART duplex changes. The r01
// forward-only prototype owns no return driver, so this operation is an
// explicit no-op. PORT-008 must replace it only with the reviewed UART adapter.
inline void setVDPProtocolDuplex(bool) noexcept {}
