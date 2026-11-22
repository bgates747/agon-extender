/* Native test entry point for the exact pixel function called from the ISR. */
#include "../pair/pair_pattern.h"

void test_pair_pixels(uint8_t *dst, unsigned frame, unsigned pair, bool primed)
{
    pair_pattern_fill(dst, frame, pair, primed);
}
