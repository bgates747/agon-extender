#pragma once
#ifdef AGON_EXTENDER_HDMI_512X384
#define STRIP_WIDTH 512
#define STRIP_HEIGHT 384
#define STRIP_BLOCKS 12
#elif defined(AGON_EXTENDER_HDMI_684X384)
#define STRIP_WIDTH 684
#define STRIP_HEIGHT 384
#define STRIP_BLOCKS 12
#else
#define STRIP_WIDTH 848
#define STRIP_HEIGHT 480
#define STRIP_BLOCKS 15
#endif
// AUTO reserves the848 maximum, then uses runtime684/848 geometry.
// Three32-row slots:147456 bytes at512 pixels,196992 at684,244224 at848.
// Keep the same conservative refill abort, since the
// pixel clock and horizontal total (and hence a row's duration) are unchanged.
#define STRIP_ROWS (STRIP_HEIGHT / STRIP_BLOCKS)
#define STRIP_ROLLING 1
#define STRIP_SLOTS 3
#define STRIP_REFILL_LIMIT_US 1600
// Optional negative control; zero disables it. Not normal workload timing.
#define STRIP_INJECT_LATE_TAG 0
