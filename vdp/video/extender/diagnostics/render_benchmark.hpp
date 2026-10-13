// BENCH-009 r01, explicit diagnostic builds only. Wall intervals, not CPU time.
// Windows use discarded buffer65535; ordinary VDP behavior has no extra reply.
#pragma once
#if defined(AGON_EXTENDER_RENDER_BENCHMARK)
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <mutex>
#include <string>
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "fenced_render_samples.hpp"
namespace agon_bench {
enum Phase {Drain,RowWait,RowCompose,Expand,Cache,Conversion,PhaseCount};
struct Counter {std::atomic<std::uint32_t> calls{},us{},max{},drops{};};
// RESEARCH-007: bounded worker-execution sidecar, not another phase array.
// Keeping this separate avoids adding tens of KiB to the 512 legacy windows.
// These counters cover queued worker AND foreground processPrimitives drawing.
// Pixel-query fences use the foreground loop even in single-buffer modes; a
// worker-only tally therefore misses most fenced rendering. Immediate drawing
// in double-buffered modes and rolling hardware-sprite composition are excluded.
constexpr unsigned RenderWindowCapacity=16;
enum class RenderKind : unsigned { Scroll, Bitmap, RefreshSprites, Other, FinalSprites, Count };
struct RenderValue {std::uint32_t calls{},us{},max{};};
struct RenderTally {
  RenderValue kinds[unsigned(RenderKind::Count)];
  std::uint32_t native_wait_us{},rendering_us{},elapsed_us{},primitive_calls{},primitive_max_us{};
};
struct RenderCounters {
  Counter kinds[unsigned(RenderKind::Count)];
  std::atomic<std::uint32_t> drains{},empty_drains{},refused_drains{},primitive_calls{},
      native_wait_us{},rendering_us{},elapsed_max_us{},primitive_max_us{},boundary_drops{},
      foreground_drains{},foreground_primitive_calls{};
  void reset() {
    for(auto &c:kinds){c.calls=0;c.us=0;c.max=0;c.drops=0;}
    drains=0;empty_drains=0;refused_drains=0;primitive_calls=0;
    native_wait_us=0;rendering_us=0;elapsed_max_us=0;primitive_max_us=0;boundary_drops=0;
    foreground_drains=0;foreground_primitive_calls=0;
  }
};
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
inline RenderCounters render_windows[RenderWindowCapacity];
inline std::atomic<bool> render_overflow{};
// Cache pilot sidecar: preserve the six legacy phases and their array indices.
// Only actual helper pre-C2M calls are timed; driver input/output maintenance,
// DMA wait and final draw_bitmap cache handoff remain in their existing scopes.
inline Counter indexed_pre_c2m[RenderWindowCapacity];
static_assert(sizeof(indexed_pre_c2m)==256,"Keep the cache pilot counters bounded");
inline std::atomic<bool> indexed_pre_c2m_overflow{};
inline void renderMaximum(std::atomic<std::uint32_t> &target,std::uint32_t value) {
  auto old=target.load(std::memory_order_relaxed);
  while(old<value&&!target.compare_exchange_weak(old,value,std::memory_order_relaxed)){}
}
// One local tally per drain: no per-primitive atomics or dynamic allocation.
// The diagnostic outer recursive guard surrounds the same single operation as
// its stock inner guard; it never locks an entire queue drain. Wait and execution
// are measured separately. Execution is elapsed wall time including nested
// helper guards/preemption, not exclusive CPU cycles. The final showSprites
// cost is included even for empty drains; normalize by workload updates, not
// drain calls, because scheduling can change batching.
class RenderBatch {
  std::uint32_t token_{};
  std::int64_t start_{};
  RenderTally tally_{};
 public:
  RenderBatch() {
    token_=active.load(std::memory_order_acquire);
    if(token_) {
      outstanding.fetch_add(1);
      if(active.load()!=token_ || !(windows[token_-1].flags&1)) {
        outstanding.fetch_sub(1);token_=0;
      } else if(token_>RenderWindowCapacity) {
        render_overflow.store(true);outstanding.fetch_sub(1);token_=0;
      }
    }
    if(token_)start_=esp_timer_get_time();
  }
  bool enabled() const {return token_!=0;}
  void operation(RenderKind kind,std::int64_t before,std::int64_t acquired,std::int64_t finished) {
    auto &c=tally_.kinds[unsigned(kind)];
    const auto duration=std::uint32_t(finished-acquired);
    ++c.calls;c.us+=duration;if(duration>c.max)c.max=duration;
    tally_.native_wait_us+=std::uint32_t(acquired-before);tally_.rendering_us+=duration;
    if(kind!=RenderKind::FinalSprites) {
      ++tally_.primitive_calls;
      if(duration>tally_.primitive_max_us)tally_.primitive_max_us=duration;
    }
  }
  void finish(std::size_t primitive_count,bool refused=false,bool foreground=false) {
    if(!token_)return;
    tally_.elapsed_us=std::uint32_t(esp_timer_get_time()-start_);
    auto &r=render_windows[token_-1];
    if(active.load(std::memory_order_acquire)!=token_)r.boundary_drops.fetch_add(1);
    else {
      if(refused)r.refused_drains.fetch_add(1);
      else {r.drains.fetch_add(1);if(!primitive_count)r.empty_drains.fetch_add(1);}
      r.primitive_calls.fetch_add(tally_.primitive_calls);
      if(foreground) {
        r.foreground_drains.fetch_add(1);
        r.foreground_primitive_calls.fetch_add(tally_.primitive_calls);
      }
      r.native_wait_us.fetch_add(tally_.native_wait_us);r.rendering_us.fetch_add(tally_.rendering_us);
      renderMaximum(r.elapsed_max_us,tally_.elapsed_us);renderMaximum(r.primitive_max_us,tally_.primitive_max_us);
      for(unsigned i=0;i<unsigned(RenderKind::Count);++i) {
        r.kinds[i].calls.fetch_add(tally_.kinds[i].calls);r.kinds[i].us.fetch_add(tally_.kinds[i].us);
        renderMaximum(r.kinds[i].max,tally_.kinds[i].max);
      }
    }
    outstanding.fetch_sub(1);token_=0;
  }
  ~RenderBatch(){if(token_)finish(tally_.primitive_calls);}
};
class RenderFenceRequest;
inline std::atomic<TaskHandle_t> render_fence_owner{};
inline RenderFenceRequest *render_fence_request{};
// A single parser task owns a scoped pixel-query request. Other foreground
// flushes cannot dereference it: first compare task ownership, then access the
// pointer only on that same task. Destruction clears ownership before releasing
// outstanding; B009 reset cannot recycle a descriptor or pool under a request.
// No new mutex, worker join, reply byte or per-primitive atomic is introduced.
class RenderFenceRequest {
  std::uint32_t token_{};
  std::uint32_t generation_{};
  bool captured_{};
  unsigned blocked_{};
  RenderFenceRequest *parent_{};
 public:
  explicit RenderFenceRequest(bool single_buffered) {
    if(!single_buffered)return;
    generation_=fence_samples.generation.load(std::memory_order_acquire);
    token_=active.load(std::memory_order_acquire);
    if(!token_||token_>FenceWindowCapacity){token_=0;return;}
    outstanding.fetch_add(1);
    if(fence_samples.generation.load(std::memory_order_acquire)!=generation_||
       active.load()!=token_||!fence_samples.windows[token_-1].enabled.load()) {
      outstanding.fetch_sub(1);token_=0;return;
    }
    auto &w=fence_samples.windows[token_-1];w.pending.fetch_add(1);
    TaskHandle_t empty{};
    const auto task=xTaskGetCurrentTaskHandle();
    if(!task||!render_fence_owner.compare_exchange_strong(empty,task)) {
      w.errors.fetch_or(FenceRequestInvariant);
      if(task&&empty==task&&render_fence_request) {
        parent_=render_fence_request;++parent_->blocked_;
      }
      w.pending.fetch_sub(1);outstanding.fetch_sub(1);token_=0;return;
    }
    render_fence_request=this;
  }
  RenderFenceRequest(RenderFenceRequest const &)=delete;
  RenderFenceRequest &operator=(RenderFenceRequest const &)=delete;
  void capture(bool single_buffered) {
    if(blocked_)return; // A nested failed request must not consume its parent.
    auto &w=fence_samples.windows[token_-1];
    if(captured_){w.errors.fetch_or(FenceRequestInvariant);return;}
    captured_=true;
    if(fence_samples.generation.load(std::memory_order_acquire)!=generation_||
       active.load(std::memory_order_acquire)!=token_) {w.errors.fetch_or(FenceBoundary);return;}
    if(!single_buffered) {w.errors.fetch_or(FenceIneligible);return;}
    if(esp_timer_get_time()-windows[token_-1].start>UINT32_MAX)w.errors.fetch_or(FenceCounterOverflow);
    fence_samples.sample(token_-1,render_windows[token_-1].rendering_us.load());
  }
  ~RenderFenceRequest() {
    if(parent_){--parent_->blocked_;return;}
    if(!token_)return;
    auto &w=fence_samples.windows[token_-1];
    if(!captured_)w.errors.fetch_or(active.load()==token_?FenceMissingBoundary:FenceBoundary);
    render_fence_request=nullptr;
    render_fence_owner.store(nullptr,std::memory_order_release);
    w.pending.fetch_sub(1,std::memory_order_release);
    outstanding.fetch_sub(1);
  }
};
inline void renderFenceAtQuiescentFlush(bool single_buffered) {
  const auto task=xTaskGetCurrentTaskHandle();
  if(!task||render_fence_owner.load(std::memory_order_acquire)!=task)return;
  if(render_fence_request)render_fence_request->capture(single_buffered);
}
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
struct IndexedPreC2MScope {
  std::uint32_t token{};std::int64_t start{};
  IndexedPreC2MScope() {
    token=active.load(std::memory_order_acquire);
    if(token) {
      outstanding.fetch_add(1);
      if(active.load()!=token || !(windows[token-1].flags&1)) {
        outstanding.fetch_sub(1);token=0;
      } else if(token>RenderWindowCapacity) {
        indexed_pre_c2m_overflow.store(true);outstanding.fetch_sub(1);token=0;
      }
    }
    if(token)start=esp_timer_get_time();
  }
  ~IndexedPreC2MScope() {
    if(!token)return;
    auto &c=indexed_pre_c2m[token-1];
    if(active.load(std::memory_order_acquire)!=token)c.drops.fetch_add(1);
    else {
      auto us=std::uint32_t(esp_timer_get_time()-start);
      c.us.fetch_add(us);c.calls.fetch_add(1);renderMaximum(c.max,us);
    }
    outstanding.fetch_sub(1);
  }
};
inline void marker(std::uint8_t const *p,std::size_t n) {
  if(n!=12||p[0]!='B'||p[1]!='0'||p[2]!='0'||p[3]!='9'||p[4]!=1)return;
  std::lock_guard<std::mutex> lock(records);
  if(p[5]==0) {
    active.store(0,std::memory_order_release);
    while(outstanding.load())vTaskDelay(1);
    used=0;overflow=false;render_overflow=false;indexed_pre_c2m_overflow=false;
    fence_samples.reset();
  } else if(p[5]==1) {
    if(active.load()||used==512){overflow=true;return;}
    auto &w=windows[used];
    if(used<RenderWindowCapacity)render_windows[used].reset();
    if(used<RenderWindowCapacity) {
      auto &c=indexed_pre_c2m[used];c.calls=0;c.us=0;c.max=0;c.drops=0;
    }
    for(auto &c:w.phases){c.calls.store(0);c.us.store(0);c.max.store(0);c.drops.store(0);}
    w.scanouts.store(0);w.updates.store(0);w.marker_valid.store(0);w.marker_invalid.store(0);w.last_frame.store(UINT32_MAX);w.marker_transitions.store(0);w.marker_repeats.store(0);
    w.id=p[6]|p[7]<<8;w.flags=p[8];w.tag=p[9]|p[10]<<8|p[11]<<16;
    w.end=0;
    if(used<FenceWindowCapacity) {
      // Allocation is outside active/measured work. Unfenced game case9 keeps
      // its original aggregate-only scope, not an invented per-update fence.
      const bool supported=w.id==3||w.id==7||w.id==8||w.id==39||w.id==41||w.id==54;
      fence_samples.open(used,(w.flags&1)&&supported);
    }
    w.start=esp_timer_get_time();
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
  char b[512];std::string out="{\"schema\":1,\"output\":\"";
#if defined(AGON_EXTENDER_BENCH_CONVERT_OFF)
  out+="convert-off";
#elif defined(AGON_EXTENDER_BENCH_OFF)
  out+="off";
#elif defined(AGON_EXTENDER_BENCH_HOLD)
  out+="hold";
#else
  out+="normal";
#endif
  std::snprintf(b,sizeof(b),"\",\"open\":%u,\"overflow\":%s,\"render_overflow\":%s,\"render_capacity\":%u,\"render_schema\":2,\"render_scope\":\"queued worker and foreground flush execution wall; excludes native wait, parser, UART, pacing, immediate double-buffer drawing and scanout composition; includes nested guards and preemption\",\"windows\":[",active.load(),overflow?"true":"false",render_overflow.load()?"true":"false",RenderWindowCapacity);out+=b;
  for(unsigned i=0;i<used;++i){auto &w=windows[i];if(i)out+=",";
    std::snprintf(b,sizeof(b),"{\"tag\":%u,\"id\":%u,\"flags\":%u,\"start_us\":%lld,\"end_us\":%lld,\"scanouts\":%u,\"updates\":%u,\"marker_valid\":%u,\"marker_invalid\":%u,\"last_frame\":%u,\"marker_transitions\":%u,\"marker_repeats\":%u,\"phases\":[",w.tag,w.id,w.flags,(long long)w.start,(long long)w.end,w.scanouts.load(),w.updates.load(),w.marker_valid.load(),w.marker_invalid.load(),w.last_frame.load(),w.marker_transitions.load(),w.marker_repeats.load());out+=b;
    for(unsigned p=0;p<PhaseCount;++p){auto &c=w.phases[p];if(p)out+=",";
      std::snprintf(b,sizeof(b),"{\"calls\":%u,\"us\":%u,\"max_us\":%u,\"boundary_drops\":%u}",c.calls.load(),c.us.load(),c.max.load(),c.drops.load());out+=b;}
    out+="],\"render\":";
    if(i>=RenderWindowCapacity)out+="null";
    else {
      auto &r=render_windows[i];
      std::snprintf(b,sizeof(b),"{\"drains\":%u,\"empty_drains\":%u,\"refused_drains\":%u,\"primitive_calls\":%u,\"native_wait_us\":%u,\"rendering_us\":%u,\"elapsed_max_us\":%u,\"primitive_max_us\":%u,\"boundary_drops\":%u,\"foreground_drains\":%u,\"foreground_primitive_calls\":%u,\"kinds\":{",r.drains.load(),r.empty_drains.load(),r.refused_drains.load(),r.primitive_calls.load(),r.native_wait_us.load(),r.rendering_us.load(),r.elapsed_max_us.load(),r.primitive_max_us.load(),r.boundary_drops.load(),r.foreground_drains.load(),r.foreground_primitive_calls.load());out+=b;
      constexpr const char *names[]={"scroll","bitmap","refresh_sprites","other","final_sprites"};
      for(unsigned k=0;k<unsigned(RenderKind::Count);++k) {
        if(k)out+=",";auto &c=r.kinds[k];
        std::snprintf(b,sizeof(b),"\"%s\":{\"calls\":%u,\"us\":%u,\"max_us\":%u}",names[k],c.calls.load(),c.us.load(),c.max.load());out+=b;
      }
      out+="}}";
    }
    out+=",\"indexed_pre_c2m\":";
    if(i>=RenderWindowCapacity)out+="null";
    else {
      auto &c=indexed_pre_c2m[i];
      std::snprintf(b,sizeof(b),"{\"calls\":%u,\"us\":%u,\"max_us\":%u,\"boundary_drops\":%u}",c.calls.load(),c.us.load(),c.max.load(),c.drops.load());out+=b;
    }
    out+=",\"render_fences\":";
    if(i>=FenceWindowCapacity)out+="null";
    else {
      // Acquire quiescence before reading final render drops: reading it
      // afterward could miss a batch which drops then retires in between.
      // Legacy output phases have independent counters. A PPA/cache/row scope
      // crossing window close makes that phase partial, not this render total.
      const bool quiescent=outstanding.load(std::memory_order_acquire)==0;
      const bool boundary_valid=!render_overflow.load()&&render_windows[i].boundary_drops.load()==0;
      fence_samples.appendJson(out,i,w.end!=0,boundary_valid,quiescent);
    }
    out+="}";
  }
  out+="]";
  out+=",\"indexed_pre_c2m_overflow\":";
  out+=indexed_pre_c2m_overflow.load()?"true":"false";
  return out+"}";
}
}
#endif
