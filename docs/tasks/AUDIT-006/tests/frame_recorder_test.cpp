#include "extender/diagnostics/frame_recorder.hpp"
#include "extender/diagnostics/frame_timing.hpp"
#include <cassert>
#include <thread>
#include <iostream>
using namespace agon::extender::diagnostics;
std::int64_t diagnostic_test_now{};
namespace agon::extender::diagnostics {
struct RecorderTestAccess {
  static void hold(FrameRecorder &r) { assert(!r.lock_.test_and_set()); }
  static void release(FrameRecorder &r) { r.lock_.clear(); }
};
}
int main() {
  FrameRecorder r; Snapshot s{};
  auto t = r.begin(Phase::Frame, 100, 7);
  r.read(s, 150);
  assert(s.active[0].consistent && s.active[0].state == 2 && s.active[0].age_us == 50);
  assert(s.active[0].context == 7 && s.totals[0].count == 0);
  auto rejected = r.begin(Phase::Frame, 151);
  r.end(rejected, 160); r.end(t, 200, 42);
  r.read(s, 210);
  assert(s.totals[0].count == 1 && s.totals[0].total_us == 100 && s.totals[0].units == 42);
  assert(s.active[0].state == 0 && s.overlapping_calls == 1);
  t = r.begin(Phase::Frame, 0xfffffff0U, 9);
  r.read(s, 16); assert(s.active[0].age_us == 32);
  r.end(t, 0x30); r.read(s, 0x31);
  assert(s.totals[0].last_us == 64 && s.totals[0].max_us == 100 && s.totals[0].max_context == 7);
  // A reader timestamp predating a new phase must not fabricate a huge hang.
  t = r.begin(Phase::Parser, 200); r.read(s, 199);
  assert(!s.active[5].consistent && s.active[5].age_us == 0); r.end(t, 210);
  // Deliberately preempt a reader while it owns the copy lock. The writer
  // must return immediately, count loss and retire its live state anyway.
  t = r.begin(Phase::Queue, 1000);
  RecorderTestAccess::hold(r);
  r.end(t, 1200); r.read(s, 1201);
  assert(!s.totals_valid && s.busy_reads == 1 && s.lost_completions == 1);
  assert(s.active[1].state == 0);
  RecorderTestAccess::release(r);
  for (unsigned i=0; i<40; ++i) {
    t=r.begin(Phase::Snapshot, i*30000, i); r.end(t, i*30000+20000, 640*480);
  }
  r.read(s, 1300000);
  assert(s.history_count == 32 && s.history_overwritten == 8);
  assert(s.history[s.history_next].context == 8);
  assert(s.totals[3].count == 40 && s.totals[3].total_us == 800000);
  // A genuine long operation must remain visible before completion and must
  // retain its exact duration afterwards even across many other fast events.
  t = r.begin(Phase::Suspend, 1300000, 1);
  r.read(s, 3300000); assert(s.active[4].age_us == 2000000);
  r.end(t, 4300000); r.read(s, 4300001);
  assert(s.totals[4].max_us == 3000000);
  // Concurrent writer and sampler: atomic live observations + locked totals,
  // and recorded+lost must account for every completed invocation.
  FrameRecorder concurrent; std::atomic<bool> done{};
  std::thread writer([&] {
    for (unsigned i=0;i<100000;++i) {
      auto token=concurrent.begin(Phase::Queue, i*10);
      concurrent.end(token, i*10+5, 1);
    }
    done.store(true);
  });
  while (!done.load()) { Snapshot sample{}; concurrent.read(sample, 1000000); }
  writer.join(); concurrent.read(s, 1000000);
  assert(s.totals_valid && s.totals[1].count+s.lost_completions == 100000);
  assert(s.totals[1].total_us == s.totals[1].count*5 && s.active[1].state == 0);
  std::cout << "PASS: live/completed timing, wrap, nesting rejection, loss, history and concurrent sampling\n";
  diagnostic_test_now = 500;
  {
    Scope frame(Phase::Frame, 3);
    diagnostic_test_now = 1500;
    { Scope queue(Phase::Queue); diagnostic_test_now = 25000; queue.units(17); }
    diagnostic_test_now = 30000;
    std::cout << timingJson() << '\n';
  }
}
