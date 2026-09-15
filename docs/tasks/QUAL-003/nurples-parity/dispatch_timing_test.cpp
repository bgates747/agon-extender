#include "extender/diagnostics/video_timing.hpp"
#include <cassert>
std::int64_t diagnostic_test_now{};
int main() {
 using namespace agon::extender::diagnostics;
 diagnostic_test_now=25;
 videoDispatchTiming(Phase::Queue,0xfffffff0u);
 diagnostic_test_now=34;
 videoDispatchTiming(Phase::TxEnqueue,25);
 Snapshot s{};videoRecorder.read(s,34);
 assert(s.totals[(unsigned)Phase::Queue].count==1);
 assert(s.totals[(unsigned)Phase::Queue].total_us==41);
 assert(s.totals[(unsigned)Phase::TxEnqueue].total_us==9);
 assert(s.totals[(unsigned)Phase::TxEnqueue].units==1);
 assert(!s.lost_completions && !s.overlapping_calls);
 auto json=videoTimingJson();assert(json.find("credit_to_ready")!=std::string::npos);
 assert(json.find("ready_to_send")!=std::string::npos);
}
