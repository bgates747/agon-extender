/* PORT-008 private qualification only. Mirrored byte-for-byte in agon-emos
 * projects/parprobe/src/pattern.h; tests verify identity. Not a wire protocol.
 * Position-dependent bits catch byte shifts that a plain arithmetic ramp misses.
 */
#ifndef PARALLEL_PROBE_PATTERN_H
#define PARALLEL_PROBE_PATTERN_H
#include <stddef.h>
#include <stdint.h>
static inline uint8_t parallel_probe_pattern(size_t i, uint8_t seed) {
    return (uint8_t)((i*73u) ^ ((i>>3)*29u) ^ (i>>8) ^ seed);
}
static inline uint8_t parallel_probe_seed(const uint8_t *offer) {
    return (uint8_t)(offer[4]^offer[5]^offer[6]^offer[7]^offer[8]^offer[9]^0xD3);
}
static inline uint32_t parallel_probe_crc(const uint8_t *p, size_t n) {
    uint32_t crc=0xFFFFFFFFu;
    while(n--) {
        crc^=*p++;
        for(unsigned bit=0;bit<8;++bit)
            crc=(crc>>1)^((crc&1u)?0xEDB88320u:0);
    }
    return crc^0xFFFFFFFFu;
}
#endif
