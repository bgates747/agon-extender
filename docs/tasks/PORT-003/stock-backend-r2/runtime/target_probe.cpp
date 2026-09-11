// Compile/link reachability only. This is not a firmware entry point and is
// never executed by the proof. Resolve real P4 task/timer/native class calls.
#include <cstdlib>
#include "canvas.h"
#include "extender/display/stock_p4_service.hpp"
using namespace agon::extender::display;
int stockRuntimeTargetLinkProbe(int colours) {
  Allocator alloc{nullptr,[](void *,std::size_t n)->void *{return std::malloc(n);},[](void *,void *p){std::free(p);}};
  StockP4Service service(alloc);
  auto controller=makeStockRuntimeController(colours);
  if(!controller) return 1;
  controller->display().begin();
  controller->display().setResolution("\"64x16\" 1 64 68 72 80 16 18 20 24 -HSync -VSync",64,16);
  if(!service.startClock()||!service.attach(*controller)) return 2;
  service.detach();
  return 0;
}
