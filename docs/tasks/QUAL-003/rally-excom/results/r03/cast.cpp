#include <stdint.h>
extern "C" uint32_t stock16(float value) { return (uint16_t)value; }
extern "C" uint32_t stock32(float value) { return (uint32_t)value; }
extern "C" uint32_t signed16_candidate(float value) { return (uint16_t)(int32_t)value; }
