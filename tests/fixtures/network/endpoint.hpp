#pragma once
#include <stdint.h>

// Keep this fixture independent of AgonDev's inherited libc scanner: its
// uscan.c character() counts a string NUL as a successful trailing %c, so the
// usual sscanf(... "%c") end check rejects valid endpoints. Remove this local
// parser only when the selected toolchain's scanner contract is qualified.
static bool parse_endpoint(const char *s, uint8_t *address) {
    for (unsigned field=0;field<5;++field) {
        unsigned value=0,digits=0;
        const unsigned maximum=field<4?255:65535;
        const unsigned limit=field<4?3:5;
        while (*s>='0' && *s<='9') {
            if (++digits>limit)return false;
            value=value*10+unsigned(*s++-'0');
            if (value>maximum)return false;
        }
        if (!digits)return false;
        if (field<4) {
            if (*s++!=(field<3?'.':':'))return false;
            address[field]=uint8_t(value);
        } else {
            if (*s || !value)return false;
            address[4]=uint8_t(value);address[5]=uint8_t(value>>8);
        }
    }
    return true;
}
