// PORT-003 Phase E host allocation adapter for the real retained Canvas path.
#pragma once

#include <cstddef>

#define MALLOC_CAP_8BIT 1
#define MALLOC_CAP_32BIT 2
#define MALLOC_CAP_INTERNAL 4
#define MALLOC_CAP_SPIRAM 8

void *phase_e_heap_caps_malloc(std::size_t size) noexcept;
void phase_e_heap_caps_free(void *allocation) noexcept;

inline void *heap_caps_malloc(std::size_t size, unsigned) {
  return phase_e_heap_caps_malloc(size);
}
inline void heap_caps_free(void *allocation) {
  phase_e_heap_caps_free(allocation);
}
inline std::size_t heap_caps_get_free_size(unsigned) { return 1U << 30; }
