#pragma once

#include <stdint.h>

// Render the existing 640x480 artwork into a full 848x480 BGR888 frame at setup.
void mode0_render_reference(uint8_t *frame);
