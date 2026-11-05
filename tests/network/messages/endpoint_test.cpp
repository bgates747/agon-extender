#include "../../fixtures/network/endpoint.hpp"
#include <assert.h>
#include <string.h>
#include <stdio.h>
int main() {
    struct Valid { const char *text;uint8_t bytes[6]; } valid[]={
        {"192.168.0.14:7671",{192,168,0,14,0xf7,0x1d}},
        {"0.0.0.0:1",{0,0,0,0,1,0}},
        {"255.255.255.255:65535",{255,255,255,255,255,255}},
        {"001.002.003.004:00080",{1,2,3,4,80,0}},
    };
    for (const auto &v:valid) {
        uint8_t bytes[6];assert(parse_endpoint(v.text,bytes));
        assert(!memcmp(bytes,v.bytes,6));
    }
    const char *invalid[]={"","1.2.3.4","1.2.3.4:","1.2.3.4:0",
        "256.0.0.1:80","1.2.3.4:65536","1.2.3.4:99999999999999999999999",
        "-1.2.3.4:80","1.2.3.4:+80","1..3.4:80","1.2.3:80",
        "1.2.3.4.5:80","1.2.3.4:80x","1.2.3.4:80 "," 1.2.3.4:80",
        "1.2.3.4:80:90","1.2.3.4:80\n","9999999999.2.3.4:80"};
    for (const char *text:invalid) {uint8_t bytes[6];assert(!parse_endpoint(text,bytes));}
    puts("Endpoint parser: 4 valid encodings and 18 malformed/boundary refusals PASS");
}
