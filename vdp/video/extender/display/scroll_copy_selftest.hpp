// RESEARCH-007 candidate-only qualification hook. Call once from FreeRTOS task
// context after PSRAM initialization, before measured workloads, only when
// SCROLL_FAST or INDEXED_SNAPSHOT_PIE, plus RENDER_BENCHMARK are selected.
// No endpoint or pipeline owner. The caller passes its selected wrapper so
// the snapshot pilot does not qualify only the scalar scroll fallback.
// The P4 call executes the actual PIE kernel through that wrapper; host use
// exercises only the portable qualification harness and libc fallback.
#pragma once
#include <cstdio>
#include <cstdlib>
#include "extender/display/scroll_copy.hpp"
#ifdef ESP_PLATFORM
#include "esp_heap_caps.h"
#endif

namespace agon::extender::display {

inline bool scrollCopySelfTest(void (*copyRow)(void *, const void *, std::size_t) = copyScrollRow)
{
  constexpr std::size_t capacity=1024+64;
#ifdef ESP_PLATFORM
  auto *allocation=static_cast<std::uint8_t *>(
      heap_caps_malloc(capacity*2,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
#else
  auto *allocation=static_cast<std::uint8_t *>(std::malloc(capacity*2));
#endif
  if (!allocation) {
    std::puts("SCROLL_FAST self-test FAIL: buffer allocation");
    return false;
  }
  auto release=[&] {
#ifdef ESP_PLATFORM
    heap_caps_free(allocation);
#else
    std::free(allocation);
#endif
  };
  auto *source=allocation;
  auto *destination=allocation+capacity;
  auto pattern=[](std::size_t i){return std::uint8_t(i*73+i/17+11);};
  for(std::size_t i=0;i<capacity;++i)source[i]=pattern(i);
  unsigned cases=0;
  constexpr std::size_t lengths[]={96,255,256,512,768,1024};
  for(const auto bytes : lengths)
    for(unsigned srcOffset=0;srcOffset<16;++srcOffset)
      for(unsigned dstOffset=0;dstOffset<16;++dstOffset) {
        std::memset(destination,0xa5,capacity);
        const auto sourceStart=std::size_t(16+srcOffset);
        const auto destinationStart=std::size_t(16+dstOffset);
        copyRow(destination+destinationStart,source+sourceStart,bytes);
        for(std::size_t i=0;i<capacity;++i) {
          const auto expected=(i>=destinationStart && i<destinationStart+bytes)
              ? pattern(sourceStart+i-destinationStart) : std::uint8_t(0xa5);
          if(destination[i]!=expected || source[i]!=pattern(i)) {
            std::printf("SCROLL_FAST self-test FAIL: bytes=%u source=%u destination=%u index=%u\n",
                unsigned(bytes),srcOffset,dstOffset,unsigned(i));
            release();
            return false;
          }
        }
        ++cases;
      }
  release();
  std::printf("SCROLL_FAST self-test PASS: %u cases, exact bytes/canaries/source preserved\n",cases);
  return true;
}

} // namespace agon::extender::display
