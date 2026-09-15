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

#include <ETH.h>
#include <Network.h>
#include <esp_http_server.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include "extender/network/browser_video_service_core.hpp"

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

class WiredNetworkService final {
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
  static void queuedSend(void *context) noexcept;
  static esp_err_t socketOpened(httpd_handle_t server, int socket) noexcept;
  static esp_err_t assetHandler(httpd_req_t *request) noexcept;
  static esp_err_t videoHandler(httpd_req_t *request) noexcept;
  static esp_err_t videoPostHandshake(httpd_req_t *request) noexcept;
  static void socketClosed(httpd_handle_t server, int socket) noexcept;

  void onNetworkEvent(arduino_event_id_t event) noexcept;
  void worker() noexcept;
  void processEvents(std::uint32_t events) noexcept;
  bool startHttp() noexcept;
  void stopHttp() noexcept;
  void attemptVideoSend() noexcept;
  void performQueuedSend() noexcept;
  void closeVideo(httpd_req_t *request, std::uint16_t code,
                  char const *reason) noexcept;
  void reportLease() const noexcept;
  void notifyWorker() noexcept;
  void increment(std::atomic<std::uint32_t> &counter) noexcept;

  OpaqueMessageProvider &provider_;
  BrowserVideoServiceCore video_{};
  // NET-001: serialize worker acquisition/queueing with HTTP-task takeover.
  // Keep at most one queued callback; it belongs to its original socket, never
  // whichever client happens to be current when the callback runs.
  std::mutex video_dispatch_mutex_;
#if defined(AGON_EXTENDER_VIDEO_DISPATCH_TIMING)
  // Diagnostic-only: no storage or clock reads in ordinary production builds.
  std::atomic<std::uint32_t> video_credit_at_{};
  std::uint32_t video_queued_at_{}; // guarded by video_dispatch_mutex_
#endif
  bool video_send_queued_{};
  VideoClientId queued_video_client_{kNoVideoClient};
  std::atomic<WiredServiceState> state_{WiredServiceState::Stopped};
  std::atomic<std::uint32_t> pending_events_{};
  std::atomic<bool> stop_requested_{};
  std::atomic<TaskHandle_t> worker_task_{};
  std::atomic<httpd_handle_t> server_{};
  bool http_fault_{}; // worker-owned; a failed rollback retains its live handle
  network_event_handle_t network_event_handle_{};
  bool network_event_registered_{};

  std::atomic<std::uint32_t> http_starts_{};
  std::atomic<std::uint32_t> http_stops_{};
  std::atomic<std::uint32_t> http_start_failures_{};
  std::atomic<std::uint32_t> queued_sends_{};
  std::atomic<std::uint32_t> queue_failures_{};
  std::atomic<std::uint32_t> socket_send_failures_{};
};

}  // namespace agon::extender::network
