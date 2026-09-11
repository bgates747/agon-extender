// Serialized timer-task model with deferred deletion, like the pinned SDK.
// Host scheduling jitter is deliberately not treated as P4 timing evidence.
#pragma once
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <memory>
#include <mutex>
#include <thread>
#include <vector>
#include <algorithm>
using esp_err_t=int;
constexpr int ESP_OK=0, ESP_TIMER_TASK=0;
#define ESP_ERROR_CHECK(expr) do { auto result=(expr); assert(result==ESP_OK); } while(false)
struct esp_timer_create_args_t {
  void (*callback)(void *){}; void *arg{}; int dispatch_method{};
  char const *name{}; bool skip_unhandled_events{};
};
struct StockHostTimer {
  esp_timer_create_args_t args;
  std::uint64_t due{},period{};
  bool armed{},running{},retired{};
};
using esp_timer_handle_t=StockHostTimer *;
inline std::int64_t esp_timer_get_time() {
  return std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
struct StockHostTimers {
  std::mutex mutex;
  std::condition_variable condition;
  std::vector<std::unique_ptr<StockHostTimer>> timers;
  bool stopping{};
  std::thread worker;
  StockHostTimers():worker([this]{run();}) {}
  ~StockHostTimers() {
    {std::lock_guard lock(mutex); stopping=true;}
    condition.notify_all(); worker.join();
  }
  void run() {
    std::unique_lock lock(mutex);
    while (!stopping) {
      timers.erase(std::remove_if(timers.begin(),timers.end(),[](auto &t){return t->retired&&!t->running;}),timers.end());
      StockHostTimer *next=nullptr;
      for(auto &t:timers) if(t->armed&&(!next||t->due<next->due)) next=t.get();
      if(!next) {condition.wait(lock); continue;}
      auto now=static_cast<std::uint64_t>(esp_timer_get_time());
      if(now<next->due) {condition.wait_for(lock,std::chrono::microseconds(next->due-now));continue;}
      next->running=true;
      if(next->period) next->due=now+next->period; else next->armed=false;
      auto args=next->args;
      lock.unlock(); args.callback(args.arg); lock.lock();
      next->running=false;
    }
  }
};
inline StockHostTimers &stockHostTimers() {static StockHostTimers timers;return timers;}
inline int esp_timer_create(esp_timer_create_args_t const *args,esp_timer_handle_t *out) {
  auto &s=stockHostTimers();std::lock_guard lock(s.mutex);
  auto t=std::make_unique<StockHostTimer>();t->args=*args;*out=t.get();s.timers.push_back(std::move(t));return ESP_OK;
}
inline int hostTimerStart(esp_timer_handle_t t,std::uint64_t delay,bool periodic) {
  auto &s=stockHostTimers();
  {std::lock_guard lock(s.mutex);assert(!t->armed&&!t->retired);t->period=periodic?delay:0;t->due=esp_timer_get_time()+delay;t->armed=true;}
  s.condition.notify_all();return ESP_OK;
}
inline int esp_timer_start_periodic(esp_timer_handle_t t,std::uint64_t p) {return hostTimerStart(t,p,true);}
inline int esp_timer_start_once(esp_timer_handle_t t,std::uint64_t p) {return hostTimerStart(t,p,false);}
inline int esp_timer_stop(esp_timer_handle_t t) {auto &s=stockHostTimers();std::lock_guard lock(s.mutex);t->armed=false;s.condition.notify_all();return ESP_OK;}
inline int esp_timer_delete(esp_timer_handle_t t) {auto &s=stockHostTimers();std::lock_guard lock(s.mutex);assert(!t->armed);t->retired=true;s.condition.notify_all();return ESP_OK;}
