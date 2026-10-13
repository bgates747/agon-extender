// RESEARCH-007 bounded cache pilot. This is output-task state, not a lock or a
// DMA ownership decision. The caller still waits for the prior submitted frame.
#pragma once
#include <cstdint>

namespace agon::extender::display {
class IndexedOutputCacheState {
 public:
  struct Attempt { unsigned target; bool preserve_cpu_writes; bool eligible; };
  // A committed mode boundary joins the old output task before this reset and
  // resets before making its replacement active. Do not reset from an ISR.
  void invalidate() noexcept { reusable_[0]=reusable_[1]=false; }
  static bool nativeMode20(int w,int h,int output_w,int output_h,bool double_buffered) noexcept {
    return w==512 && h==384 && output_w==684 && output_h==384 && !double_buffered;
  }
  Attempt begin(unsigned target,bool eligible,bool cpu_clear) noexcept {
    if(!eligible || target>=2)invalidate();
    const bool reuse=target<2 && eligible && !cpu_clear && reusable_[target];
    // Failure/refusal after begin remains conservative: only successful PPA,
    // post-invalidation AND panel submission can restore this eligibility.
    if(target<2)reusable_[target]=false;
    return {target,!reuse,eligible && target<2};
  }
  void submitted(Attempt const &attempt) noexcept {
    if(attempt.target<2)reusable_[attempt.target]=attempt.eligible;
  }
 private:
  bool reusable_[2]{};
};
}
