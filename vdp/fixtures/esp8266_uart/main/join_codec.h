#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>
namespace n8join {
inline void wipe(void *p,size_t n){volatile uint8_t *b=static_cast<volatile uint8_t *>(p);while(n--)*b++=0;}
// Match the accepted old ESP-AT utility: escape quotes, backslashes and commas.
// Secret bytes are runtime-only, never formatted into a diagnostic message.
inline bool build(char *out,size_t cap,const uint8_t *ssid,size_t ns,const uint8_t *password,size_t np) {
 if(ns<1||ns>32||np>64||cap<220)return false;
 size_t at=0;const char *prefix="AT+CWJAP_CUR=\"";std::memcpy(out,prefix,std::strlen(prefix));at=std::strlen(prefix);
 for(unsigned field=0;field<2;++field){const uint8_t *p=field?password:ssid;size_t n=field?np:ns;
  for(size_t i=0;i<n;++i){unsigned c=p[i];if(c<32||c==127||(field&&c>126)){wipe(out,cap);return false;}if(c=='"'||c=='\\'||c==',')out[at++]='\\';out[at++]=char(c);}
  out[at++]='"';if(!field){out[at++]=',';out[at++]='"';}
 }
 out[at++]='\r';out[at++]='\n';out[at]=0;return true;
}
}
