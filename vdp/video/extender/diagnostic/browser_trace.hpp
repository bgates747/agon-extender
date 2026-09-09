// Temporary REMOTE-001 timing instrumentation. No wire-format or timeout changes.
// Task context only; fixed-capacity ring, no hot-path allocation or serial I/O.
#pragma once
#include <cstdint>
#if defined(AGON_EXTENDER_BROWSER_TYPING)
#include <array>
#include <mutex>
#include <esp_timer.h>
#include <esp_heap_caps.h>
namespace agon::extender::diagnostic {
struct TraceRecord { int64_t us; const char *event; uint64_t id; int64_t a,b,c; };
class BrowserTrace {
 public:
  static constexpr unsigned capacity=8192;
  void begin() {
    std::lock_guard<std::mutex> guard(mutex_);
    if (!records_) records_=static_cast<TraceRecord *>(heap_caps_malloc(
        sizeof(TraceRecord)*capacity,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
    enabled_=records_!=nullptr;
  }
  void add(const char *event,uint64_t id=0,int64_t a=0,int64_t b=0,int64_t c=0) {
    const auto before=esp_timer_get_time();
    std::lock_guard<std::mutex> guard(mutex_);
    if (!enabled_ || frozen_ || !records_) return;
    records_[total_%capacity]={esp_timer_get_time(),event,id,a,b,c}; ++total_;
    const auto cost=esp_timer_get_time()-before;
    cost_us_+=cost; if(cost>max_cost_us_) max_cost_us_=cost;
  }
  // Export freezes recording, not application traffic. Only a new enable/disable
  // request clears records. Never request export in the measured hot path.
  uint64_t freeze() { std::lock_guard<std::mutex> g(mutex_); frozen_=true; return total_; }
  bool read(uint64_t index,TraceRecord &out) {
    std::lock_guard<std::mutex> g(mutex_);
    if(!records_ || !frozen_ || index>=total_ || total_-index>capacity) return false;
    out=records_[index%capacity]; return true;
  }
  void configure(bool on) {
    std::lock_guard<std::mutex> g(mutex_);
    total_=0; cost_us_=max_cost_us_=0; frozen_=false; enabled_=on&&records_;
  }
  bool available() const { return records_!=nullptr; }
  int64_t cost_us() const { return cost_us_; } // read only after freeze
  int64_t max_cost_us() const { return max_cost_us_; }
 private:
  std::mutex mutex_;
  TraceRecord *records_{};
  uint64_t total_{};
  int64_t cost_us_{},max_cost_us_{};
  bool enabled_{},frozen_{};
};
inline BrowserTrace &browserTrace() { static BrowserTrace t; return t; }
inline void trace(const char *e,uint64_t id=0,int64_t a=0,int64_t b=0,int64_t c=0) {
  browserTrace().add(e,id,a,b,c);
}
}
#else
namespace agon::extender::diagnostic {
inline void trace(const char *,uint64_t=0,int64_t=0,int64_t=0,int64_t=0) {}
}
#endif
