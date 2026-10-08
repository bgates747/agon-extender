#ifdef AGON_EXTENDER_ROLLING_SCANOUT
#include "esp_heap_caps.h"
#endif
#include "extender/diagnostics/render_benchmark.hpp"
// Extracted from WiredNetworkService: shared socket/credit/lease ownership.
#include "http_video_service.hpp"
#include "extender/diagnostics/video_timing.hpp"
#include <array>
#include <cstring>
#include <limits>
#include <cerrno>
#include <cstdlib>
#include <esp_timer.h>
#include <esp_log.h>
#include <lwip/sockets.h>
#if !CONFIG_HTTPD_WS_SUPPORT || !CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT
#error "HTTP video requires WS and post-handshake support"
#endif
namespace agon::extender::network {
namespace {
constexpr char kTag[]="http_video";
constexpr int kVideoSendWaitSeconds=5;
constexpr std::uint8_t kFrameRequest[]={'f','r','a','m','e'};
}
HttpVideoService::~HttpVideoService() {
  // A live HTTP task can still invoke virtual callbacks: never destroy its owner.
  // Explicit stop is required while the complete derived object is alive.
  if (server_.load()!=nullptr) abort();
}
bool HttpVideoService::startServer(web::EmbeddedAsset const *assets, std::size_t count,
                                  HttpVideoConfig const &options) noexcept {
  if (server_.load()!=nullptr) return !http_fault_;
  if ((count && !assets) || options.max_uri_handlers < count+1 ||
      options.max_open_sockets < 1 || options.port==options.control_port) return false;
  httpd_config_t config=HTTPD_DEFAULT_CONFIG();
  config.server_port=options.port; config.ctrl_port=options.control_port;
  config.max_uri_handlers=options.max_uri_handlers;
  config.max_open_sockets=options.max_open_sockets;config.stack_size=options.stack_bytes;
#ifdef AGON_EXTENDER_ROLLING_SCANOUT
  // HDMI02-F: socket/FAT-only handlers; no flash/NVS/cache-off operations.
  // IDF owns matching capability-aware deletion on server stop.
  config.task_caps = MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT;
#endif
  config.open_fn=&socketOpened;config.close_fn=&socketClosed;
  config.send_wait_timeout=kVideoSendWaitSeconds;config.lru_purge_enable=false;
  config.global_user_ctx=this;config.global_user_ctx_free_fn=nullptr;
  httpd_handle_t server=nullptr;
  if(httpd_start(&server,&config)!=ESP_OK){increment(http_start_failures_);return false;}
  server_.store(server);
  for(std::size_t i=0;i<count;++i){
    auto const &asset=assets[i];httpd_uri_t uri{};
    uri.uri=asset.route;uri.method=HTTP_GET;uri.handler=&assetHandler;
    uri.user_ctx=const_cast<web::EmbeddedAsset *>(&asset);
    if(!asset.route || !asset.media_type || !asset.data || !asset.size ||
       httpd_register_uri_handler(server,&uri)!=ESP_OK){
      http_fault_=true;increment(http_start_failures_);stopServer();return false;
    }
  }
#if !defined(AGON_EXTENDER_HDMI)
  httpd_uri_t video{};video.uri="/video";video.method=HTTP_GET;
  video.handler=&videoHandler;video.user_ctx=this;video.is_websocket=true;
  video.ws_post_handshake_cb=&videoPostHandshake;
  if(httpd_register_uri_handler(server,&video)!=ESP_OK){
    http_fault_=true;increment(http_start_failures_);stopServer();return false;
  }
#endif
#ifdef AGON_EXTENDER_RENDER_BENCHMARK
  httpd_uri_t bench{};bench.uri="/diagnostics/render-benchmark";bench.method=HTTP_GET;
  bench.handler=[](httpd_req_t *req)->esp_err_t {
    auto data=agon_bench::json();httpd_resp_set_type(req,"application/json");
    return httpd_resp_send(req,data.data(),data.size());
  };
  if(httpd_register_uri_handler(server,&bench)!=ESP_OK){http_fault_=true;stopServer();return false;}
#endif
  http_fault_=false;increment(http_starts_);return true;
}
bool HttpVideoService::stopServer() noexcept {
  auto server=server_.load();if(!server)return true;
  if(httpd_stop(server)!=ESP_OK){http_fault_=true;return false;}
  // HTTP task and queued callbacks have ended. Now release any remaining lease.
  {std::lock_guard<std::mutex> guard(video_dispatch_mutex_);
   video_.disconnect(video_.client());video_send_queued_=false;queued_video_client_=kNoVideoClient;}
  server_.store(nullptr);http_fault_=false;increment(http_stops_);return true;
}
esp_err_t HttpVideoService::sendSegments(httpd_handle_t server,int socket,
    OpaqueMessageSegment const *segments,std::size_t count) noexcept {
  for(std::size_t index=0;index<count;++index){
    httpd_ws_frame_t frame{};frame.fragmented=count>1;frame.final=index+1==count;
    frame.type=index==0?HTTPD_WS_TYPE_BINARY:HTTPD_WS_TYPE_CONTINUE;
    frame.payload=const_cast<std::uint8_t*>(segments[index].data);frame.len=segments[index].size;
    auto result=httpd_ws_send_frame_async(server,socket,&frame);if(result!=ESP_OK)return result;
  }
  return ESP_OK;
}
esp_err_t HttpVideoService::sendMessage(httpd_handle_t server,int socket,
    OpaqueMessageView const &view) noexcept {
  return sendSegments(server,socket,view.segments.data(),view.segment_count);
}
namespace {
int completeSend(httpd_handle_t, int fd, const char *data, size_t length, int flags) {
  // F003: IDF 5.5.5 WebSocket callers accept a positive short send. This
  // override returns the whole requested segment or an error, never a prefix.
  size_t sent=0;
  const auto start=esp_timer_get_time();
  while (sent<length) {
    if (esp_timer_get_time()-start>kVideoSendWaitSeconds*1000000LL) {
      return HTTPD_SOCK_ERR_TIMEOUT;
    }
    const auto n=send(fd,data+sent,length-sent,flags);
    if (n<0 && errno==EINTR) continue;
    if (n<=0) return HTTPD_SOCK_ERR_FAIL;
    sent+=size_t(n);
  }
  return int(sent);
}
}
void HttpVideoService::increment(
    std::atomic<std::uint32_t> &counter) noexcept {
  std::uint32_t value = counter.load(std::memory_order_relaxed);
  while (value != std::numeric_limits<std::uint32_t>::max() &&
         !counter.compare_exchange_weak(value, value + 1,
                                        std::memory_order_relaxed,
                                        std::memory_order_relaxed)) {
  }
}

esp_err_t HttpVideoService::socketOpened(httpd_handle_t server,int socket) noexcept {
  return httpd_sess_set_send_override(server,socket,&completeSend);
}

esp_err_t HttpVideoService::assetHandler(httpd_req_t *request) noexcept {
  auto const *asset = static_cast<web::EmbeddedAsset const *>(request->user_ctx);
  if (asset == nullptr || asset->data == nullptr || asset->size == 0)
    return httpd_resp_send_500(request);
  httpd_resp_set_type(request, asset->media_type);
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  // NET-001: idle page-download keep-alives can occupy all seven HTTP slots,
  // preventing a replacement viewer from even reaching its WS handshake.
  // Assets are finite responses; release their sockets, never the live stream.
  httpd_resp_set_hdr(request, "Connection", "close");
  auto const result = httpd_resp_send(request,
                         reinterpret_cast<char const *>(asset->data),
                         static_cast<ssize_t>(asset->size));
  if (result != ESP_OK) return result;
  return httpd_sess_trigger_close(request->handle, httpd_req_to_sockfd(request));
}

esp_err_t HttpVideoService::videoPostHandshake(
    httpd_req_t *request) noexcept {
  auto *service = static_cast<HttpVideoService *>(request->user_ctx);
  if (service == nullptr) return ESP_FAIL;
  service->negotiate(request);
  auto const socket = httpd_req_to_sockfd(request);
  std::lock_guard<std::mutex> guard(service->video_dispatch_mutex_);
  auto const previous = service->video_.client();
  if (previous >= 0 && previous != socket) {
    // Handshake and actual sends execute on the same HTTP task. The dispatch
    // mutex also excludes worker acquisition; releasing the old lease cannot
    // race a send. Old queued work is retained but cannot target the new client.
    service->video_.disconnect(previous);
    const std::uint8_t payload[] = {0x03, 0xe8, 'V','i','e','w','e','r',' ',
      'r','e','p','l','a','c','e','d'};
    httpd_ws_frame_t close{};
    close.type = HTTPD_WS_TYPE_CLOSE;
    close.payload = const_cast<std::uint8_t *>(payload);
    close.len = sizeof(payload);
    httpd_ws_send_frame_async(request->handle, previous, &close);
    httpd_sess_trigger_close(request->handle, previous);
    ESP_LOGI(kTag, "video viewer replaced fd=%d by fd=%d", previous, socket);
  }
  if (service->video_.connect(socket) == VideoConnectResult::Accepted) {
    ESP_LOGI(kTag, "video client accepted fd=%d", socket);
    return ESP_OK;
  }
  ESP_LOGW(kTag, "video client refused fd=%d", socket);
  service->closeVideo(request, 1013, "video client busy");
  return ESP_OK;
}

void HttpVideoService::closeVideo(httpd_req_t *request,
                                     std::uint16_t code,
                                     char const *reason) noexcept {
  std::array<std::uint8_t, 64> payload{};
  payload[0] = static_cast<std::uint8_t>(code >> 8U);
  payload[1] = static_cast<std::uint8_t>(code);
  auto const reason_size = std::strlen(reason);
  auto const copied = reason_size < payload.size() - 2 ? reason_size
                                                       : payload.size() - 2;
  std::memcpy(payload.data() + 2, reason, copied);
  httpd_ws_frame_t close{};
  close.type = HTTPD_WS_TYPE_CLOSE;
  close.payload = payload.data();
  close.len = copied + 2;
  auto const socket = httpd_req_to_sockfd(request);
  httpd_ws_send_frame(request, &close);
  video_.disconnect(socket);
  httpd_sess_trigger_close(request->handle, socket);
}

esp_err_t HttpVideoService::videoHandler(httpd_req_t *request) noexcept {
  auto *service = static_cast<HttpVideoService *>(request->user_ctx);
  if (service == nullptr) return ESP_FAIL;
  auto const socket = httpd_req_to_sockfd(request);

  httpd_ws_frame_t frame{};
  auto result = httpd_ws_recv_frame(request, &frame, 0);
  if (result != ESP_OK) return result;
  if (frame.type != HTTPD_WS_TYPE_TEXT || frame.len != sizeof(kFrameRequest)) {
    ESP_LOGW(kTag, "video protocol error fd=%d", socket);
    service->closeVideo(request, 1002, "expected frame credit");
    return ESP_OK;
  }
  std::array<std::uint8_t, sizeof(kFrameRequest)> payload{};
  frame.payload = payload.data();
  result = httpd_ws_recv_frame(request, &frame, payload.size());
  if (result != ESP_OK) return result;
  if (std::memcmp(payload.data(), kFrameRequest, payload.size()) != 0) {
    ESP_LOGW(kTag, "video protocol error fd=%d", socket);
    service->closeVideo(request, 1002, "expected frame credit");
    return ESP_OK;
  }

#if defined(AGON_EXTENDER_VIDEO_DISPATCH_TIMING)
  // Publish before admission makes the credit visible to the network worker.
  // Invalid/duplicate requests invalidate the diagnostic run, never change VDU.
  service->video_credit_at_.store(diagnostics::videoTimingNow(), std::memory_order_release);
#endif
  auto const credit = service->video_.requestFrame(socket);
  if (credit != VideoCreditResult::Accepted) {
    ESP_LOGW(kTag, "duplicate or invalid video credit fd=%d", socket);
    service->closeVideo(request, 1002, "duplicate frame credit");
    return ESP_OK;
  }
  service->notifyWorker();
  return ESP_OK;
}

void HttpVideoService::attemptVideoSend() noexcept {
#if defined(AGON_EXTENDER_HDMI)
  // HDMI owns presentation in this build. HTTP and its independent keyboard
  // WebSocket remain available without requesting a browser snapshot.
  return;
#endif
  if (!allowSend()) return;
  std::lock_guard<std::mutex> guard(video_dispatch_mutex_);
  if (video_send_queued_) return;
  auto const prepared = video_.tryPrepare(provider_);
  if (prepared == VideoPrepareResult::NoCredit ||
      prepared == VideoPrepareResult::NoNewMessage ||
      prepared == VideoPrepareResult::Disconnected)
    return;
  if (prepared == VideoPrepareResult::ProviderUnavailable ||
      prepared == VideoPrepareResult::ProviderInvalid) {
    auto const socket = video_.client();
    ESP_LOGE(kTag, "video provider unavailable or invalid fd=%d", socket);
    auto const server = server_.load(std::memory_order_acquire);
    if (server != nullptr && socket >= 0)
      httpd_sess_trigger_close(server, socket);
    return;
  }

  auto const server = server_.load(std::memory_order_acquire);
  if (server == nullptr ||
      httpd_queue_work(server, &queuedSend, this) != ESP_OK) {
    increment(queue_failures_);
    auto const socket = video_.client();
    video_.complete(socket, OpaqueReleaseDisposition::Failed);
    ESP_LOGE(kTag, "video send queue failed fd=%d", socket);
    if (server != nullptr && socket >= 0)
      httpd_sess_trigger_close(server, socket);
    return;
  }
#if defined(AGON_EXTENDER_VIDEO_DISPATCH_TIMING)
  diagnostics::videoDispatchTiming(diagnostics::Phase::Queue,
      video_credit_at_.load(std::memory_order_acquire));
  video_queued_at_ = diagnostics::videoTimingNow();
#endif
  queued_video_client_ = video_.client();
  video_send_queued_ = true;
  increment(queued_sends_);
}

void HttpVideoService::queuedSend(void *context) noexcept {
  static_cast<HttpVideoService *>(context)->performQueuedSend();
}

void HttpVideoService::performQueuedSend() noexcept {
  std::lock_guard<std::mutex> guard(video_dispatch_mutex_);
  if (!video_send_queued_) return;
  auto const socket = queued_video_client_;
  video_send_queued_ = false;
  queued_video_client_ = kNoVideoClient;
  auto const view = video_.sendingView(socket);
  auto const server = server_.load(std::memory_order_acquire);
  if (server == nullptr || socket < 0 || !view.valid() ||
      httpd_ws_get_fd_info(server, socket) !=
          HTTPD_WS_CLIENT_WEBSOCKET) {
    video_.complete(socket, OpaqueReleaseDisposition::Disconnected);
    return;
  }

#if defined(AGON_EXTENDER_VIDEO_DISPATCH_TIMING)
  diagnostics::videoDispatchTiming(diagnostics::Phase::TxEnqueue, video_queued_at_);
#endif
  const auto result = sendMessage(server, socket, view);
  if (result == ESP_OK) {
    video_.complete(socket, OpaqueReleaseDisposition::Sent);
  } else {
    increment(socket_send_failures_);
    video_.complete(socket, OpaqueReleaseDisposition::Failed);
    ESP_LOGE(kTag, "video socket send failed fd=%d err=%d", socket, result);
    httpd_sess_trigger_close(server, socket);
  }
}

void HttpVideoService::socketClosed(httpd_handle_t server,
                                       int socket) noexcept {
  auto *service = static_cast<HttpVideoService *>(
      httpd_get_global_user_ctx(server));
  if (service != nullptr && service->video_.disconnect(socket))
    ESP_LOGI(kTag, "video client disconnected fd=%d", socket);
  lwip_close(socket);
}

} // namespace agon::extender::network
