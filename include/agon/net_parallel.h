/* NET-004 experimental ext.netp caller. Foreground ADL/MBASE0, IRQs enabled.
 * This include never installs a callback or touches peripheral registers.
 * No fallback to ext.net. Keep the object static; errors do not authorize replay.
 * See docs/protocols/application-network-parallel.md for lifetime/close rules.
 */
#ifndef AGON_NET_PARALLEL_H
#define AGON_NET_PARALLEL_H
#include "net.h"
#define AGON_NETP_TOO_SMALL 130
#define AGON_NETP_EMPTY 131
#define AGON_NETP_FAULT 132
#define AGON_NETP_INVALID 19
#define AGON_NETP_OPEN 0
#define AGON_NETP_TAKE 1
#define AGON_NETP_SUBMIT 2
#define AGON_NETP_RELEASE 3
typedef struct agon_netp_client {
    uint8_t request[66], input[1+4+AGON_NET_BODY];
    uint32_t token, query;
    uint8_t pending, operation;
} agon_netp_client;

static inline uint8_t agon_netp_call(agon_netp_client*c,unsigned n,
                                   uint8_t*out,unsigned capacity,unsigned*length){
    uint8_t*r=c->request;memset(r,0,66);
    r[0]=66;r[2]=1;r[4]=3;r[5]=3;r[6]=2;
    memcpy(r+25,"ext",3);memcpy(r+41,"netp",4);
    agon_net_pointer(r+10,c->input);r[13]=(uint8_t)n;
    if(capacity){agon_net_pointer(r+16,out);r[19]=(uint8_t)capacity;}
    {uint8_t result=(uint8_t)AGON_NET_CALL(r);
     *length=(unsigned)r[22]|((unsigned)r[23]<<8);
     if(r[24])return AGON_NET_PROTOCOL_ERROR;
     return result;}
}
static inline uint8_t agon_netp_open(agon_netp_client*c){
    uint8_t result,*reply=c->input+1;unsigned n=0;
    if(c->token)return AGON_NET_LOCAL_BUSY;
    c->input[0]=AGON_NETP_OPEN;
    result=agon_netp_call(c,1,reply,8,&n);
    if(result)return result;
    if(n!=8||memcmp(reply,"NP\001\001",4)||!agon_net_u32(reply+4))return AGON_NET_PROTOCOL_ERROR;
    c->token=agon_net_u32(reply+4);c->pending=0;c->query=0;return 0;
}
static inline uint8_t agon_netp_submit(agon_netp_client*c,const uint8_t*p,unsigned n){
    unsigned ignored;uint8_t result;
    if(!c->token)return AGON_NET_UNAVAILABLE;
    if(c->pending)return AGON_NET_LOCAL_BUSY;
    if(!p||n<AGON_NET_HEADER||n>AGON_NET_BODY||memcmp(p,"NM\001",3)||
       p[3]<1||p[3]>3||agon_net_u32(p+4)!=c->token||
       !agon_net_u32(p+8)||agon_net_u32(p+8)<=c->query||p[12]!=n-AGON_NET_HEADER||p[13]||
       (p[3]==AGON_NET_CONNECT?p[12]!=6:p[3]==AGON_NET_POLL?p[12]!=0:0))
        return AGON_NETP_INVALID;
    c->input[0]=AGON_NETP_SUBMIT;agon_net_put32(c->input+1,c->token);
    memcpy(c->input+5,p,n);result=agon_netp_call(c,n+5,0,0,&ignored);
    if(!result){c->pending=1;c->operation=p[3];c->query=agon_net_u32(p+8);}
    return result;
}
static inline uint8_t agon_netp_take(agon_netp_client*c,uint8_t*out,unsigned capacity,unsigned*length){
    uint8_t result;
    *length=0;
    if(!c->token)return AGON_NET_UNAVAILABLE;
    if(!out||capacity>AGON_NET_BODY||!capacity)return AGON_NETP_INVALID;
    c->input[0]=AGON_NETP_TAKE;agon_net_put32(c->input+1,c->token);
    result=agon_netp_call(c,5,out,capacity,length);
    if(result)return result; // TOO_SMALL retains record; FAULT retains ownership.
    if(!c->pending||*length<AGON_NET_HEADER||*length>capacity||
       memcmp(out,"NM\001",3)||out[3]!=(uint8_t)(c->operation|0x80)||
       agon_net_u32(out+4)!=c->token||agon_net_u32(out+8)!=c->query||
       out[12]!=*length-AGON_NET_HEADER||out[13]>AGON_NET_INVALID||
       (out[13]==AGON_NET_RECEIVED?c->operation!=AGON_NET_POLL:
        out[13]==AGON_NET_FAULT?out[12]!=1:out[12]!=0))return AGON_NET_PROTOCOL_ERROR;
    c->pending=0;return 0;
}
static inline uint8_t agon_netp_release(agon_netp_client*c){
    uint8_t result;unsigned ignored;
    if(!c->token)return 0;
    c->input[0]=AGON_NETP_RELEASE;agon_net_put32(c->input+1,c->token);
    result=agon_netp_call(c,5,0,0,&ignored);
    if(!result){c->token=0;c->pending=0;}
    return result; // BUSY/fault leaves object owned; caller must service cleanup.
}
#endif
