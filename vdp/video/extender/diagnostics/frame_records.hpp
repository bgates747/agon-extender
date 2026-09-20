// Shared diagnostic recorder for classic ESP32 VDP and P4 EDP.
// Parser-owner only: no allocation, printing, or per-primitive instrumentation.
// Durations are unsigned microsecond differences; runs must be <2^32 us.
#pragma once
#include <stdint.h>
namespace agon_frame_records {
constexpr unsigned Capacity=240;
struct Record { uint32_t submitted_us{}, completed_us{}, drain_us{}; };
class Recorder {
 public:
  bool reset() { size_=0; active_=false; fault_=false; stopped_=false; return true; }
  bool begin(uint16_t id,uint32_t now) {
    if(fault_ || stopped_ || active_ || id!=size_ || size_==Capacity) return fail();
    start_=now; active_=true; return true;
  }
  bool end(uint16_t id,uint32_t submitted,uint32_t completed) {
    if(fault_ || stopped_ || !active_ || id!=size_) return fail();
    rows_[size_++]={submitted-start_,completed-start_,completed-submitted};
    active_=false;return true;
  }
  bool stop() { if(active_ || fault_)return fail();stopped_=true;return true; }
  const Record *get(unsigned id) const {return stopped_ && !fault_ && id<size_?&rows_[id]:nullptr;}
  unsigned size() const {return size_;}
  bool fault() const {return fault_;}
  bool fail() {fault_=true;active_=false;return false;}
 private:
  Record rows_[Capacity]{};
  unsigned size_{};uint32_t start_{};bool active_{},fault_{},stopped_{true};
};
}
