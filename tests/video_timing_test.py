"""Optional output-scope accounting and normal-build exclusion, no physical I/O."""
from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

ENABLED = r'''
#include "extender/diagnostics/video_timing.hpp"
#include <cassert>
#include <iostream>
using namespace agon::extender::diagnostics;
static std::int64_t now;
std::int64_t esp_timer_get_time() { return now; }
namespace agon::extender::diagnostics {
struct RecorderTestAccess {
 static void hold(FrameRecorder &r) { assert(!r.lock_.test_and_set()); }
 static void release(FrameRecorder &r) { r.lock_.clear(); }
};
}
int main() {
 now=100;
 {
  VideoTimingScope snapshot(VideoPhase::Snapshot, (640U<<16)|480);
  now=300;
  { VideoTimingScope send(VideoPhase::SocketSend, 2); now=1300;send.finish(307232); }
  now=2100;snapshot.finish(307200);snapshot.finish(999); // never double-count
 }
 std::cout << videoTimingJson() << '\n';
 now=0xfffffff0U;
 {VideoTimingScope snapshot(VideoPhase::Snapshot, (320U<<16)|240);now=0x30;snapshot.finish(76800);}
 std::cout << videoTimingJson() << '\n';
 {VideoTimingScope canceled(VideoPhase::Snapshot, 123);now=0x40;} // zero units
 now=0x50;
 {
  VideoTimingScope snapshot(VideoPhase::Snapshot, 456);
  {VideoTimingScope duplicate(VideoPhase::Snapshot, 789);duplicate.finish(1);}
  RecorderTestAccess::hold(videoRecorder);
  snapshot.finish(12); // lost aggregate update, but active state must clear
  std::cout << videoTimingJson() << '\n';
  RecorderTestAccess::release(videoRecorder);
 }
 std::cout << videoTimingJson() << '\n';
}
'''

DISABLED = r'''
#include "extender/diagnostics/video_timing.hpp"
extern "C" void ordinary_output() {
 using namespace agon::extender::diagnostics;
 VideoTimingScope scope(VideoPhase::Snapshot, 123);
 scope.finish(456);
}
int main() { ordinary_output(); }
'''


def main():
    with tempfile.TemporaryDirectory() as temporary:
        p = Path(temporary)
        (p/'esp_timer.h').write_text('#pragma once\n#include <cstdint>\nstd::int64_t esp_timer_get_time();\n')
        (p/'enabled.cpp').write_text(ENABLED)
        common = ['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-I'+str(ROOT/'vdp/video'), '-I'+str(p)]
        subprocess.run([*common, '-DAGON_EXTENDER_VIDEO_TIMING=1', '-fsanitize=address,undefined',
                        str(p/'enabled.cpp'), '-o', str(p/'enabled')], check=True)
        result = subprocess.run([str(p/'enabled')], check=True, text=True, capture_output=True)
        first, wrap, busy, final = [json.loads(line) for line in result.stdout.splitlines()]
        assert [v['name'] for v in first['phases']] == ['snapshot', 'socket_send']
        a, b = first['phases']
        assert (a['count'], a['total_us'], a['units'], a['max_context']) == (1, 2000, 307200, (640<<16)|480)
        assert (b['count'], b['total_us'], b['units']) == (1, 1000, 307232)
        assert a['active']['state'] == b['active']['state'] == 0
        assert wrap['phases'][0]['total_us'] == 2064 and wrap['phases'][0]['count'] == 2
        assert not busy['totals_valid'] and busy['lost_completions'] == 1 and busy['busy_reads'] == 1
        assert busy['phases'][0]['active']['state'] == 0
        assert final['totals_valid'] and final['overlapping_calls'] == 1
        assert (final['phases'][0]['count'], final['phases'][0]['units']) == (3, 384000)
        (p/'disabled.cpp').write_text(DISABLED)
        subprocess.run([*common, '-O2', str(p/'disabled.cpp'), '-o', str(p/'disabled')], check=True)
        subprocess.run([str(p/'disabled')], check=True)
        symbols = subprocess.check_output(['nm', '-C', str(p/'disabled')], text=True)
        assert all(token not in symbols for token in ('esp_timer', 'videoRecorder', 'FrameRecorder', 'videoTimingJson'))
        # The native adapter must retain its exact original scanline body.
        stock = ROOT/'vdp/video/extender/display/stock_scanline.cpp'
        original = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:'+str(stock.relative_to(ROOT))])
        assert stock.read_bytes() == original
        print('PASS: two-boundary units/durations, wrap, cancellation, contention, readonly reporting; disabled recorder/timestamps absent; stock scanline unchanged')


if __name__ == '__main__':
    main()
