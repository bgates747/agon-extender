// PORT-003 local startup-crash diagnostic; absent from ordinary console builds.
// Link with --wrap=pthread_mutex_init and --wrap=pthread_mutex_destroy.
// GCC's shared_ptr mutex policy ignores
// initialization errors: capture an actual failure before a later destructor
// could consume an uninitialized handle. This probe does not repair that path.
#pragma once
#include <atomic>
#include <cstdlib>
#include <pthread.h>
#include "esp_heap_caps.h"
#include "esp_log.h"
#if defined(AGON_EXTENDER_HEAP_PROBE)
#include "esp_heap_trace.h"
#include "esp_memory_utils.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// The prebuilt libstdc++ allocator lacks frame pointers, truncating heap-trace
// stacks at operator new. Diagnostic-only link wrappers preserve successful
// default-heap allocation and expose callers. Allocation failure aborts here;
// they intentionally do not provide production new_handler/exception behavior.
extern "C" void *__wrap__Znwj(std::size_t size) {
  void *result = std::malloc(size ? size : 1);
  if (!result) std::abort();
  return result;
}
extern "C" void *__wrap__Znaj(std::size_t size) {
  void *result = std::malloc(size ? size : 1);
  if (!result) std::abort();
  return result;
}
#endif

extern "C" int __real_pthread_mutex_init(pthread_mutex_t *, const pthread_mutexattr_t *);
extern "C" int __real_pthread_mutex_destroy(pthread_mutex_t *);
namespace {
std::atomic<unsigned> mutexProbeCreated{}, mutexProbeDestroyed{};

#if defined(AGON_EXTENDER_HEAP_PROBE)
// ESP-IDF 5.5 standalone tracing permits PSRAM records but excludes ISR
// allocations with that storage. This is an intentionally incomplete task-
// allocation diagnostic, not a production fix or a performance measurement.
// Start after early startup, without adding a global allocation constructor.
void mutexProbeStartTrace(unsigned call) {
  if (call != 512) return;
  constexpr size_t capacity = 32768;
  auto *records = static_cast<heap_trace_record_t *>(heap_caps_malloc(
      capacity * sizeof(heap_trace_record_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
  if (!records || heap_trace_init_standalone(records, capacity) != ESP_OK ||
      heap_trace_start(HEAP_TRACE_LEAKS) != ESP_OK) {
    esp_rom_printf("heap_probe: setup failed at call %u\n", call);
    std::abort();
  }
  esp_rom_printf("heap_probe: started call=%u capacity=%u record_bytes=%u internal=%u largest=%u\n",
                 call, unsigned(capacity), unsigned(sizeof(heap_trace_record_t)),
                 unsigned(heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)),
                 unsigned(heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)));
}

void mutexProbeDumpTrace() {
  const auto stopped = heap_trace_stop();
  heap_trace_summary_t summary{};
  const auto result = heap_trace_summary(&summary);
  esp_rom_printf("heap_probe: stop=%d summary=%d count=%u capacity=%u high=%u overflow=%u allocations=%u frees=%u\n",
                 stopped, result, unsigned(summary.count), unsigned(summary.capacity),
                 unsigned(summary.high_water_mark), unsigned(summary.has_overflowed),
                 unsigned(summary.total_allocations), unsigned(summary.total_frees));
  if (result != ESP_OK) return;
  unsigned count = 0, bytes = 0;
  // Unlike the SDK dump helper, do not hold its critical section while writing
  // a potentially long USB log. The trace is stopped; get copies one record.
  // Addresses identify allocation sites only and are never dereferenced here.
  for (size_t i = 0; i < summary.count; ++i) {
    heap_trace_record_t record{};
    if (heap_trace_get(i, &record) != ESP_OK) break;
    if (record.address && !record.freed && esp_ptr_internal(record.address)) {
      ++count; bytes += record.size;
      esp_rom_printf("heap_live: %p %u", record.address, unsigned(record.size));
      for (const auto caller : record.alloced_by) esp_rom_printf(" %p", caller);
      esp_rom_printf("\n");
    }
    if ((i & 31) == 31) vTaskDelay(1);
  }
  esp_rom_printf("heap_probe: complete internal_count=%u internal_bytes=%u\n", count, bytes);
}
#else
void mutexProbeStartTrace(unsigned) {}
void mutexProbeDumpTrace() {}
#endif
}
extern "C" int __wrap_pthread_mutex_init(pthread_mutex_t *mutex,
                                         const pthread_mutexattr_t *attributes) {
  static std::atomic<unsigned> calls{};
  const unsigned call = calls.fetch_add(1, std::memory_order_relaxed) + 1;
  mutexProbeStartTrace(call);
  const int result = __real_pthread_mutex_init(mutex, attributes);
  if (result != 0) {
    ESP_LOGE("mutex_probe", "init failure call=%u status=%d object=%p internal=%u largest=%u total=%u created=%u destroyed=%u",
             call, result, static_cast<void *>(mutex),
             unsigned(heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)),
             unsigned(heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT)),
             unsigned(heap_caps_get_free_size(MALLOC_CAP_8BIT)),
             mutexProbeCreated.load(std::memory_order_relaxed),
             mutexProbeDestroyed.load(std::memory_order_relaxed));
    mutexProbeDumpTrace();
    std::abort();
  }
  mutexProbeCreated.fetch_add(1, std::memory_order_relaxed);
  return result;
}
extern "C" int __wrap_pthread_mutex_destroy(pthread_mutex_t *mutex) {
  const int result = __real_pthread_mutex_destroy(mutex);
  if (result != 0) {
    ESP_LOGE("mutex_probe", "destroy failure status=%d object=%p created=%u destroyed=%u",
             result, static_cast<void *>(mutex),
             mutexProbeCreated.load(std::memory_order_relaxed),
             mutexProbeDestroyed.load(std::memory_order_relaxed));
    mutexProbeDumpTrace();
    std::abort();
  }
  mutexProbeDestroyed.fetch_add(1, std::memory_order_relaxed);
  return result;
}
