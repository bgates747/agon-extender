#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iostream>
#include <limits>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "extender/transport/extender_vdp_stream.hpp"
#include "extender/transport/p4_parallel_data_plane.hpp"
#include "extender/transport/p4_parallel_target_config.hpp"

namespace transport = agon::extender::transport;

namespace {

constexpr transport::ReceiveWaitPolicy waitPolicy(
    std::uint32_t completion_timeout_ms) {
  return {completion_timeout_ms, 1};
}

[[noreturn]] void fail(char const *expression, char const *file, int line) {
  std::cerr << file << ':' << line << ": check failed: " << expression << '\n';
  std::exit(1);
}

#define CHECK(expression) \
  do {                    \
    if (!(expression)) fail(#expression, __FILE__, __LINE__); \
  } while (false)

struct Trace {
  std::vector<std::string> events;

  void add(std::string event) { events.push_back(std::move(event)); }
  void clear() { events.clear(); }

  std::size_t index(std::string const &event) const {
    auto const iterator = std::find(events.begin(), events.end(), event);
    CHECK(iterator != events.end());
    return static_cast<std::size_t>(iterator - events.begin());
  }
};

class FakeHardware final : public transport::P4EpochHardware {
 public:
  explicit FakeHardware(Trace &trace) : trace_(trace) {}

  void failOnce(std::string operation) { fail_once_ = std::move(operation); }

  bool releaseReady() noexcept override {
    return perform("ready.release", [this] { ready_asserted = false; });
  }

  bool releaseParallelForwardBanks() noexcept override {
    return perform("forward.release", [this] { forward_enabled = false; });
  }

  bool releaseReturnBank() noexcept override {
    return perform("return.release", [this] { return_enabled = false; });
  }

  bool disableSharedUartOutputs() noexcept override {
    return perform("uart.disable", [this] { uart_outputs_enabled = false; });
  }

  bool configureParallelInputPads() noexcept override {
    return perform("pads.parallel", [this] { parallel_pads = true; });
  }

  bool releaseParallelInputPads() noexcept override {
    return perform("pads.release", [this] { parallel_pads = false; });
  }

  bool enableParallelForwardBanks() noexcept override {
    return perform("forward.enable", [this] { forward_enabled = true; });
  }

  bool assertReady() noexcept override {
    return perform("ready.assert", [this] { ready_asserted = true; });
  }

  bool ready_asserted{};
  bool forward_enabled{};
  bool return_enabled{true};
  bool uart_outputs_enabled{true};
  bool parallel_pads{};

 private:
  template <typename Action>
  bool perform(char const *name, Action action) noexcept {
    trace_.add(name);
    if (fail_once_ == name) {
      fail_once_.clear();
      return false;
    }
    action();
    return true;
  }

  Trace &trace_;
  std::string fail_once_;
};

class FakeAuthority final : public transport::ParallelEpochAuthority {
 public:
  bool isLive(transport::ParallelEpochLease const &lease) const noexcept override {
    ++checks;
    if (checks == callback_on_check && on_check) on_check();
    if (!live || lease.generation != generation) return false;
    if (successful_checks_before_revocation == 0) return false;
    if (successful_checks_before_revocation > 0) {
      --successful_checks_before_revocation;
    }
    return true;
  }

  bool live{true};
  std::uint64_t generation{17};
  mutable int successful_checks_before_revocation{-1};
  mutable std::size_t checks{};
  std::size_t callback_on_check{std::numeric_limits<std::size_t>::max()};
  std::function<void()> on_check;
};

struct ScriptedReceive {
  transport::ReceiveStatus status{transport::ReceiveStatus::kComplete};
  std::vector<std::uint8_t> bytes;
};

class FakeBackend final : public transport::ParlioReceiveBackend {
 public:
  explicit FakeBackend(Trace &trace) : trace_(trace) {}

  void failOnce(std::string operation) { fail_once_ = std::move(operation); }

  void receive(std::vector<std::uint8_t> bytes) {
    script_.push_back({transport::ReceiveStatus::kComplete, std::move(bytes)});
  }

  void completeWith(transport::ReceiveStatus status) {
    script_.push_back({status, {}});
  }

  void waitUntilCancelled() noexcept {
    block_until_cancel_.store(true, std::memory_order_release);
  }

  bool waitEntered() const noexcept {
    return wait_entered_.load(std::memory_order_acquire);
  }

  bool observedCancel() const noexcept {
    return observed_cancel_.load(std::memory_order_acquire);
  }

  bool acquire(std::uint8_t *record_storage,
               std::size_t capacity) noexcept override {
    trace_.add("rx.acquire");
    storage_ = record_storage;
    capacity_ = capacity;
    if (shouldFail("rx.acquire")) return false;
    acquired = true;
    return true;
  }

  bool enable() noexcept override {
    trace_.add("rx.enable");
    if (shouldFail("rx.enable")) return false;
    if (!acquired) return false;
    enabled = true;
    return true;
  }

  bool arm() noexcept override {
    trace_.add("rx.arm");
    if (shouldFail("rx.arm")) return false;
    if (!enabled || armed) return false;
    armed = true;
    if (after_arm) after_arm();
    return true;
  }

  transport::ReceiveCompletion wait(
      transport::ReceiveWaitPolicy policy,
      std::atomic<bool> const &cancel_requested) noexcept override {
    trace_.add("rx.wait:" + std::to_string(policy.completion_timeout_ms) +
               "/" + std::to_string(policy.cancellation_poll_ms));
    if (block_until_cancel_.load(std::memory_order_acquire)) {
      wait_entered_.store(true, std::memory_order_release);
      auto const deadline =
          std::chrono::steady_clock::now() + std::chrono::seconds(2);
      while (!cancel_requested.load(std::memory_order_acquire) &&
             std::chrono::steady_clock::now() < deadline) {
        std::this_thread::yield();
      }
      bool const cancelled =
          cancel_requested.load(std::memory_order_acquire);
      observed_cancel_.store(cancelled, std::memory_order_release);
      if (cancelled) {
        armed = false;
        return {transport::ReceiveStatus::kCancelled, 0};
      }
      return {transport::ReceiveStatus::kTimeout, 0};
    }
    if (cancel_requested.load(std::memory_order_acquire)) {
      armed = false;
      return {transport::ReceiveStatus::kCancelled, 0};
    }
    if (script_.empty()) return {transport::ReceiveStatus::kTimeout, 0};
    ScriptedReceive operation = std::move(script_.front());
    script_.pop_front();
    if (operation.status != transport::ReceiveStatus::kComplete) {
      if (operation.status == transport::ReceiveStatus::kCancelled) {
        armed = false;
      }
      return {operation.status, 0};
    }
    if (operation.bytes.size() <= capacity_) {
      std::copy(operation.bytes.begin(), operation.bytes.end(), storage_);
    }
    armed = false;
    return {operation.status, operation.bytes.size()};
  }

  bool cancel() noexcept override {
    trace_.add("rx.cancel");
    if (shouldFail("rx.cancel")) return false;
    armed = false;
    return true;
  }

  bool disable() noexcept override {
    trace_.add("rx.disable");
    if (shouldFail("rx.disable")) return false;
    enabled = false;
    armed = false;
    return true;
  }

  bool release() noexcept override {
    trace_.add("rx.release");
    if (shouldFail("rx.release")) return false;
    acquired = false;
    enabled = false;
    armed = false;
    storage_ = nullptr;
    capacity_ = 0;
    return true;
  }

  bool acquired{};
  bool enabled{};
  bool armed{};
  std::function<void()> after_arm;

 private:
  bool shouldFail(char const *name) noexcept {
    if (fail_once_ != name) return false;
    fail_once_.clear();
    return true;
  }

  Trace &trace_;
  std::string fail_once_;
  std::deque<ScriptedReceive> script_;
  std::uint8_t *storage_{};
  std::size_t capacity_{};
  std::atomic<bool> block_until_cancel_{};
  std::atomic<bool> wait_entered_{};
  std::atomic<bool> observed_cancel_{};
};

class CaptureReturn final : public transport::VdpReturnChannel {
 public:
  std::size_t write(std::uint8_t const *bytes,
                    std::size_t length) noexcept override {
    std::size_t const call = write_calls++;
    if (call == fail_on_write_call) return 0;
    std::size_t const accepted = std::min(length, accept_limit);
    captured.insert(captured.end(), bytes, bytes + accepted);
    return accepted;
  }

  bool flush() noexcept override {
    ++flush_calls;
    return flush_result;
  }

  bool setProtocolDuplex(bool full_duplex) noexcept override {
    ++duplex_calls;
    requested_full_duplex = full_duplex;
    return duplex_result;
  }

  std::size_t accept_limit{static_cast<std::size_t>(-1)};
  std::size_t fail_on_write_call{static_cast<std::size_t>(-1)};
  bool flush_result{true};
  bool duplex_result{true};
  bool requested_full_duplex{};
  std::size_t write_calls{};
  std::size_t flush_calls{};
  std::size_t duplex_calls{};
  std::vector<std::uint8_t> captured;
};

class CountingCancellation final : public transport::TransportCancellation {
 public:
  void requestCancel() noexcept override { ++requests; }

  std::size_t requests{};
};

class BarrierCancellation final : public transport::TransportCancellation {
 public:
  explicit BarrierCancellation(transport::TransportAdmissionBarrier &barrier)
      : barrier_(barrier) {}

  void requestCancel() noexcept override {
    entered.store(true, std::memory_order_release);
    barrier_.requestCancel();
    returned.store(true, std::memory_order_release);
  }

  transport::TransportAdmissionBarrier &barrier_;
  std::atomic<bool> entered{};
  std::atomic<bool> returned{};
};

struct Fixture {
  Fixture(std::size_t queue_capacity, std::size_t maximum_record)
      : hardware(trace),
        backend(trace),
        queue_storage(queue_capacity),
        record_storage(maximum_record),
        queue(queue_storage.data(), queue_storage.size()),
        ingress(backend, queue, fault, record_storage.data(),
                record_storage.size(), maximum_record),
        plane(hardware, authority, ingress, queue, fault),
        stream(queue, output, fault, plane) {}

  bool start() {
    return plane.enterAuthorizedEpoch({authority.generation});
  }

  Trace trace;
  FakeHardware hardware;
  FakeAuthority authority;
  FakeBackend backend;
  std::vector<std::uint8_t> queue_storage;
  std::vector<std::uint8_t> record_storage;
  transport::SpscByteQueue queue;
  transport::TransportFaultLatch fault;
  transport::P4ParlioIngress ingress;
  transport::P4ParallelDataPlane plane;
  CaptureReturn output;
  transport::ExtenderVdpStream stream;
};

void checkSafe(Fixture const &fixture) {
  CHECK(!fixture.hardware.ready_asserted);
  CHECK(!fixture.hardware.forward_enabled);
  CHECK(!fixture.hardware.return_enabled);
  CHECK(!fixture.hardware.parallel_pads);
  CHECK(!fixture.backend.acquired);
  CHECK(!fixture.backend.enabled);
  CHECK(!fixture.backend.armed);
}

void testOrderedLifecycle() {
  Fixture fixture(16, 4);
  CHECK(fixture.start());
  std::vector<std::string> const expected_start = {
      "ready.release", "forward.release", "return.release", "uart.disable",
      "pads.parallel", "rx.acquire", "rx.enable", "forward.enable"};
  CHECK(fixture.trace.events == expected_start);
  CHECK(fixture.hardware.forward_enabled);
  CHECK(!fixture.hardware.ready_asserted);
  CHECK(!fixture.hardware.return_enabled);
  CHECK(!fixture.hardware.uart_outputs_enabled);
  CHECK(fixture.hardware.parallel_pads);

  fixture.backend.receive({0xA5});
  fixture.trace.clear();
  CHECK(fixture.plane.serviceOnce(waitPolicy(23)) ==
        transport::ServiceResult::kRecordQueued);
  std::vector<std::string> const expected_receive = {
      "rx.arm", "ready.assert", "rx.wait:23/1", "ready.release"};
  CHECK(fixture.trace.events == expected_receive);
  CHECK(!fixture.hardware.ready_asserted);

  fixture.trace.clear();
  CHECK(fixture.plane.stop());
  std::vector<std::string> const expected_stop = {
      "ready.release", "forward.release", "rx.disable", "rx.release",
      "pads.release", "return.release"};
  CHECK(fixture.trace.events == expected_stop);
  CHECK(fixture.trace.index("forward.release") <
        fixture.trace.index("rx.disable"));
  checkSafe(fixture);
}

void testRecordFlatteningAndByteCoverage() {
  Fixture fixture(512, 256);
  CHECK(fixture.start());

  std::vector<std::uint8_t> all_bytes(256);
  for (std::size_t index = 0; index < all_bytes.size(); ++index) {
    all_bytes[index] = static_cast<std::uint8_t>(index);
  }
  // The leading sequence ends exactly at one physical-record boundary; the
  // following 256-byte record is exposed as a continuation, not a new frame.
  std::vector<std::uint8_t> const prefix = {23, 0, 0, 0};
  fixture.backend.receive(prefix);
  fixture.backend.receive(all_bytes);
  CHECK(fixture.plane.serviceOnce(waitPolicy(10)) ==
        transport::ServiceResult::kRecordQueued);
  CHECK(fixture.plane.serviceOnce(waitPolicy(10)) ==
        transport::ServiceResult::kRecordQueued);

  std::vector<std::uint8_t> expected = prefix;
  expected.insert(expected.end(), all_bytes.begin(), all_bytes.end());
  CHECK(fixture.stream.available() == static_cast<int>(expected.size()));
  CHECK(fixture.stream.peek() == expected.front());
  for (std::uint8_t byte : expected) CHECK(fixture.stream.read() == byte);
  CHECK(fixture.stream.read() == -1);
  CHECK(fixture.stream.peek() == -1);
  CHECK(fixture.plane.stop());
}

void testQueueRejectsNonPowerOfTwoCapacity() {
  std::uint8_t storage[3]{};
  std::uint8_t const byte = 0xA5;
  transport::SpscByteQueue queue(storage, sizeof(storage));
  CHECK(!queue.valid());
  CHECK(queue.capacity() == sizeof(storage));
  CHECK(queue.size() == 0);
  CHECK(queue.freeSpace() == 0);
  CHECK(!queue.pushRecord(&byte, 1));
  CHECK(queue.read() == -1);
  CHECK(queue.peek() == -1);
}

void testProductionTargetPinPlan() {
  using Config = transport::P4ParallelTargetConfig;
  std::array<int, 8> const expected_data_pins{
      22, 12, 23, 11, 32, 10, 33, 9};
  CHECK(Config::kDataPins == expected_data_pins);
  CHECK(Config::kClockPin == 14);
  CHECK(Config::kValidPin == 13);
  CHECK(Config::kForwardBankAEnablePin == 15);
  CHECK(Config::kForwardBankBEnablePin == 17);
  CHECK(Config::kReturnBankEnablePin == 21);
  CHECK(Config::kReadyPin == 20);
  CHECK(transport::p4ParallelTargetPinsAreUnique());
}

void testTargetIdleWaitKeepsAdvertisedTransactionArmed() {
  std::ifstream input(
      "vdp/video/extender/transport/p4_parallel_target.cpp",
      std::ios::binary);
  CHECK(input.good());
  std::string const source((std::istreambuf_iterator<char>(input)),
                           std::istreambuf_iterator<char>());
  CHECK(source.find("deadline_us = now_us + timeout_us;") !=
        std::string::npos);
  CHECK(source.find("ReceiveStatus::kIdle") == std::string::npos);
}

void testMaximumReservationBackpressure() {
  Fixture fixture(8, 4);
  CHECK(fixture.start());
  fixture.backend.receive({1, 2, 3, 4});
  fixture.backend.receive({5, 6, 7, 8});
  fixture.backend.receive({9, 10, 11, 12});
  CHECK(fixture.plane.serviceOnce(waitPolicy(10)) ==
        transport::ServiceResult::kRecordQueued);
  CHECK(fixture.plane.serviceOnce(waitPolicy(10)) ==
        transport::ServiceResult::kRecordQueued);

  fixture.trace.clear();
  CHECK(fixture.plane.serviceOnce(waitPolicy(10)) ==
        transport::ServiceResult::kBackpressured);
  CHECK(fixture.trace.events.empty());
  CHECK(fixture.stream.read() == 1);
  CHECK(fixture.plane.serviceOnce(waitPolicy(10)) ==
        transport::ServiceResult::kBackpressured);
  CHECK(fixture.stream.read() == 2);
  CHECK(fixture.stream.read() == 3);
  CHECK(fixture.stream.read() == 4);

  fixture.trace.clear();
  CHECK(fixture.plane.serviceOnce(waitPolicy(10)) ==
        transport::ServiceResult::kRecordQueued);
  CHECK(fixture.trace.index("rx.arm") < fixture.trace.index("ready.assert"));
  CHECK(fixture.trace.index("ready.assert") <
        fixture.trace.index("ready.release"));
  std::vector<std::uint8_t> const expected = {5, 6, 7, 8, 9, 10, 11, 12};
  for (std::uint8_t byte : expected) CHECK(fixture.stream.read() == byte);
  CHECK(fixture.plane.stop());
}

void testEveryPartialStartFailureAndRetry() {
  using transport::TransportFault;
  std::vector<std::pair<std::string, TransportFault>> const failures = {
      {"ready.release", TransportFault::kReadyRelease},
      {"forward.release", TransportFault::kForwardBanksRelease},
      {"return.release", TransportFault::kReturnBankRelease},
      {"uart.disable", TransportFault::kSharedUartDisable},
      {"pads.parallel", TransportFault::kParallelPadsConfigure},
      {"rx.acquire", TransportFault::kIngressAcquire},
      {"rx.enable", TransportFault::kIngressEnable},
      {"forward.enable", TransportFault::kParallelForwardEnable},
  };

  for (auto const &[operation, expected_fault] : failures) {
    Fixture fixture(16, 4);
    if (operation.rfind("rx.", 0) == 0) {
      fixture.backend.failOnce(operation);
    } else {
      fixture.hardware.failOnce(operation);
    }
    CHECK(!fixture.start());
    CHECK(fixture.fault.fault() == expected_fault);
    CHECK(fixture.plane.state() == transport::DataPlaneState::kStopped);
    checkSafe(fixture);
    CHECK(fixture.plane.resetFault());
    CHECK(fixture.start());
    CHECK(fixture.plane.stop());
    checkSafe(fixture);
  }
}

void testBoundedReceiveFaultsAndRetry() {
  using transport::ReceiveStatus;
  using transport::TransportFault;
  std::vector<std::pair<ReceiveStatus, TransportFault>> const failures = {
      {ReceiveStatus::kTimeout, TransportFault::kReceiveTimeout},
      {ReceiveStatus::kOverflow, TransportFault::kReceiveOverflow},
      {ReceiveStatus::kError, TransportFault::kReceiveBackend},
  };

  for (auto const &[status, expected_fault] : failures) {
    Fixture fixture(16, 4);
    CHECK(fixture.start());
    fixture.backend.completeWith(status);
    fixture.trace.clear();
    CHECK(fixture.plane.serviceOnce(waitPolicy(41)) ==
          transport::ServiceResult::kFaulted);
    CHECK(fixture.fault.fault() == expected_fault);
    CHECK(fixture.plane.state() == transport::DataPlaneState::kFaulted);
    CHECK(!fixture.hardware.ready_asserted);
    CHECK(!fixture.hardware.forward_enabled);
    CHECK(fixture.trace.index("forward.release") <
          fixture.trace.index("rx.cancel"));
    CHECK(fixture.plane.stop());
    checkSafe(fixture);
    CHECK(fixture.plane.resetFault());
    CHECK(fixture.start());
    fixture.backend.receive({0x6D});
    CHECK(fixture.plane.serviceOnce(waitPolicy(41)) ==
          transport::ServiceResult::kRecordQueued);
    CHECK(fixture.stream.read() == 0x6D);
    CHECK(fixture.plane.stop());
  }
}

void testIdlePollDoesNotFaultOrStopIngress() {
  Fixture fixture(16, 4);
  CHECK(fixture.start());

  for (int poll = 0; poll < 2; ++poll) {
    fixture.backend.completeWith(transport::ReceiveStatus::kIdle);
    fixture.trace.clear();
    CHECK(fixture.plane.serviceOnce(waitPolicy(41)) ==
          transport::ServiceResult::kBackpressured);
    CHECK(fixture.fault.healthy());
    CHECK(fixture.plane.state() == transport::DataPlaneState::kActive);
    CHECK(!fixture.hardware.ready_asserted);
    CHECK(fixture.hardware.forward_enabled);
    CHECK(fixture.backend.enabled);
    CHECK(!fixture.backend.armed);
    CHECK(fixture.trace.index("ready.release") <
          fixture.trace.index("rx.cancel"));
  }

  fixture.backend.receive({0x6D});
  CHECK(fixture.plane.serviceOnce(waitPolicy(41)) ==
        transport::ServiceResult::kRecordQueued);
  CHECK(fixture.stream.read() == 0x6D);
  CHECK(fixture.plane.stop());
}

void testArmFailureReleasesDirectionBeforeCancellation() {
  Fixture fixture(16, 4);
  CHECK(fixture.start());
  fixture.backend.failOnce("rx.arm");
  fixture.trace.clear();
  CHECK(fixture.plane.serviceOnce(waitPolicy(10)) ==
        transport::ServiceResult::kFaulted);
  CHECK(fixture.fault.fault() == transport::TransportFault::kReceiveArm);
  CHECK(fixture.trace.index("forward.release") <
        fixture.trace.index("rx.cancel"));
  CHECK(!fixture.hardware.ready_asserted);
  CHECK(!fixture.hardware.forward_enabled);
  CHECK(fixture.plane.stop());
  CHECK(fixture.plane.resetFault());
  CHECK(fixture.start());
  CHECK(fixture.plane.stop());
}

void testCleanupFailureRequiresStopRetry() {
  Fixture fixture(16, 4);
  CHECK(fixture.start());
  fixture.hardware.failOnce("pads.release");
  CHECK(!fixture.plane.stop());
  CHECK(fixture.plane.state() == transport::DataPlaneState::kFaulted);
  CHECK(fixture.fault.fault() ==
        transport::TransportFault::kParallelPadsRelease);
  CHECK(fixture.plane.stop());
  CHECK(fixture.plane.state() == transport::DataPlaneState::kStopped);
  checkSafe(fixture);
  CHECK(fixture.plane.resetFault());
  CHECK(fixture.start());
  CHECK(fixture.plane.stop());

  Fixture start_cleanup(16, 4);
  start_cleanup.authority.successful_checks_before_revocation = 1;
  start_cleanup.hardware.failOnce("pads.release");
  CHECK(!start_cleanup.start());
  CHECK(start_cleanup.fault.fault() ==
        transport::TransportFault::kEpochLeaseLost);
  CHECK(start_cleanup.plane.state() == transport::DataPlaneState::kFaulted);
  CHECK(start_cleanup.plane.stop());
  checkSafe(start_cleanup);
  CHECK(start_cleanup.plane.resetFault());
  start_cleanup.authority.successful_checks_before_revocation = -1;
  CHECK(start_cleanup.start());
  CHECK(start_cleanup.plane.stop());
}

void testStaleBytesCannotCrossEpoch() {
  Fixture fixture(16, 4);
  CHECK(fixture.start());
  fixture.backend.receive({0x17, 0x00});
  CHECK(fixture.plane.serviceOnce(waitPolicy(8)) ==
        transport::ServiceResult::kRecordQueued);
  CHECK(fixture.plane.stop());

  CHECK(!fixture.start());
  CHECK(fixture.fault.fault() ==
        transport::TransportFault::kStaleBufferedInput);
  CHECK(fixture.plane.resetFault());
  CHECK(fixture.plane.discardBufferedInput());
  CHECK(fixture.start());
  CHECK(fixture.stream.available() == 0);
  CHECK(fixture.plane.stop());
}

void testCancellationAndLeaseRevocation() {
  Fixture cancelled(16, 4);
  CHECK(cancelled.start());
  cancelled.plane.requestCancel();
  cancelled.trace.clear();
  CHECK(cancelled.plane.serviceOnce(waitPolicy(8)) ==
        transport::ServiceResult::kCancelled);
  CHECK(cancelled.trace.events.empty());
  CHECK(cancelled.fault.healthy());
  CHECK(cancelled.plane.stop());

  Fixture during_wait(16, 4);
  CHECK(during_wait.start());
  during_wait.backend.completeWith(transport::ReceiveStatus::kCancelled);
  during_wait.trace.clear();
  CHECK(during_wait.plane.serviceOnce(waitPolicy(8)) ==
        transport::ServiceResult::kCancelled);
  CHECK(during_wait.fault.healthy());
  CHECK(during_wait.trace.index("rx.arm") <
        during_wait.trace.index("ready.assert"));
  CHECK(during_wait.trace.index("ready.assert") <
        during_wait.trace.index("ready.release"));
  CHECK(during_wait.trace.index("ready.release") <
        during_wait.trace.index("rx.cancel"));
  CHECK(during_wait.plane.stop());

  Fixture revoked(16, 4);
  CHECK(revoked.start());
  revoked.authority.live = false;
  revoked.trace.clear();
  CHECK(revoked.plane.serviceOnce(waitPolicy(8)) ==
        transport::ServiceResult::kFaulted);
  CHECK(revoked.fault.fault() ==
        transport::TransportFault::kEpochLeaseLost);
  CHECK(revoked.trace.index("ready.release") <
        revoked.trace.index("forward.release"));
  CHECK(std::find(revoked.trace.events.begin(), revoked.trace.events.end(),
                  "rx.arm") == revoked.trace.events.end());
  CHECK(revoked.plane.stop());
}

void testCancellationAfterArmDoesNotAssertReady() {
  Fixture fixture(16, 4);
  CHECK(fixture.start());
  fixture.backend.after_arm = [&fixture] { fixture.plane.requestCancel(); };
  fixture.trace.clear();
  CHECK(fixture.plane.serviceOnce(waitPolicy(8)) ==
        transport::ServiceResult::kCancelled);
  CHECK(fixture.fault.healthy());
  CHECK(fixture.trace.events ==
        std::vector<std::string>({"rx.arm", "rx.cancel"}));
  CHECK(!fixture.hardware.ready_asserted);
  CHECK(fixture.plane.stop());
}

void testInvalidRecordsFailClosed() {
  Fixture zero(16, 4);
  CHECK(zero.start());
  zero.backend.receive({});
  CHECK(zero.plane.serviceOnce(waitPolicy(8)) ==
        transport::ServiceResult::kFaulted);
  CHECK(zero.fault.fault() ==
        transport::TransportFault::kInvalidRecordLength);
  CHECK(zero.stream.available() == 0);
  CHECK(zero.plane.stop());

  Fixture oversized(16, 4);
  CHECK(oversized.start());
  oversized.backend.receive({1, 2, 3, 4, 5});
  CHECK(oversized.plane.serviceOnce(waitPolicy(8)) ==
        transport::ServiceResult::kFaulted);
  CHECK(oversized.fault.fault() ==
        transport::TransportFault::kInvalidRecordLength);
  CHECK(oversized.stream.available() == 0);
  CHECK(oversized.plane.stop());
}

void testInvalidWaitPolicyFailsBeforeAdmission() {
  Fixture fixture(16, 4);
  CHECK(fixture.start());
  fixture.trace.clear();
  CHECK(fixture.plane.serviceOnce({100, 0}) ==
        transport::ServiceResult::kFaulted);
  CHECK(fixture.fault.fault() ==
        transport::TransportFault::kInvalidConfiguration);
  CHECK(std::find(fixture.trace.events.begin(), fixture.trace.events.end(),
                  "rx.arm") == fixture.trace.events.end());
  CHECK(std::find(fixture.trace.events.begin(), fixture.trace.events.end(),
                  "ready.assert") == fixture.trace.events.end());
  CHECK(fixture.plane.stop());
}

void testOutputFailureLatch() {
  std::vector<std::uint8_t> const packet = {0x17, 0x00, 0x80, 1, 2, 3, 4, 5};
  for (std::size_t accepted = 0; accepted < packet.size(); ++accepted) {
    Fixture fixture(16, 4);
    fixture.output.accept_limit = accepted;
    CHECK(fixture.stream.write(packet.data(), packet.size()) == accepted);
    CHECK(fixture.fault.fault() ==
          transport::TransportFault::kOutputShortWrite);
    CHECK(fixture.output.captured.size() == accepted);
    std::size_t const calls = fixture.output.write_calls;
    CHECK(fixture.stream.write(static_cast<std::uint8_t>(0xEE)) == 0);
    CHECK(fixture.output.write_calls == calls);
  }

  Fixture single(16, 4);
  single.output.accept_limit = 1;
  CHECK(single.stream.write(static_cast<std::uint8_t>(0xA5)) == 1);
  CHECK(single.output.captured == std::vector<std::uint8_t>{0xA5});
  CHECK(single.fault.healthy());
  single.output.flush_result = false;
  single.stream.flush();
  CHECK(single.fault.fault() == transport::TransportFault::kOutputFlush);
  CHECK(single.output.flush_calls == 1);

  Fixture duplex_ok(16, 4);
  CHECK(duplex_ok.stream.setProtocolDuplex(true));
  CHECK(duplex_ok.output.duplex_calls == 1);
  CHECK(duplex_ok.output.requested_full_duplex);
  CHECK(duplex_ok.fault.healthy());

  Fixture duplex_rejected(16, 4);
  duplex_rejected.output.duplex_result = false;
  CHECK(!duplex_rejected.stream.setProtocolDuplex(true));
  CHECK(duplex_rejected.fault.fault() ==
        transport::TransportFault::kOutputDuplexControl);

  Fixture active(16, 4);
  CHECK(active.start());
  active.output.accept_limit = 0;
  CHECK(active.stream.write(static_cast<std::uint8_t>(0x80)) == 0);
  active.trace.clear();
  CHECK(active.plane.serviceOnce(waitPolicy(8)) ==
        transport::ServiceResult::kFaulted);
  CHECK(std::find(active.trace.events.begin(), active.trace.events.end(),
                  "rx.arm") == active.trace.events.end());
  CHECK(std::find(active.trace.events.begin(), active.trace.events.end(),
                  "ready.assert") == active.trace.events.end());
  CHECK(active.trace.index("ready.release") <
        active.trace.index("forward.release"));
  CHECK(active.plane.stop());
}

void testSourceDerivedParserByteTraceFailsClosedAtEveryOffset() {
  // This deliberately does not impersonate VDUStreamProcessor.  The paired
  // source-contract test checks that the retained parser frames General Poll
  // and Mode Information this way and calls Stream::write once per byte.  The
  // Mode payload below uses representative fixed-mode values; this test covers
  // only byte-call offsets and the production Stream/data-plane boundary.
  constexpr std::array<std::uint8_t, 13> kParserSourceDerivedWriteTrace = {
      0x80, 0x01, 0x01,              // General Poll: code, length, echo.
      0x86, 0x08,                    // Mode Information: code, length.
      0x80, 0x02, 0xE0, 0x01,        // Fixture canvas: 640 x 480.
      0x50, 0x3C, 0x10, 0x00,        // 80 x 60, 16 colours, mode 0.
  };

  for (std::size_t fault_offset = 0;
       fault_offset < kParserSourceDerivedWriteTrace.size(); ++fault_offset) {
    Fixture fixture(16, 4);
    CHECK(fixture.start());
    fixture.output.fail_on_write_call = fault_offset;

    for (std::uint8_t byte : kParserSourceDerivedWriteTrace) {
      (void)fixture.stream.write(byte);
    }

    CHECK(fixture.output.write_calls == fault_offset + 1);
    CHECK(fixture.output.captured ==
          std::vector<std::uint8_t>(
              kParserSourceDerivedWriteTrace.begin(),
              kParserSourceDerivedWriteTrace.begin() + fault_offset));
    CHECK(fixture.fault.fault() ==
          transport::TransportFault::kOutputShortWrite);

    fixture.trace.clear();
    CHECK(fixture.plane.serviceOnce(waitPolicy(8)) ==
          transport::ServiceResult::kFaulted);
    CHECK(std::find(fixture.trace.events.begin(), fixture.trace.events.end(),
                    "rx.arm") == fixture.trace.events.end());
    CHECK(std::find(fixture.trace.events.begin(), fixture.trace.events.end(),
                    "ready.assert") == fixture.trace.events.end());
    CHECK(!fixture.hardware.ready_asserted);
    CHECK(!fixture.hardware.forward_enabled);
    CHECK(fixture.plane.stop());
  }
}

void testOutputFaultCancelsArmedReceive() {
  Fixture fixture(16, 4);
  CHECK(fixture.start());
  fixture.backend.waitUntilCancelled();
  fixture.trace.clear();

  transport::ServiceResult result = transport::ServiceResult::kNotActive;
  std::thread service([&fixture, &result] {
    result = fixture.plane.serviceOnce(waitPolicy(1500));
  });

  auto const wait_deadline =
      std::chrono::steady_clock::now() + std::chrono::seconds(2);
  while (!fixture.backend.waitEntered() &&
         std::chrono::steady_clock::now() < wait_deadline) {
    std::this_thread::yield();
  }
  CHECK(fixture.backend.waitEntered());

  fixture.output.accept_limit = 0;
  CHECK(fixture.stream.write(static_cast<std::uint8_t>(0x80)) == 0);
  service.join();

  CHECK(fixture.backend.observedCancel());
  CHECK(result == transport::ServiceResult::kFaulted);
  CHECK(fixture.fault.fault() ==
        transport::TransportFault::kOutputShortWrite);
  CHECK(!fixture.hardware.ready_asserted);
  CHECK(!fixture.hardware.forward_enabled);
  CHECK(fixture.trace.index("ready.assert") <
        fixture.trace.index("ready.release"));
  CHECK(fixture.trace.index("ready.release") <
        fixture.trace.index("rx.cancel"));
  CHECK(fixture.plane.stop());
}

void testRecordPublicationArbitratesWithOutputFault() {
  transport::TransportAdmissionBarrier barrier;
  std::uint8_t storage[8]{};
  transport::SpscByteQueue queue(storage, sizeof(storage));
  transport::TransportFaultLatch fault;
  CaptureReturn output;
  BarrierCancellation cancellation(barrier);
  transport::ExtenderVdpStream stream(queue, output, fault, cancellation);
  output.accept_limit = 0;

  CHECK(barrier.tryAdmitRecordPublication());
  std::thread writer([&stream] {
    CHECK(stream.write(static_cast<std::uint8_t>(0x80)) == 0);
  });
  writer.join();
  CHECK(cancellation.entered.load(std::memory_order_acquire));
  CHECK(cancellation.returned.load(std::memory_order_acquire));
  CHECK(barrier.cancelRequested());
  CHECK(fault.fault() == transport::TransportFault::kOutputShortWrite);
  CHECK(!barrier.tryAdmitRecordPublication());
}

void testPostCommitFaultQuarantinesRecord() {
  Fixture fixture(16, 4);
  CHECK(fixture.start());
  fixture.backend.receive({0xD4});
  fixture.output.accept_limit = 0;
  fixture.authority.callback_on_check = fixture.authority.checks + 4;
  fixture.authority.on_check = [&fixture] {
    CHECK(fixture.stream.write(static_cast<std::uint8_t>(0x80)) == 0);
  };

  CHECK(fixture.plane.serviceOnce(waitPolicy(41)) ==
        transport::ServiceResult::kFaulted);
  CHECK(fixture.fault.fault() ==
        transport::TransportFault::kOutputShortWrite);
  CHECK(!fixture.hardware.ready_asserted);
  CHECK(!fixture.hardware.forward_enabled);
  CHECK(fixture.stream.available() == 0);
  CHECK(fixture.queue.size() == 1);
  CHECK(fixture.queue.read() == 0xD4);
  CHECK(fixture.plane.stop());
}

void testAdvertisedReadCannotBecomeSyntheticSentinel() {
  {
    Fixture fixture(8, 4);
    std::uint8_t const bytes[] = {0x41, 0x42};
    CHECK(fixture.queue.pushRecord(bytes, sizeof(bytes)));
    CHECK(fixture.stream.available() == 2);
    fixture.output.accept_limit = 0;
    CHECK(fixture.stream.write(static_cast<std::uint8_t>(0x80)) == 0);
    CHECK(fixture.stream.read() == 0x41);
    CHECK(fixture.stream.read() == -1);
    CHECK(fixture.queue.read() == 0x42);
  }
  {
    Fixture fixture(8, 4);
    std::uint8_t const byte = 0x55;
    CHECK(fixture.queue.pushRecord(&byte, 1));
    CHECK(fixture.stream.peek() == byte);
    fixture.output.flush_result = false;
    fixture.stream.flush();
    CHECK(fixture.stream.peek() == byte);
    CHECK(fixture.stream.read() == byte);
    CHECK(fixture.stream.read() == -1);
  }
  {
    Fixture fixture(8, 4);
    std::uint8_t const byte = 0x66;
    CHECK(fixture.queue.pushRecord(&byte, 1));
    fixture.output.duplex_result = false;
    CHECK(!fixture.stream.setProtocolDuplex(true));
    CHECK(fixture.stream.available() == 0);
    CHECK(fixture.stream.read() == -1);
    CHECK(fixture.queue.read() == byte);
  }
}

void testEveryOutputFaultRequestsCancellation() {
  {
    std::uint8_t storage[8]{};
    transport::SpscByteQueue queue(storage, sizeof(storage));
    transport::TransportFaultLatch fault;
    CaptureReturn output;
    CountingCancellation cancellation;
    transport::ExtenderVdpStream stream(queue, output, fault, cancellation);
    CHECK(stream.write(nullptr, 1) == 0);
    CHECK(cancellation.requests == 1);
  }
  {
    std::uint8_t storage[8]{};
    transport::SpscByteQueue queue(storage, sizeof(storage));
    transport::TransportFaultLatch fault;
    CaptureReturn output;
    CountingCancellation cancellation;
    transport::ExtenderVdpStream stream(queue, output, fault, cancellation);
    output.accept_limit = 0;
    CHECK(stream.write(static_cast<std::uint8_t>(0x80)) == 0);
    CHECK(cancellation.requests == 1);
  }
  {
    std::uint8_t storage[8]{};
    transport::SpscByteQueue queue(storage, sizeof(storage));
    transport::TransportFaultLatch fault;
    CaptureReturn output;
    CountingCancellation cancellation;
    transport::ExtenderVdpStream stream(queue, output, fault, cancellation);
    output.flush_result = false;
    stream.flush();
    CHECK(cancellation.requests == 1);
  }
  {
    std::uint8_t storage[8]{};
    transport::SpscByteQueue queue(storage, sizeof(storage));
    transport::TransportFaultLatch fault;
    CaptureReturn output;
    CountingCancellation cancellation;
    transport::ExtenderVdpStream stream(queue, output, fault, cancellation);
    output.duplex_result = false;
    CHECK(!stream.setProtocolDuplex(true));
    CHECK(cancellation.requests == 1);
  }
}

void testFaultLatchPublishesFirstFailure() {
  transport::TransportFaultLatch latch;
  CHECK(latch.healthy());
  CHECK(latch.latch(transport::TransportFault::kReceiveTimeout));
  CHECK(!latch.latch(transport::TransportFault::kOutputShortWrite));
  CHECK(latch.fault() == transport::TransportFault::kReceiveTimeout);
  latch.clear();
  CHECK(latch.healthy());
}

void testConcurrentSpscPublication() {
  constexpr std::size_t kRecordBytes = 7;
  constexpr std::size_t kRecordCount = 4096;
  std::vector<std::uint8_t> storage(256);
  transport::SpscByteQueue queue(storage.data(), storage.size());

  std::thread producer([&queue] {
    std::uint8_t record[kRecordBytes]{};
    for (std::size_t sequence = 0; sequence < kRecordCount; ++sequence) {
      for (std::size_t offset = 0; offset < kRecordBytes; ++offset) {
        record[offset] = static_cast<std::uint8_t>(sequence + offset);
      }
      while (!queue.pushRecord(record, kRecordBytes)) {
        std::this_thread::yield();
      }
    }
  });

  for (std::size_t sequence = 0; sequence < kRecordCount; ++sequence) {
    for (std::size_t offset = 0; offset < kRecordBytes; ++offset) {
      int value = -1;
      while ((value = queue.read()) < 0) std::this_thread::yield();
      CHECK(value == static_cast<std::uint8_t>(sequence + offset));
    }
  }
  producer.join();
  CHECK(queue.size() == 0);
}

}  // namespace

int main() {
  testOrderedLifecycle();
  testRecordFlatteningAndByteCoverage();
  testQueueRejectsNonPowerOfTwoCapacity();
  testProductionTargetPinPlan();
  testTargetIdleWaitKeepsAdvertisedTransactionArmed();
  testMaximumReservationBackpressure();
  testEveryPartialStartFailureAndRetry();
  testBoundedReceiveFaultsAndRetry();
  testIdlePollDoesNotFaultOrStopIngress();
  testArmFailureReleasesDirectionBeforeCancellation();
  testCleanupFailureRequiresStopRetry();
  testStaleBytesCannotCrossEpoch();
  testCancellationAndLeaseRevocation();
  testCancellationAfterArmDoesNotAssertReady();
  testInvalidRecordsFailClosed();
  testInvalidWaitPolicyFailsBeforeAdmission();
  testOutputFailureLatch();
  testSourceDerivedParserByteTraceFailsClosedAtEveryOffset();
  testOutputFaultCancelsArmedReceive();
  testRecordPublicationArbitratesWithOutputFault();
  testPostCommitFaultQuarantinesRecord();
  testAdvertisedReadCannotBecomeSyntheticSentinel();
  testEveryOutputFaultRequestsCancellation();
  testFaultLatchPublishesFirstFailure();
  testConcurrentSpscPublication();
  std::cout << "p4-production-data-plane: 25 cases passed\n";
}
