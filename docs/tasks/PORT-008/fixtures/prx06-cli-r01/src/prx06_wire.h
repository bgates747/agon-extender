#ifndef AGON_EXTENDER_PRX06_WIRE_H
#define AGON_EXTENDER_PRX06_WIRE_H
#include <stdint.h>
enum {
    PRX06_PROFILES = 7,
    PRX06_REPEATS = 3,
    PRX06_OK = 0,
    PRX06_READY_TIMEOUT = 1,
    PRX06_RELEASE_TIMEOUT = 2,
};
void prx06_enter_idle(void);
uint8_t prx06_send(const uint8_t *record, uint8_t profile);
#endif
