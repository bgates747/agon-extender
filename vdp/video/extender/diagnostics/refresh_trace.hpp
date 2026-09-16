#include "row_priority.hpp"
// QUAL-003/N04w diagnostic only; disabled in normal builds. Stock buffer WRITE
// to65535 still consumes/discards its bytes. Exact markers only arm observation.
// No per-frame UART, allocation, logging, scheduling or drawing changes.
#pragma once
#ifdef AGON_EXTENDER_REFRESH_TRACE
#include "lock_wake_trace.hpp"
#include "owner_trace.hpp"
#include <cstdint>
#include <cstdio>
#include <cstring>
#ifdef AGON_EXTENDER_OUTPUT_ISOLATION
#include "output_isolation.hpp"
#endif
#ifdef AGON_EXTENDER_NATIVE_WAIT_TRACE
#include "native_wait_trace.hpp"
#endif
#ifdef NP_TRACE_HOST
#include <cstdlib>
#include <mutex>
#else
#include <esp_heap_caps.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#endif
namespace agon_refresh_trace {
constexpr unsigned Capacity=4096;
struct Sample { uint32_t enqueue_us, complete_us; };
struct Recorder {
 Sample *samples{};
 uint8_t nonce[8]{};
 uint32_t submitted{}, completed{}, maximum_pending{};
 bool active{}, invalid{};
 bool begin(const uint8_t *id, Sample *storage) {
  if(active || !storage) return false;
  samples=storage; submitted=completed=maximum_pending=0; invalid=false;
  std::memcpy(nonce,id,8); active=true; return true;
 }
 void enqueue(uint32_t t) {
  if(!active)return;
  auto i=submitted++;
  if(i<Capacity)samples[i]={t,0}; else invalid=true;
  if(submitted-completed>maximum_pending)maximum_pending=submitted-completed;
 }
 void complete(uint32_t t) {
  if(!active)return;
  auto i=completed++;
  if(i>=submitted || i>=Capacity)invalid=true; else samples[i].complete_us=t;
 }
 bool stop(const uint8_t *id) {
  if(!active || std::memcmp(nonce,id,8))return false;
  active=false; if(submitted!=completed)invalid=true; return true;
 }
};
inline Recorder recorder;
#ifdef NP_TRACE_HOST
inline std::mutex mux;
struct Guard { Guard(){mux.lock();} ~Guard(){mux.unlock();} };
inline uint32_t now(){return 0;}
#else
inline portMUX_TYPE mux=portMUX_INITIALIZER_UNLOCKED;
struct Guard { Guard(){portENTER_CRITICAL(&mux);} ~Guard(){portEXIT_CRITICAL(&mux);} };
inline uint32_t now(){return uint32_t(esp_timer_get_time());}
#endif
inline void enqueue(){
#ifdef AGON_EXTENDER_NATIVE_WAIT_TRACE
 agon_native_wait::boundary(); // UART driver query stays outside trace critical section.
#endif
 Guard guard;recorder.enqueue(now());
#ifdef AGON_EXTENDER_OWNER_TRACE
 agon_owner_trace::refresh_sequence.store(recorder.submitted,std::memory_order_relaxed);
#endif
}
inline void complete(){Guard guard;recorder.complete(now());}
// Called solely by the parser, after all marker bytes have been consumed.
inline void marker(const uint8_t *data, unsigned size) {
 if(size!=16 || (std::memcmp(data,"NPTRACE1",8) && std::memcmp(data,"NPTRACE0",8)))return;
 if(data[7]=='1') {
  // Allocation is outside the observation window and explicitly PSRAM on P4.
  static Sample *storage=nullptr;
  if(!storage) {
#ifdef NP_TRACE_HOST
   storage=static_cast<Sample*>(std::calloc(Capacity,sizeof(Sample)));
#else
   storage=static_cast<Sample*>(heap_caps_calloc(Capacity,sizeof(Sample),MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
#endif
  }
#ifdef AGON_EXTENDER_NATIVE_WAIT_TRACE
  agon_native_wait::prepare(); // outside active observation, explicitly PSRAM
#endif
  bool began;{Guard guard;began=recorder.begin(data+8,storage);}
#ifdef AGON_EXTENDER_NATIVE_WAIT_TRACE
  if(began)agon_native_wait::arm();
#else
  (void)began;
#endif
#ifdef AGON_EXTENDER_OUTPUT_ISOLATION
  if(began)agon_output_isolation::begin(data+8);
#if defined(AGON_EXTENDER_ROW_PRIORITY) || defined(AGON_EXTENDER_SNAPSHOT_PRIORITY)
  if(began)agon_row_priority::begin(data+8);
#endif
#ifdef AGON_EXTENDER_OWNER_TRACE
  if(began)agon_owner_trace::begin(data+8);
#endif
#ifdef AGON_EXTENDER_LOCK_WAKE_TRACE
  if(began)agon_lock_wake::begin(data+8);
#endif
#endif
  return;
 }
 bool stopped;
 {Guard guard;stopped=recorder.stop(data+8);}
 if(!stopped)return;
#ifdef AGON_EXTENDER_NATIVE_WAIT_TRACE
 agon_native_wait::stop();
#endif
#ifdef AGON_EXTENDER_OUTPUT_ISOLATION
#ifdef AGON_EXTENDER_LOCK_WAKE_TRACE
 agon_lock_wake::active=false; // stop admission at the terminal marker
#endif
#ifdef AGON_EXTENDER_OWNER_TRACE
 agon_owner_trace::enabled=false;agon_owner_trace::recording=false;
#endif
 agon_output_isolation::stop(data+8);
#if defined(AGON_EXTENDER_ROW_PRIORITY) || defined(AGON_EXTENDER_SNAPSHOT_PRIORITY)
 agon_row_priority::stop(data+8);
#endif
#ifdef AGON_EXTENDER_OWNER_TRACE
 agon_owner_trace::stop(data+8);
#endif
#ifdef AGON_EXTENDER_LOCK_WAKE_TRACE
 agon_lock_wake::stop(data+8);
#endif
#endif
 // No further records admitted. Parser owns marker processing, so another
 // start cannot overlap this dump. USB output is strictly after terminal fence.
 std::printf("\nNPTRACE begin ");
 for(auto b:recorder.nonce)std::printf("%02x",unsigned(b));
 std::printf(" %lu %lu %lu %u\n",(unsigned long)recorder.submitted,
  (unsigned long)recorder.completed,(unsigned long)recorder.maximum_pending,unsigned(recorder.invalid));
 for(unsigned i=0;i<recorder.submitted && i<Capacity;++i)
  std::printf("NPTRACE row %u %lu %lu\n",i,(unsigned long)recorder.samples[i].enqueue_us,
   (unsigned long)recorder.samples[i].complete_us);
 std::printf("NPTRACE end ");for(auto b:recorder.nonce)std::printf("%02x",unsigned(b));
 std::printf("\n");
#ifdef AGON_EXTENDER_NATIVE_WAIT_TRACE
 agon_native_wait::dump(recorder.nonce);
#endif
}
}
#endif
