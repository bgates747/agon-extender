/* NET-003 experimental application network client. Keep this object static in
 * ordinary application RAM. Foreground, enabled IRQs, complete VDU boundaries.
 * EMOS owns every transport operation; app ISR copies replies, no direct I/O.
 * Return0 means local operation success,31 busy/not-ready, not game execution.
 * Caller's deadline/decision policy remains outside resident firmware. */
#ifndef AGON_APPLICATION_NET_H
#define AGON_APPLICATION_NET_H
#include <stdint.h>
#include <stddef.h>
#include <string.h>
// BEGIN canonical messages/wire.h
/* NET-003 matched development endpoint. No CRC/checksum, peripheral access or
 * game semantics. Canonical bytes are mirrored into EMOS and the C app include. */
#ifndef AGON_NET_WIRE_H
#define AGON_NET_WIRE_H
#include <stdint.h>
#define AGON_NET_VERSION 1
#define AGON_NET_VDU 0xF4
#define AGON_NET_REPLY 0x8F
#define AGON_NET_HEADER 14
#define AGON_NET_PAYLOAD 128
#define AGON_NET_BODY 142
#define AGON_NET_INPUT 147
#define AGON_NET_CONNECT 1
#define AGON_NET_POLL 2
#define AGON_NET_SEND 3
#define AGON_NET_CONNECTED 0
#define AGON_NET_CONNECTING 1
#define AGON_NET_RECEIVED 2
#define AGON_NET_ACCEPTED 3
#define AGON_NET_BUSY 4
#define AGON_NET_FAULT 5
#define AGON_NET_CLOSED 6
#define AGON_NET_INVALID 7
#define AGON_NET_LOCAL_OPEN 0
#define AGON_NET_LOCAL_TAKE 1
#define AGON_NET_LOCAL_SUBMIT 2
#define AGON_NET_LOCAL_RELEASE 3
/* Stable generic fault payload; socket errno stays in P4 diagnostics. */
#define AGON_NET_PEER_CLOSED 1
#define AGON_NET_CONNECT_FAILED 2
#define AGON_NET_CONNECT_TIMEOUT 3
#define AGON_NET_BAD_FRAME 4
#define AGON_NET_IO_FAILED 5
#define AGON_NET_LEASE_EXPIRED 6
static inline uint32_t agon_net_u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static inline void agon_net_put32(uint8_t*p,uint32_t v){p[0]=v;p[1]=v>>8;p[2]=v>>16;p[3]=v>>24;}
#endif
// END canonical messages/wire.h
#define AGON_NET_OK 0
#define AGON_NET_LOCAL_BUSY 31
#define AGON_NET_UNAVAILABLE 35
#define AGON_NET_PROTOCOL_ERROR 128
#define AGON_NET_QUERY_EXHAUSTED 129
#if defined(_EZ80)
#include <agon/mos.h>
static __attribute__((naked,noinline,unused)) uint24_t agon_net_native(uint8_t*request){
    __asm__ volatile("push ix\n ld ix,0\n add ix,sp\n push iy\n ld hl,(ix+6)\n"
                     "ld a,0x51\n rst.lil 08h\n ld hl,0\n ld l,a\n pop iy\n pop ix\n ret\n");
}
#ifndef AGON_NET_CALL
#define AGON_NET_CALL(request) agon_net_native(request)
#endif
#endif
#ifndef AGON_NET_CALL
#define AGON_NET_CALL(request) AGON_NET_UNAVAILABLE
#endif
#ifndef AGON_NET_CLOCK
#if defined(_EZ80)
#define AGON_NET_CLOCK() (*(volatile uint8_t*)mos_sysvars())
#else
#define AGON_NET_CLOCK() 0
#endif
#endif
#define AGON_NET_BARRIER() __asm__ volatile("" ::: "memory")
/* Optional owner adapter hooks. Defaults retain the synchronous ext.net ABI.
 * An async adapter must refuse BEFORE query/header/payload construction; a
 * later gateway BUSY cannot undo writes into an outstanding source borrow. */
#ifndef AGON_NET_PROVIDER
#define AGON_NET_PROVIDER "net"
#endif
#ifndef AGON_NET_OPEN_FRAME
#define AGON_NET_OPEN_FRAME(c) 1
#endif
#ifndef AGON_NET_SUBMIT_GUARD
#define AGON_NET_SUBMIT_GUARD(c) 0
#endif
#ifndef AGON_NET_RELEASED
#define AGON_NET_RELEASED(c) ((void)0)
#endif
#ifndef AGON_NET_BAD_OPEN
#define AGON_NET_BAD_OPEN(c) do { \
    (c)->input[0]=AGON_NET_LOCAL_RELEASE;(void)agon_net_exchange(c,1,0); \
} while(0)
#endif
typedef struct agon_net_client {
    uint8_t request[66],input[AGON_NET_INPUT],reply[AGON_NET_BODY];
    uint32_t token,query;
    volatile uint8_t pending,ready;
    uint8_t admitted,kind,reply_length,at,previous[3];
} agon_net_client;
static inline void agon_net_pointer(uint8_t*p,const void*v){
    uintptr_t n=(uintptr_t)v;p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);p[2]=(uint8_t)(n>>16);
}
static inline uint8_t agon_net_exchange(agon_net_client*c,unsigned n,unsigned capacity){
    uint8_t*r=c->request;memset(r,0,66);r[0]=66;r[2]=1;r[4]=3;r[5]=sizeof(AGON_NET_PROVIDER)-1;r[6]=2;
    memcpy(r+25,"ext",3);memcpy(r+41,AGON_NET_PROVIDER,sizeof(AGON_NET_PROVIDER)-1);
    agon_net_pointer(r+10,c->input);r[13]=(uint8_t)n;
    if(capacity){agon_net_pointer(r+16,c->reply);r[19]=(uint8_t)capacity;}
    return (uint8_t)AGON_NET_CALL(r);
}
static inline uint8_t agon_net_begin(agon_net_client*c){
    uint8_t r;if(c->admitted)return AGON_NET_LOCAL_BUSY;
    c->input[0]=AGON_NET_LOCAL_OPEN;r=agon_net_exchange(c,AGON_NET_OPEN_FRAME(c),7);
    if(!r&&(c->request[22]!=7||c->request[23]||c->request[24]||
       !agon_net_u32(c->reply)||c->reply[3])){
        AGON_NET_BAD_OPEN(c);
        return AGON_NET_PROTOCOL_ERROR;
    }
    if(!r){c->token=agon_net_u32(c->reply);c->query=0;c->pending=c->ready=0;c->admitted=1;c->reply_length=0;memcpy(c->previous,c->reply+4,3);}
    return r;
}
static inline uint8_t agon_net_release(agon_net_client*c){
    uint8_t r;c->input[0]=AGON_NET_LOCAL_RELEASE;r=agon_net_exchange(c,1,0);
    if(!r){c->admitted=c->pending=c->ready=0;c->token=c->query=0;AGON_NET_RELEASED(c);}
    return r;
}
static inline uint8_t agon_net_submit(agon_net_client*c,uint8_t kind,const void*payload,uint8_t length){
    uint8_t*r=c->input+5,result;
    if(!c->admitted)return AGON_NET_UNAVAILABLE;
    if(c->pending)return AGON_NET_LOCAL_BUSY;
    result=AGON_NET_SUBMIT_GUARD(c);if(result)return result;
    if(kind<1||kind>3||length>AGON_NET_PAYLOAD||(length&&!payload)||
       (kind==1?length!=6:kind==2?length!=0:0))return 19;
    if(c->query==UINT32_MAX)return AGON_NET_QUERY_EXHAUSTED;
    ++c->query;memset(r,0,AGON_NET_HEADER);r[0]='N';r[1]='M';r[2]=1;r[3]=kind;
    agon_net_put32(r+4,c->token);agon_net_put32(r+8,c->query);r[12]=length;
    if(length)memcpy(r+AGON_NET_HEADER,payload,length);
    c->input[0]=AGON_NET_LOCAL_SUBMIT;c->input[1]=23;c->input[2]=0;c->input[3]=AGON_NET_VDU;
    c->input[4]=AGON_NET_HEADER+length;
    c->kind=kind;c->at=(uint8_t)AGON_NET_CLOCK();c->ready=0;
    AGON_NET_BARRIER();c->pending=1;
    // Arm before sending: UART IRQ can deliver reply before serializer returns.
    result=agon_net_exchange(c,5+AGON_NET_HEADER+length,0);
    if(result){c->pending=c->ready=0;if(result!=AGON_NET_LOCAL_BUSY)c->admitted=0;}
    return result;
}
/* Classifier reads only the four bytes every ordinary KEY payload has.
 * Key down/up values0/1 cannot collide with the reply-kind high bit. EMOS
 * validates the actual NM frame length before invoking the existing callback. */
static inline int agon_net_is_reply(const uint8_t*p){
    return !memcmp(p,"NM\001",3)&&p[3]>=0x81&&p[3]<=0x83;
}
/* ISR only: caller chains non-NM packets to its saved vector. No MOS call,
 * allocation, wait or consumer work; payload is borrowed until ISR returns. */
static inline void agon_net_receive(agon_net_client*c,const uint8_t*p){
    if(!c->pending||c->ready||!agon_net_is_reply(p)||p[12]>AGON_NET_PAYLOAD||
       agon_net_u32(p+4)!=c->token||agon_net_u32(p+8)!=c->query)return;
    uint8_t n=AGON_NET_HEADER+p[12];memcpy(c->reply,p,n);
    AGON_NET_BARRIER();c->ready=n;
}
static inline uintptr_t agon_net_previous(const agon_net_client*c){
    return (uintptr_t)c->previous[0]|((uintptr_t)c->previous[1]<<8)|((uintptr_t)c->previous[2]<<16);
}
static inline uint8_t agon_net_take(agon_net_client*c){
    uint8_t n;
    if(!c->admitted)return AGON_NET_UNAVAILABLE;
    if(!c->pending)return AGON_NET_LOCAL_BUSY;
    n=c->ready;AGON_NET_BARRIER();
    if(!n){
        if((uint8_t)((uint8_t)AGON_NET_CLOCK()-c->at)<30)return AGON_NET_LOCAL_BUSY;
        (void)agon_net_release(c);return AGON_NET_UNAVAILABLE;
    }
    c->pending=0;
    if(n<AGON_NET_HEADER||n>AGON_NET_BODY||
       memcmp(c->reply,"NM\001",3)||c->reply[3]!=(uint8_t)(c->kind|0x80)||
       agon_net_u32(c->reply+4)!=c->token||agon_net_u32(c->reply+8)!=c->query||
       c->reply[12]!=n-AGON_NET_HEADER||c->reply[13]>AGON_NET_INVALID||
       (c->reply[13]==AGON_NET_RECEIVED?c->kind!=AGON_NET_POLL:
        c->reply[13]==AGON_NET_FAULT?c->reply[12]!=1:c->reply[12]!=0)){
        (void)agon_net_release(c);return AGON_NET_PROTOCOL_ERROR;
    }
    c->reply_length=n;return AGON_NET_OK;
}
static inline uint8_t agon_net_status(const agon_net_client*c){return c->reply[13];}
static inline uint8_t agon_net_size(const agon_net_client*c){return c->reply[12];}
static inline const uint8_t*agon_net_data(const agon_net_client*c){return c->reply+AGON_NET_HEADER;}
#endif
