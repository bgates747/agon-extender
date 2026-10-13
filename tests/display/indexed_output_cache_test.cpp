#include "extender/display/indexed_output_cache.hpp"
#include <cassert>
#include <cstdio>

using agon::extender::display::IndexedOutputCacheState;
int main() {
  using State=IndexedOutputCacheState;
  assert(State::nativeMode20(512,384,684,384,false));
  assert(!State::nativeMode20(512,384,684,384,true));
  assert(!State::nativeMode20(320,240,848,480,false));
  assert(!State::nativeMode20(684,384,684,384,false));
  assert(!State::nativeMode20(512,384,848,480,false));
  State state;
  for(unsigned target=0;target<2;++target) {
    auto a=state.begin(target,true,true);assert(a.preserve_cpu_writes);
    state.submitted(a);
  }
  for(unsigned target=0;target<2;++target) {
    auto a=state.begin(target,true,false);assert(!a.preserve_cpu_writes);
    state.submitted(a);
  }
  // Every refusal/failure after begin leaves this target needing writeback.
  for(unsigned failure=0;failure<5;++failure) {
    auto abandoned=state.begin(0,true,false);assert(!abandoned.preserve_cpu_writes);
    auto retry=state.begin(0,true,false);assert(retry.preserve_cpu_writes);
    state.submitted(retry);
  }
  auto clear=state.begin(0,true,true);assert(clear.preserve_cpu_writes);
  state.submitted(clear);
  state.invalidate(); // includes identical-size controller replacement
  for(unsigned target=0;target<2;++target) {
    auto a=state.begin(target,true,false);assert(a.preserve_cpu_writes);
    state.submitted(a);
  }
  auto other=state.begin(1,false,false);assert(other.preserve_cpu_writes);
  state.submitted(other);
  for(unsigned target=0;target<2;++target) {
    auto a=state.begin(target,true,false);assert(a.preserve_cpu_writes);
    state.submitted(a);
  }
  auto invalid=state.begin(2,true,false);assert(invalid.preserve_cpu_writes&&!invalid.eligible);
  state.submitted(invalid);
  assert(state.begin(0,true,false).preserve_cpu_writes);
  std::puts("PASS: cache eligibility first/clear/two planes/failure/mode/path/bounds transitions");
}
