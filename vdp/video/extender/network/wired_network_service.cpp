#if defined(AGON_EXTENDER_TELEMETRY)
#include "../telemetry/target.hpp"
#endif
// Video, SD RPC and explicit host keyboard requests; browser input stays retired.
// Keep F003 complete writes and F012 failed-stop containment; no browser input
// lease or browser-keyboard callback belongs here. Optional timing endpoints
// are read-only diagnostics; they do not reinstate browser input.
#include "extender/network/wired_network_service.hpp"
#include "extender/diagnostics/frame_timing.hpp"
#if defined(AGON_EXTENDER_SD_SERVICE)
#include "extender/storage/sd_target.hpp"
#include <cstdio>
#endif
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
#include "extender/input/remote_target.hpp"
#include <cstdio>
#endif

#include <array>
#include <cstring>
#include <limits>
#include <cerrno>
#include <cstdlib>
#include <esp_timer.h>

#include <esp_log.h>
#include <lwip/sockets.h>

#include "extender/web/embedded_assets.hpp"

#if !CONFIG_HTTPD_WS_SUPPORT
#error "PORT-006 requires CONFIG_HTTPD_WS_SUPPORT"
#endif
#if !CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT
#error "PORT-006 requires CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT"
#endif

namespace agon::extender::network {
namespace {

constexpr char kTag[] = "extender_net";
// Restore the video-only baseline's ESP-IDF 5.5.5 default socket timeout.
// Browser-input work shortened it to one second, which also affected video.
// Keep complete-or-error writes (F003) without that experimental deadline.
constexpr int kVideoSendWaitSeconds = 5;
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
esp_err_t WiredNetworkService::socketOpened(httpd_handle_t server,int socket) noexcept {
  return httpd_sess_set_send_override(server,socket,&completeSend);
}
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

#if defined(AGON_EXTENDER_FRAME_TIMING)
namespace {
esp_err_t timingHandler(httpd_req_t *request) {
  const auto body = agon::extender::diagnostics::timingJson();
  if (body.empty()) return httpd_resp_send_500(request);
  httpd_resp_set_type(request, "application/json");
  httpd_resp_set_hdr(request, "Cache-Control", "no-store");
  return httpd_resp_send(request, body.data(), body.size());
}
}
#endif


#if defined(AGON_EXTENDER_SD_SERVICE)
namespace {
std::uint32_t sdNow() { return std::uint32_t(esp_timer_get_time()/1000); }
esp_err_t sdStatusHandler(httpd_req_t *request) {
  bool online,pending;std::uint32_t boot;
  storage::sdStatus(sdNow(),online,pending,boot);
  char body[100];
  const int n=snprintf(body,sizeof(body),
      "{\"protocol\":1,\"online\":%s,\"pending\":%s,\"boot\":%lu}",
      online?"true":"false",pending?"true":"false",(unsigned long)boot);
  httpd_resp_set_type(request,"application/json");
  httpd_resp_set_hdr(request,"Cache-Control","no-store");
  return httpd_resp_send(request,body,n);
}
esp_err_t sdRpcHandler(httpd_req_t *request) {
  if(request->content_len<SD_HEADER || request->content_len>SD_MAX_RECORD)
    return httpd_resp_send_err(request,HTTPD_400_BAD_REQUEST,"Invalid record length");
  std::uint8_t input[SD_MAX_RECORD],output[SD_MAX_RECORD];
  unsigned received=0,out_length=0;
  const auto started=esp_timer_get_time();
  // Only receive this small HTTP body here. Filesystem/UART completion is
  // asynchronous; repeated identical POSTs retrieve the cached result.
  while(received<request->content_len) {
    const int n=httpd_req_recv(request,reinterpret_cast<char *>(input+received),
                               request->content_len-received);
    if(n<=0 || esp_timer_get_time()-started>3000000) return ESP_FAIL;
    received+=unsigned(n);
  }
  const unsigned status=storage::sdPost(input,received,output,out_length,sdNow());
  const char *label=status==200?"200 OK":status==202?"202 Accepted":
      status==409?"409 Conflict":status==503?"503 Service Unavailable":"400 Bad Request";
  httpd_resp_set_status(request,label);
  httpd_resp_set_hdr(request,"Cache-Control","no-store");
  httpd_resp_set_type(request,"application/octet-stream");
  return httpd_resp_send(request,reinterpret_cast<const char *>(output),out_length);
}
}
#endif

#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
namespace {
std::uint32_t keyboardNow() { return std::uint32_t(esp_timer_get_time()/1000); }
esp_err_t keyboardReply(httpd_req_t *request,unsigned code) {
  const auto s=input::remoteLocked([](auto &r){return r.status(keyboardNow());});
  char body[450];
  const int n=snprintf(body,sizeof(body),
    "{\"protocol\":1,\"boot\":%lu,\"session\":%lu,\"sequence\":%lu,"
    "\"emitted\":%lu,\"accepted\":%lu,\"discarded\":%lu,\"pending\":%u,\"held\":%u,\"locale\":%u,"
    "\"ready\":%s,\"physical_neutral\":%s,\"caps\":%s,\"reason\":%u}",
    (unsigned long)s.boot,(unsigned long)s.session,(unsigned long)s.sequence,
    (unsigned long)s.emitted,(unsigned long)s.accepted,(unsigned long)s.discarded,s.pending,s.held,s.locale,s.ready?"true":"false",
    s.physical_neutral?"true":"false",s.caps?"true":"false",unsigned(s.reason));
  httpd_resp_set_status(request,code==200?"200 OK":code==409?"409 Conflict":
      code==503?"503 Service Unavailable":"400 Bad Request");
  httpd_resp_set_type(request,"application/json");
  httpd_resp_set_hdr(request,"Cache-Control","no-store");
  return httpd_resp_send(request,body,n);
}
esp_err_t keyboardStatusHandler(httpd_req_t *request) { return keyboardReply(request,200); }
esp_err_t keyboardRpcHandler(httpd_req_t *request) {
  // Intent header plus no browser Origin keeps the retired browser input path
  // unavailable. This is a local bench endpoint, not an Internet-auth service.
  char intent[4]{};
  if(httpd_req_get_hdr_value_len(request,"Origin") ||
     httpd_req_get_hdr_value_str(request,"X-Agon-Keyboard",intent,sizeof(intent))!=ESP_OK ||
     std::strcmp(intent,"1") || request->content_len<input::REMOTE_HEADER ||
     request->content_len>input::REMOTE_MAX)return httpd_resp_send_err(request,HTTPD_400_BAD_REQUEST,"Invalid keyboard request");
  uint8_t body[input::REMOTE_MAX];unsigned used=0;const auto began=esp_timer_get_time();
  while(used<request->content_len) {
    int n=httpd_req_recv(request,reinterpret_cast<char *>(body+used),request->content_len-used);
    if(n<=0 || esp_timer_get_time()-began>3000000)return ESP_FAIL;
    used+=unsigned(n);
  }
  auto code=input::remoteLocked([&](auto &r){return r.post(body,used,keyboardNow());});
  return keyboardReply(request,code);
}
}
#endif

#if defined(AGON_EXTENDER_TELEMETRY)
namespace {
esp_err_t telemetryHandler(httpd_req_t *request) {
  const auto snapshot=telemetry::snapshot();
  const auto now=std::uint32_t(esp_timer_get_time()/1000);
  char hex[telemetry::SnapshotSize*2+1];
  static const char digits[]="0123456789abcdef";
  for(unsigned i=0;i<telemetry::SnapshotSize;++i) {
    hex[i*2]=digits[snapshot.bytes[i]>>4];hex[i*2+1]=digits[snapshot.bytes[i]&15];
  }
  hex[telemetry::SnapshotSize*2]=0;
  char body[440];
  const int n=snprintf(body,sizeof(body),
      "{\"online\":%s,\"age_ms\":%lu,\"received\":%lu,\"payload\":\"%s\"}",
      snapshot.online(now)?"true":"false",(unsigned long)snapshot.age(now),
      (unsigned long)snapshot.received,hex);
  httpd_resp_set_type(request,"application/json");
  httpd_resp_set_hdr(request,"Cache-Control","no-store");
  return httpd_resp_send(request,body,n);
}
}
#endif

bool WiredNetworkService::startHttp() noexcept {
  if (server_.load(std::memory_order_acquire) != nullptr) return !http_fault_;

  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.max_uri_handlers = 6;
#if defined(AGON_EXTENDER_TELEMETRY)
  ++config.max_uri_handlers;
#endif
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
  config.max_uri_handlers += 2;
#endif
#if defined(AGON_EXTENDER_SD_SERVICE)
  config.max_uri_handlers += 2;
#endif
#if defined(AGON_EXTENDER_FRAME_TIMING)
  ++config.max_uri_handlers; // five assets + video + diagnostic GET
#endif
  config.open_fn = &socketOpened;
  config.send_wait_timeout = kVideoSendWaitSeconds;
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

#if defined(AGON_EXTENDER_FRAME_TIMING)
  httpd_uri_t timing{};
  timing.uri = "/diagnostics/frame-timing";
  timing.method = HTTP_GET;
  timing.handler = &timingHandler;
  if (httpd_register_uri_handler(server, &timing) != ESP_OK) {
    http_fault_ = true;
    stopHttp();
    increment(http_start_failures_);
    return false;
  }
#endif
#if defined(AGON_EXTENDER_SD_SERVICE)
  httpd_uri_t sd_status{},sd_rpc{};
  sd_status.uri="/sd/status";sd_status.method=HTTP_GET;sd_status.handler=&sdStatusHandler;
  sd_rpc.uri="/sd/rpc";sd_rpc.method=HTTP_POST;sd_rpc.handler=&sdRpcHandler;
  if(httpd_register_uri_handler(server,&sd_status)!=ESP_OK ||
     httpd_register_uri_handler(server,&sd_rpc)!=ESP_OK) {
    http_fault_=true;stopHttp();increment(http_start_failures_);return false;
  }
#endif
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
  httpd_uri_t key_status{},key_rpc{};
  key_status.uri="/keyboard/status";key_status.method=HTTP_GET;key_status.handler=&keyboardStatusHandler;
  key_rpc.uri="/keyboard/rpc";key_rpc.method=HTTP_POST;key_rpc.handler=&keyboardRpcHandler;
  if(httpd_register_uri_handler(server,&key_status)!=ESP_OK ||
     httpd_register_uri_handler(server,&key_rpc)!=ESP_OK) {
    http_fault_=true;stopHttp();increment(http_start_failures_);return false;
  }
#endif
#if defined(AGON_EXTENDER_TELEMETRY)
  httpd_uri_t telemetry_uri{};
  telemetry_uri.uri="/telemetry/latest";telemetry_uri.method=HTTP_GET;
  telemetry_uri.handler=&telemetryHandler;
  if(httpd_register_uri_handler(server,&telemetry_uri)!=ESP_OK) {
    http_fault_=true;stopHttp();increment(http_start_failures_);return false;
  }
#endif
  http_fault_=false;
  increment(http_starts_);
  ESP_LOGI(kTag, "HTTP browser service ready");
  return true;
}

void WiredNetworkService::stopHttp() noexcept {
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
  input::remoteLocked([](auto &r){r.cancel(input::RemoteKeyboard::disconnected);return 0;});
#endif
  auto const server = server_.load(std::memory_order_acquire);
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
  auto *service = static_cast<WiredNetworkService *>(
      httpd_get_global_user_ctx(server));
  if (service != nullptr && service->video_.disconnect(socket))
    ESP_LOGI(kTag, "video client disconnected fd=%d", socket);
  lwip_close(socket);
}

}  // namespace agon::extender::network
