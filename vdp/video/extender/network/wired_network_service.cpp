#include "extender/network/wired_network_service.hpp"

#include <array>
#include <cstring>
#include <limits>
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <new>
#include "extender/diagnostic/browser_trace.hpp"
#include <esp_timer.h>
#include "extender/input/browser_keyboard.hpp"

#include <esp_log.h>
#include <lwip/sockets.h>

#include "extender/web/embedded_assets.hpp"
#ifdef AGON_EXTENDER_BROWSER_TYPING
#include "../../../.pio/build-identities/p4-browser-typing/build_identity.hpp"
#endif

#if !CONFIG_HTTPD_WS_SUPPORT
#error "PORT-006 requires CONFIG_HTTPD_WS_SUPPORT"
#endif
#if !CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT
#error "PORT-006 requires CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT"
#endif

namespace agon::extender::network {
using diagnostic::trace;
namespace {

constexpr char kTag[] = "extender_net";
constexpr std::uint8_t kFrameRequest[] = {'f', 'r', 'a', 'm', 'e'};
constexpr std::uint32_t kWorkerPollMilliseconds = 10;
constexpr std::uint32_t kWorkerStackBytes = 8192;
constexpr UBaseType_t kWorkerPriority = 3;

}  // namespace

WiredNetworkService::WiredNetworkService(
    OpaqueMessageProvider &provider) noexcept
    : provider_(provider) {}

WiredNetworkService::~WiredNetworkService() {
  stop();
  // F012 containment: destruction with a live callback target is forbidden.
  // The static product service has process lifetime; a failed stop is fatal
  // for a hypothetical shorter-lived owner rather than a use-after-free.
  if (server_.load()!=nullptr) abort();
}

void WiredNetworkService::increment(
    std::atomic<std::uint32_t> &counter) noexcept {
  std::uint32_t value = counter.load(std::memory_order_relaxed);
  while (value != std::numeric_limits<std::uint32_t>::max() &&
         !counter.compare_exchange_weak(value, value + 1,
                                        std::memory_order_relaxed,
                                        std::memory_order_relaxed)) {
  }
}

bool WiredNetworkService::start() noexcept {
  auto expected = WiredServiceState::Stopped;
  if (!state_.compare_exchange_strong(expected, WiredServiceState::Starting))
    return expected != WiredServiceState::Faulted;

  stop_requested_.store(false, std::memory_order_release);
  pending_events_.store(0, std::memory_order_release);
  network_event_handle_ = Network.onEvent(
      [this](arduino_event_id_t event, arduino_event_info_t) {
        onNetworkEvent(event);
      });
  network_event_registered_ = true;

  TaskHandle_t task = nullptr;
  if (xTaskCreate(&workerEntry, "extender-net", kWorkerStackBytes, this,
                  kWorkerPriority, &task) != pdPASS) {
    Network.removeEvent(network_event_handle_);
    network_event_registered_ = false;
    state_.store(WiredServiceState::Faulted, std::memory_order_release);
    ESP_LOGE(kTag, "network worker creation failed");
    return false;
  }
  worker_task_.store(task, std::memory_order_release);

  // Olimex ESP32-P4-DevKit Rev D1 IP101GRI wiring. DHCP remains the
  // NetworkInterface default; no address is compiled into this call.
  if (!ETH.begin(ETH_PHY_IP101, 1, 31, 52, 51, EMAC_CLK_EXT_IN)) {
    ESP_LOGE(kTag, "ETH.begin failed");
    state_.store(WiredServiceState::Faulted, std::memory_order_release);
    stop();
    state_.store(WiredServiceState::Faulted, std::memory_order_release);
    return false;
  }
  ESP_LOGI(kTag, "wired service starting with DHCP");
  return true;
}

void WiredNetworkService::stop() noexcept {
  auto const current = state_.load(std::memory_order_acquire);
  if (current == WiredServiceState::Stopped &&
      worker_task_.load(std::memory_order_acquire) == nullptr)
    return;

  stop_requested_.store(true, std::memory_order_release);
  notifyWorker();
  while (worker_task_.load(std::memory_order_acquire) != nullptr)
    vTaskDelay(pdMS_TO_TICKS(1));

  if (network_event_registered_) {
    Network.removeEvent(network_event_handle_);
    network_event_registered_ = false;
  }
  ETH.end();
  state_.store(WiredServiceState::Stopped, std::memory_order_release);
  ESP_LOGI(kTag, "wired service stopped");
}

WiredServiceState WiredNetworkService::state() const noexcept {
  return state_.load(std::memory_order_acquire);
}

WiredNetworkMetrics WiredNetworkService::metrics() const noexcept {
  return {
      video_.metrics(),
      http_starts_.load(std::memory_order_relaxed),
      http_stops_.load(std::memory_order_relaxed),
      http_start_failures_.load(std::memory_order_relaxed),
      queued_sends_.load(std::memory_order_relaxed),
      queue_failures_.load(std::memory_order_relaxed),
      socket_send_failures_.load(std::memory_order_relaxed),
  };
}

void WiredNetworkService::notifyWorker() noexcept {
  auto const task = worker_task_.load(std::memory_order_acquire);
  if (task != nullptr) xTaskNotifyGive(task);
}

void WiredNetworkService::onNetworkEvent(arduino_event_id_t event) noexcept {
  trace("network_event",0,event);
  std::uint32_t bit = 0;
  switch (event) {
    case ARDUINO_EVENT_ETH_START: bit = EthernetStarted; break;
    case ARDUINO_EVENT_ETH_CONNECTED: bit = EthernetConnected; break;
    case ARDUINO_EVENT_ETH_GOT_IP: bit = EthernetGotIp; break;
    case ARDUINO_EVENT_ETH_LOST_IP: bit = EthernetLostIp; break;
    case ARDUINO_EVENT_ETH_DISCONNECTED: bit = EthernetDisconnected; break;
    case ARDUINO_EVENT_ETH_STOP: bit = EthernetStopped; break;
    default: return;
  }
  pending_events_.fetch_or(bit, std::memory_order_release);
  notifyWorker();
}

void WiredNetworkService::workerEntry(void *context) noexcept {
  static_cast<WiredNetworkService *>(context)->worker();
}

void WiredNetworkService::worker() noexcept {
  while (!stop_requested_.load(std::memory_order_acquire)) {
    auto const events = pending_events_.exchange(0, std::memory_order_acq_rel);
    if (events != 0) processEvents(events);
    if (http_fault_) { stopHttp(); if (!http_fault_ && ETH.hasIP()) processEvents(EthernetGotIp); }
    if (state() == WiredServiceState::LeasedServing) attemptVideoSend();
    ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(kWorkerPollMilliseconds));
  }
  stopHttp();
  worker_task_.store(nullptr, std::memory_order_release);
  vTaskDelete(nullptr);
}

void WiredNetworkService::processEvents(std::uint32_t events) noexcept {
  if ((events & EthernetStarted) != 0) {
    state_.store(WiredServiceState::LinkDown, std::memory_order_release);
    ESP_LOGI(kTag, "Ethernet interface started");
  }
  if ((events & EthernetConnected) != 0) {
    state_.store(WiredServiceState::LinkUpNoLease,
                 std::memory_order_release);
    ESP_LOGI(kTag, "Ethernet link connected");
  }

  // Event bits can coalesce before this worker runs. Current interface truth,
  // not arbitrary bit order, decides whether HTTP may remain active.
  if ((events & (EthernetLostIp | EthernetDisconnected | EthernetStopped)) !=
          0 &&
      !ETH.hasIP()) {
    stopHttp();
    auto const next = ETH.linkUp() ? WiredServiceState::LinkUpNoLease
                                   : WiredServiceState::LinkDown;
    state_.store(next, std::memory_order_release);
    if ((events & EthernetLostIp) != 0) ESP_LOGW(kTag, "DHCP lease lost");
    if ((events & EthernetDisconnected) != 0)
      ESP_LOGW(kTag, "Ethernet link disconnected");
  }
  if ((events & EthernetGotIp) != 0 && ETH.hasIP()) {
    reportLease();
    if (startHttp())
      state_.store(WiredServiceState::LeasedServing,
                   std::memory_order_release);
    else
      state_.store(WiredServiceState::Faulted, std::memory_order_release);
  }
}

void WiredNetworkService::reportLease() const noexcept {
  auto const ip = ETH.localIP().toString();
  auto const mask = ETH.subnetMask().toString();
  auto const gateway = ETH.gatewayIP().toString();
  auto const dns = ETH.dnsIP().toString();
  ESP_LOGI(kTag, "DHCP ip=%s netmask=%s gateway=%s dns=%s", ip.c_str(),
           mask.c_str(), gateway.c_str(), dns.c_str());
}

namespace {
int completeSend(httpd_handle_t, int fd, const char *data, size_t length, int flags) {
  // F003: IDF 5.5.5 WebSocket callers accept a positive short send. This
  // override returns the whole requested segment or an error, never a prefix.
  size_t sent=0;
  const auto start=esp_timer_get_time();
  while (sent<length) {
    if (esp_timer_get_time()-start>1000000) {
      trace("send_budget",fd,length,sent,esp_timer_get_time()-start);
      return HTTPD_SOCK_ERR_TIMEOUT;
    }
    const auto n=send(fd,data+sent,length-sent,flags);
    if (n<0 && errno==EINTR) continue;
    if (n<=0) { trace("send_error",fd,length,sent,n<0?errno:0); return HTTPD_SOCK_ERR_FAIL; }
    sent+=size_t(n);
  }
  return int(sent);
}
}
esp_err_t WiredNetworkService::socketOpened(httpd_handle_t server,int socket) noexcept {
  trace("socket_open",socket);
  return httpd_sess_set_send_override(server,socket,&completeSend);
}
esp_err_t WiredNetworkService::keyboardAdmission(httpd_req_t *request) noexcept {
  // Deliberately trusted bench LAN, explicit same-origin opt-in. No credentials
  // or general remote access claim. Host and Origin must equal the leased IP;
  // attacker-controlled matching Host/Origin names cannot pass DNS rebinding.
  char origin[80]{},host[64]{};
  auto expected=ETH.localIP().toString();
  if (httpd_req_get_hdr_value_str(request,"Host",host,sizeof(host))!=ESP_OK ||
      httpd_req_get_hdr_value_str(request,"Origin",origin,sizeof(origin))!=ESP_OK ||
      expected!=host || (String("http://")+expected)!=origin) return ESP_FAIL;
  return ESP_OK;
}
namespace {
struct KeyTraceContext { uint32_t session{}, ordinal{}; };
uint32_t traceSession(httpd_req_t *r) {
  char query[80]{}, value[20]{};
  if(httpd_req_get_url_query_str(r,query,sizeof(query))!=ESP_OK ||
     httpd_query_key_value(query,"sid",value,sizeof(value))!=ESP_OK) return 0;
  return uint32_t(strtoul(value,nullptr,10));
}
}
esp_err_t WiredNetworkService::keyboardPostHandshake(httpd_req_t *request) noexcept {
  // IDF 5.5.5 httpd_uri.c returns after the WebSocket handshake callbacks;
  // it explicitly skips the URI handler for the initial GET. r02/r03 put
  // this allocation in keyboardHandler's GET branch, so every first message
  // lacked context and was rejected. Keep initialization in this callback.
  if(request->sess_ctx) return ESP_FAIL;
  auto *ctx=static_cast<KeyTraceContext *>(calloc(1,sizeof(KeyTraceContext)));
  if(!ctx) return ESP_ERR_NO_MEM;
  ctx->session=traceSession(request); request->sess_ctx=ctx; request->free_ctx=free;
  trace("keyboard_open",ctx->session,httpd_req_to_sockfd(request));
  return ESP_OK;
}
esp_err_t WiredNetworkService::keyboardHandler(httpd_req_t *request) noexcept {
  const int socket=httpd_req_to_sockfd(request);
  if(request->method==HTTP_GET) return ESP_OK;
  auto *ctx=static_cast<KeyTraceContext *>(request->sess_ctx);
  if(!ctx) { trace("key_context_missing",socket); return ESP_FAIL; }
  auto &keys=input::browserKeyboard();
  httpd_ws_frame_t frame{};
  auto rc=httpd_ws_recv_frame(request,&frame,0);
  if (rc!=ESP_OK) { trace("key_recv_header_error",ctx->session,socket,rc); keys.close(socket); return rc; }
  uint8_t bytes[4]{};
  if (frame.type!=HTTPD_WS_TYPE_BINARY || (frame.len!=1 && frame.len!=4) || !frame.final) {
    trace("key_frame_rejected",ctx->session,socket,frame.type,frame.len);
    keys.close(socket); return ESP_FAIL;
  }
  frame.payload=bytes;
  rc=httpd_ws_recv_frame(request,&frame,sizeof(bytes));
  if (rc!=ESP_OK) { trace("key_recv_payload_error",ctx->session,socket,rc); keys.close(socket); return rc; }
  ++ctx->ordinal;
  const auto packed=uint32_t(bytes[0])|(uint32_t(bytes[1])<<8)|(uint32_t(bytes[2])<<16)|(uint32_t(bytes[3])<<24);
  trace("key_message",ctx->session,ctx->ordinal,packed,socket);
  const auto now=uint32_t(esp_timer_get_time()/1000);
  bool ok=false;
  if (frame.len==1 && bytes[0]=='T') ok=keys.take(socket,now);
  else if (frame.len==1 && bytes[0]=='H') ok=keys.heartbeat(socket,now);
  else if (frame.len==1 && bytes[0]=='R') { keys.close(socket); ok=true; }
  else if (frame.len==4 && bytes[0]=='K') ok=keys.push(socket,{bytes[1],bytes[2],bytes[3],ctx->session,ctx->ordinal},now);
  if (!ok) { trace("key_rejected",ctx->session,ctx->ordinal,packed,socket); keys.close(socket); return ESP_FAIL; }
  // Acknowledgement is admission, not confirmation of EMOS consumption.
  httpd_ws_frame_t ack{}; uint8_t accepted='A';
  ack.type=HTTPD_WS_TYPE_BINARY; ack.payload=&accepted; ack.len=1;
  trace("key_ack_start",ctx->session,ctx->ordinal);
  rc=httpd_ws_send_frame(request,&ack);
  trace("key_ack_end",ctx->session,ctx->ordinal,rc);
  if (rc!=ESP_OK) keys.close(socket);
  return rc;
}

#ifdef AGON_EXTENDER_BROWSER_TYPING
esp_err_t WiredNetworkService::traceHandler(httpd_req_t *request) noexcept {
  // Explicit after-run export only. It shares HTTP execution with video; the
  // page disconnects video first. Never poll this endpoint during measurement.
  auto &t=diagnostic::browserTrace();
  char query[40]{};
  httpd_req_get_url_query_str(request,query,sizeof(query));
  httpd_resp_set_hdr(request,"Cache-Control","no-store");
  if(!strcmp(query,"on") || !strcmp(query,"off")) {
    t.configure(!strcmp(query,"on"));
    return httpd_resp_sendstr(request,t.available()?"ok":"trace allocation failed");
  }
  auto total=t.freeze();
  httpd_resp_set_type(request,"text/plain");
  // r02's 2 KiB automatic buffer overflowed IDF 5.5.5's 4 KiB HTTP
  // stack during snprintf/response handling (P4 stack-protection panic).
  // Allocate only for after-run export; retain the ordinary task stack and
  // measured traffic behavior. Keep this buffer off-stack in future revisions.
  constexpr size_t chunk_size=2048;
  std::unique_ptr<char[]> storage(new(std::nothrow) char[chunk_size]);
  if(!storage) return httpd_resp_send_500(request);
  char *chunk=storage.get();
  int used=snprintf(chunk,chunk_size,"# " AGON_EXTENDER_BUILD_ID " (" AGON_EXTENDER_ARTIFACT_STATUS ")\n# browser timing v1; us=P4 monotonic; capacity=%u; total=%llu; overwritten=%llu; available=%d; cost_us=%lld; max_cost_us=%lld\nindex,us,event,id,a,b,c\n",
    t.capacity,(unsigned long long)total,(unsigned long long)(total>t.capacity?total-t.capacity:0),t.available(),
    (long long)t.cost_us(),(long long)t.max_cost_us());
  diagnostic::TraceRecord row{};
  for(auto i=total>t.capacity?total-t.capacity:0;i<total;++i) {
    if(!t.read(i,row)) continue;
    if(used>int(chunk_size)-200) {
      if(httpd_resp_send_chunk(request,chunk,used)!=ESP_OK) return ESP_FAIL;
      used=0;
    }
    used+=snprintf(chunk+used,chunk_size-used,"%llu,%lld,%s,%llu,%lld,%lld,%lld\n",
      (unsigned long long)i,(long long)row.us,row.event,(unsigned long long)row.id,
      (long long)row.a,(long long)row.b,(long long)row.c);
  }
  if(used && httpd_resp_send_chunk(request,chunk,used)!=ESP_OK) return ESP_FAIL;
  return httpd_resp_send_chunk(request,nullptr,0);
}
#endif

esp_err_t WiredNetworkService::assetHandler(httpd_req_t *request) noexcept {
  auto const *asset = static_cast<web::EmbeddedAsset const *>(request->user_ctx);
  if (asset == nullptr || asset->data == nullptr || asset->size == 0)
    return httpd_resp_send_500(request);
  httpd_resp_set_type(request, asset->media_type);
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  return httpd_resp_send(request,
                         reinterpret_cast<char const *>(asset->data),
                         static_cast<ssize_t>(asset->size));
}

bool WiredNetworkService::startHttp() noexcept {
  if (server_.load(std::memory_order_acquire) != nullptr) return !http_fault_;

  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.max_uri_handlers = 8;
  config.open_fn = &socketOpened;
  config.send_wait_timeout = 1;
  config.recv_wait_timeout = 1;
  config.lru_purge_enable = false;
  config.global_user_ctx = this;
  config.global_user_ctx_free_fn = nullptr;
  config.close_fn = &socketClosed;
  httpd_handle_t server = nullptr;
  if (httpd_start(&server, &config) != ESP_OK) {
    increment(http_start_failures_);
    ESP_LOGE(kTag, "HTTP server start failed");
    return false;
  }
  server_.store(server, std::memory_order_release);

  for (auto const &asset : web::embeddedBrowserAssets()) {
    httpd_uri_t uri{};
    uri.uri = asset.route;
    uri.method = HTTP_GET;
    uri.handler = &assetHandler;
    uri.user_ctx = const_cast<web::EmbeddedAsset *>(&asset);
    if (httpd_register_uri_handler(server, &uri) != ESP_OK) {
      ESP_LOGE(kTag, "HTTP route registration failed: %s", asset.route);
      http_fault_=true;
      stopHttp();
      increment(http_start_failures_);
      return false;
    }
  }

  httpd_uri_t video{};
  video.uri = "/video";
  video.method = HTTP_GET;
  video.handler = &videoHandler;
  video.user_ctx = this;
  video.is_websocket = true;
  video.ws_post_handshake_cb = &videoPostHandshake;
  if (httpd_register_uri_handler(server, &video) != ESP_OK) {
    ESP_LOGE(kTag, "video WebSocket registration failed");
    http_fault_=true;
    stopHttp();
    increment(http_start_failures_);
    return false;
  }

#ifdef AGON_EXTENDER_BROWSER_TYPING
  httpd_uri_t keyboard{};
  keyboard.uri="/keyboard"; keyboard.method=HTTP_GET;
  keyboard.handler=&keyboardHandler; keyboard.user_ctx=this;
  keyboard.is_websocket=true;
  keyboard.ws_pre_handshake_cb=&keyboardAdmission;
  keyboard.ws_post_handshake_cb=&keyboardPostHandshake;
  if (httpd_register_uri_handler(server,&keyboard)!=ESP_OK) {
    http_fault_=true; stopHttp(); increment(http_start_failures_); return false;
  }
#endif
#ifdef AGON_EXTENDER_BROWSER_TYPING
  httpd_uri_t timing{};
  timing.uri="/diagnostics"; timing.method=HTTP_GET; timing.handler=&traceHandler;
  if(httpd_register_uri_handler(server,&timing)!=ESP_OK) {
    http_fault_=true; stopHttp(); increment(http_start_failures_); return false;
  }
#endif
  http_fault_=false;
  increment(http_starts_);
  ESP_LOGI(kTag, "HTTP browser service ready");
  return true;
}

void WiredNetworkService::stopHttp() noexcept {
  auto const server = server_.load(std::memory_order_acquire);
  input::browserKeyboard().ready(false);
  if (server == nullptr) return;
  if (httpd_stop(server) == ESP_OK) {
    server_.store(nullptr,std::memory_order_release);
    http_fault_=false;
    increment(http_stops_);
    ESP_LOGI(kTag, "HTTP browser service stopped");
  } else {
    http_fault_=true;
    ESP_LOGE(kTag, "HTTP browser service stop failed; live handle retained");
  }
}

esp_err_t WiredNetworkService::videoPostHandshake(
    httpd_req_t *request) noexcept {
  auto *service = static_cast<WiredNetworkService *>(request->user_ctx);
  if (service == nullptr) return ESP_FAIL;
  auto const socket = httpd_req_to_sockfd(request);
  trace("video_open",traceSession(request),socket);
  if (service->video_.connect(socket) == VideoConnectResult::Accepted) {
    ESP_LOGI(kTag, "video client accepted fd=%d", socket);
    return ESP_OK;
  }
  ESP_LOGW(kTag, "video client refused fd=%d", socket);
  service->closeVideo(request, 1013, "video client busy");
  return ESP_OK;
}

void WiredNetworkService::closeVideo(httpd_req_t *request,
                                     std::uint16_t code,
                                     char const *reason) noexcept {
  trace("video_close_requested",httpd_req_to_sockfd(request),code);
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

esp_err_t WiredNetworkService::videoHandler(httpd_req_t *request) noexcept {
  auto *service = static_cast<WiredNetworkService *>(request->user_ctx);
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

  auto const credit = service->video_.requestFrame(socket);
  if (credit != VideoCreditResult::Accepted) {
    ESP_LOGW(kTag, "duplicate or invalid video credit fd=%d", socket);
    service->closeVideo(request, 1002, "duplicate frame credit");
    return ESP_OK;
  }
  service->notifyWorker();
  return ESP_OK;
}

void WiredNetworkService::attemptVideoSend() noexcept {
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
  const auto queued_view=video_.sendingView(video_.client());
  trace("video_queued",queued_view.token,video_.client());
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
  increment(queued_sends_);
}

void WiredNetworkService::queuedSend(void *context) noexcept {
  static_cast<WiredNetworkService *>(context)->performQueuedSend();
}

void WiredNetworkService::performQueuedSend() noexcept {
  auto const socket = video_.client();
  auto const view = video_.sendingView(socket);
  auto const server = server_.load(std::memory_order_acquire);
  if (server == nullptr || socket < 0 || !view.valid() ||
      httpd_ws_get_fd_info(server, socket) !=
          HTTPD_WS_CLIENT_WEBSOCKET) {
    video_.complete(socket, OpaqueReleaseDisposition::Disconnected);
    return;
  }

  trace("video_send_start",view.token,socket,view.total_bytes);
  esp_err_t result = ESP_OK;
  for (std::size_t index = 0; index < view.segment_count; ++index) {
    httpd_ws_frame_t frame{};
    frame.fragmented = view.segment_count > 1;
    frame.final = index + 1 == view.segment_count;
    frame.type = index == 0 ? HTTPD_WS_TYPE_BINARY : HTTPD_WS_TYPE_CONTINUE;
    frame.payload = const_cast<std::uint8_t *>(view.segments[index].data);
    frame.len = view.segments[index].size;
    result = httpd_ws_send_frame_async(server, socket, &frame);
    if (result != ESP_OK) break;
  }

  trace("video_send_end",view.token,socket,result);
  if (result == ESP_OK) {
    video_.complete(socket, OpaqueReleaseDisposition::Sent);
  } else {
    increment(socket_send_failures_);
    video_.complete(socket, OpaqueReleaseDisposition::Failed);
    ESP_LOGE(kTag, "video socket send failed fd=%d err=%d", socket, result);
    httpd_sess_trigger_close(server, socket);
  }
}

void WiredNetworkService::socketClosed(httpd_handle_t server,
                                       int socket) noexcept {
  trace("socket_close",socket);
  input::browserKeyboard().close(socket);
  auto *service = static_cast<WiredNetworkService *>(
      httpd_get_global_user_ctx(server));
  if (service != nullptr && service->video_.disconnect(socket))
    ESP_LOGI(kTag, "video client disconnected fd=%d", socket);
  lwip_close(socket);
}

}  // namespace agon::extender::network
