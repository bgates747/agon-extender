// Host qualification for the PORT-006 bounded service core and PORT-003 EVF1
// provider. Expected header bytes and transitions come from the frozen Phase F
// contracts; no ESP-IDF or browser implementation is imported.
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>

#include "extender/display/presentation_snapshot_pool.hpp"
#include "extender/network/browser_video_service_core.hpp"
#include "extender/web/browser_video_provider.hpp"

namespace display = agon::extender::display;
namespace network = agon::extender::network;
namespace web = agon::extender::web;

namespace {

void require(bool condition, char const *message) {
  if (!condition) {
    std::cerr << message << '\n';
    std::exit(1);
  }
}

void *allocate(void *, std::size_t size) { return std::malloc(size); }
void deallocate(void *, void *allocation) { std::free(allocation); }

void publish(display::PresentationSnapshotPool &pool, std::uint64_t time,
             std::uint8_t seed) {
  display::MutableSnapshotView destination{};
  require(pool.tryBegin(2, 2, time, destination) ==
              display::SnapshotBeginResult::Ok,
          "snapshot production begins");
  destination.pixels[0] = {seed, 0, static_cast<std::uint8_t>(seed * 3)};
  destination.pixels[1] = {static_cast<std::uint8_t>(seed + 1), 0,
                           static_cast<std::uint8_t>(seed * 3 + 1)};
  destination.pixels[2] = {seed, 2,
                           static_cast<std::uint8_t>(seed * 3 + 1)};
  destination.pixels[3] = {static_cast<std::uint8_t>(seed + 1), 2,
                           static_cast<std::uint8_t>(seed * 3)};
  require(pool.finish(display::CompositionResult::Ok, 16667) ==
              display::SnapshotFinishResult::Published,
          "snapshot publishes");
}

void checkHeader(network::OpaqueMessageView const &message,
                 std::uint32_t expected_sequence, std::uint8_t seed) {
  require(message.valid() && message.segment_count == 2,
          "EVF1 is one valid two-segment opaque message");
  require(message.total_bytes == 44, "EVF1 compact total length");
  std::array<std::uint8_t, 32> expected{
      0x45, 0x56, 0x46, 0x31, 0x01, 0x20, 0x01, 0x03,
      static_cast<std::uint8_t>(expected_sequence),
      static_cast<std::uint8_t>(expected_sequence >> 8),
      static_cast<std::uint8_t>(expected_sequence >> 16),
      static_cast<std::uint8_t>(expected_sequence >> 24),
      0x02, 0x00, 0x02, 0x00, 0x06, 0x00, 0x00, 0x00,
      0x0c, 0x00, 0x00, 0x00, 0x1b, 0x41, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00,
  };
  require(message.segments[0].size == expected.size(), "EVF1 header length");
  for (std::size_t index = 0; index < expected.size(); ++index)
    require(message.segments[0].data[index] == expected[index],
            "EVF1 exact header byte");
  std::array<std::uint8_t, 12> expected_pixels{
      seed, 0, static_cast<std::uint8_t>(seed * 3),
      static_cast<std::uint8_t>(seed + 1), 0,
      static_cast<std::uint8_t>(seed * 3 + 1), seed, 2,
      static_cast<std::uint8_t>(seed * 3 + 1),
      static_cast<std::uint8_t>(seed + 1), 2,
      static_cast<std::uint8_t>(seed * 3),
  };
  require(message.segments[1].size == expected_pixels.size(),
          "EVF1 payload length");
  for (std::size_t index = 0; index < expected_pixels.size(); ++index)
    require(message.segments[1].data[index] == expected_pixels[index],
            "EVF1 exact payload byte");
}

void checkServiceAndProvider() {
  display::PresentationSnapshotPool pool({nullptr, allocate, deallocate});
  require(pool.enabled(), "snapshot pool enabled");
  publish(pool, 0, 7);

  web::BrowserVideoProvider provider(pool);
  network::BrowserVideoServiceCore service;

  require(service.connect(41) == network::VideoConnectResult::Accepted,
          "first client accepted");
  require(service.connect(42) == network::VideoConnectResult::Busy,
          "second client refused");
  require(service.requestFrame(41) == network::VideoCreditResult::Accepted,
          "first credit accepted");
  require(service.requestFrame(41) ==
              network::VideoCreditResult::ProtocolError,
          "duplicate credit rejected");
  require(service.disconnect(41), "protocol client disconnects");

  require(service.connect(43) == network::VideoConnectResult::Accepted,
          "replacement client accepted");
  require(service.requestFrame(43) == network::VideoCreditResult::Accepted,
          "replacement credit accepted");
  require(service.tryPrepare(provider) ==
              network::VideoPrepareResult::Prepared,
          "latest snapshot acquired");
  checkHeader(service.sendingView(43), 1, 7);
  service.complete(43, network::OpaqueReleaseDisposition::Sent);
  require(service.state() == network::VideoClientState::Idle,
          "successful send returns idle");
  require(service.lastSuccessfulToken() == 1,
          "successful token retained per connection");

  require(service.requestFrame(43) == network::VideoCreditResult::Accepted,
          "next presentation grants one credit");
  require(service.tryPrepare(provider) ==
              network::VideoPrepareResult::NoNewMessage,
          "same generation is not reacquired");
  require(service.state() == network::VideoClientState::CreditPending,
          "credit remains pending for a later generation");

  publish(pool, 200000, 9);
  require(service.tryPrepare(provider) ==
              network::VideoPrepareResult::Prepared,
          "pending credit selects new latest");
  checkHeader(service.sendingView(43), 2, 9);
  require(service.disconnect(43), "disconnect during send is bounded");
  require(service.state() == network::VideoClientState::Disconnected,
          "disconnect resets client state");

  require(service.connect(44) == network::VideoConnectResult::Accepted,
          "reconnecting client accepted");
  require(service.requestFrame(44) == network::VideoCreditResult::Accepted,
          "reconnecting client credit");
  require(service.tryPrepare(provider) ==
              network::VideoPrepareResult::Prepared,
          "reconnect reacquires retained latest");
  checkHeader(service.sendingView(44), 2, 9);
  service.complete(44, network::OpaqueReleaseDisposition::Failed);
  require(service.disconnect(44), "failed client cleanup");

  auto const provider_metrics = provider.metrics();
  require(provider_metrics.acquired == 3, "three provider acquisitions");
  require(provider_metrics.no_new_message == 1,
          "one no-new provider result");
  require(provider_metrics.released_sent == 1,
          "one sent provider release");
  require(provider_metrics.released_disconnected == 1,
          "one disconnected provider release");
  require(provider_metrics.released_failed == 1,
          "one failed provider release");

  auto const service_metrics = service.metrics();
  require(service_metrics.clients_accepted == 3,
          "accepted clients counted");
  require(service_metrics.clients_refused == 1,
          "refused client counted");
  require(service_metrics.protocol_errors == 1,
          "duplicate credit counted");
  require(service_metrics.sends_completed == 1,
          "completed send counted");
  require(service_metrics.sends_failed == 1, "failed send counted");
  require(service_metrics.disconnect_releases == 1,
          "disconnect lease counted");
}

void checkRepeatedAndSustainedLifecycle() {
  display::PresentationSnapshotPool pool({nullptr, allocate, deallocate});
  web::BrowserVideoProvider provider(pool);
  network::BrowserVideoServiceCore service;

  // Repeated connect/disconnect is the host-visible start/stop boundary for
  // the one-client service core. Each connection begins with fresh credit and
  // generation state and leaves no retained service lease.
  for (int iteration = 0; iteration < 256; ++iteration) {
    auto const client = 1000 + iteration;
    require(service.connect(client) == network::VideoConnectResult::Accepted,
            "repeated client start accepted");
    require(service.requestFrame(client) ==
                network::VideoCreditResult::Accepted,
            "repeated client credit accepted");
    require(service.tryPrepare(provider) ==
                network::VideoPrepareResult::NoNewMessage,
            "empty provider remains bounded");
    require(service.disconnect(client), "repeated client stop accepted");
  }

  int const client = 9000;
  require(service.connect(client) == network::VideoConnectResult::Accepted,
          "sustained client accepted");
  std::uint64_t time = 0;
  for (std::uint32_t generation = 1; generation <= 2048; ++generation) {
    publish(pool, time, static_cast<std::uint8_t>(generation));
    time += display::kPresentationSnapshotMinimumIntervalUs;
    require(service.requestFrame(client) ==
                network::VideoCreditResult::Accepted,
            "fast consumer grants one credit");
    require(service.tryPrepare(provider) ==
                network::VideoPrepareResult::Prepared,
            "fast consumer acquires complete latest");
    require(service.sendingView(client).total_bytes == 44,
            "fast consumer sees bounded compact message");
    service.complete(client, network::OpaqueReleaseDisposition::Sent);
  }

  // Hold one send while many newer snapshots publish. No network queue grows;
  // completion followed by one credit selects only the newest generation.
  publish(pool, time, 1);
  time += display::kPresentationSnapshotMinimumIntervalUs;
  require(service.requestFrame(client) == network::VideoCreditResult::Accepted,
          "slow consumer grants one credit");
  require(service.tryPrepare(provider) == network::VideoPrepareResult::Prepared,
          "slow consumer holds one lease");
  for (std::uint32_t generation = 2050; generation <= 3072; ++generation) {
    publish(pool, time, static_cast<std::uint8_t>(generation));
    time += display::kPresentationSnapshotMinimumIntervalUs;
  }
  service.complete(client, network::OpaqueReleaseDisposition::Sent);
  require(service.requestFrame(client) == network::VideoCreditResult::Accepted,
          "slow consumer grants next credit after presentation");
  require(service.tryPrepare(provider) == network::VideoPrepareResult::Prepared,
          "slow consumer selects collapsed latest");
  require(service.sendingView(client).token == 3072,
          "slow consumer receives only newest generation");
  service.complete(client, network::OpaqueReleaseDisposition::Sent);
  require(service.disconnect(client), "sustained client disconnects cleanly");

  auto const metrics = service.metrics();
  require(metrics.clients_accepted == 257,
          "repeated and sustained client starts counted");
  require(metrics.sends_completed == 2050,
          "fast and slow completed sends counted");
  require(service.state() == network::VideoClientState::Disconnected,
          "sustained lifecycle ends disconnected");
  require(pool.metrics().publications == 3072,
          "disconnected/fast/slow publication count is exact");
}

}  // namespace

int main() {
  checkServiceAndProvider();
  checkRepeatedAndSustainedLifecycle();
  std::cout << "network-service=pass\n";
  return 0;
}
