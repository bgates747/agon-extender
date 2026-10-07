// BENCH-009 r01, explicit diagnostic builds only. Wall intervals, not CPU time.
// Windows use discarded buffer65535; ordinary VDP behavior has no extra reply.
#pragma once
#if defined(AGON_EXTENDER_RENDER_BENCHMARK)
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <mutex>
#include <string>
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
namespace agon_bench {
enum Phase {Drain,RowWait,RowCompose,Expand,Cache,Conversion,PhaseCount};
struct Counter {std::atomic<std::uint32_t> calls{},us{},max{},drops{};};
struct Window {
  Counter phases[PhaseCount];
  std::atomic<std::uint32_t> scanouts{},updates{},marker_valid{},marker_invalid{},last_frame{},marker_transitions{},marker_repeats{};
  std::uint32_t tag{},id{},flags{};
  std::int64_t start{},end{};
};
inline Window windows[512];
inline std::atomic<std::uint32_t> active{},outstanding{};
inline unsigned used{};
inline bool overflow{};
inline std::mutex records;
struct Scope {
  std::uint32_t token{}; std::int64_t start{}; Phase phase;
  explicit Scope(Phase p):phase(p) {
    token=active.load(std::memory_order_acquire);
    if(token) {outstanding.fetch_add(1); if(active.load()!=token) {outstanding.fetch_sub(1); token=0;}}
    if(token && (windows[token-1].flags&1)) start=esp_timer_get_time();
  }
  void finish() {
    if(!token)return;
    auto &c=windows[token-1].phases[phase];
    if(start) {
      if(active.load(std::memory_order_acquire)!=token) c.drops.fetch_add(1);
      else {
        auto us=static_cast<std::uint32_t>(esp_timer_get_time()-start);
        c.us.fetch_add(us); c.calls.fetch_add(1);
        auto m=c.max.load();while(m<us&&!c.max.compare_exchange_weak(m,us)){}
      }
    }
    outstanding.fetch_sub(1);token=0;
  }
  ~Scope(){finish();}
};
inline void marker(std::uint8_t const *p,std::size_t n) {
  if(n!=12||p[0]!='B'||p[1]!='0'||p[2]!='0'||p[3]!='9'||p[4]!=1)return;
  std::lock_guard<std::mutex> lock(records);
  if(p[5]==0) {
    active.store(0,std::memory_order_release);
    while(outstanding.load())vTaskDelay(1);
    used=0;overflow=false;
  } else if(p[5]==1) {
    if(active.load()||used==512){overflow=true;return;}
    auto &w=windows[used];
    for(auto &c:w.phases){c.calls.store(0);c.us.store(0);c.max.store(0);c.drops.store(0);}
    w.scanouts.store(0);w.updates.store(0);w.marker_valid.store(0);w.marker_invalid.store(0);w.last_frame.store(UINT32_MAX);w.marker_transitions.store(0);w.marker_repeats.store(0);
    w.id=p[6]|p[7]<<8;w.flags=p[8];w.tag=p[9]|p[10]<<8|p[11]<<16;
    w.end=0;w.start=esp_timer_get_time();
    active.store(++used,std::memory_order_release);
  } else if(p[5]==2) {
    auto t=active.exchange(0,std::memory_order_acq_rel);
    if(!t||windows[t-1].id!=(unsigned)(p[6]|p[7]<<8)||windows[t-1].tag!=(unsigned)(p[9]|p[10]<<8|p[11]<<16)){overflow=true;return;}
    windows[t-1].end=esp_timer_get_time();
  }
}
inline void scanout() {auto t=active.load(std::memory_order_relaxed);if(t)windows[t-1].scanouts.fetch_add(1,std::memory_order_relaxed);}
inline void update(std::uint32_t token,int frame) {
  if(!token||active.load()!=token)return;
  auto &w=windows[token-1];w.updates.fetch_add(1);
  if(frame>=0){w.marker_valid.fetch_add(1);auto previous=w.last_frame.exchange(frame);
    if(previous!=unsigned(frame))w.marker_transitions.fetch_add(1);else w.marker_repeats.fetch_add(1);}else w.marker_invalid.fetch_add(1);
}
inline std::string json() {
  std::lock_guard<std::mutex> lock(records);
  char b[400];std::string out="{\"schema\":1,\"output\":\"";
#if defined(AGON_EXTENDER_BENCH_CONVERT_OFF)
  out+="convert-off";
#elif defined(AGON_EXTENDER_BENCH_OFF)
  out+="off";
#elif defined(AGON_EXTENDER_BENCH_HOLD)
  out+="hold";
#else
  out+="normal";
#endif
  std::snprintf(b,sizeof(b),"\",\"open\":%u,\"overflow\":%s,\"windows\":[",active.load(),overflow?"true":"false");out+=b;
  for(unsigned i=0;i<used;++i){auto &w=windows[i];if(i)out+=",";
    std::snprintf(b,sizeof(b),"{\"tag\":%u,\"id\":%u,\"flags\":%u,\"start_us\":%lld,\"end_us\":%lld,\"scanouts\":%u,\"updates\":%u,\"marker_valid\":%u,\"marker_invalid\":%u,\"last_frame\":%u,\"marker_transitions\":%u,\"marker_repeats\":%u,\"phases\":[",w.tag,w.id,w.flags,(long long)w.start,(long long)w.end,w.scanouts.load(),w.updates.load(),w.marker_valid.load(),w.marker_invalid.load(),w.last_frame.load(),w.marker_transitions.load(),w.marker_repeats.load());out+=b;
    for(unsigned p=0;p<PhaseCount;++p){auto &c=w.phases[p];if(p)out+=",";
      std::snprintf(b,sizeof(b),"{\"calls\":%u,\"us\":%u,\"max_us\":%u,\"boundary_drops\":%u}",c.calls.load(),c.us.load(),c.max.load(),c.drops.load());out+=b;}
    out+="]}";
  }
  return out+"]}";
}
}
#endif
