#if defined(AGON_EXTENDER_SD_SERVICE)
#include "extender/storage/local/http.hpp"
#endif
#include "display_status.hpp"
#include "screen_text.hpp"
#include "pair_rle.hpp"
#include "packed_frame.hpp"
#include "extender/diagnostics/rle2/bench.hpp"
#ifdef AGON_EXTENDER_OUTPUT_ISOLATION
#include "extender/diagnostics/output_isolation.hpp"
#endif
#if defined(AGON_EXTENDER_TELEMETRY)
#include "../telemetry/target.hpp"
#endif
// Video and input use independent sessions. Retain complete video writes and
// failed-stop containment; browser input is arbitrated by the console owner.
#include "extender/network/wired_network_service.hpp"
#include "extender/diagnostics/frame_timing.hpp"
#include "extender/diagnostics/video_timing.hpp"
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
#include <new>
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
// Only HTTP task accesses these after startup; one active video connection.
static uint8_t *rle2_scratch=nullptr;
static bool rle2_requested=false, packed_requested=false, sixbit_requested=false;
static uint8_t *packed_scratch=nullptr, *pair_scratch=nullptr;
static bool pair_requested=false;
static uint64_t rle2_encode_us=0,rle2_attempts=0,rle2_frames=0;


namespace {

constexpr char kTag[] = "extender_net";
// PORT-003 isolated polling-latency comparison. Keep the ordinary value until
// review; a shorter wait changes scheduling demand, not the frame/credit API.
#ifndef AGON_EXTENDER_VIDEO_POLL_MS
#define AGON_EXTENDER_VIDEO_POLL_MS 10
#endif
constexpr std::uint32_t kWorkerPollMilliseconds = AGON_EXTENDER_VIDEO_POLL_MS;
static_assert(kWorkerPollMilliseconds >= 1 && kWorkerPollMilliseconds <= 10,
              "Video polling experiment must stay within 1..10 ms");
constexpr std::uint32_t kWorkerStackBytes = 8192;
constexpr UBaseType_t kWorkerPriority = 3;

}  // namespace

WiredNetworkService::WiredNetworkService(
    OpaqueMessageProvider &provider) noexcept
    : HttpVideoService(provider) {}

WiredNetworkService::~WiredNetworkService() {
  stop();
  // F012 containment: destruction with a live callback target is forbidden.
  // The static product service has process lifetime; a failed stop is fatal
  // for a hypothetical shorter-lived owner rather than a use-after-free.
  if (server_.load()!=nullptr) abort();
}

bool WiredNetworkService::start() noexcept {
  auto expected = WiredServiceState::Stopped;
  if (!state_.compare_exchange_strong(expected, WiredServiceState::Starting))
    return expected != WiredServiceState::Faulted;

  stop_requested_.store(false, std::memory_order_release);
  pending_events_.store(0, std::memory_order_release);
  TaskHandle_t task = nullptr;
  if (xTaskCreate(&workerEntry, "extender-net", kWorkerStackBytes, this,
                  kWorkerPriority, &task) != pdPASS) {
    state_.store(WiredServiceState::Faulted, std::memory_order_release);
    ESP_LOGE(kTag, "network worker creation failed");
    return false;
  }
  worker_task_.store(task, std::memory_order_release);

  // Olimex ESP32-P4-DevKit Rev D1 IP101GRI wiring. DHCP remains the
  // NetworkInterface default; no address is compiled into this call.
  if (!ethernet_.start([](void *context, DevkitEthernet::Event event) noexcept {
        static_cast<WiredNetworkService *>(context)->onNetworkEvent(event);
      }, this)) {
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

  ethernet_.stop();
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

void WiredNetworkService::onNetworkEvent(DevkitEthernet::Event event) noexcept {
  std::uint32_t bit = 0;
  switch (event) {
    case DevkitEthernet::Event::Started: bit = EthernetStarted; break;
    case DevkitEthernet::Event::Connected: bit = EthernetConnected; break;
    case DevkitEthernet::Event::GotIp: bit = EthernetGotIp; break;
    case DevkitEthernet::Event::LostIp: bit = EthernetLostIp; break;
    case DevkitEthernet::Event::Disconnected: bit = EthernetDisconnected; break;
    case DevkitEthernet::Event::Stopped: bit = EthernetStopped; break;
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
    if (http_fault_) { stopHttp(); if (!http_fault_ && ethernet_.hasIP()) processEvents(EthernetGotIp); }
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
      !ethernet_.hasIP()) {
    stopHttp();
    auto const next = ethernet_.linkUp() ? WiredServiceState::LinkUpNoLease
                                   : WiredServiceState::LinkDown;
    state_.store(next, std::memory_order_release);
    if ((events & EthernetLostIp) != 0) ESP_LOGW(kTag, "DHCP lease lost");
    if ((events & EthernetDisconnected) != 0)
      ESP_LOGW(kTag, "Ethernet link disconnected");
  }
  if ((events & EthernetGotIp) != 0 && ethernet_.hasIP()) {
    reportLease();
    if (startHttp())
      state_.store(WiredServiceState::LeasedServing,
                   std::memory_order_release);
    else
      state_.store(WiredServiceState::Faulted, std::memory_order_release);
  }
}

void WiredNetworkService::reportLease() const noexcept {
  auto const lease = ethernet_.lease();
  ESP_LOGI(kTag, "DHCP ip=%s netmask=%s gateway=%s dns=%s", lease.address.c_str(),
           lease.mask.c_str(), lease.gateway.c_str(), lease.dns.c_str());
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

#if defined(AGON_EXTENDER_VIDEO_TIMING)
namespace {
esp_err_t videoTimingHandler(httpd_req_t *request) {
  const auto body = diagnostics::videoTimingJson();
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
#if AGON_EXTENDER_ADMISSION_PROBE
esp_err_t admissionProbeHandler(httpd_req_t *request) {
  char command='0';
  if(request->method==HTTP_POST) {
    if(request->content_len!=1 || httpd_req_recv(request,&command,1)!=1 || command<'0'||command>'3')
      return httpd_resp_send_err(request,HTTPD_400_BAD_REQUEST,"Expected diagnostic case 0..3");
    portENTER_CRITICAL(&storage::sd_mutex);
    bool ok=!storage::sd_service.online(sdNow()) && storage::admission_probe.arm(command-'0',sdNow());
    portEXIT_CRITICAL(&storage::sd_mutex);
    if(!ok) {httpd_resp_set_status(request,"503 Service Unavailable");return httpd_resp_sendstr(request,"No fresh idle poll or probe busy");}
  }
  char body[220];
  portENTER_CRITICAL(&storage::sd_mutex);
  auto &p=storage::admission_probe;
  int n=snprintf(body,sizeof(body),"{\"diagnostic\":true,\"hello\":%u,\"poll\":%u,\"decide\":%u,\"close\":%u,\"last\":%u,\"armed\":%u}",p.hellos,p.polls,p.decides,p.closes,p.last,p.armed);
  portEXIT_CRITICAL(&storage::sd_mutex);
  httpd_resp_set_type(request,"application/json");
  return httpd_resp_send(request,body,n);
}
#endif
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
#include "browser_keyboard.inc"
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
  // Host automation remains separate from the same-origin browser WebSocket.
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

#if defined(AGON_EXTENDER_SD_SERVICE)
  if (!local_sd::startHttp()) ESP_LOGW(kTag, "P4 SD HTTP server unavailable");
#endif
  if (server_.load(std::memory_order_acquire) != nullptr) return !http_fault_;

  if(!pair_scratch)pair_scratch=(uint8_t*)heap_caps_malloc(786432,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
  if(!packed_scratch)packed_scratch=(uint8_t*)heap_caps_malloc(589828,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
  if(!rle2_scratch)rle2_scratch=(uint8_t*)heap_caps_malloc(786446,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
  auto const &assets = web::embeddedBrowserAssets();
  HttpVideoConfig options;
  options.max_uri_handlers = 18; // common assets/video plus optional console routes
  if (!startServer(assets.data(), assets.size(), options)) return false;
  auto const server = server_.load(std::memory_order_acquire);
  httpd_uri_t screen{};
  screen.uri="/screen/text";screen.method=HTTP_GET;screen.handler=&screen_text::handle;
  if(httpd_register_uri_handler(server,&screen)!=ESP_OK){http_fault_=true;stopHttp();return false;}


  httpd_uri_t displayStatus{};
  displayStatus.uri="/display/status"; displayStatus.method=HTTP_GET;
  displayStatus.handler=&display_status::handle;
  if(httpd_register_uri_handler(server,&displayStatus)!=ESP_OK) {
    http_fault_=true;stopHttp();return false;
  }

  httpd_uri_t codec{};codec.uri="/diagnostics/rle2";codec.method=HTTP_GET;codec.handler=&rle2bench::handler;
  if(httpd_register_uri_handler(server,&codec)!=ESP_OK){http_fault_=true;stopHttp();return false;}
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
#if defined(AGON_EXTENDER_VIDEO_TIMING)
  httpd_uri_t video_timing{};
  video_timing.uri = "/diagnostics/video-timing";
  video_timing.method = HTTP_GET;
  video_timing.handler = &videoTimingHandler;
  if (httpd_register_uri_handler(server, &video_timing) != ESP_OK) {
    http_fault_ = true;
    stopHttp();
    increment(http_start_failures_);
    return false;
  }
#endif
#if defined(AGON_EXTENDER_SD_SERVICE)
#if AGON_EXTENDER_ADMISSION_PROBE
  httpd_uri_t probe_get{},probe_post{};
  probe_get.uri=probe_post.uri="/diagnostics/admission";
  probe_get.method=HTTP_GET;probe_post.method=HTTP_POST;
  probe_get.handler=probe_post.handler=&admissionProbeHandler;
  if(httpd_register_uri_handler(server,&probe_get)!=ESP_OK || httpd_register_uri_handler(server,&probe_post)!=ESP_OK) {
    http_fault_=true;stopHttp();increment(http_start_failures_);return false;
  }
#endif
  httpd_uri_t sd_status{},sd_rpc{};
  sd_status.uri="/sd/status";sd_status.method=HTTP_GET;sd_status.handler=&sdStatusHandler;
  sd_rpc.uri="/sd/rpc";sd_rpc.method=HTTP_POST;sd_rpc.handler=&sdRpcHandler;
  if(httpd_register_uri_handler(server,&sd_status)!=ESP_OK ||
     httpd_register_uri_handler(server,&sd_rpc)!=ESP_OK) {
    http_fault_=true;stopHttp();increment(http_start_failures_);return false;
  }
#endif
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
  httpd_uri_t key_status{},key_rpc{},key_browser{};
  key_browser.uri="/keyboard/browser";key_browser.method=HTTP_GET;
  key_browser.handler=&browserKeyboardHandler;key_browser.is_websocket=true;
  key_browser.ws_post_handshake_cb=&browserKeyboardOpened;
  key_status.uri="/keyboard/status";key_status.method=HTTP_GET;key_status.handler=&keyboardStatusHandler;
  key_rpc.uri="/keyboard/rpc";key_rpc.method=HTTP_POST;key_rpc.handler=&keyboardRpcHandler;
  if(httpd_register_uri_handler(server,&key_status)!=ESP_OK ||
     httpd_register_uri_handler(server,&key_rpc)!=ESP_OK ||
     httpd_register_uri_handler(server,&key_browser)!=ESP_OK) {
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
  ESP_LOGI(kTag, "HTTP browser service ready");
  return true;
}

void WiredNetworkService::stopHttp() noexcept {
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
  input::remoteLocked([](auto &r){r.cancel(input::RemoteKeyboard::disconnected);return 0;});
#endif
  stopServer();
}

void WiredNetworkService::negotiate(httpd_req_t *request) noexcept {
  char query[32]{};
  rle2_requested=httpd_req_get_url_query_str(request,query,sizeof(query))==ESP_OK && (std::strcmp(query,"rle2=1")==0 || std::strcmp(query,"rle2=1&packed=1")==0 || (std::strcmp(query,"rle2=1&packed=2")==0 || std::strcmp(query,"rle2=1&packed=2&pair=1")==0));
  pair_requested=std::strcmp(query,"pair=1")==0 || std::strcmp(query,"rle2=1&packed=2&pair=1")==0;
  sixbit_requested=std::strcmp(query,"packed=2")==0 || (std::strcmp(query,"rle2=1&packed=2")==0 || std::strcmp(query,"rle2=1&packed=2&pair=1")==0);
  packed_requested=sixbit_requested || std::strcmp(query,"packed=1")==0 || std::strcmp(query,"rle2=1&packed=1")==0;
}

esp_err_t WiredNetworkService::sendMessage(httpd_handle_t server, int socket,
    OpaqueMessageView const &view) noexcept {
  diagnostics::VideoTimingScope timing(diagnostics::VideoPhase::SocketSend,
      static_cast<std::uint32_t>(view.segment_count));
#ifdef AGON_EXTENDER_OUTPUT_ISOLATION
  agon_output_isolation::Scope isolatedSend(agon_output_isolation::Phase::Send);
#endif
  // HTTP task serializes negotiation, scratch use and complete sends. Snapshot
  // lease is immutable here; no graphics lock is acquired for compression.
  std::array<OpaqueMessageSegment,2> compressed{};
  uint8_t compressed_header[32];
  auto segments=view.segments.data();size_t count=view.segment_count;
  size_t transmitted=view.total_bytes;
  if(rle2_requested && rle2_scratch && count==2 && segments[0].size==32) {
    auto h=segments[0].data;const auto n=segments[1].size;
    const size_t width=size_t(h[12])|(size_t(h[13])<<8);
    const size_t height=size_t(h[14])|(size_t(h[15])<<8);
    if(std::memcmp(h,"EVF1",4)==0 && h[6]==2 && n<=786432 && n==width*height && rle2::get32(h+16)==width && rle2::get32(h+20)==n){
      auto begin=esp_timer_get_time();auto encoded=rle2::encode_auto(segments[1].data,n,rle2_scratch,786446,true);
      rle2_encode_us+=esp_timer_get_time()-begin;++rle2_attempts;
      if(encoded && encoded.bytes<n){
        std::memcpy(compressed_header,h,32);compressed_header[2]='R';
        compressed[0]={compressed_header,32};compressed[1]={rle2_scratch,encoded.bytes};
        segments=compressed.data();count=2;transmitted=32+encoded.bytes;++rle2_frames;
      }
    }
  }
  if(packed_requested && packed_scratch && view.segment_count==2 && view.segments[0].size==32) {
    auto h=view.segments[0].data;auto pixels=view.segments[1];
    size_t w=size_t(h[12])|(size_t(h[13])<<8),hh=size_t(h[14])|(size_t(h[15])<<8);
    if(std::memcmp(h,"EVF1",4)==0 && h[6]==2 && pixels.size==w*hh && rle2::get32(h+16)==w && rle2::get32(h+20)==pixels.size) {
      auto bytes=packed_frame::encode(pixels.data,pixels.size,packed_scratch,589828,transmitted-32,sixbit_requested);
      if(bytes){std::memcpy(compressed_header,h,32);compressed_header[2]='P';
        compressed[0]={compressed_header,32};compressed[1]={packed_scratch,bytes};
        segments=compressed.data();count=2;transmitted=32+bytes;}
    }
  }
  if(pair_requested && pair_scratch && view.segment_count==2 && view.segments[0].size==32) {
    auto h=view.segments[0].data;auto pixels=view.segments[1];
    const size_t w=size_t(h[12])|(size_t(h[13])<<8),hh=size_t(h[14])|(size_t(h[15])<<8);
    if(std::memcmp(h,"EVF1",4)==0 && h[6]==2 && pixels.size==w*hh && rle2::get32(h+16)==w && rle2::get32(h+20)==pixels.size){
      const size_t limit=(!rle2_requested && !packed_requested)?pixels.size+1:transmitted-32;
      auto bytes=pair_rle::encode(pixels.data,pixels.size,pair_scratch,786432,limit);
      if(bytes){std::memcpy(compressed_header,h,32);compressed_header[2]='Q';
        compressed[0]={compressed_header,32};compressed[1]={pair_scratch,bytes};
        segments=compressed.data();count=2;transmitted=32+bytes;}
    }
  }
  const auto result = sendSegments(server, socket, segments, count);

  timing.finish(result == ESP_OK ? transmitted : 0);
#ifdef AGON_EXTENDER_OUTPUT_ISOLATION
  isolatedSend.finish(result == ESP_OK ? transmitted : 0, result == ESP_OK);
#endif
  return result;
}

bool WiredNetworkService::allowSend() noexcept {
#ifdef AGON_EXTENDER_OUTPUT_ISOLATION
  return !agon_output_isolation::blocksNetwork();
#else
  return true;
#endif
}

}  // namespace agon::extender::network
