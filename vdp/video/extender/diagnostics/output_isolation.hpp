// QUAL-003 P02 diagnostic only: existing nonce selects a bounded output control.
// No production flag, VDU extension, renderer change or altered browser credit.
#pragma once
#ifdef AGON_EXTENDER_OUTPUT_ISOLATION
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#ifdef NP_TRACE_HOST
#include <mutex>
#include <chrono>
#include <thread>
#else
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#endif
namespace agon_output_isolation {
enum class Mode : unsigned { Normal, Off, Discard, Prebuilt };
enum class Phase : unsigned { Compose, Prebuilt, Send, Count };
inline Mode decode(const uint8_t *n) {
 return n[0]=='P' && n[1]=='0' && n[2]=='2' && n[3]<=3 ? Mode(n[3]) : Mode::Normal;
}
struct Total { uint32_t calls{}, units{}, elapsed{}, failures{}; };
inline std::atomic<Mode> mode{Mode::Normal};
inline bool active{}, invalid{};
inline unsigned in_flight{};
inline uint32_t started{}, stopped{};
inline std::array<Total,unsigned(Phase::Count)> totals{};
#ifdef NP_TRACE_HOST
inline std::mutex mutex;
struct Guard { std::lock_guard<std::mutex> lock{mutex}; };
inline uint32_t now(){return uint32_t(std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());}
inline void yield(){std::this_thread::sleep_for(std::chrono::milliseconds(1));}
#else
inline portMUX_TYPE mutex=portMUX_INITIALIZER_UNLOCKED;
struct Guard {Guard(){portENTER_CRITICAL(&mutex);} ~Guard(){portEXIT_CRITICAL(&mutex);}};
inline uint32_t now(){return uint32_t(esp_timer_get_time());}
inline void yield(){vTaskDelay(1);}
#endif
inline bool begin(const uint8_t *nonce) {
 if(nonce[0]!='P'||nonce[1]!='0'||nonce[2]!='2'||nonce[3]>3)return false;
 Guard g;if(active || in_flight)return false;
 totals={};invalid=false;started=now();stopped=0;active=true;mode.store(decode(nonce));return true;
}
// Each phase records only operations admitted inside the window. Stop joins
// those operations before reading totals. No per-row or per-byte accounting.
class Scope {
 bool measured_{};Phase phase_;uint32_t start_{};
 public:
 explicit Scope(Phase p):phase_(p){Guard g;measured_=active;if(measured_){++in_flight;start_=now();}}
 void finish(uint32_t units,bool ok=true){if(!measured_)return;const auto elapsed=now()-start_;Guard g;auto &t=totals[unsigned(phase_)];++t.calls;t.units+=units;t.elapsed+=elapsed;t.failures+=!ok;--in_flight;measured_=false;}
 ~Scope(){finish(0,false);}
 Scope(const Scope&)=delete;Scope& operator=(const Scope&)=delete;
};
inline bool blocksNetwork(){auto m=mode.load();return m==Mode::Off || m==Mode::Discard;}
inline void stop(const uint8_t *nonce) {
 {Guard g;if(!active)return;active=false;stopped=now();mode.store(Mode::Off);}
 auto start=now();
 for(;;){bool done;{Guard g;done=in_flight==0;}if(done)break;if(uint32_t(now()-start)>6000000){Guard g;invalid=true;break;}yield();}
 std::array<Total,unsigned(Phase::Count)> saved;unsigned pending;bool failed;uint32_t duration;
 {Guard g;saved=totals;pending=in_flight;failed=invalid;duration=stopped-started;}
 std::printf("\nNPOUT begin ");for(unsigned i=0;i<8;++i)std::printf("%02x",unsigned(nonce[i]));
 std::printf(" %u %u %u\n",unsigned(duration),pending,unsigned(failed));
 for(unsigned i=0;i<saved.size();++i){auto t=saved[i];std::printf("NPOUT row %u %u %u %u %u\n",i,t.calls,t.units,t.elapsed,t.failures);}
 std::printf("NPOUT end\n");
 mode.store(Mode::Normal);
}
// Producer-owned slots only. Real composition invalidates cached content.
class PrebuiltSlots {
 struct Entry {uint8_t *p{};size_t w{},h{};};std::array<Entry,3> entries_{};
 public:
 void invalidate(uint8_t *p){for(auto &e:entries_)if(e.p==p)e={};}
 bool prepare(uint8_t *p,size_t w,size_t h){
  if(!p||!w||!h||w>1024||h>768)return false;
  for(auto &e:entries_)if(e.p==p&&e.w==w&&e.h==h)return true;
  Entry *slot=nullptr;for(auto &e:entries_)if(e.p==p){slot=&e;break;}
  if(!slot)for(auto &e:entries_)if(!e.p){slot=&e;break;}
  if(!slot)return false;
  for(size_t y=0;y<h;++y)std::memset(p+y*w,(y/16)%2?0x3c:0x03,w);
  *slot={p,w,h};return true;
 }
};
}
#endif
