// QUAL-003 P01cd, default-off instrumentation; elapsed scopes include preemption.
#pragma once
#ifdef AGON_EXTENDER_LOCK_WAKE_TRACE
#include <atomic>
#include <array>
#include <cstdint>
#include <cstdio>
#ifdef NP_TRACE_HOST
#include <mutex>
#include <chrono>
#include <thread>
#else
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#endif
namespace agon_lock_wake {
#ifdef NP_TRACE_HOST
inline std::mutex mutex;
struct Guard {std::lock_guard<std::mutex> g{mutex};};
inline void *task(){static thread_local int x;return &x;}
inline uint32_t now(){return uint32_t(std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());}
inline void yield(){std::this_thread::sleep_for(std::chrono::milliseconds(1));}
#else
inline portMUX_TYPE mutex=portMUX_INITIALIZER_UNLOCKED;
struct Guard{Guard(){portENTER_CRITICAL(&mutex);}~Guard(){portEXIT_CRITICAL(&mutex);}};
inline void *task(){return xTaskGetCurrentTaskHandle();}
inline uint32_t now(){return uint32_t(esp_timer_get_time());}
inline void yield(){vTaskDelay(1);}
#endif
// 0 parser, 1 draw, 2 output. Metrics: native wait/hold then wake age.
struct Total {uint32_t count{}, maximum{};uint64_t sum{};std::array<uint32_t,32> bins{};};
inline std::array<Total,8> totals{};
inline std::array<std::atomic<void*>,3> owners{};
inline std::array<unsigned,3> depths{}; // each owner alone modifies its nesting
inline std::array<std::atomic<uint32_t>,2> pending{};
inline std::atomic<bool> active{};
inline unsigned in_flight{};
inline bool invalid{};
inline void add(unsigned metric,uint32_t us){auto &t=totals[metric];++t.count;t.sum+=us;if(us>t.maximum)t.maximum=us;unsigned b=0;for(auto n=us;n>1;n>>=1)++b;++t.bins[b];}
inline void registerWorker(unsigned owner){owners[owner].store(task());}
inline bool begin(const uint8_t *nonce){Guard g;if(in_flight||active)return false;totals={};invalid=false;pending[0]=0;pending[1]=0;owners[0]=task();active=nonce[0]=='P'&&nonce[1]=='0'&&nonce[2]=='2'&&nonce[4]==1;return true;}
struct Ticket {
 int owner=-1;bool measured=false,outer=false;uint32_t start=0,acquired_at=0;
 void enter(){if(!active.load(std::memory_order_relaxed))return;auto t=task();for(unsigned i=0;i<3;++i)if(owners[i].load()==t){owner=int(i);break;}if(owner<0)return;Guard g;if(!active)return;measured=true;++in_flight;outer=depths[owner]++==0;if(outer)start=now();}
 void acquired(){if(measured&&outer)acquired_at=now();}
 void released(){if(!measured)return;auto end=outer?now():0;Guard g;if(outer){add(unsigned(owner)*2,acquired_at-start);add(unsigned(owner)*2+1,end-acquired_at);}--depths[owner];--in_flight;measured=false;}
};
inline void notify(unsigned worker){if(!active.load(std::memory_order_relaxed))return;uint32_t zero=0;pending[worker].compare_exchange_strong(zero,now());}
inline void entered(unsigned worker){if(!active.load(std::memory_order_relaxed))return;auto stamp=pending[worker].exchange(0);if(!stamp)return;auto age=now()-stamp;Guard g;if(active)add(6+worker,age);}
inline void stop(const uint8_t *nonce){active=false;auto start=now();for(;;){bool done;{Guard g;done=in_flight==0;}if(done)break;if(uint32_t(now()-start)>6000000){Guard g;invalid=true;break;}yield();}
 std::array<Total,8> saved;unsigned pending_scopes;bool bad;{Guard g;saved=totals;pending_scopes=in_flight;bad=invalid;}
 std::printf("NPLOCK begin ");for(unsigned i=0;i<8;++i)std::printf("%02x",unsigned(nonce[i]));std::printf(" %u %u\n",pending_scopes,unsigned(bad));
 for(unsigned i=0;i<8;++i){auto &t=saved[i];std::printf("NPLOCK row %u %u %llu %u",i,t.count,(unsigned long long)t.sum,t.maximum);for(auto b:t.bins)std::printf(" %u",b);std::printf("\n");}std::printf("NPLOCK end\n");
}
}
#endif
