#include <cassert>
#include <vector>
#include <algorithm>
#include "video/extender/transport/console_stream.hpp"
static std::vector<uint8_t> input;
static size_t offset,calls,last_length;
static unsigned timeout;
static bool fail_driver;
int uart_read_bytes(int port,void *p,uint32_t n,unsigned wait) {
 assert(port==UART_NUM_1);++calls;last_length=n;timeout=wait;
 if(fail_driver)return -1;
 size_t got=std::min<size_t>(n,input.size()-offset);if(got)std::memcpy(p,input.data()+offset,got);offset+=got;return int(got);
}
int uart_get_buffered_data_len(int,size_t *n){*n=input.size()-offset;return 0;}
static void load(std::vector<uint8_t> bytes){input=bytes;offset=calls=last_length=timeout=0;fail_driver=false;}
static void admit(ConsoleStream &s) {
 uint8_t p[CONSOLE_SIZE]={'E','X',1,CONSOLE_PREPARE,1},reply[CONSOLE_SIZE];p[12]=1;console_seal(p);
 assert(s.session.request(p,0,42,reply));std::memcpy(p+8,reply+8,4);p[3]=CONSOLE_COMMIT;console_seal(p);assert(s.session.request(p,1,42,reply));
}
int main() {
 ConsoleStream s;Stream &base=s;s.setTimeout(200);uint8_t bytes[16]{};
 load({1,2,3,4});assert(base.readBytes(bytes,4)==0 && calls==0); // inactive never consumes UART
 admit(s);assert(base.readBytes(bytes,4)==4 && calls==1 && last_length==4 && timeout==200);assert(bytes[0]==1 && bytes[3]==4);
 load({5,6,7});assert(s.peek()==5 && calls==1);assert(base.readBytes(bytes,3)==3 && calls==2 && last_length==2);assert(bytes[0]==5 && bytes[1]==6 && bytes[2]==7);
 load({8,9});assert(s.peek()==8);uint8_t setup[]={10,11,12,13};s.feed(setup);
 assert(base.readBytes(bytes,3)==3 && bytes[0]==10 && bytes[2]==12 && calls==1);
 assert(base.readBytes(bytes,3)==3 && bytes[0]==13 && bytes[1]==8 && bytes[2]==9 && calls==2);
 load({20,21});char chars[4]{};assert(base.readBytes(chars,4)==2 && chars[0]==20 && chars[1]==21 && calls==1 && timeout==200); // partial timeout count preserved
 load({22});fail_driver=true;assert(base.readBytes(bytes,4)==0 && calls==1); // driver error is not huge unsigned count
 load({23});assert(base.readBytes(bytes,0)==0 && base.readBytes(static_cast<uint8_t*>(nullptr),4)==0 && calls==0);
 assert(s.peek()==23);s.session.cancel();assert(base.readBytes(bytes,2)==1 && bytes[0]==23 && calls==1); // cached byte preserved, no new UART admission
 assert(base.readBytes(bytes,1)==0 && calls==1);
#if defined(AGON_EXTENDER_FRAME_TIMING)
 assert(s.diagnostic_rx_bytes==12); // UART bytes once; setup is synthetic and peek is not recounted
#endif
}
