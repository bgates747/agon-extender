#ifndef HDMI_TIMING_TEST_PATTERN_H
#define HDMI_TIMING_TEST_PATTERN_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Static diagnostic only: no VDU renderer, animation, SDK or framebuffer owner.
 * Pixels are packed B,G,R bytes. The caller supplies writable storage and owns
 * any cache flush/presentation. Row padding remains untouched. The diagnostic
 * supports >=640x480 surfaces, including the 848x480 trial and 640x480 control.
 * False means invalid geometry/storage, with no bytes modified. */
bool hdmi_timing_pattern_bgr888(uint8_t *pixels, size_t size_bytes,
                              size_t stride_bytes, unsigned width,
                              unsigned height);

#ifdef __cplusplus
}
#endif
#endif
