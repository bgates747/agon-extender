#include "extender/diagnostics/video_timing.hpp"
#include <cassert>
std::int64_t diagnostic_test_now{};
int main() {
  using namespace agon::extender::diagnostics;
  VideoRowTotals row;
  row.add(5,7); row.add(11,13);
  diagnostic_test_now=5; // Exercise wrap in the synthetic aggregate interval.
  row.publish(0x02000180);
  Snapshot s{}; videoRecorder.read(s,5);
  const auto wait=static_cast<unsigned>(Phase::Parser);
  const auto work=static_cast<unsigned>(Phase::Sprites);
  assert(s.totals[wait].total_us==16 && s.totals[work].total_us==20);
  assert(s.totals[wait].count==1 && s.totals[wait].units==2);
  row.reset(); row.add(3,4); diagnostic_test_now=100; row.publish(0);
  videoRecorder.read(s,100);
  assert(s.totals[wait].total_us==19 && s.totals[work].total_us==24);
  assert(s.totals[wait].units==3);
  row.reset(); row.add(UINT32_MAX,0); row.add(1,0); row.publish(0);
  videoRecorder.read(s,100);
  assert(s.totals[wait].count==3 && s.totals[wait].units==3);
  assert(s.totals[wait].total_us==19); // Overflow is a zero-unit invalid sample.
  assert(s.totals_valid && !s.lost_completions && !s.overlapping_calls);
  auto json=videoTimingJson();
  assert(json.find("row_wait_sum")!=std::string::npos);
  assert(json.find("row_work_sum")!=std::string::npos);
}
