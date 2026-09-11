// Ordinary host allocations. Capability behavior is qualified by target build
// and subsequent hardware work, not by this allocator.
#pragma once
#include <cstdlib>
#include <cstddef>
#define MALLOC_CAP_8BIT 1
#define MALLOC_CAP_32BIT 2
#define MALLOC_CAP_INTERNAL 4
#define MALLOC_CAP_SPIRAM 8
#define MALLOC_CAP_DMA 16
inline void *heap_caps_malloc(std::size_t n, unsigned) { return std::malloc(n); }
inline void heap_caps_free(void *p) { std::free(p); }
inline std::size_t heap_caps_get_largest_free_block(unsigned) { return 1024 * 1024; }
