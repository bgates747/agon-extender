// RESEARCH-007: default-off P4 row-copy experiment. The stock VScroll helper
// still owns overlap order, sprite erasure and exposed-row filling; this helper
// copies only one pair of disjoint row spans and never changes framebuffer
// layout, output ownership, cache publication or VDU behaviour.
#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>

#if defined(AGON_EXTENDER_SCROLL_FAST) && AGON_EXTENDER_SCROLL_FAST && defined(ESP_PLATFORM)
#include "sdkconfig.h"
#include "soc/soc_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"
#if !CONFIG_IDF_TARGET_ESP32P4 || !SOC_CPU_HAS_PIE || !defined(__riscv_xesppie) || __riscv_xlen != 32
#error "SCROLL_FAST requires ESP32-P4 RV32 with the XEspPIE ISA"
#endif
// This experiment is bounded to the product's current v1.x-or-newer silicon
// range. Earlier engineering revisions require their own review/qualification.
#if CONFIG_ESP_REV_MIN_FULL < 100
#error "SCROLL_FAST has not been reviewed for P4 revisions below v1.0"
#endif
#define AGON_EXTENDER_SCROLL_COPY_PIE 1
extern "C" void agon_extender_scroll_copy_pie(std::uint8_t *destination,
                                             const std::uint8_t *alignedSource,
                                             std::size_t bytes,
                                             unsigned sourceShift);
#endif

namespace agon::extender::display {

struct ScrollCopyPlan {
  std::size_t head;
  std::size_t body;
  std::size_t tail;
};

inline ScrollCopyPlan scrollCopyPlan(std::uintptr_t destination, std::size_t bytes)
{
  if (bytes < 96) return {bytes, 0, 0};
  // Keep at least 16 bytes before/after the vector body. Align the destination
  // to 16; the assembly explicitly aligns the source down and splices adjacent
  // vector loads. Its read-ahead can reach at most 15 bytes beyond the body's
  // nominal source span, entirely inside the caller's original requested span.
  const auto head = std::size_t(16 + ((-destination) & 15));
  const auto body = (bytes - head - 16) & ~std::size_t(31);
  return {head, body, bytes - head - body};
}

// Body is injectable for host bounds/overlap tests; the normal product call
// below supplies the actual P4 assembly. Host tests do not qualify that ISA.
template <typename Body>
inline void copyScrollRowBounded(void *destination, const void *source,
                                 std::size_t bytes, Body body)
{
  auto *dst = static_cast<std::uint8_t *>(destination);
  auto *src = static_cast<const std::uint8_t *>(source);
  const auto plan = scrollCopyPlan(reinterpret_cast<std::uintptr_t>(dst), bytes);
  if (!plan.body) {
    if (bytes) std::memcpy(dst, src, bytes);
    return;
  }
  std::memcpy(dst, src, plan.head);
  const auto sourceAddress = reinterpret_cast<std::uintptr_t>(src + plan.head);
  body(dst + plan.head,
       reinterpret_cast<const std::uint8_t *>(sourceAddress & ~std::uintptr_t(15)),
       plan.body, unsigned(sourceAddress & 15));
  std::memcpy(dst + plan.head + plan.body, src + plan.head + plan.body, plan.tail);
}

inline void copyScrollRow(void *destination, const void *source, std::size_t bytes)
{
#ifdef AGON_EXTENDER_SCROLL_COPY_PIE
  // IDF 5.5.5 saves q0/q1/q2 and SAR_BYTES for FreeRTOS tasks, but deliberately
  // forbids PIE from ISRs. A future ISR caller retains the ordinary copy path.
  // The kernel does not read/write global PIE CFG, acquire DMA/PPA, mask
  // interrupts or require a particular core. Ordinary cache publication stays
  // with the existing renderer/output owner.
  if (!xPortInIsrContext()) {
    copyScrollRowBounded(destination, source, bytes, agon_extender_scroll_copy_pie);
    return;
  }
#endif
  if (bytes) std::memcpy(destination, source, bytes);
}

} // namespace agon::extender::display
