// Matched recorder controls: classified calls, disabled capture, and unfinished
// operations at a measurement boundary. No assertion depends on host speed.
#define USERSPACE 1
#define AGON_GRAPHICS_TIMING 1
#include "graphics_timing.hpp"
#include <cassert>
using namespace agon_graphics_timing;
int main() {
  begin(true);
  { Scope outer(Primitive); Scope scroll(Scroll); }
  { Scope outer(Primitive); Scope bitmap(Bitmap); }
  { Scope ignored(MetricCount); }
  auto r=finish(0);
  assert(r.count[Primitive].calls==2);
  assert(r.count[Scroll].calls==1 && r.count[Bitmap].calls==1);
  assert(r.count[Scroll].crossing==0 && r.count[Bitmap].crossing==0);
  begin(false);
  { Scope outer(Primitive); Scope scroll(Scroll); }
  r=finish(0);
  for(auto &c:r.count)assert(c.calls==0);
  begin(true);
  { Scope unfinished(Bitmap);
    r=finish(0);assert(r.count[Bitmap].crossing==1);
  }
  begin(true);r=finish(0);
  assert(r.count[Bitmap].crossing==0);
}
