#pragma once
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Non-reentrant original codec, guarded internally. 0 success, 1 invalid/codec
   error, 2 output capacity, 3 memory budget, 4 busy. Output unpublished on error. */
int p4_szip(int decode, const uint8_t *source, size_t length,
            uint8_t *output, size_t capacity, size_t *written);
#ifdef __cplusplus
}
#endif
