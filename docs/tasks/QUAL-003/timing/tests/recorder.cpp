#define USERSPACE 1
#define AGON_GRAPHICS_TIMING 1
#include "extender/diagnostics/graphics_timing.hpp"
#include <cassert>
#include <chrono>
#include <thread>
using namespace agon_graphics_timing;
int main() {
  begin(false); {Scope s(Primitive);} auto r=finish(0);assert(r.count[0].calls==0);
  begin(true); {Scope s(Primitive);std::this_thread::sleep_for(std::chrono::milliseconds(2));}
  r=finish(17);assert(r.count[0].calls==1 && r.count[0].us>=1000 && r.drain==17);
  begin(true); {Scope crossing(ScanlineDecoration);r=finish(0);assert(r.count[2].crossing==1);begin(true);}
  r=finish(0);assert(r.count[2].calls==0 && r.count[2].crossing==1);
  auto t=issue();assert(!complete(t));reached(t);assert(!complete(t));{FinishSprites s;}assert(complete(t));
  auto next=issue();assert(next!=t && !complete(next));
  std::thread worker([&]{reached(next);{FinishSprites s;}});worker.join();assert(complete(next));
}
