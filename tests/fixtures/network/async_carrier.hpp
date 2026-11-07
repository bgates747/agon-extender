// Provisional owner-isolation binding. Generic U1 code stays application-owned.
// Do not install vanilla IRQ vectors: EMOS owns RX/LSR/CTS and hook service.
#pragma once
extern "C" {
#include <agon/net_async.h>
void (*agon_net_callback_previous)(void);
void agon_net_callback(void);
}
static agon_neta_client client;
static bool callback_installed;
extern "C" unsigned agon_net_callback_packet(const uint8_t*p){
    if(!agon_net_is_reply(p))return 0;
    agon_net_receive(&client.net,p);return 1;
}
static uint8_t probe_begin(){
    const uint8_t r=agon_neta_begin(&client);
    if(!r){
        agon_net_callback_previous=reinterpret_cast<void(*)(void)>(agon_net_previous(&client.net));
        mos_setkbvector(agon_net_callback,0);callback_installed=true;
    }
    return r;
}
static uint8_t probe_submit(uint8_t kind,const uint8_t*p,uint8_t n){
    // SDK guards before it constructs the next request in borrowed storage.
    return agon_net_submit(&client.net,kind,p,n);
}
static uint8_t probe_take(){
    const uint8_t r=agon_neta_progress(&client);
    if(r==31)return AGON_NET_LOCAL_BUSY;
    if(r)return r;
    if(client.tx.phase!=U1_IDLE)return AGON_NET_LOCAL_BUSY;
    return agon_net_take(&client.net);
}
static uint8_t probe_status(){return agon_net_status(&client.net);}
static uint8_t probe_size(){return agon_net_size(&client.net);}
static const uint8_t*probe_data(){return agon_net_data(&client.net);}
static uint8_t probe_release(){
    // A rejected begin with no attached association has nothing to retire.
    return agon_neta_active==&client?agon_neta_close(&client):0;
}
static void probe_restore_callback(){
    if(callback_installed){mos_setkbvector(agon_net_callback_previous,0);callback_installed=false;}
}
