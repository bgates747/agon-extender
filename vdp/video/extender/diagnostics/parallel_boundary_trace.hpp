// PORT-008 boundary attribution only; compile off in every ordinary build.
// One parser publishes completed adjustment/offer records. Native acquisitions
// retain the same mutex operations; elapsed wait includes observer/preemption.
// HTTP copies completed records after STOP, never the live per-lock accumulator.
#pragma once
#ifdef AGON_EXTENDER_PARALLEL_BOUNDARY_TRACE
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <memory>
#include <string>
#ifdef NP_TRACE_HOST
#include <mutex>
#else
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#endif
namespace agon_parallel_boundary {
#ifdef NP_TRACE_HOST
inline std::mutex mutex;
struct Guard { std::lock_guard<std::mutex> lock{mutex}; };
inline std::atomic<uint32_t> hostClock{};
inline uint32_t now(){return hostClock.fetch_add(1);}
inline void *task(){static thread_local int identity;return &identity;}
#else
inline portMUX_TYPE mutex=portMUX_INITIALIZER_UNLOCKED;
struct Guard{Guard(){portENTER_CRITICAL(&mutex);}~Guard(){portEXIT_CRITICAL(&mutex);}};
inline uint32_t now(){return uint32_t(esp_timer_get_time());}
inline void *task(){return xTaskGetCurrentTaskHandle();}
#endif
struct Adjust {uint32_t buffer{},op{},bytes{},begin{},end{},wait_max{},calls{};uint64_t wait_total{};};
struct Offer {uint32_t sequence{},bytes{},reverse{},seen{},accepted{},retired{},attempts{};};
struct Snapshot {
 std::array<Adjust,64> adjusts{};std::array<Offer,128> offers{};
 uint32_t adjustment_count{},offer_count{},dropped{},state{},invalid{};
};
inline Snapshot saved;
inline Adjust live;
inline std::atomic<void*> parser{};
inline unsigned currentOffer=128;
inline bool observing(){return parser.load(std::memory_order_relaxed)==task();}
inline void start(){Guard g;saved={};saved.state=1;currentOffer=128;if(parser.load())saved.invalid=1;}
inline void stop(){Guard g;if(parser.load())saved.invalid=1;saved.state=3;}
class Adjustment {
 bool active_{};
 public:
 explicit Adjustment(uint32_t buffer){
  Guard g;
  // Fixture's reserved buffer57600 starts collection after CLI/input setup;
  // poison/setup adjustments are retained and distinguished by op/count.
  if(buffer!=57600 || (saved.state!=1 && saved.state!=2))return;
  if(parser.load()){saved.invalid=1;return;}
  saved.state=2;live={};live.buffer=buffer;live.begin=now();
  parser.store(task(),std::memory_order_release);active_=true;
 }
 void tag(uint32_t op,uint32_t count){if(active_){live.op=op;live.bytes=count;}}
 ~Adjustment(){
  if(!active_)return;
  live.end=now();parser.store(nullptr,std::memory_order_release);Guard g;
  if(saved.adjustment_count<saved.adjusts.size())saved.adjusts[saved.adjustment_count++]=live;
  else ++saved.dropped;
 }
};
inline void acquired(uint32_t us){live.wait_total+=us;if(us>live.wait_max)live.wait_max=us;++live.calls;}
inline void offer(const uint8_t *p){
 const auto stamp=now();Guard g;if(saved.state!=2)return;
 const uint32_t sequence=p[8]|uint32_t(p[9])<<8;
 if(currentOffer<saved.offer_count && saved.offers[currentOffer].sequence==sequence){++saved.offers[currentOffer].attempts;return;}
 if(saved.offer_count==saved.offers.size()){++saved.dropped;currentOffer=128;return;}
 currentOffer=saved.offer_count++;auto &r=saved.offers[currentOffer];
 r={sequence,uint32_t(p[10])|uint32_t(p[11])<<8,p[12],stamp,0,0,1};
}
inline void accepted(){const auto stamp=now();Guard g;if(saved.state==2 && currentOffer<saved.offer_count)saved.offers[currentOffer].accepted=stamp;}
inline void retired(){const auto stamp=now();Guard g;if(saved.state==2 && currentOffer<saved.offer_count)saved.offers[currentOffer].retired=stamp;}
inline bool snapshot(Snapshot &out){Guard g;if(saved.state!=3 || parser.load())return false;out=saved;return true;}
inline std::string json(){
 // HTTP stack is small. The bounded snapshot and JSON allocation stay on heap
 // outside measurement; no live record is read without its publication lock.
 auto s=std::make_unique<Snapshot>();if(!snapshot(*s))return {};
 char b[400];std::string out="{\"clock\":\"P4 esp_timer microseconds, uint32 wrap\",\"frozen\":true,\"dropped\":"+std::to_string(s->dropped)+",\"invalid\":"+std::to_string(s->invalid)+",\"adjustments\":[";
 for(unsigned i=0;i<s->adjustment_count;++i){auto &r=s->adjusts[i];
  std::snprintf(b,sizeof(b),"%s{\"buffer\":%u,\"op\":%u,\"bytes\":%u,\"begin_us\":%u,\"end_us\":%u,\"wait_total_us\":%llu,\"wait_max_us\":%u,\"lock_calls\":%u}",i?",":"",r.buffer,r.op,r.bytes,r.begin,r.end,(unsigned long long)r.wait_total,r.wait_max,r.calls);out+=b;
 }
 out+="],\"offers\":[";
 for(unsigned i=0;i<s->offer_count;++i){auto &r=s->offers[i];
  std::snprintf(b,sizeof(b),"%s{\"sequence\":%u,\"bytes\":%u,\"reverse\":%u,\"seen_us\":%u,\"accepted_us\":%u,\"retired_us\":%u,\"attempts\":%u}",i?",":"",r.sequence,r.bytes,r.reverse,r.seen,r.accepted,r.retired,r.attempts);out+=b;
 }
 return out+"]}";
}
}
#endif
