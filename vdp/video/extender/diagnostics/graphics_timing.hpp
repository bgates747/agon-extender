// QUAL-003 temporary measurement only. No scheduling or drawing changes.
// Counters reside in internal static RAM. ISR paths never allocate or emit UART.
// Both targets use this exact recorder and the same stock operation boundaries.
#pragma once
#include <stdint.h>
#ifdef AGON_GRAPHICS_TIMING
#include "frame_records.hpp"
#ifdef USERSPACE
#include <mutex>
#include <chrono>
#ifndef IRAM_ATTR
#define IRAM_ATTR
#endif
#else
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#endif
namespace agon_graphics_timing {
enum Metric : unsigned { Primitive, SoftwareSprites, ScanlineDecoration, MetricCount };
struct Count { uint32_t calls{}, us{}, maximum{}, crossing{}; };
struct Result { Count count[MetricCount]; uint32_t elapsed{}, drain{}, overhead{}; };
#ifdef USERSPACE
inline std::recursive_mutex mux;
inline void enter() { mux.lock(); }
inline void leave() { mux.unlock(); }
#else
inline portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
inline void IRAM_ATTR enter() { portENTER_CRITICAL_ISR(&mux); }
inline void IRAM_ATTR leave() { portEXIT_CRITICAL_ISR(&mux); }
#endif
inline Count counts[MetricCount];
inline uint32_t generation{}, start_us{};
inline unsigned active[MetricCount]{};
inline bool enabled{};
inline uint16_t fence_issued{}, fence_reached{}, fence_done{};
inline void IRAM_ATTR reached(uint16_t value) {
  enter(); fence_reached = value; leave();
}
class FinishSprites {
 public:
  __attribute__((always_inline)) ~FinishSprites() {
    enter(); fence_done = fence_reached; leave();
  }
};
inline uint16_t issue() {
  enter(); if (++fence_issued == 0) ++fence_issued;
  uint16_t t=fence_issued; leave(); return t;
}
inline bool complete(uint16_t t) {
  enter(); bool done=fence_done==t; leave(); return done;
}
inline uint32_t IRAM_ATTR now() {
#ifdef USERSPACE
  return uint32_t(std::chrono::duration_cast<std::chrono::microseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count());
#else
  return uint32_t(esp_timer_get_time());
#endif
}
class Scope {
  Metric metric_; uint32_t generation_{}, start_{}; bool admitted_{};
 public:
  explicit __attribute__((always_inline)) Scope(Metric metric) : metric_(metric) {
    enter();
    admitted_ = enabled;
    if (admitted_) { generation_ = generation; ++active[metric_]; }
    leave();
    if (admitted_) start_ = now();
  }
  __attribute__((always_inline)) ~Scope() {
    if (!admitted_) return;
    uint32_t elapsed = now() - start_;
    enter();
    --active[metric_];
    if (enabled && generation_ == generation) {
      auto &c = counts[metric_]; ++c.calls; c.us += elapsed;
      if (elapsed > c.maximum) c.maximum = elapsed;
    }
    leave();
  }
};
inline void begin(bool instrument) {
  enter();
  enabled = false; ++generation;
  for (unsigned i=0; i<MetricCount; ++i) {
    counts[i] = {}; counts[i].crossing = active[i];
  }
  start_us = now(); enabled = instrument;
  leave();
}
inline Result finish(uint32_t drain_us) {
  Result r;
  enter();
  enabled = false;
  r.elapsed = now()-start_us; r.drain = drain_us;
  for (unsigned i=0; i<MetricCount; ++i) {
    r.count[i] = counts[i]; r.count[i].crossing += active[i];
  }
  leave();
  // Empty timer-pair cost, after measurement. Not subtracted from observations.
  uint32_t t = now(); for (unsigned i=0; i<256; ++i) { (void)now(); (void)now(); }
  r.overhead = now()-t;
  return r;
}
} // namespace
#define AGON_GRAPHICS_SCOPE(metric) agon_graphics_timing::Scope qual_scope(agon_graphics_timing::metric)
#else
#define AGON_GRAPHICS_SCOPE(metric)
#endif
