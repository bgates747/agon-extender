#include "../vdp/fixtures/esp8266_uart/main/join_codec.h"
#include <cassert>
#include <string>
int main(){
 char out[256]{};const std::string ssid="a,\"\\",pass="p,\\\"";
 assert(n8join::build(out,sizeof(out),reinterpret_cast<const uint8_t*>(ssid.data()),ssid.size(),reinterpret_cast<const uint8_t*>(pass.data()),pass.size()));
 assert(std::string(out)=="AT+CWJAP_CUR=\"a\\,\\\"\\\\\",\"p\\,\\\\\\\"\"\r\n");
 std::string maxssid(32,'\\'),maxpass(64,'"');
 assert(n8join::build(out,sizeof(out),reinterpret_cast<const uint8_t*>(maxssid.data()),32,reinterpret_cast<const uint8_t*>(maxpass.data()),64));
 assert(std::strlen(out)<sizeof(out));
 uint8_t bad[]={10};assert(!n8join::build(out,sizeof(out),bad,1,bad,1));for(char c:out)assert(c==0);
 assert(!n8join::build(out,sizeof(out),bad,0,bad,1));
 n8join::wipe(out,sizeof(out));for(char c:out)assert(c==0);
}
