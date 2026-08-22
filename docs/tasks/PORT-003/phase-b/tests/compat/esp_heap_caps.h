// PORT-003 host allocator adapter for upstream retained common code.
#pragma once
#include <cstdlib>
#include <cstddef>
#define MALLOC_CAP_8BIT 1
#define MALLOC_CAP_32BIT 2
#define MALLOC_CAP_INTERNAL 4
#define MALLOC_CAP_SPIRAM 8
inline void *heap_caps_malloc(std::size_t size, unsigned) { return std::malloc(size); }
inline void heap_caps_free(void *allocation) { std::free(allocation); }
