// Shared ESP-IDF HTTP/video transport. No Ethernet, VDP, EMOS or SD startup.
#pragma once
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <mutex>
#include <esp_http_server.h>
#include "extender/network/browser_video_service_core.hpp"
#include "extender/web/embedded_assets.hpp"
namespace agon::extender::network {
struct HttpVideoConfig {
  std::uint16_t port{80};
  std::uint16_t control_port{32768};
  std::uint16_t max_uri_handlers{8};
  std::uint16_t max_open_sockets{7};
  std::uint32_t stack_bytes{4096};
};
class HttpVideoService {
 public:
  explicit HttpVideoService(OpaqueMessageProvider &provider) noexcept : provider_(provider) {}
  virtual ~HttpVideoService();
  HttpVideoService(HttpVideoService const &) = delete;
  HttpVideoService &operator=(HttpVideoService const &) = delete;
  // Caller serializes start/stop/poll; never call from an HTTP callback.
  // Provider, assets, strings and callback target outlive successful stop.
  bool startServer(web::EmbeddedAsset const *assets, std::size_t count,
                   HttpVideoConfig const &options = {}) noexcept;
  bool stopServer() noexcept; // false retains live handle; owner must remain alive
  void poll() noexcept { if (server_.load() && !http_fault_) attemptVideoSend(); }
  bool running() const noexcept { return server_.load()!=nullptr && !http_fault_; }
  BrowserVideoServiceMetrics videoMetrics() const noexcept { return video_.metrics(); }
 protected:
  virtual void notifyWorker() noexcept {} // optional nonblocking wakeup
  virtual void negotiate(httpd_req_t *) noexcept {} // HTTP task; raw default
  virtual bool allowSend() noexcept { return true; }
  virtual esp_err_t sendMessage(httpd_handle_t, int, OpaqueMessageView const &) noexcept;
  static esp_err_t sendSegments(httpd_handle_t, int, OpaqueMessageSegment const *, std::size_t) noexcept;
  static void increment(std::atomic<std::uint32_t> &) noexcept;
  void attemptVideoSend() noexcept;
  OpaqueMessageProvider &provider_;
  BrowserVideoServiceCore video_{};
  std::mutex video_dispatch_mutex_;
#if defined(AGON_EXTENDER_VIDEO_DISPATCH_TIMING)
  std::atomic<std::uint32_t> video_credit_at_{};
  std::uint32_t video_queued_at_{};
#endif
  bool video_send_queued_{};
  VideoClientId queued_video_client_{kNoVideoClient};
  std::atomic<httpd_handle_t> server_{};
  bool http_fault_{}; // lifecycle worker only; failed stop retains handle
  std::atomic<std::uint32_t> http_starts_{}, http_stops_{}, http_start_failures_{};
  std::atomic<std::uint32_t> queued_sends_{}, queue_failures_{}, socket_send_failures_{};
 private:
  static void queuedSend(void *) noexcept;
  void performQueuedSend() noexcept;
  static esp_err_t socketOpened(httpd_handle_t, int) noexcept;
  static void socketClosed(httpd_handle_t, int) noexcept;
  static esp_err_t assetHandler(httpd_req_t *) noexcept;
  static esp_err_t videoHandler(httpd_req_t *) noexcept;
  static esp_err_t videoPostHandshake(httpd_req_t *) noexcept;
  void closeVideo(httpd_req_t *, std::uint16_t, char const *) noexcept;
};
} // namespace agon::extender::network
