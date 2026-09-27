// Compile-only consumer: no console, VDP, Ethernet or storage includes/startup.
#include "extender/network/http_video_service.hpp"
using namespace agon::extender;
class IdleProvider final : public network::OpaqueMessageProvider {
 public:
  network::OpaqueAcquireResult tryAcquireAfter(std::uint64_t,
      network::OpaqueMessageLease &) noexcept override {
    return network::OpaqueAcquireResult::NoNewMessage;
  }
};
// Never run as a firmware: verifies the public composition/lifetime interface.
bool detachedConsumerCompileCheck() {
  IdleProvider provider;
  static constexpr std::uint8_t page[] = "Pattern viewer";
  static const web::EmbeddedAsset assets[] = {{"/", "text/plain", page, sizeof(page)-1}};
  network::HttpVideoService transport(provider);
  network::HttpVideoConfig config;
  config.port=80; config.control_port=32768; config.max_open_sockets=3;
  bool started=transport.startServer(assets,1,config);
  if(started) transport.poll();
  // On failure a real consumer must retain the object and retry, not return.
  while(!transport.stopServer()) {}
  return started;
}
