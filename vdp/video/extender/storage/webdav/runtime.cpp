#include "completion_stream.hpp"
#include "runtime.hpp"
#if AGON_EXTENDER_STAGED_WEBDAV
#include "../admission/channel.hpp"
#include "../local/media.hpp"
#include "../sd_target.hpp"
#include "connection.hpp"
#include <atomic>
#include <cerrno>
#include <cstdio>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <lwip/inet.h>
#include <lwip/sockets.h>
namespace agon::extender::webdav {
namespace {
constexpr unsigned Port = 8081, Quota = 32U * 1024U * 1024U,
                   WorkerStack = 32768;
std::atomic_flag workerBusy = ATOMIC_FLAG_INIT;
TaskHandle_t acceptTask = nullptr;
class QueueAccess final : public storage::admission::Access {
public:
  void
  locked(const std::function<void(storage::admission::Peer &)> &f) override {
    portENTER_CRITICAL(&storage::sd_mutex);
    f(storage::sd_peer);
    portEXIT_CRITICAL(&storage::sd_mutex);
  }
  bool manualBusy() override { return storage::sd_service.online(now()); }
  std::uint32_t now() override {
    return std::uint32_t(esp_timer_get_time() / 1000);
  }
  void pause() override { vTaskDelay(1); }
  void rejected(unsigned phase, std::uint32_t age, bool manual) override {
    // Candidate diagnostic runs outside the queue critical section. No UART1
    // traffic: this goes to the P4 USB programming/debug console only.
    std::printf("WebDAV admission unavailable: phase=%u poll_age_ms=%lu manual=%u\n",
                phase, static_cast<unsigned long>(age), unsigned(manual));
  }
};
class Socket final : public Stream {
  int fd_;
  std::int64_t start_ = esp_timer_get_time();
  bool expired() const { return esp_timer_get_time() - start_ >= 600000000LL; }

public:
  explicit Socket(int fd) : fd_(fd) {
    timeval t{5, 0};
    setsockopt(fd_, SOL_SOCKET, SO_RCVTIMEO, &t, sizeof t);
    setsockopt(fd_, SOL_SOCKET, SO_SNDTIMEO, &t, sizeof t);
  }
  ~Socket() { close(); }
  int read(void *p, size_t n) override {
    return expired() ? -1 : recv(fd_, p, n, 0);
  }
  int send(const void *p, size_t n) override {
    return expired() ? -1 : ::send(fd_, p, n, 0);
  }
  void close() override {
    if (fd_ >= 0) {
      shutdown(fd_, SHUT_RDWR);
      ::close(fd_);
      fd_ = -1;
    }
  }
};
void unavailable(Stream &s) {
  const char response[] = "HTTP/1.1 503 Service Unavailable\r\nContent-Length: "
                          "0\r\nConnection: close\r\n\r\n";
  (void)s.send(response, sizeof response - 1);
}
void unavailable(int fd) {
  Socket s(fd);
  unavailable(s);
}
void worker(void *arg) {
  int fd = static_cast<int>(reinterpret_cast<intptr_t>(arg));
  Socket socket(fd);
  CompletionStream completion(socket);
  {
    local_sd::MediaLease lease;
    std::string directory;
    if (!lease || !local_sd::prepareSpool(directory))
      unavailable(completion);
    else {
      sockaddr_in local{};
      socklen_t n = sizeof local;
      char address[INET_ADDRSTRLEN]{};
      if (getsockname(fd, reinterpret_cast<sockaddr *>(&local), &n) ||
          !inet_ntop(AF_INET, &local.sin_addr, address, sizeof address))
        unavailable(completion);
      else {
        QueueAccess access;
        storage::admission::Channel channel(access);
        WireBackend backend(channel, directory, Quota);
        Adapter adapter(backend, "http://" + std::string(address) + ":" +
                                     std::to_string(Port));
        serveConnection(adapter, completion);
      }
    }
  }
  workerBusy.clear();
  completion.complete();
  vTaskDelete(nullptr);
}
void acceptLoop(void *arg) {
  int server = static_cast<int>(reinterpret_cast<intptr_t>(arg));
  for (;;) {
    int fd = accept(server, nullptr, nullptr);
    if (fd < 0) {
      vTaskDelay(pdMS_TO_TICKS(100));
      continue;
    }
    if (workerBusy.test_and_set()) {
      unavailable(fd);
      continue;
    }
    if (xTaskCreate(worker, "sd-webdav", WorkerStack,
                    reinterpret_cast<void *>(static_cast<intptr_t>(fd)), 1,
                    nullptr) != pdPASS) {
      workerBusy.clear();
      unavailable(fd);
    }
  }
}
} // namespace
bool startRuntime() noexcept {
  if (acceptTask)
    return true;
  int fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
  if (fd < 0)
    return false;
  int yes = 1;
  setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes);
  sockaddr_in addr{};
  addr.sin_family = AF_INET;
  addr.sin_port = htons(Port);
  addr.sin_addr.s_addr = htonl(INADDR_ANY);
  if (bind(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) ||
      listen(fd, 2) ||
      xTaskCreate(acceptLoop, "sd-dav-accept", 4096,
                  reinterpret_cast<void *>(static_cast<intptr_t>(fd)), 1,
                  &acceptTask) != pdPASS) {
    ::close(fd);
    return false;
  }
  portENTER_CRITICAL(&storage::sd_mutex);
  storage::sd_runtime_ready = true;
  portEXIT_CRITICAL(&storage::sd_mutex);
  return true;
}
} // namespace agon::extender::webdav
#else
namespace agon::extender::webdav {
bool startRuntime() noexcept { return false; }
} // namespace agon::extender::webdav
#endif
