// Fixture-only carrier adapter. Reuse one workload/mode/receipt lifecycle;
// the parallel variant has no NM callback and owns all record storage in RAM.
#pragma once
#ifdef NETPROBE_PARALLEL
#include <agon/net_parallel.h>
static agon_netp_client client;
static uint8_t probe_command[AGON_NET_BODY],probe_reply[AGON_NET_BODY];
static bool probe_sized;
static unsigned probe_size_checks;
static uint8_t probe_begin(){return agon_netp_open(&client);}
static uint8_t probe_submit(uint8_t kind,const uint8_t*p,uint8_t n){
    if(n>AGON_NET_PAYLOAD||client.query==UINT32_MAX)return AGON_NET_PROTOCOL_ERROR;
    memcpy(probe_command,"NM\001",3);probe_command[3]=kind;
    agon_net_put32(probe_command+4,client.token);agon_net_put32(probe_command+8,client.query+1);
    probe_command[12]=n;probe_command[13]=0;
    if(n)memcpy(probe_command+AGON_NET_HEADER,p,n);
    auto result=agon_netp_submit(&client,probe_command,AGON_NET_HEADER+n);
    if(!result)probe_sized=false;
    return result; // Refused or uncertain SUBMIT is never automatically repeated.
}
static uint8_t probe_take(){
    unsigned n=0;
    if(!probe_sized){
        auto result=agon_netp_take(&client,probe_reply,AGON_NET_HEADER-1,&n);
        if(result==AGON_NETP_EMPTY||result==31)return AGON_NET_LOCAL_BUSY;
        if(result!=AGON_NETP_TOO_SMALL||n<AGON_NET_HEADER||n>AGON_NET_BODY)
            return result?result:AGON_NET_PROTOCOL_ERROR;
        ++probe_size_checks;probe_sized=true;
        return AGON_NET_LOCAL_BUSY;
    }
    auto result=agon_netp_take(&client,probe_reply,sizeof(probe_reply),&n);
    return result==AGON_NETP_EMPTY||result==31?AGON_NET_LOCAL_BUSY:result;
}
static uint8_t probe_status(){return probe_reply[13];}
static uint8_t probe_size(){return probe_reply[12];}
static const uint8_t*probe_data(){return probe_reply+AGON_NET_HEADER;}
static uint8_t probe_release(){return agon_netp_release(&client);}
static void probe_restore_callback(){}
static const char probe_carrier[]="parallel";
#else
#include <agon/net.h>
static agon_net_client client;
static unsigned probe_size_checks;
extern "C" {
void (*agon_net_callback_previous)(void);
void agon_net_callback(void);
unsigned agon_net_callback_packet(const uint8_t*p){
    if(!agon_net_is_reply(p))return 0;
    agon_net_receive(&client,p);return 1;
}
}
static uint8_t probe_begin(){
    auto result=agon_net_begin(&client);
    if(!result){
        agon_net_callback_previous=reinterpret_cast<void(*)(void)>(agon_net_previous(&client));
        mos_setkbvector(agon_net_callback,0);
    }
    return result;
}
static uint8_t probe_submit(uint8_t kind,const uint8_t*p,uint8_t n){return agon_net_submit(&client,kind,p,n);}
static uint8_t probe_take(){return agon_net_take(&client);}
static uint8_t probe_status(){return agon_net_status(&client);}
static uint8_t probe_size(){return agon_net_size(&client);}
static const uint8_t*probe_data(){return agon_net_data(&client);}
static uint8_t probe_release(){return agon_net_release(&client);}
static void probe_restore_callback(){mos_setkbvector(agon_net_callback_previous,0);}
static const char probe_carrier[]="uart";
#endif
