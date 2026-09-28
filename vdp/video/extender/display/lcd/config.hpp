#pragma once
// Opt-in candidate; ordinary console builds keep LCD disabled.
#ifndef AGON_EXTENDER_LCD
#define AGON_EXTENDER_LCD 0
#endif

// Explicit bench-only DSI generator; bypasses renderer and PPA output.
#ifndef AGON_EXTENDER_LCD_PATTERN
#define AGON_EXTENDER_LCD_PATTERN 0
#endif

// Bench-only comparison with vendor-documented IDF5.4.1 host timing rounding.
#ifndef AGON_EXTENDER_LCD_LEGACY_TIMING
#define AGON_EXTENDER_LCD_LEGACY_TIMING 0
#endif
