/* Actual SDK + unchanged core + actual owner C; fake registers only.
 * Reuse the lifetime harness without duplicating its owner/gateway model.
 * No native ISR, timer or hardware execution is implied by this check. */
static void notify(void *);
#define AGON_NETA_NOTIFY(c) notify(c)
#define main original_composition_main
#include "rx_scope.c"
#undef main

static unsigned notifications, releases, tails, idles, faults;
static unsigned source_before_return;
static volatile unsigned sticky;
static void notify(void *value) {
    agon_neta_client *c=value;
    assert(c==active && c==agon_neta_active && !irq && reserved);
    ++notifications;sticky=1;
    if(c->source_released && c->tx.phase==U1_TAIL) {
        /* Callback publication, not pre-write TEMT, has released the source. */
        assert(!c->tx.source && !c->tx.remaining && !c->tx.callback);
        ++releases;
        if(finish_before_return)++source_before_return;
    }
    if(c->tx.phase==U1_TAIL)++tails;
    if(c->tx.phase==U1_IDLE)++idles;
    if(c->tx.phase==U1_FAULT) {
        assert(c->tx.fault!=U1_NO_FAULT);++faults;
    }
}

int main(void) {
    (void)notify; /* Old-header negative control still compiles before failing. */
    void *ram=mmap((void*)0x40000,0x20000,PROT_READ|PROT_WRITE,
                  MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
    assert(ram==(void*)0x40000);agon_neta_client *c=ram;
    unsigned prior;

    fresh(c);assert(!notifications); /* OPEN/initial IDLE is not a transition. */
    stop=1;assert(!agon_net_submit(&c->net,AGON_NET_POLL,0,0));
    assert(notifications==1 && sticky && c->tx.phase==U1_SOURCE);
    sticky=0;prior=notifications;
    for(unsigned i=0;i<20;++i)tick();
    assert(notifications==prior && !sticky); /* CTS/no-progress cannot spin. */
    /* Same service START refusal has no state change and no wake. */
    irq=0;assert(agon_neta_service(1,0)==U1_BUSY);irq=1;
    assert(notifications==prior);
    /* Early NM reply/TAKE cannot reuse the source or retire ownership. */
    reply_due=1;tick();assert(!agon_net_take(&c->net));
    assert(agon_net_submit(&c->net,AGON_NET_POLL,0,0)==31);
    assert(agon_neta_close(c)==31 && agon_neta_active==c && reserved);
    assert(notifications==prior && !sticky);
    stop=0;lsr=0x20;tick();assert(bytes==16 && notifications==prior);
    lsr=0x20;tick();
    assert(c->source_released && c->tx.phase==U1_TAIL);
    assert(notifications==prior+2 && releases==2 && tails==2 && sticky);
    /* Source and phase notifications coalesce; neither is physical drain. */
    sticky=0;prior=notifications;
    for(unsigned i=0;i<20;++i){lsr=0;assert(agon_neta_progress(c)==31);}
    assert(notifications==prior && !sticky && agon_neta_close(c)==31);
    lsr=0x60;assert(!agon_neta_progress(c));
    assert(c->tx.phase==U1_IDLE && idles==1 && notifications==prior+1);
    sticky=0;prior=notifications;
    for(unsigned i=0;i<20;++i)assert(!agon_neta_progress(c));
    assert(notifications==prior && !sticky);
    assert(!agon_neta_close(c) && !reserved && !agon_neta_active);
    assert(notifications==prior); /* Positive foreground detach adds no hook. */

    /* An existing source callback may publish before SUBMIT returns. */
    fresh(c);finish_before_return=1;prior=notifications;
    assert(!agon_net_submit(&c->net,AGON_NET_POLL,0,0));
    assert(source_before_return==2 && c->source_released && sticky);
    assert(notifications==prior+3);finish_before_return=0;
    lsr=0x60;assert(!agon_neta_close(c));

    /* First error is published before notification; close still refuses. */
    fresh(c);stop=1;assert(!agon_net_submit(&c->net,AGON_NET_POLL,0,0));
    const uint8_t *borrow=c->tx.source;prior=notifications;error=2;tick();
    assert(faults==1 && notifications==prior+1 && c->tx.fault_error==2);
    assert(c->tx.source==borrow && !c->source_released);
    sticky=0;prior=notifications;
    for(unsigned i=0;i<20;++i){irq=0;agon_neta_service(2,2);irq=1;}
    assert(notifications==prior && !sticky); /* Retained same fault is quiet. */
    assert(agon_neta_close(c)==35 && reserved && agon_neta_active==c);
    /* Owner abort does not invent a source/drain/health notification. */
    emos_net_reset();assert(!reserved && pending_fault);
    assert(agon_neta_progress(c)==35 && c->tx.source==borrow);
    assert(notifications==prior);
    puts("actual SDK notify: publication, transitions, quiet service, early source, retained lifetime PASS");
}
