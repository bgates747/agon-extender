/* Actual app adapter + unchanged UART core + actual EMOS net/neta C.
 * Host substitutes hardware only; no electrical/IRQ-machine execution claim. */
#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <stdio.h>
static uint32_t gateway(uint8_t *);
static uint8_t clock_byte;
#define AGON_NET_CALL(r) gateway(r)
#define AGON_NET_CLOCK() clock_byte
#include <agon/net_async.h>

extern uint32_t emos_neta_gateway(void *),emos_net_gateway(void *);
extern void emos_neta_service(uint8_t),emos_neta_tick(void),emos_net_reset(void);
extern void emos_net_packet(const uint8_t*,uint8_t);
uint8_t test_ier=1,uart1_keyboard_owned=1,emos_key_source=2,emos_key_faulted;
uint32_t user_kbvector=0x456789;
static uint8_t irq=1,reserved,stop,lsr=0x60,error,reply_due;
static unsigned bursts,bytes,rx_visits,forced_rx;
static uint8_t finish_before_return,bad_open,refuse_close,refuse_submit;
static uint8_t wire[512];
static agon_neta_client *active;
uint8_t emos_application_context(void){return 1;}
uint8_t emos_application_span(uint32_t p,uint32_t n){
    return (p>=0x40000&&p<0xb0000&&n<=0xb0000-p)||
        (p==(uint32_t)(uintptr_t)agon_neta_service&&n==1);
}
uint32_t emos_read24(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16);}
uint8_t emos_get_mode(void){return 0;}
uint8_t emos_keyboard_lock(void){uint8_t v=irq;irq=0;return v;}
void emos_keyboard_unlock(uint8_t v){irq=v;}
uint8_t emos_keyboard_app_reserve(void){assert(!irq);if(reserved)return 3;reserved=1;return 1;}
void emos_keyboard_app_release(uint8_t fault){assert(!irq);assert(reserved);reserved=0;if(fault)emos_key_faulted=1;}
uint8_t emos_keyboard_send(const uint8_t*p,uint16_t n){(void)p;(void)n;assert(!reserved);return 0;}
void emos_neta_tx_irq(uint8_t enabled){assert(!irq);test_ier=(test_ier&~2)|(enabled?2:0);}
uint8_t emos_neta_cts(void){assert(!irq);return stop?8:0;}
void emos_reply_callback(const uint8_t*p){assert(!irq);agon_net_receive(&active->net,p);}
static void reply(uint8_t status){
    uint8_t p[14]={'N','M',1,(uint8_t)(active->net.kind|128)};
    agon_net_put32(p+4,active->net.token);agon_net_put32(p+8,active->net.query);p[13]=status;
    emos_net_packet(p,sizeof p);
}
void uart1_keyboard_irq(void){
    assert(!irq);++rx_visits;
    if(forced_rx>=16){forced_rx-=16;return;} /* cap defers TX, no stale data sample */
    if(reply_due){reply_due=0;reply(AGON_NET_ACCEPTED);}
    emos_neta_service(lsr|error);
}
uint8_t u1_emit_uart1(const uint8_t*p,uint8_t n){
    assert(!irq&&reserved&&!stop&&(lsr&0x20)&&!error);
    assert(n&&n<=16&&bytes+n<=sizeof wire);memcpy(wire+bytes,p,n);bytes+=n;++bursts;
    lsr=0;return 1;
}
static uint32_t gateway(uint8_t*r){
    assert(r[5]==4&&!memcmp(r+41,"neta",4));
    uint8_t op=active->net.input[0];
    if(op==3&&refuse_close)return 31; /* owner refusal boundary, hook stays live */
    if(op==2&&refuse_submit)return 35; /* refusal before source acceptance */
    uint32_t result=emos_neta_gateway(r);
    if(op==0&&!result&&bad_open)r[22]=6;
    if(op==2&&!result&&finish_before_return){
        irq=0;while(active->tx.phase==U1_SOURCE){lsr=0x20;uart1_keyboard_irq();}irq=1;
    }
    return result;
}
static void tick(void){assert(irq);irq=0;emos_neta_tick();irq=1;}
static void fresh(agon_neta_client*c){
    memset(c,0,sizeof(*c));active=c;bytes=bursts=rx_visits=0;lsr=0x60;stop=error=reply_due=0;
    assert(agon_neta_begin(c)==0);assert(reserved&&c->net.admitted);
}
static void drain(agon_neta_client*c,unsigned n){
    while(c->tx.phase==U1_SOURCE){unsigned prior=bytes;lsr=0x20;tick();assert(bytes>prior);}
    assert(bytes==n&&c->source_released&&c->tx.phase==U1_TAIL);
    assert(agon_neta_close(c)==31&&c->net.admitted&&reserved);
    lsr=0x60;assert(agon_neta_progress(c)==0&&c->tx.phase==U1_IDLE);
}
int main(void){
    void*ram=mmap((void*)0x40000,0x20000,PROT_READ|PROT_WRITE,
                 MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(ram==(void*)0x40000);agon_neta_client*c=ram;
    uint8_t payload[128],saved[146];for(unsigned i=0;i<128;++i)payload[i]=(uint8_t)i;
    fresh(c);stop=1;
    assert(agon_net_submit(&c->net,AGON_NET_SEND,payload,128)==0);
    assert(!bytes&&!c->source_released&&!(test_ier&2));
    for(int i=0;i<8;++i)tick();assert(!bytes&&c->tx.phase==U1_SOURCE);
    memcpy(saved,c->net.input+1,146);uint32_t query=c->net.query;
    /* Reply before release, TAKE, then new SUBMIT must not rewrite borrow. */
    reply_due=1;tick();assert(agon_net_take(&c->net)==0&&!c->net.pending);
    assert(agon_net_submit(&c->net,AGON_NET_POLL,0,0)==31);
    assert(c->net.query==query&&!memcmp(saved,c->net.input+1,146));
    assert(agon_net_release(&c->net)==31&&c->net.admitted&&reserved);
    stop=0;forced_rx=16;tick();assert(!bytes);tick();assert(bytes==16&&bursts==1);
    drain(c,146);assert(bursts==10&&!memcmp(saved,wire,146));
    assert(agon_neta_close(c)==0&&!reserved&&!agon_neta_active&&c->tx.phase==U1_DETACHED);
    /* Masked call refuses without accepting/publishing or touching query. */
    fresh(c);irq=0;assert(agon_net_submit(&c->net,AGON_NET_POLL,0,0)==31);irq=1;
    assert(c->net.query==0&&!bytes);assert(agon_neta_close(c)==0);
    /* Very short source may release before SUBMIT returns. TEMT still later. */
    fresh(c); /* POLL wire18, so force one-byte remaining via bounded SEND0 below */
    assert(agon_net_submit(&c->net,AGON_NET_POLL,0,0)==0);assert(bytes==16);
    lsr=0x20;tick();assert(bytes==18&&c->source_released&&c->tx.phase==U1_TAIL);
    clock_byte=31;assert(agon_net_take(&c->net)==35);assert(c->net.admitted&&reserved);
    assert(c->tx.phase==U1_TAIL&&agon_neta_close(c)==31);
    lsr=0x60;assert(agon_neta_close(c)==0);
    /* Source callback can run after MOS unlock but before SDK SUBMIT returns. */
    fresh(c);finish_before_return=1;
    assert(agon_net_submit(&c->net,AGON_NET_POLL,0,0)==0);
    assert(c->source_released&&c->tx.phase==U1_TAIL&&bytes==18);
    finish_before_return=0;lsr=0x60;assert(agon_neta_close(c)==0);
    /* Invalid early reply cannot detach live source/tail. */
    clock_byte=0;fresh(c);stop=1;assert(agon_net_submit(&c->net,AGON_NET_POLL,0,0)==0);
    irq=0;reply(99);irq=1;assert(agon_net_take(&c->net)==128);
    assert(c->net.admitted&&reserved&&c->tx.phase==U1_SOURCE);
    stop=0;drain(c,18);assert(agon_neta_close(c)==0);
    /* Malformed successful OPEN + refused cleanup retains app association.
     * This is a synthetic provider-output/refusal ordering, not a live defect. */
    memset(c,0,sizeof(*c));active=c;bad_open=refuse_close=1;
    assert(agon_neta_begin(c)==128&&agon_neta_active==c&&reserved);
    assert(c->net.admitted&&!c->open_valid&&c->net.token==0);
    assert(agon_net_submit(&c->net,AGON_NET_POLL,0,0)==35&&c->net.query==0);
    irq=0;uart1_keyboard_irq();irq=1; /* still-installed hook remains callable */
    assert(agon_neta_close(c)==31&&agon_neta_active==c);
    bad_open=refuse_close=0;assert(agon_neta_close(c)==0&&!agon_neta_active&&!reserved);
    /* A rejected SUBMIT clears NM admission, not the hook cleanup handle. */
    fresh(c);refuse_submit=1;
    assert(agon_net_submit(&c->net,AGON_NET_POLL,0,0)==35&&!c->net.admitted);
    assert(agon_neta_active==c&&reserved&&c->tx.phase==U1_IDLE);
    refuse_submit=0;assert(agon_neta_close(c)==0&&!reserved&&!agon_neta_active);
    /* One shared error sample records fault and never releases borrowed source. */
    fresh(c);stop=1;assert(agon_net_submit(&c->net,AGON_NET_POLL,0,0)==0);
    const uint8_t*borrow=c->tx.source;error=2;tick();
    assert(c->tx.phase==U1_FAULT&&c->tx.source==borrow&&!c->source_released);
    assert(agon_neta_close(c)==35&&reserved&&c->net.admitted&&!(test_ier&2));
    /* Abnormal application exit atomically removes hook and poisons stream. */
    emos_net_reset();assert(!reserved&&emos_key_faulted);
    assert(agon_neta_progress(c)==35&&c->tx.source==borrow);
    assert(irq&&rx_visits);puts("actual app/core/EMOS composition: lifetime, RX-first, CTS, tail, detach PASS");
}
