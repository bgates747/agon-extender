// Compile-only native C public API check. This file is never a test autoexec.
#include <agon/net.h>
static agon_net_client client;
unsigned net003_native_client_probe(void){
    unsigned r=agon_net_begin(&client);
    if(!r){const uint8_t address[]={127,0,0,1,0xf6,0x1d};
        r=agon_net_submit(&client,AGON_NET_CONNECT,address,6);
        if(!r)r=agon_net_take(&client);
        (void)agon_net_release(&client);
    }
    return r;
}
