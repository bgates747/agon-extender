// PORT-006 first-tranche compile/link diagnostic only.
//
// This binds the actual P4 PSRAM snapshot pool, PORT-003 EVF1 provider, and
// PORT-006 wired service. It deliberately publishes no frame and is not the
// bootable retained VDP target or a hardware-qualified deployment image.
#include <Arduino.h>

#include <esp_heap_caps.h>
#include <esp_log.h>

#include "extender/display/plane_storage.hpp"
#include "extender/display/presentation_snapshot_pool.hpp"
#include "extender/network/wired_network_service.hpp"
#include "extender/web/browser_video_provider.hpp"

namespace display = agon::extender::display;
namespace network = agon::extender::network;
namespace web = agon::extender::web;

namespace {

network::WiredNetworkService *service{};

void *allocateSnapshot(void *, std::size_t size) {
  return heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
}

void releaseSnapshot(void *, void *allocation) { heap_caps_free(allocation); }

}  // namespace

void setup() {
  static display::PresentationSnapshotPool snapshots(
      {nullptr, &allocateSnapshot, &releaseSnapshot});
  static web::BrowserVideoProvider provider(snapshots);
  static network::WiredNetworkService wired(provider);
  service = &wired;

  if (!snapshots.enabled()) {
    ESP_LOGE("network-canary", "snapshot allocation disabled");
    return;
  }
  if (!service->start()) {
    ESP_LOGE("network-canary", "wired service start failed");
    return;
  }
  ESP_LOGI("network-canary", "PORT-006 compile/link diagnostic started");
}

void loop() { delay(1000); }
