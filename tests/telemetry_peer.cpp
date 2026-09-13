#include "extender/telemetry/latest.hpp"
#include <cstdio>
static agon::extender::telemetry::Latest latest;
extern "C" {
unsigned telemetry_receive(const unsigned char *p,unsigned n,unsigned now){return latest.receive(p,n,now);}
unsigned telemetry_status(char *p,unsigned capacity,unsigned now){
    const auto s=latest.snapshot();char hex[281];static const char digits[]="0123456789abcdef";
    for(unsigned i=0;i<140;++i){hex[2*i]=digits[s.bytes[i]>>4];hex[2*i+1]=digits[s.bytes[i]&15];}
    hex[280]=0;
    return std::snprintf(p,capacity,"{\"online\":%s,\"age_ms\":%u,\"received\":%u,\"payload\":\"%s\"}",
                         s.online(now)?"true":"false",s.age(now),s.received,hex);
}
}
