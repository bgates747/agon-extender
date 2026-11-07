/* NET-004 provisional ext.neta adapter: APPLICATION RAM, one client/source.
 * Include this INSTEAD OF net.h in the single transport-owning C unit. Link
 * UART's pinned, unchanged u1_tx.c/u1_emit.src; do not install its vanilla IRQ.
 * Requires the separately matched INTEG-024 EMOS owner; old ROM refuses neta.
 * No callback/IRQ may invoke MOS, EI, allocate, log, wait or reenter this API.
 * Source release, later TEMT, and NM reply remain independent. On refused
 * close/fault retain this object, source, code and callback storage. No replay.
 */
#ifndef AGON_APPLICATION_NET_ASYNC_H
#define AGON_APPLICATION_NET_ASYNC_H
#ifdef AGON_APPLICATION_NET_H
#error "Include net_async.h instead of net.h in the transport-owning unit"
#endif
#include "u1_tx.h"
struct agon_net_client;
static uint8_t agon_neta_open_frame(struct agon_net_client *);
static uint8_t agon_neta_guard(struct agon_net_client *);
static void agon_neta_released(struct agon_net_client *);
static void agon_neta_bad_open(struct agon_net_client *);
#define AGON_NET_PROVIDER "neta"
#define AGON_NET_OPEN_FRAME(c) agon_neta_open_frame(c)
#define AGON_NET_SUBMIT_GUARD(c) agon_neta_guard(c)
#define AGON_NET_RELEASED(c) agon_neta_released(c)
#define AGON_NET_BAD_OPEN(c) agon_neta_bad_open(c)
#include "net.h"

typedef struct {
    agon_net_client net;
    u1_tx tx;
    volatile uint8_t source_released;
    uint8_t open_valid;
} agon_neta_client;
/* This pointer and every engine field are in the application's BSS, not EMOS. */
static agon_neta_client *agon_neta_active;
uint8_t u1_emit_uart1(const uint8_t *,uint8_t);

static void agon_neta_source_done(void){agon_neta_active->source_released=1;}
/* Private matched ordinary C hook, called by EMOS with interrupts excluded and
 * both register sets protected. event:0 shared RX-first sample,1 admit source,
 * 2 owner fault. sample carries LSR bits with DR replaced by active-high STOP
 * from PC3. Return for service:0 idle,1 TX,2 CTS retry,3 tail,4 retained fault.
 * START returns an admission result, before any byte is emitted. */
static uint8_t agon_neta_service(uint8_t event,uint8_t sample){
    agon_neta_client*c=agon_neta_active;
    if(event==1)return u1_start(&c->tx,c->net.input+1,c->net.request[13]-1,agon_neta_source_done);
    if(event==2)u1_report_fault(&c->tx,sample?U1_LINE_ERROR:U1_OWNER_LOST,sample);
    else {
        u1_sample s={1,(sample&0x20)!=0,(sample&1)==0,(sample&0x40)!=0,sample&0x9e};
        (void)u1_step(&c->tx,s,u1_emit_uart1);
    }
    if(c->tx.phase==U1_FAULT)return 4;
    if(c->tx.phase==U1_IDLE)return 0;
    if(c->tx.phase==U1_TAIL)return 3;
    return sample&1?2:1;
}
static uint8_t agon_neta_open_frame(agon_net_client*c){
    agon_net_pointer(c->input+1,(const void*)agon_neta_service);return 4;
}
/* Foreground, enabled IRQs. Only selector input[0] changes here, outside the
 * input+1 TX span. EMOS performs bounded RX/service and positive later TEMT. */
static inline uint8_t agon_neta_progress(agon_neta_client*c){
    uint8_t r;
    /* NM admission can be cleared by a failed SUBMIT while the separately
     * attached service hook still exists. Keep progress/cleanup available via
     * this association; only positive RELEASE retires it. */
    if(agon_neta_active!=c)return AGON_NET_UNAVAILABLE;
    c->net.input[0]=4;AGON_NET_BARRIER();r=agon_net_exchange(&c->net,1,0);AGON_NET_BARRIER();
    return r;
}
static uint8_t agon_neta_guard(agon_net_client*c){
    agon_neta_client*a=agon_neta_active;uint8_t r;
    if(!a||&a->net!=c||!a->open_valid)return AGON_NET_UNAVAILABLE;
    r=agon_neta_progress(a);
    if(r)return r;
    if(a->tx.phase!=U1_IDLE)return AGON_NET_LOCAL_BUSY;
    a->source_released=0;return 0;
}
static void agon_neta_released(agon_net_client*c){
    agon_neta_client*a=agon_neta_active;
    if(a && &a->net==c&&u1_detach(&a->tx)==0)agon_neta_active=0;
}
static void agon_neta_bad_open(agon_net_client*c){
    /* OPEN returned success, so a hook may exist despite its malformed reply.
     * Keep a cleanup handle until RELEASE positively removes it. Do not let
     * this provisional ownership admit payloads with an unvalidated token. */
    c->admitted=1;c->pending=c->ready=0;c->token=c->query=0;
    (void)agon_net_release(c);
}
static inline uint8_t agon_neta_begin(agon_neta_client*c){
    uint8_t r;
    if(agon_neta_active||c->net.admitted)return AGON_NET_LOCAL_BUSY;
    r=u1_init(&c->tx,16,16);if(r)return r;
    agon_neta_active=c;c->source_released=0;c->open_valid=0;
    r=agon_net_begin(&c->net);
    if(!r)c->open_valid=1;
    else if(!c->net.admitted)agon_neta_active=0;
    return r;
}
static inline uint8_t agon_neta_close(agon_neta_client*c){
    uint8_t r;
    if(agon_neta_active!=c)return AGON_NET_UNAVAILABLE;
    r=agon_neta_progress(c);if(r)return r;
    return agon_net_release(&c->net);
}
#endif
