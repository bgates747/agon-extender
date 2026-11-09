#include "../vdp/fixtures/esp8266_uart/main/bw_codec.h"
#include <cstdio>
int main() {
 if(n8bw::crc("123456789",9)!=0xcbf43926u)return 1;
 uint8_t data[1024],out[1040];n8bw::pattern(data,sizeof(data),7,n8bw::up_salt);
 size_t n=n8bw::frame(out,7,data,sizeof(data));if(!n8bw::valid(out,n))return 2;
 for(size_t i=0;i<n;++i)std::printf("%02x",out[i]);
 std::puts("");
 out[100]^=1;if(n8bw::valid(out,n))return 3;
 if(n8bw::frame(out,8,nullptr,0)!=16||!n8bw::valid(out,16))return 4;
 return 0;
}
