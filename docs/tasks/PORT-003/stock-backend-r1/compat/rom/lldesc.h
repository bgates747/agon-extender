// Parse-only host declaration for the unchanged GPIOStream header and the
// unchanged (uninvoked) onSetupDMABuffer virtual method. This is not a DMA ABI,
// descriptor emulator or target definition. Target builds use the real SDK.
#pragma once
#include <cstdint>
struct lldesc_t { std::uint8_t *buf; unsigned eof; };
