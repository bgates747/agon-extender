#pragma once
// Shared Olimex ESP32-P4 Ethernet ownership. Arduino 3.3.11
// supplies IP101/RMII and DHCP; consumers supply workers and HTTP/services.
// No initArduino(), VDP, EMOS, web routes, USB or storage startup occurs here.
#include <ETH.h>
#include <Network.h>
#include <cstdint>
#include <mutex>
#include <string>
#if defined(AGON_EXTENDER_NATIVE_BUILD)
#include "agon_extender_board_config.hpp"
#endif

namespace agon::extender::network {
class DevkitEthernet final {
 public:
  enum class Event { Started, Connected, GotIp, LostIp, Disconnected, Stopped };
  using Callback = void (*)(void *, Event) noexcept;
  struct Lease { std::string address, mask, gateway, dns; };

  DevkitEthernet() = default;
  ~DevkitEthernet() { stop(); }
  DevkitEthernet(const DevkitEthernet &) = delete;
  DevkitEthernet &operator=(const DevkitEthernet &) = delete;

  // Caller serializes start/stop. Callback runs on Arduino's event task and must
  // only enqueue/notify: do not call start/stop or block waiting for the owner.
  bool start(Callback callback, void *context) noexcept {
    if (!callback) return false;
    std::uint64_t generation;
    {
      std::lock_guard<std::mutex> lock(guard_);
      if (owner_) return owner_ == this;
      owner_ = this;
      callback_ = callback;
      context_ = context;
      generation = ++generation_;
    }
    event_handle_ = Network.onEvent(
        [generation](arduino_event_id_t id, arduino_event_info_t) {
          Event event;
          switch (id) {
            case ARDUINO_EVENT_ETH_START: event = Event::Started; break;
            case ARDUINO_EVENT_ETH_CONNECTED: event = Event::Connected; break;
            case ARDUINO_EVENT_ETH_GOT_IP: event = Event::GotIp; break;
            case ARDUINO_EVENT_ETH_LOST_IP: event = Event::LostIp; break;
            case ARDUINO_EVENT_ETH_DISCONNECTED: event = Event::Disconnected; break;
            case ARDUINO_EVENT_ETH_STOP: event = Event::Stopped; break;
            default: return;
          }
          // The lambda captures no owner pointer. Teardown waits for an active
          // notification, then clears the target. Queued old-generation events
          // cannot enter a destroyed or restarted consumer.
          std::lock_guard<std::mutex> lock(guard_);
          if (owner_ && generation == generation_)
            owner_->callback_(owner_->context_, event);
        });
    registered_ = event_handle_ != 0;
    // Both reviewed Olimex boards use IP101 and external RMII clock GPIO50.
    // Retain the public class name for detached DevKit consumers. Their legacy
    // builds use the original tuple; native builds use the checked board file.
#if defined(AGON_EXTENDER_NATIVE_BUILD)
    if (!registered_ || !ETH.begin(ETH_PHY_IP101, board::kPhyAddress,
                                   board::kEthMdc, board::kEthMdio,
                                   board::kEthReset, EMAC_CLK_EXT_IN)) {
#else
    if (!registered_ || !ETH.begin(ETH_PHY_IP101, 1, 31, 52, 51, EMAC_CLK_EXT_IN)) {
#endif
      stop();
      return false;
    }
    return true;
  }

  // Stop consumer services before this call. No consumer callbacks can execute
  // after it returns, including callbacks queued before removeEvent().
  void stop() noexcept {
    {
      std::lock_guard<std::mutex> lock(guard_);
      if (owner_ != this) return;
      callback_ = nullptr;
      context_ = nullptr;
      // Retain ownership until ETH.end completes, preventing another instance
      // from starting the same peripheral during teardown.
      ++generation_;
    }
    if (registered_) Network.removeEvent(event_handle_);
    registered_ = false;
    ETH.end();
    std::lock_guard<std::mutex> lock(guard_);
    owner_ = nullptr;
  }

  bool hasIP() const noexcept { return ETH.hasIP(); }
  bool linkUp() const noexcept { return ETH.linkUp(); }
  Lease lease() const {
    return {ETH.localIP().toString().c_str(), ETH.subnetMask().toString().c_str(),
            ETH.gatewayIP().toString().c_str(), ETH.dnsIP().toString().c_str()};
  }
 private:
  inline static std::mutex guard_;
  inline static DevkitEthernet *owner_ = nullptr;
  inline static std::uint64_t generation_ = 0;
  network_event_handle_t event_handle_{};
  bool registered_ = false;
  Callback callback_ = nullptr;
  void *context_ = nullptr;
};
} // namespace agon::extender::network
