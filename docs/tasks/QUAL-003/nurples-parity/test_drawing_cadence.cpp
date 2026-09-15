#include "extender/display/drawing_cadence.hpp"
#include "extender/display/stock_native_access.hpp"
#include <cassert>
#include <cstdio>
#include <initializer_list>
using namespace agon::extender::display;
int main(){
 for(auto period:{1u,16667u,20000u,0xffffffffu}){
  assert(drawingTimerPeriodUs(period,false)==period);
  const auto tick=drawingTimerPeriodUs(period,true);assert(tick && uint64_t(tick)*2>=period);
  StockClock clock;StockFrameCounter count;count=0;clock.start(0,period);
  for(uint64_t i=1;i<=10000;++i){clock.observe(i*tick);assert(uint32_t(count)==i*tick/period);}
  auto now=uint64_t(10020)*tick;clock.observe(now);assert(uint32_t(count)==now/period);
 }
 std::puts("Logical counters preserve elapsed-time cadence at half-period observations");
}
