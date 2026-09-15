// QUAL-003 N04ae diagnostic only. Parser-owned counters; no per-byte probe.
// Native acquisition timing adds observer cost and is NOT parity evidence.
#pragma once
#ifdef AGON_EXTENDER_NATIVE_WAIT_TRACE
#include <atomic>
#include <cstdint>
#include <cstdio>
#ifdef NP_TRACE_HOST
#include <chrono>
#include <cstdlib>
#else
#include <esp_heap_caps.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <driver/uart.h>
#endif
namespace agon_native_wait {
constexpr unsigned Capacity=4096;
struct Sample { uint32_t wait_us, maximum_us, calls, rx_bytes; };
inline Sample *samples{};
inline uint32_t total{}, maximum{}, calls{}, count{};
inline bool invalid{};
inline std::atomic<void*> parser{};
inline void *currentTask() {
#ifdef NP_TRACE_HOST
 static thread_local int identity;return &identity;
#else
 return xTaskGetCurrentTaskHandle();
#endif
}
inline bool observing(){return parser.load(std::memory_order_relaxed)==currentTask();}
inline uint32_t now(){
#ifdef NP_TRACE_HOST
 return uint32_t(std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());
#else
 return uint32_t(esp_timer_get_time());
#endif
}
inline void prepare(){
 if(samples)return;
#ifdef NP_TRACE_HOST
 samples=static_cast<Sample*>(std::calloc(Capacity,sizeof(Sample)));
#else
 samples=static_cast<Sample*>(heap_caps_calloc(Capacity,sizeof(Sample),MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
#endif
}
inline void arm(){
 total=maximum=calls=count=0;invalid=!samples;
 if(samples)parser.store(currentTask(),std::memory_order_release);
}
inline void acquired(uint32_t elapsed){
 // Only the identified parser calls this; no cross-task aggregate lock needed.
 total+=elapsed;if(elapsed>maximum)maximum=elapsed;++calls;
}
inline void boundary(){
 if(!observing())return;
 size_t buffered=0;
#ifndef NP_TRACE_HOST
 if(uart_get_buffered_data_len(UART_NUM_1,&buffered)!=ESP_OK)invalid=true;
#endif
 if(count<Capacity)samples[count]={total,maximum,calls,uint32_t(buffered)};
 else invalid=true;
 ++count;total=maximum=calls=0;
}
inline void stop(){parser.store(nullptr,std::memory_order_release);}
inline void dump(const uint8_t *nonce){
 std::printf("NPNATIVE begin ");for(unsigned i=0;i<8;++i)std::printf("%02x",unsigned(nonce[i]));
 std::printf(" %u %u\n",unsigned(count),unsigned(invalid));
 for(unsigned i=0;i<count && i<Capacity;++i){auto &s=samples[i];
  std::printf("NPNATIVE row %u %u %u %u %u\n",i,s.wait_us,s.maximum_us,s.calls,s.rx_bytes);}
 std::printf("NPNATIVE end ");for(unsigned i=0;i<8;++i)std::printf("%02x",unsigned(nonce[i]));std::printf("\n");
}
}
#endif
