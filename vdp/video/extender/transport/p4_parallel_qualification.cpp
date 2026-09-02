// Keep the non-release composition marker local to its qualification owner.
#define AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION 1

#include "extender/transport/p4_parallel_qualification.hpp"

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <new>

#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "extender/transport/p4_parallel_target.hpp"

namespace agon::extender::transport {
namespace {

constexpr char kTag[] = "p4_nonrelease_parallel";
constexpr std::size_t kQueueCapacity = 8192;
constexpr std::size_t kMaximumRecordBytes = 4096;
constexpr std::size_t kCaptureCapacity = 4096;
constexpr ReceiveWaitPolicy kQualificationWaitPolicy{
    5000, 1};  // Both fields are milliseconds, not RTOS ticks.

class FixedQualificationEpoch final : public ParallelEpochAuthority {
 public:
  ParallelEpochLease authorize() noexcept {
    std::uint64_t generation = next_generation_++;
    if (generation == 0) generation = next_generation_++;
    live_generation_.store(generation, std::memory_order_release);
    return {generation};
  }

  void revoke(ParallelEpochLease const &lease) noexcept {
    std::uint64_t expected = lease.generation;
    (void)live_generation_.compare_exchange_strong(
        expected, 0, std::memory_order_acq_rel, std::memory_order_acquire);
  }

  bool isLive(ParallelEpochLease const &lease) const noexcept override {
    return lease.generation != 0 &&
           live_generation_.load(std::memory_order_acquire) ==
               lease.generation;
  }

 private:
  std::atomic<std::uint64_t> live_generation_{};
  std::uint64_t next_generation_{1};
};

class VisibleCaptureReturn final : public VdpReturnChannel {
 public:
  std::size_t write(std::uint8_t const *bytes,
                    std::size_t length) noexcept override {
    write_calls_.fetch_add(1, std::memory_order_relaxed);
    if ((length != 0 && bytes == nullptr) ||
        length > captured_.size() - used_) {
      capture_failures_.fetch_add(1, std::memory_order_relaxed);
      ESP_LOGE(kTag, "return capture full/invalid used=%u requested=%u",
               static_cast<unsigned>(used_),
               static_cast<unsigned>(length));
      return 0;
    }
    if (length != 0) std::memcpy(captured_.data() + used_, bytes, length);
    for (std::size_t offset = 0; offset < length; ++offset) {
      ESP_LOGI(kTag, "return[%u]=0x%02x",
               static_cast<unsigned>(used_ + offset),
               static_cast<unsigned>(bytes[offset]));
    }
    used_ += length;
    bytes_captured_.store(static_cast<std::uint32_t>(used_),
                          std::memory_order_release);
    return length;
  }

  bool flush() noexcept override {
    flush_calls_.fetch_add(1, std::memory_order_relaxed);
    ESP_LOGI(kTag, "return capture flush bytes=%u",
             static_cast<unsigned>(used_));
    return true;
  }

  bool setProtocolDuplex(bool full_duplex) noexcept override {
    duplex_rejections_.fetch_add(1, std::memory_order_relaxed);
    ESP_LOGE(kTag,
             "UART duplex request rejected full_duplex=%u: no UART owner",
             static_cast<unsigned>(full_duplex));
    return false;
  }

  P4QualificationCaptureMetrics metrics(
      TransportFault fault) const noexcept {
    return {
        write_calls_.load(std::memory_order_acquire),
        bytes_captured_.load(std::memory_order_acquire),
        capture_failures_.load(std::memory_order_acquire),
        flush_calls_.load(std::memory_order_acquire),
        duplex_rejections_.load(std::memory_order_acquire),
        fault,
    };
  }

 private:
  std::array<std::uint8_t, kCaptureCapacity> captured_{};
  std::size_t used_{};  // The retained parser is the sole writer.
  std::atomic<std::uint32_t> write_calls_{};
  std::atomic<std::uint32_t> bytes_captured_{};
  std::atomic<std::uint32_t> capture_failures_{};
  std::atomic<std::uint32_t> flush_calls_{};
  std::atomic<std::uint32_t> duplex_rejections_{};
};

struct QualificationContext final {
  QualificationContext() noexcept
      : queue(queue_storage.data(), queue_storage.size()),
        ingress(backend, queue, fault, record_storage.data(),
                record_storage.size(), record_storage.size()),
        plane(hardware, authority, ingress, queue, fault) {}

  std::array<std::uint8_t, kQueueCapacity> queue_storage{};
  std::array<std::uint8_t, kMaximumRecordBytes> record_storage{};
  SpscByteQueue queue;
  TransportFaultLatch fault;
  EspP4EpochHardware hardware;
  EspP4ParlioBackend backend;
  P4ParlioIngress ingress;
  FixedQualificationEpoch authority;
  P4ParallelDataPlane plane;
  VisibleCaptureReturn capture;
  ParallelEpochLease lease{};
  std::atomic<ExtenderVdpStream *> stream{};
  TaskHandle_t service_task{};
};

QualificationContext &context() noexcept {
  static QualificationContext instance;
  return instance;
}

void stopAndRevokeQualificationEpoch(
    QualificationContext &qualification) noexcept {
  std::uint32_t attempts = 0;
  while (!qualification.plane.stop()) {
    ++attempts;
    // A failed stop deliberately retains ownership so this sole lifecycle
    // actor can retry.  Log the first failure and powers of two without
    // flooding a persistent target fault.
    if (attempts == 1 || (attempts & (attempts - 1)) == 0) {
      ESP_LOGE(kTag, "production data-plane cleanup retry=%u fault=%u",
               static_cast<unsigned>(attempts),
               static_cast<unsigned>(qualification.fault.fault()));
    }
    vTaskDelay(1);
  }
  qualification.authority.revoke(qualification.lease);
  qualification.lease = {};
}

void serviceTask(void *parameter) {
  auto &qualification = *static_cast<QualificationContext *>(parameter);
  for (;;) {
    ServiceResult const result =
        qualification.plane.serviceOnce(kQualificationWaitPolicy);
    if (result == ServiceResult::kRecordQueued) continue;
    if (result == ServiceResult::kBackpressured) {
      vTaskDelay(1);
      continue;
    }

    ESP_LOGE(kTag, "production data-plane service stopped result=%u fault=%u",
             static_cast<unsigned>(result),
             static_cast<unsigned>(qualification.fault.fault()));
    stopAndRevokeQualificationEpoch(qualification);
    qualification.service_task = nullptr;
    vTaskDelete(nullptr);
    return;
  }
}

}  // namespace

ExtenderVdpStream *beginP4ParallelNonreleaseQualification() noexcept {
  auto &qualification = context();
  if (qualification.stream.load(std::memory_order_acquire) != nullptr ||
      qualification.service_task != nullptr) {
    return nullptr;
  }

  ESP_LOGW(kTag,
           "PORT-008-D002 NON-RELEASE COMPILE/LINK QUALIFICATION ONLY; "
           "no activation, UART return, deployment identity, or physical "
           "authorization");
  qualification.lease = qualification.authority.authorize();
  if (!qualification.plane.enterAuthorizedEpoch(qualification.lease)) {
    ESP_LOGE(kTag, "fixed qualification epoch entry failed fault=%u",
             static_cast<unsigned>(qualification.fault.fault()));
    stopAndRevokeQualificationEpoch(qualification);
    return nullptr;
  }

  auto *stream = new (std::nothrow) ExtenderVdpStream(
      qualification.queue, qualification.capture, qualification.fault,
      qualification.plane);
  if (stream == nullptr) {
    qualification.plane.requestCancel();
    stopAndRevokeQualificationEpoch(qualification);
    ESP_LOGE(kTag, "composite Stream allocation failed");
    return nullptr;
  }

  if (xTaskCreate(serviceTask, "p4ParallelRx", 4096, &qualification, 4,
                  &qualification.service_task) != pdPASS) {
    qualification.plane.requestCancel();
    stopAndRevokeQualificationEpoch(qualification);
    delete stream;
    ESP_LOGE(kTag, "production data-plane service task creation failed");
    return nullptr;
  }
  qualification.stream.store(stream, std::memory_order_release);
  return stream;
}

void requestP4ParallelNonreleaseQualificationStop() noexcept {
  context().plane.requestCancel();
}

P4QualificationCaptureMetrics p4QualificationCaptureMetrics() noexcept {
  auto &qualification = context();
  return qualification.capture.metrics(qualification.fault.fault());
}

void logP4QualificationStatus() noexcept {
  P4QualificationCaptureMetrics const metrics =
      p4QualificationCaptureMetrics();
  ESP_LOGI(kTag,
           "capture writes=%u bytes=%u failures=%u flushes=%u "
           "duplex_rejections=%u fault=%u",
           static_cast<unsigned>(metrics.write_calls),
           static_cast<unsigned>(metrics.bytes_captured),
           static_cast<unsigned>(metrics.capture_failures),
           static_cast<unsigned>(metrics.flush_calls),
           static_cast<unsigned>(metrics.duplex_rejections),
           static_cast<unsigned>(metrics.fault));
}

void setP4QualificationProtocolDuplex(bool full_duplex) noexcept {
  auto &qualification = context();
  ExtenderVdpStream *stream =
      qualification.stream.load(std::memory_order_acquire);
  if (stream != nullptr) {
    (void)stream->setProtocolDuplex(full_duplex);
    return;
  }
  qualification.fault.latch(TransportFault::kOutputDuplexControl);
  qualification.plane.requestCancel();
  ESP_LOGE(kTag, "UART duplex request arrived before composite Stream binding");
}

}  // namespace agon::extender::transport
