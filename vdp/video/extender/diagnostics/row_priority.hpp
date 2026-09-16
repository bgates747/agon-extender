// QUAL-003 P01f S: diagnostic only. Priority changes surround an unlocked
// caller's row operation; never save an inherited priority from inside a mutex.
#pragma once
namespace agon_row_priority {
template<class Runtime> class Ceiling {
 unsigned previous_{}; bool changed_{};
 public:
 explicit Ceiling(bool enabled) {
  if (!enabled) return;
  previous_=Runtime::get();
  Runtime::require(previous_==2 || previous_==19);
  if(previous_==19) return; // a nested ceiling leaves restoration to its owner
  Runtime::set(19); changed_=true;
  Runtime::require(Runtime::get()==19);
 }
 ~Ceiling() {
  if(!changed_) return;
  Runtime::require(Runtime::get()==19);
  Runtime::set(previous_);
  Runtime::require(Runtime::get()==previous_);
 }
 Ceiling(const Ceiling&)=delete;
 Ceiling& operator=(const Ceiling&)=delete;
};
}
#ifdef AGON_EXTENDER_ROW_PRIORITY
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
namespace agon_row_priority {
inline std::atomic<bool> enabled{false};
struct Runtime {
 static unsigned get(){return uxTaskPriorityGet(nullptr);}
 static void set(unsigned n){vTaskPrioritySet(nullptr,n);}
 static void require(bool ok){configASSERT(ok);}
};
using Scope=Ceiling<Runtime>;
inline void begin(const uint8_t *n) {
 enabled.store(n[0]=='P' && n[1]=='0' && n[2]=='2' && n[3]==0 && n[4]==1);
}
inline void stop(const uint8_t *n) {
 const bool selected=enabled.exchange(false);
 std::printf("\nNPPRIO ");for(unsigned i=0;i<8;++i)std::printf("%02x",unsigned(n[i]));
 std::printf(" %u\n",selected?19u:2u);
}
}
#endif
