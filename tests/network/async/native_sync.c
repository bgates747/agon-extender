/* Matched link-only synchronous source-placement control; never stage/RUN. */
#include <agon/net.h>
static agon_net_client client;
int main(void){
    uint8_t address[6]={127,0,0,1,1,1};
    int r=agon_net_begin(&client);
    if(!r){
        r=agon_net_submit(&client,AGON_NET_CONNECT,address,6);
        if(!r)r=agon_net_take(&client);
        if(!r)r=agon_net_release(&client);
    }
    return r;
}
