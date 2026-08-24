// PORT-003 Phase E host-only Arduino allocation surface for retained Teletext.
//
// The target uses the real Arduino framework. This header exists solely so the
// host harness can inject Teletext PSRAM success/failure without replacing any
// official Teletext code.
#pragma once

#include <cstddef>

bool phase_e_psram_init() noexcept;
void *phase_e_ps_malloc(std::size_t size) noexcept;

inline bool psramInit() { return phase_e_psram_init(); }
inline void *ps_malloc(std::size_t size) { return phase_e_ps_malloc(size); }
