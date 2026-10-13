// RESEARCH-007 NP02/NP04: diagnostic-only queued-render fence observations.
// One shared PSRAM pool, allocated before a window opens, never per update.
// Cumulative samples are not elapsed fences, CPU cycles or HDMI composition.
#pragma once
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <string>
#include "esp_heap_caps.h"

namespace agon_bench {
constexpr unsigned FenceSampleCapacity = 4096;
constexpr unsigned FenceWindowCapacity = 16;
enum FenceError : std::uint32_t {
  FenceAllocation = 1, FenceExhausted = 2, FenceCounterOverflow = 4,
  FenceBoundary = 8, FenceRequestInvariant = 16, FenceMissingBoundary = 32,
  FenceIneligible = 64,
};
struct FenceWindow {
  std::atomic<std::uint32_t> offset{UINT32_MAX}, count{}, pending{}, errors{};
  std::atomic<bool> enabled{};
  void reset(bool enable = false) {
    offset=UINT32_MAX; count=0; pending=0; errors=0; enabled=enable;
  }
};
static_assert(sizeof(FenceWindow)*FenceWindowCapacity <= 1024,
              "Keep the bounded fence descriptors below one KiB");
class FenceSamples {
  std::uint32_t *pool_{};
  std::atomic<unsigned> used_{};
 public:
  // Distinguishes slot reuse after reset; active's legacy slot token alone can
  // otherwise repeat when a request is preempted before claiming outstanding.
  std::atomic<std::uint32_t> generation{};
  FenceWindow windows[FenceWindowCapacity];
  // This setup method is called only before active.store(open). The injectable
  // allocator permits an allocation-failure host check, not a runtime fallback.
  bool prepare(decltype(&heap_caps_malloc) allocate = heap_caps_malloc) {
    if (!pool_) pool_=static_cast<std::uint32_t *>(
        allocate(FenceSampleCapacity*sizeof(std::uint32_t),MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
    return pool_!=nullptr;
  }
  void reset() {
    // Existing B009 reset has first closed active and joined outstanding owners.
    generation.fetch_add(1,std::memory_order_release);
    used_=0; for(auto &w:windows)w.reset();
  }
  void open(unsigned slot,bool enabled) {
    auto &w=windows[slot]; w.reset(enabled);
    if(enabled&&!prepare())w.errors.fetch_or(FenceAllocation);
  }
  void sample(unsigned slot,std::uint32_t value) {
    auto &w=windows[slot];
    if(!pool_) {w.errors.fetch_or(FenceAllocation);return;}
    const auto count=w.count.load(std::memory_order_relaxed);
    const auto offset=w.offset.load(std::memory_order_relaxed);
    if(count&&value<pool_[offset+count-1])w.errors.fetch_or(FenceCounterOverflow);
    const auto next=used_.load(std::memory_order_relaxed);
    if(next>=FenceSampleCapacity) {w.errors.fetch_or(FenceExhausted);return;}
    if(count&&offset+count!=next) {w.errors.fetch_or(FenceBoundary);return;}
    if(!count)w.offset.store(next,std::memory_order_relaxed);
    pool_[next]=value;
    used_.store(next+1,std::memory_order_relaxed);
    // Release publishes the plain uint32 entry. Entries never change before
    // reset, which holds the existing records mutex and waits for requests.
    w.count.store(count+1,std::memory_order_release);
  }
  unsigned used() const {return used_.load(std::memory_order_relaxed);}
  std::uint32_t at(unsigned slot,unsigned index) const {
    return pool_[windows[slot].offset.load()+index];
  }
  void appendJson(std::string &out,unsigned slot,bool closed,bool render_valid,bool quiescent) const {
    auto const &w=windows[slot];
    const auto pending=w.pending.load(std::memory_order_acquire);
    const auto count=w.count.load(std::memory_order_acquire);
    const auto errors=w.errors.load(std::memory_order_relaxed);
    const bool complete=closed&&quiescent&&!pending&&w.enabled.load()&&!errors&&render_valid&&count;
    char b[256];
    std::snprintf(b,sizeof(b),"{\"schema\":1,\"capacity\":%u,\"count\":%u,\"pending_requests\":%u,\"errors\":%u,\"enabled\":%s,\"samples_complete\":%s,\"fixture_mapping_required\":true,\"cumulative_render_us\":",
                  FenceSampleCapacity,count,pending,errors,w.enabled.load()?"true":"false",complete?"true":"false");
    // Append into the existing response, rather than constructing a second
    // potentially45 KiB raw-array string alongside its destination.
    out+=b;
    // Closed-only exposure prevents a host from treating partial active samples
    // as a finished update distribution. Existing outstanding ownership also
    // covers a request preempted before publishing its per-window pending bit,
    // and queued render batches which can still report a late boundary drop.
    // Independent output-phase drops remain supplemental evidence only.
    if(!closed||!quiescent||pending){out+="null}";return;}
    out+="[";
    for(unsigned i=0;i<count;++i) {
      if(i)out+=",";
      std::snprintf(b,sizeof(b),"%u",at(slot,i));out+=b;
    }
    out+="]}";
  }
};
inline FenceSamples fence_samples;
} // namespace agon_bench
