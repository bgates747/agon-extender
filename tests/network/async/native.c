/* Link-only application placement/size check. Never stage or RUN this probe. */
#include <agon/net_async.h>
static agon_neta_client client;
int main(void){
    uint8_t address[6]={127,0,0,1,1,1};
    int r=agon_neta_begin(&client);
    if(!r){
        r=agon_net_submit(&client.net,AGON_NET_CONNECT,address,6);
        if(!r)r=agon_neta_progress(&client);
        if(!r)r=agon_net_take(&client.net);
        if(!r)r=agon_neta_close(&client);
    }
    return r;
}
