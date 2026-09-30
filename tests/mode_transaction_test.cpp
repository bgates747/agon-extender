#include <cassert>
#include <memory>
#include <string>
#include <vector>

#include "extender/display/mode_transaction.hpp"

using agon::extender::display::PreparedModeCandidate;
using agon::extender::display::commitPreparedMode;
using agon::extender::display::prepareModeCandidate;

namespace {
struct Lifetime {
  explicit Lifetime(int &count) : count(count) { ++count; }
  virtual ~Lifetime() { --count; }
  int &count;
};
struct Controller : Lifetime { using Lifetime::Lifetime; };
struct Canvas : Lifetime { using Lifetime::Lifetime; };
struct Service : Lifetime { using Lifetime::Lifetime; };
using Candidate = PreparedModeCandidate<Controller, Canvas, Service>;

void failuresPreserveLiveMode() {
  for (int fail = 0; fail != 7; ++fail) {
    int controllers{}, canvases{}, services{};
    bool old_live = true;
    Candidate candidate{};
    candidate.width = 640;
    candidate.height = 480;
    candidate.colours = 16;
    candidate.refresh_hz = 60;
    int step{};
    const bool prepared = prepareModeCandidate(
        candidate,
        [&] {
          if (step++ == fail) return std::unique_ptr<Controller>{};
          return std::make_unique<Controller>(controllers);
        },
        [&](Controller &) { return step++ != fail; },
        [&](Controller &) {
          if (step++ == fail) return std::unique_ptr<Canvas>{};
          return std::make_unique<Canvas>(canvases);
        },
        [&] {
          if (step++ == fail) return std::unique_ptr<Service>{};
          return std::make_unique<Service>(services);
        },
        [&](Service &, Controller &) {
          // Timer, drawing worker and output worker are distinct injected
          // ordinals inside the selected service-preparation callback.
          for (int resource = 0; resource != 3; ++resource)
            if (step++ == fail) return false;
          return true;
        });
    assert(old_live);
    assert(prepared == (fail >= step));
    if (!prepared) {
      candidate = {};
      assert(controllers == 0 && canvases == 0 && services == 0);
    }
  }
}

void commitHasNoAcquisitionAfterRetirement() {
  int controllers{}, canvases{}, services{};
  Candidate candidate{};
  candidate.controller = std::make_unique<Controller>(controllers);
  candidate.canvas = std::make_unique<Canvas>(canvases);
  candidate.service = std::make_unique<Service>(services);
  candidate.width = 512;
  candidate.height = 384;
  candidate.colours = 64;
  candidate.refresh_hz = 60;
  std::vector<std::string> events;
  bool published{};
  commitPreparedMode(
      std::move(candidate),
      [&] { events.emplace_back("old-readers-joined"); },
      [&](Controller &) { events.emplace_back("candidate-aliases-bound"); },
      [&](Service &) { events.emplace_back("candidate-activated"); },
      [&](Candidate &&prepared) {
        assert(prepared.complete());
        events.emplace_back("candidate-published");
        Candidate accepted = std::move(prepared);
        assert(accepted.complete());
        published = true;
      });
  assert(published);
  assert((events == std::vector<std::string>{
      "old-readers-joined", "candidate-aliases-bound",
      "candidate-activated", "candidate-published"}));
  assert(controllers == 0 && canvases == 0 && services == 0);
}
}  // namespace

int main() {
  failuresPreserveLiveMode();
  commitHasNoAcquisitionAfterRetirement();
}
