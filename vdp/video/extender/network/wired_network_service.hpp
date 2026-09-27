// PORT-006 first-tranche wired Ethernet and HTTP/WebSocket adapter.
//
// Arduino-ESP32 owns IP101/RMII and DHCP events. ESP-IDF owns HTTP socket
// execution. BrowserVideoServiceCore owns the bounded one-client/one-credit
// lifecycle, while the injected provider owns every opaque byte and lease.
#pragma once

#if !defined(ESP_PLATFORM)
#error "WiredNetworkService is an ESP32-P4 target adapter"
#endif

#include <atomic>
#include <cstdint>

#include "extender/network/devkit_ethernet.hpp"
#include <esp_http_server.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "extender/network/http_video_service.hpp"

namespace agon::extender::network {

enum class WiredServiceState : std::uint8_t {
  Stopped,
  Starting,
  LinkDown,
  LinkUpNoLease,
  LeasedServing,
  Faulted,
};

struct WiredNetworkMetrics {
  BrowserVideoServiceMetrics video;
  std::uint32_t http_starts{};
  std::uint32_t http_stops{};
  std::uint32_t http_start_failures{};
  std::uint32_t queued_sends{};
  std::uint32_t queue_failures{};
  std::uint32_t socket_send_failures{};
};

class WiredNetworkService final : public HttpVideoService {
 public:
  explicit WiredNetworkService(OpaqueMessageProvider &provider) noexcept;
  ~WiredNetworkService();

  WiredNetworkService(WiredNetworkService const &) = delete;
  WiredNetworkService &operator=(WiredNetworkService const &) = delete;

  bool start() noexcept;
  void stop() noexcept;
  WiredServiceState state() const noexcept;
  WiredNetworkMetrics metrics() const noexcept;

 private:
  enum EventBits : std::uint32_t {
    EthernetStarted = 1U << 0U,
    EthernetConnected = 1U << 1U,
    EthernetGotIp = 1U << 2U,
    EthernetLostIp = 1U << 3U,
    EthernetDisconnected = 1U << 4U,
    EthernetStopped = 1U << 5U,
  };

  static void workerEntry(void *context) noexcept;
  void onNetworkEvent(DevkitEthernet::Event event) noexcept;
  void worker() noexcept;
  void processEvents(std::uint32_t events) noexcept;
  bool startHttp() noexcept;
  void stopHttp() noexcept;
  void negotiate(httpd_req_t *) noexcept override;
  esp_err_t sendMessage(httpd_handle_t, int, OpaqueMessageView const &) noexcept override;
  bool allowSend() noexcept override;
  void reportLease() const noexcept;
  void notifyWorker() noexcept override;
  std::atomic<WiredServiceState> state_{WiredServiceState::Stopped};
  std::atomic<std::uint32_t> pending_events_{};
  std::atomic<bool> stop_requested_{};
  std::atomic<TaskHandle_t> worker_task_{};
  DevkitEthernet ethernet_;


};

}  // namespace agon::extender::network
