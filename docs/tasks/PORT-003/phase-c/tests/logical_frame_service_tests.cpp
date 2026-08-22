// PORT-003 Phase C host protocol harness.
//
// A Python runner feeds the independently generated operation fixtures to this
// executable. This harness invokes the production LogicalFrameService while a
// deliberately simple fake executor supplies only deterministic queue/storage
// boundaries. It never contains expected traces.
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "extender/display/logical_frame_service.hpp"

using namespace agon::extender::display;

namespace {

struct Event {
  std::string name;
  std::vector<std::pair<std::string, std::string>> fields;
};

std::string quote(std::string const &value) {
  std::string result = "\"";
  for (char character : value) {
    if (character == '\\' || character == '"') result += '\\';
    result += character;
  }
  return result + '"';
}

struct Item {
  std::uint64_t sequence;
  std::string kind;
  bool dynamic;
};

struct MockConsumer {
  bool connected{true};
  std::uint64_t slot{};
  std::uint32_t drops{};
  int mailbox{-1};
};

struct Harness final : FrameWorkExecutor {
  explicit Harness(bool double_buffered, std::uint32_t initial_frame,
                   std::size_t budget)
      : double_buffered(double_buffered), frame(initial_frame),
        service(*this, budget) {
    observer_slot = service.registerConsumer();
    if (observer_slot < 0) std::abort();
  }

  bool double_buffered;
  std::uint32_t frame;
  std::uint64_t submitted{};
  std::uint64_t started{};
  std::uint64_t completed{};
  std::uint8_t visible{};
  std::uint8_t drawing{double_buffered ? std::uint8_t{1} : std::uint8_t{0}};
  bool active_running{};
  bool stopped{};
  std::deque<Item> queue;
  std::vector<Item> active;
  std::vector<std::uint64_t> drained_on_stop;
  std::vector<Event> events;
  std::map<std::string, MockConsumer> consumers;
  LogicalFrameService service;
  int observer_slot{-1};

  void event(std::string name,
             std::vector<std::pair<std::string, std::string>> fields = {}) {
    events.push_back({std::move(name), std::move(fields)});
  }

  void ensureStarted() {
    if (!service.running() && !stopped && !service.start()) std::abort();
  }

  void submit(std::string const &kind, bool dynamic) {
    if (double_buffered && kind != "swap") {
      event("immediate", {{"kind", quote(kind)}});
      return;
    }
    Item item{++submitted, kind, dynamic};
    queue.push_back(item);
    event("submitted", {{"sequence", std::to_string(item.sequence)},
                        {"kind", quote(item.kind)}});
  }

  void startOne() {
    if (!active.empty() || queue.empty()) {
      event("start-none");
      return;
    }
    active.push_back(queue.front());
    queue.pop_front();
    started = active.front().sequence;
    event("started", {{"sequence", std::to_string(started)},
                      {"kind", quote(active.front().kind)}});
  }

  Item finishOne(bool record_completion) {
    if (active.empty()) {
      event("finish-none");
      return {};
    }
    Item item = active.front();
    active.clear();
    if (item.kind == "swap") {
      std::swap(visible, drawing);
      event("planes-swapped", {{"sequence", std::to_string(item.sequence)},
                               {"visible", std::to_string(visible)},
                               {"drawing", std::to_string(drawing)}});
    }
    if (item.dynamic)
      event("payload-released", {{"sequence", std::to_string(item.sequence)}});
    if (record_completion) complete(item);
    return item;
  }

  void complete(Item const &item) {
    completed = item.sequence;
    event("completed", {{"sequence", std::to_string(item.sequence)},
                        {"kind", quote(item.kind)}});
  }

  void setFrameServiceRunning(bool running) noexcept override {
    active_running = running;
    if (!running) {
      if (!active.empty()) {
        drained_on_stop.push_back(active.front().sequence);
        finishOne(true);
      }
      while (!queue.empty()) {
        startOne();
        drained_on_stop.push_back(active.front().sequence);
        finishOne(true);
      }
    }
  }

  std::size_t executeFrameWork(std::size_t maximum) override {
    std::size_t executed = 0;
    while (executed < maximum && !queue.empty()) {
      startOne();
      finishOne(true);
      ++executed;
    }
    return executed;
  }

  std::uint32_t advanceFrameCounter(std::uint32_t elapsed) noexcept override {
    frame += elapsed;
    event("frame-edge", {{"elapsed", std::to_string(elapsed)},
                         {"frame_counter", std::to_string(frame)}});
    return frame;
  }

  std::uint32_t frameCounter() const noexcept override { return frame; }
  std::size_t logicalWidth() const noexcept override { return 8; }
  std::size_t logicalHeight() const noexcept override { return 6; }
  NativePixelFormat logicalFormat() const noexcept override {
    return NativePixelFormat::SBGR2222;
  }
  bool logicalDoubleBuffered() const noexcept override { return double_buffered; }
  std::uint8_t visiblePlaneIdentity() const noexcept override { return visible; }

  void registerConsumer(std::string const &name) {
    auto [iterator, inserted] = consumers.try_emplace(name);
    if (!inserted) std::abort();
    iterator->second.mailbox = service.registerConsumer();
    if (iterator->second.mailbox < 0) std::abort();
    event("consumer-registered", {{"consumer", quote(name)}});
  }

  void observePublications() {
    FrameNotice notice{};
    if (!service.tryConsumeLatest(observer_slot, notice)) std::abort();
    event("published", {{"generation", std::to_string(notice.generation)},
                        {"frame_counter", std::to_string(notice.frame_counter)},
                        {"visible", std::to_string(notice.visible_plane)}});
    for (auto &[name, consumer] : consumers) {
      if (!consumer.connected) continue;
      std::uint32_t drops = service.consumerDrops(consumer.mailbox);
      if (drops != consumer.drops) {
        if (drops != consumer.drops + 1 || consumer.slot == 0) std::abort();
        consumer.drops = drops;
        event("consumer-drop", {{"consumer", quote(name)},
                                {"dropped_generation", std::to_string(consumer.slot)},
                                {"drops", std::to_string(consumer.drops)}});
      }
      if (!service.tryPeekLatest(consumer.mailbox, notice)) std::abort();
      consumer.slot = notice.generation;
      event("consumer-notified", {{"consumer", quote(name)},
                                  {"generation", std::to_string(consumer.slot)}});
    }
  }

  void stop() {
    service.stop();
    stopped = true;
    std::string list = "[";
    for (std::size_t index = 0; index < drained_on_stop.size(); ++index) {
      if (index != 0) list += ',';
      list += std::to_string(drained_on_stop[index]);
    }
    event("stopped", {{"drained", list + ']'}});
  }
};

void emit(Harness const &harness) {
  auto metrics = harness.service.metrics();
  std::cout << "{\"events\":[";
  for (std::size_t index = 0; index < harness.events.size(); ++index) {
    if (index != 0) std::cout << ',';
    auto const &event = harness.events[index];
    std::cout << "{\"event\":" << quote(event.name);
    for (auto const &[key, value] : event.fields)
      std::cout << ',' << quote(key) << ':' << value;
    std::cout << '}';
  }
  std::cout << "],\"final\":{"
            << "\"frame_counter\":" << harness.frame << ','
            << "\"generation\":" << harness.service.generation() << ','
            << "\"pending_ticks\":" << harness.service.pendingTicks() << ','
            << "\"submitted_sequence\":" << harness.submitted << ','
            << "\"started_sequence\":" << harness.started << ','
            << "\"completed_sequence\":" << harness.completed << ','
            << "\"queue_depth\":" << harness.queue.size() << ','
            << "\"active\":";
  if (harness.active.empty()) std::cout << "null";
  else std::cout << harness.active.front().sequence;
  std::cout << ",\"visible_plane\":" << unsigned(harness.visible)
            << ",\"drawing_plane\":" << unsigned(harness.drawing)
            << ",\"metrics\":{"
            << "\"elapsed_ticks\":" << metrics.elapsed_ticks << ','
            << "\"serviced_edges\":" << metrics.serviced_edges
            << "},\"consumers\":{";
  bool first = true;
  for (auto const &[name, consumer] : harness.consumers) {
    if (!first) std::cout << ',';
    first = false;
    std::cout << quote(name) << ":{\"connected\":"
              << (consumer.connected ? "true" : "false") << ",\"slot\":";
    if (consumer.slot == 0) std::cout << "null";
    else std::cout << consumer.slot;
    std::cout << ",\"drops\":" << consumer.drops << '}';
  }
  std::cout << "}}}\n";
}

}  // namespace

int main() {
  std::string command;
  bool double_buffered = false;
  std::uint32_t initial_frame = 0;
  std::size_t budget = 64;
  if (!(std::cin >> command >> double_buffered >> initial_frame >> budget) ||
      command != "INIT") return 2;
  Harness harness(double_buffered, initial_frame, budget);
  while (std::cin >> command) {
    if (command == "SUBMIT") {
      std::string kind;
      bool dynamic;
      std::cin >> kind >> dynamic;
      harness.submit(kind, dynamic);
    } else if (command == "TICK") {
      std::uint32_t count;
      std::cin >> count;
      harness.ensureStarted();
      if (!harness.service.recordTicks(count)) std::abort();
      harness.event("ticks-recorded", {{"count", std::to_string(count)},
                                       {"pending", std::to_string(harness.service.pendingTicks())}});
    } else if (command == "SERVICE") {
      std::size_t requested_budget;
      std::cin >> requested_budget;
      harness.ensureStarted();
      if (requested_budget != budget) std::abort();
      if (harness.service.servicePending() == FrameServiceResult::Serviced)
        harness.observePublications();
    } else if (command == "START_ONE") {
      harness.startOne();
    } else if (command == "FINISH_ONE") {
      harness.finishOne(true);
    } else if (command == "WAIT") {
      std::uint64_t target;
      std::cin >> target;
      // Upstream primitivesExecutionWait() observes queue depth only. An item
      // already dequeued into active execution therefore satisfies the wait.
      std::string result = harness.queue.empty() ? "satisfied" : "blocked";
      harness.event("wait-result", {{"sequence", std::to_string(target)},
                                    {"result", quote(result)}});
    } else if (command == "WRITE_FRAME") {
      std::uint32_t value;
      std::cin >> value;
      harness.frame = value;
      harness.event("frame-counter-written", {{"value", std::to_string(value)}});
    } else if (command == "REGISTER") {
      std::string name;
      std::cin >> name;
      harness.registerConsumer(name);
    } else if (command == "CONSUME") {
      std::string name;
      std::cin >> name;
      auto &consumer = harness.consumers.at(name);
      FrameNotice notice{};
      bool available = harness.service.tryConsumeLatest(consumer.mailbox, notice);
      auto generation = available ? notice.generation : 0;
      consumer.slot = 0;
      harness.event("consumer-consumed", {{"consumer", quote(name)},
                                          {"generation", generation == 0 ? "null" : std::to_string(generation)}});
    } else if (command == "DISCONNECT" || command == "RECONNECT") {
      std::string name;
      std::cin >> name;
      auto &consumer = harness.consumers.at(name);
      consumer.connected = command == "RECONNECT";
      if (!harness.service.setConsumerConnected(consumer.mailbox,
                                                consumer.connected)) {
        std::abort();
      }
      if (!consumer.connected) consumer.slot = 0;
      harness.event(consumer.connected ? "consumer-reconnected" : "consumer-disconnected",
                    {{"consumer", quote(name)}});
    } else if (command == "STOP") {
      harness.ensureStarted();
      harness.stop();
    } else if (command == "END") {
      break;
    } else {
      return 3;
    }
  }
  emit(harness);
  return 0;
}
