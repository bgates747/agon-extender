// P01e diagnostic only. No transport/allocation from scheduler hooks.
#pragma once
#ifdef AGON_EXTENDER_OWNER_TRACE
#include <atomic>
#include <cstdint>
#include <cstdio>
#ifdef NP_TRACE_HOST
#include <thread>
#include <chrono>
#define OWNER_IRAM
#else
#include <esp_attr.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#define OWNER_IRAM IRAM_ATTR
#endif
namespace agon_owner_trace {
constexpr unsigned Capacity=512;
struct Event {uint32_t time,task;uint16_t priority;uint8_t kind,reserved;char name[16];};
struct Ring {Event events[Capacity]{};uint32_t count{};};
inline Ring rings[2];
inline std::atomic<bool> enabled{},recording{},busy[2];
inline std::atomic<void*> output_task{};
inline std::atomic<unsigned> in_flight{},refresh_sequence{};
inline unsigned depth{}; // output task alone owns nesting and hold totals
inline uint32_t holds{},max_hold{};inline uint64_t total_hold{};
struct Trigger {uint32_t task,start,end,sequence,core;bool fired{};};
inline Trigger trigger;
inline uint32_t window_start{},window_end{};
#ifdef NP_TRACE_HOST
inline uint32_t now(){return uint32_t(std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());}
inline void* task(){static thread_local int t;return &t;}
inline unsigned core(){return 1;}
inline void pause(){std::this_thread::sleep_for(std::chrono::milliseconds(1));}
#else
inline OWNER_IRAM uint32_t now(){return uint32_t(esp_timer_get_time());}
inline void* task(){return xTaskGetCurrentTaskHandle();}
inline unsigned core(){return xPortGetCoreID();}
inline void pause(){vTaskDelay(1);}
#endif
inline void registerOutput(){output_task=task();}
// Scheduler already serializes callbacks on each core. Never acquire an
// application mutex here; retain names now rather than dereference retired TCBs.
inline OWNER_IRAM void switched(unsigned c,unsigned kind,void *t,const char *name,unsigned priority){
 if(c>1 || !recording.load(std::memory_order_relaxed))return;
 busy[c].store(true,std::memory_order_release);
 if(recording.load(std::memory_order_acquire)){
  auto &r=rings[c];auto &e=r.events[r.count%Capacity];
  e.time=now();e.task=uint32_t(reinterpret_cast<uintptr_t>(t));e.priority=priority;e.kind=kind;
  unsigned i=0;for(;i<15 && name[i];++i)e.name[i]=name[i];for(;i<16;++i)e.name[i]=0;
  ++r.count;
 }
 busy[c].store(false,std::memory_order_release);
}
inline bool begin(const uint8_t *nonce){
 if(enabled || in_flight || busy[0] || busy[1])return false;
 rings[0].count=rings[1].count=0;trigger={};holds=max_hold=0;total_hold=0;depth=0;refresh_sequence=0;
 window_start=now();window_end=0;
 bool on=nonce[0]=='P'&&nonce[1]=='0'&&nonce[2]=='2'&&nonce[4]==1;
 enabled=on;recording=on;return true;
}
struct Ticket {
 bool measured=false,outer=false;uint32_t start{},finish{},sequence{};unsigned cpu{};
 void enter(){if(!enabled.load(std::memory_order_relaxed)||task()!=output_task.load())return;
  ++in_flight;measured=true;outer=depth++==0;
 }
 void acquired(){if(measured&&outer){cpu=core();sequence=refresh_sequence.load(std::memory_order_relaxed);start=now();}}
 void beforeRelease(){if(!measured||!outer)return;finish=now();
  // Freeze while still owning the native mutex; no waiting or copying here.
  if(!trigger.fired && uint32_t(finish-start)>=8000){
   trigger={uint32_t(reinterpret_cast<uintptr_t>(task())),start,finish,sequence,cpu,true};
   recording=false;
  }
 }
 void afterRelease(){if(!measured)return;if(outer){auto us=uint32_t(finish-start);++holds;total_hold+=us;if(us>max_hold)max_hold=us;}
  --depth;--in_flight;measured=false;
 }
};
inline void stop(const uint8_t *nonce){
 enabled=false;recording=false;window_end=now();auto t=now();
 while((in_flight||busy[0]||busy[1]) && uint32_t(now()-t)<6000000)pause();
 const bool bad=in_flight||busy[0]||busy[1];
 std::printf("NPOWNER begin ");for(unsigned i=0;i<8;++i)std::printf("%02x",unsigned(nonce[i]));
 std::printf(" %u %u %u %u %llu %u\n",unsigned(bad),window_start,window_end,holds,(unsigned long long)total_hold,max_hold);
 if(bad){std::printf("NPOWNER invalid\n");return;}
 std::printf("NPOWNER trigger %u %u %u %u %u %u\n",unsigned(trigger.fired),trigger.task,trigger.start,trigger.end,trigger.sequence,trigger.core);
 for(unsigned c=0;c<2;++c){auto &r=rings[c];auto count=r.count<Capacity?r.count:Capacity;auto first=r.count-count;
  std::printf("NPOWNER ring %u %u %u\n",c,r.count,count);
  for(unsigned i=first;i<r.count;++i){auto &e=r.events[i%Capacity];
   std::printf("NPOWNER event %u %u %u %u %u %u ",c,i,e.time,e.task,e.kind,unsigned(e.priority));
   for(unsigned k=0;k<16;++k){std::printf("%02x",unsigned(uint8_t(e.name[k])));}
   std::printf("\n");
  }
 }
 std::printf("NPOWNER end\n");
}
}
#endif
